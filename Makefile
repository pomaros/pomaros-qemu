# SPDX-License-Identifier: MIT
# Copyright (c) 2026 John Knipper
.PHONY: all test package
all: build/pomaros-qemu
build:
	mkdir -p $@
build/pomaros-qemu: src/main.swift entitlements.plist | build
	swiftc -target arm64-apple-macos13.0 -O -warnings-as-errors -framework AppKit src/main.swift -o $@
	codesign --force --sign - --entitlements entitlements.plist $@
test: all
	python3 -m unittest discover -s tests -p 'test_*.py'
package: all
	python3 tools/package-app.py --esp "$(ESP)" --output "$(OUTPUT)"
