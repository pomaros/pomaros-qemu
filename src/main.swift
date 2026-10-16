// SPDX-License-Identifier: MIT
// Copyright (c) 2026 John Knipper
import AppKit
import Darwin

func failure(_ text: String) -> NSError {
    NSError(domain: "PomAROSQEMU", code: 1, userInfo: [NSLocalizedDescriptionKey: text])
}
func regular(_ path: URL) throws {
    let values = try path.resourceValues(forKeys: [.isRegularFileKey, .isSymbolicLinkKey])
    guard values.isRegularFile == true && values.isSymbolicLink != true else {
        throw failure("Expected an ordinary file: \(path.path)")
    }
}
func directory(_ path: URL) throws {
    try FileManager.default.createDirectory(at: path, withIntermediateDirectories: true,
                                          attributes: [.posixPermissions: 0o700])
    let values = try path.resourceValues(forKeys: [.isDirectoryKey, .isSymbolicLinkKey])
    guard values.isDirectory == true && values.isSymbolicLink != true else {
        throw failure("Expected a private directory: \(path.path)")
    }
}
struct Options {
    var resources: URL = Bundle.main.resourceURL!
    var profile: URL = FileManager.default.homeDirectoryForCurrentUser
        .appendingPathComponent("Library/Application Support/PomAROS QEMU/Default", isDirectory: true)
    var accel = "hvf"
    var inspect = false
    var headless = false
    var timeout: Double? = nil
    init(_ arguments: [String]) throws {
        var i = 0
        while i < arguments.count {
            let key = arguments[i]
            if key == "--inspect" { inspect = true }
            else if key == "--headless" { headless = true }
            else if ["--resources", "--profile", "--accel", "--timeout"].contains(key) {
                i += 1
                guard i < arguments.count else { throw failure("Missing value for \(key)") }
                let value = arguments[i]
                if key == "--resources" { resources = URL(fileURLWithPath: value, isDirectory: true) }
                if key == "--profile" { profile = URL(fileURLWithPath: value, isDirectory: true) }
                if key == "--accel" { accel = value }
                if key == "--timeout" {
                    guard let t = Double(value), t > 0, t <= 3600, t.isFinite else { throw failure("Invalid timeout") }
                    timeout = t
                }
            } else { throw failure("Unknown option: \(key)") }
            i += 1
        }
        guard ["hvf", "tcg"].contains(accel) else { throw failure("Select hvf or tcg explicitly") }
        if let override = ProcessInfo.processInfo.environment["POMAROS_QEMU_STATE_DIRECTORY"] {
            profile = URL(fileURLWithPath: override, isDirectory: true)
        }
    }
}
func run(_ options: Options) throws -> Int32 {
    let fm = FileManager.default
    let configURL = options.resources.appendingPathComponent("launch.json")
    try regular(configURL)
    let object = try JSONSerialization.jsonObject(with: Data(contentsOf: configURL))
    guard let config = object as? [String: String], let executable = config["qemu"],
          let firmware = config["firmware"], config["machine"] == "virt-11.0" else {
        throw failure("Invalid or unsupported launch configuration")
    }
    let qemu = URL(fileURLWithPath: executable)
    let efi = options.resources.appendingPathComponent(firmware)
    let seed = options.resources.appendingPathComponent("System.img")
    try regular(qemu); try regular(efi); try regular(seed)
    guard fm.isExecutableFile(atPath: qemu.path) else { throw failure("QEMU is missing. Install QEMU 11 with Homebrew and rebuild the app.") }
    let version = Process(); version.executableURL = qemu; version.arguments = ["--version"]
    let versionPipe = Pipe(); version.standardOutput = versionPipe; version.standardError = versionPipe
    try version.run()
    let versionData = versionPipe.fileHandleForReading.readDataToEndOfFile(); version.waitUntilExit()
    let versionText = String(decoding: versionData, as: UTF8.self)
    guard version.terminationStatus == 0 && versionText.contains("version 11.") else {
        throw failure("This package requires QEMU 11; rebuild and qualify after changing QEMU.")
    }
    try directory(options.profile)
    let lockURL = options.profile.appendingPathComponent("profile.lock")
    let fd = open(lockURL.path, O_RDWR | O_CREAT | O_NOFOLLOW, 0o600)
    guard fd >= 0 else { throw failure("Cannot lock the selected profile") }
    defer { close(fd) }
    guard flock(fd, LOCK_EX | LOCK_NB) == 0 else { throw failure("This PomAROS QEMU profile is already running") }
    defer { flock(fd, LOCK_UN) }
    let disk = options.profile.appendingPathComponent("system.img")
    if !fm.fileExists(atPath: disk.path) {
        let temporary = options.profile.appendingPathComponent(".seed-" + UUID().uuidString)
        defer { try? fm.removeItem(at: temporary) }
        try fm.copyItem(at: seed, to: temporary)
        try fm.moveItem(at: temporary, to: disk)
    }
    try regular(disk)
    // QEMU -blockdev JSON handles profile paths containing commas and spaces.
    let drive: [String: Any] = ["driver": "raw", "node-name": "system",
        "file": ["driver": "file", "filename": disk.path], "cache": ["direct": false, "no-flush": false]]
    let driveJSON = String(decoding: try JSONSerialization.data(withJSONObject: drive, options: [.sortedKeys]), as: UTF8.self)
    let serial = options.profile.appendingPathComponent("serial.log")
    let firmwareSerial = options.profile.appendingPathComponent("firmware.log")
    for path in [serial, firmwareSerial] where fm.fileExists(atPath: path.path) {
        try regular(path)
    }
    // chardev filename syntax uses comma doubling; JSON blockdev is used for the disk.
    func escaped(_ text: String) -> String { text.replacingOccurrences(of: ",", with: ",,") }
    var args = ["-name", "PomAROS QEMU", "-accel", options.accel, "-M", "virt-11.0,acpi=on,gic-version=3,msi=gicv2m",
                "-cpu", options.accel == "hvf" ? "host" : "cortex-a72", "-m", "512", "-smp", "1",
                "-bios", efi.path, "-blockdev", driveJSON,
                "-device", "virtio-blk-pci,drive=system,disable-legacy=on",
                "-device", "virtio-gpu-pci,id=gpu,xres=1024,yres=768",
                "-device", "qemu-xhci,id=xhci", "-device", "usb-kbd,bus=xhci.0", "-device", "usb-tablet,bus=xhci.0",
                "-netdev", "user,id=net", "-device", "virtio-net-pci,netdev=net,disable-legacy=on",
                "-device", "virtio-rng-pci,disable-legacy=on", "-display", options.headless ? "none" : "cocoa",
                "-chardev", "file,id=firmware,path=" + escaped(firmwareSerial.path), "-serial", "chardev:firmware",
                "-chardev", "file,id=vmconsole,path=" + escaped(serial.path),
                "-device", "virtio-serial-pci,disable-legacy=on,id=vmconsole",
                "-device", "virtconsole,chardev=vmconsole,bus=vmconsole.0,name=aros.console", "-no-reboot"]
    if options.inspect { args += ["-S"] }
    let command: [String: Any] = ["executable": qemu.path, "arguments": args, "version": versionText,
                                 "seed": seed.path, "profile": options.profile.path]
    let commandData = try JSONSerialization.data(withJSONObject: command, options: [.prettyPrinted, .sortedKeys])
    try commandData.write(to: options.profile.appendingPathComponent("command.json"), options: .atomic)
    if options.inspect { print(String(decoding: commandData, as: UTF8.self)); return 0 }
    let log = options.profile.appendingPathComponent("qemu.log")
    if !fm.fileExists(atPath: log.path) { fm.createFile(atPath: log.path, contents: nil) }
    try regular(log)
    let stream = try FileHandle(forWritingTo: log); defer { try? stream.close() }
    try stream.truncate(atOffset: 0)
    let process = Process(); process.executableURL = qemu; process.arguments = args
    process.standardOutput = stream; process.standardError = stream
    try process.run()
    if let timeout = options.timeout {
        DispatchQueue.global().asyncAfter(deadline: .now() + timeout) {
            if process.isRunning { process.terminate() }
        }
    }
    process.waitUntilExit()
    return process.terminationStatus
}
do {
    let options = try Options(Array(CommandLine.arguments.dropFirst()))
    let result = try run(options)
    if result != 0 { throw failure("QEMU stopped with status \(result). See qemu.log in the profile.") }
} catch {
    fputs("PomAROS QEMU: \(error.localizedDescription)\n", stderr)
    if Bundle.main.bundleURL.pathExtension == "app" {
        let alert = NSAlert(); alert.messageText = "PomAROS QEMU could not start"
        alert.informativeText = error.localizedDescription; alert.runModal()
    }
    exit(1)
}
