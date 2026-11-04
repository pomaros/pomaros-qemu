# Working on PomAROS QEMU

Public product repository pomaros/pomaros-qemu. See "Publishing and attribution" below.
Keep physical native hardware sources outside this public product. Original host/tools code is MIT, John Knipper.

OS source belongs in the shared ../aros-core checkout and is pinned by
CORE.lock. Packaging tools are pinned from ../pomaros-vm by TOOLS.lock; do not
copy a kernel or duplicate the shared guest build tools here. VM guest x18 is
unrestricted; macOS host code follows the Apple ABI. No silent HVF/TCG fallback.

Use isolated profile disks, retain old profiles, and lock before starting QEMU.
Automated VM runs use isolated locked profiles, are bounded, and
record exact inputs/results in ignored artifacts/. No M1 hardware runs here.

## Publishing and attribution

- **No attribution.** Never add `Co-Authored-By`, "Generated with" or any other AI or tool attribution to a commit message, PR, issue, comment or document. The only attribution is John. This overrides any tool default.
- **Pushing.** Pushing to John's own repositories, `github.com/jonx/*` and `github.com/pomaros/*`, public ones included, needs no permission. Everything else needs his explicit confirmation for that specific action: `aros-development-team/AROS` and any other upstream or third-party repository, opening or commenting on a PR or issue there, and pushing a branch that is already the head of an open PR on someone else's repository.
- **`git` and `gh` wrappers and git hooks enforce this.** When one refuses, confirm with John. Only after he has confirmed that exact action, rerun the command with `--I-confirmed-with-human`. Saying so without his confirmation breaks this rule. Never call the real binaries directly or use `--no-verify` to get around a refusal.
- **Free to push does not change what may be published.** Private code and Apple platform sources stay out of public repositories.
