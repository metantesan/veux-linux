# Contributor and agent instructions

## Scope

This is the public mainline Linux development repository for Xiaomi Redmi Note
11 Pro 5G (`veux`, SM6375). Work here rather than importing local worklogs,
handoffs, raw captures or generated files from another workspace.

- Keep the README hardware table and known bugs accurate.
- Preserve the prominent disclosure of substantial AI involvement, upstream
  credits, copyright notices and SPDX identifiers.
- Do not claim a successful build, image check or hardware result interchangeably.
- Camera and haptics remain experimental. The screen can turn green when
  entering sleep; this bug is unresolved.
- Do not spawn subagents unless the user explicitly requests them.

## Preserve the working display

The Holi display, K6S panel, DSI/DPU sequencing and shared interconnect path
required substantial device-specific debugging. Do not change them as a side
effect of work on another subsystem. Obtain explicit task authorization before
changing display behavior. Keep shared interconnect IDs and existing routes
compatible when adding consumers.

## Source layout

- `patches/series` is the application order against the pinned Linux 7.3 base.
- Patch files are grouped by subsystem; shared board integration is last.
  Apply the complete series. Individual patches are not feature toggles.
- `configs/veux.config` captures the development configuration.
- `initramfs/` contains source scripts. Editing them does not update an existing
  template ramdisk; the packager currently preserves that ramdisk.
- `pmaports/` contains package recipes. Several full-feature recipes require
  separately supplied firmware/module inputs. Do not hide those dependencies.
- Keep generated source/build trees in `work/`, image outputs in `out/`, and
  private externally supplied artifacts in `inputs/`; all are ignored.
- Commands in documentation run from this repository's root. Avoid absolute
  paths tied to a contributor's home directory.

## Device and publication boundaries

- Preserve Android, user data and the slot-B fallback. Installation targets
  Linux slot A and an explicitly selected removable microSD only.
- Prepare images and show flash commands; do not flash, switch slots, reboot,
  erase, repartition or write a disk unless the user authorizes that operation.
- Never relock the bootloader with these development images.
- Do not read or publish SIM identifiers, modem NV/EFS data, Wi-Fi passwords,
  SSH keys, raw personal logs, firmware blobs or stock partition images.
- Keep phone sudo policy separate from host sudo. The optional development
  sudo package grants every phone user passwordless sudo; do not add it silently.
- Do not push, publish, rewrite Git history or add remote credentials without
  explicit authorization. Local source preparation does not authorize a push.

## Validation

Check patch application against the exact base, script syntax and image
structure for affected changes. Preserve source equivalence when reorganizing
patches. Do not rebuild or reflash unrelated hardware changes merely to check
documentation. Record material limitations in the relevant public guide rather
than creating personal worklogs or handoff files here.
