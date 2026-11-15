# veux Linux

Mainline Linux development sources for Xiaomi Redmi Note 11 Pro 5G
(`veux`, Qualcomm SM6375 / Snapdragon 695), based on Linux 7.3.

**This project was developed heavily using AI, including OpenAI Codex.**
AI tools contributed substantially to the code, kernel patches, hardware
investigation, debugging and documentation, under the owner's direction.
AI-generated changes may contain mistakes; hardware verification is incomplete.

This repository contains the [kernel patch series](patches/README.md), the
captured kernel configuration in `configs/veux.config`, initramfs sources,
and postmarketOS package recipes. Local worklogs, device dumps, firmware,
compiled modules and boot images are excluded.

## Status

Results refer to the development phone and its configured rootfs. They do not
mean every feature is enabled by a fresh minimal installation.

| Component | Status | Limits / remaining work |
|---|---|---|
| Boot / systemd | Working | microSD root; experimental installation |
| Display / Plasma Mobile | Working | Intermittent green screen when entering sleep |
| Touchscreen | Working | Goodix GT9896; full multitouch and resume coverage pending |
| GPU | Partial | Accelerated Plasma and Vulkan work; locked at 266 MHz with only one operating point; dynamic frequency scaling is unfinished |
| USB | Working | Serial console and USB networking; host/OTG unverified |
| microSD | Working | Root filesystem boots from partition 2 |
| Internal UFS | Partial | Not an installation target; reliable access unverified |
| Battery | Working | Capacity, voltage, current, temperature and UPower telemetry |
| Charging | Partial | Standard charging observed; 67 W HyperCharge unsupported |
| Wi-Fi | Working | Association and internet observed; startup/recovery needs wider testing |
| Modem / SIM | Working with one SIM | Second SIM untested: its position shares the microSD slot used by the rootfs |
| Calls | Working signalling | User confirms calls work; call audio integration remains unfinished |
| SMS | Working | User confirmed; tested with one SIM |
| Cellular data | Unverified | End-to-end data connection not confirmed |
| Speaker output | Working | User confirmed playback; broader routing testing pending |
| Earpiece / microphones | Unfinished | Capture and call routing not verified |
| Power / volume buttons | Partial | Volume input events verified; full wake/suspend behavior pending |
| CPU frequency / temperature | Partial | Source support present; complete thermal/throttling validation pending |
| Cameras | Not working | Main sensor ID read times out; no capture |
| Haptics | Working | Continuous FF_RUMBLE confirmed on device; one-second cap; no RAM/streamed effects |
| Bluetooth / GNSS | Unverified | No complete pairing or location test |
| Motion / light / proximity sensors | Unverified | Drivers and userspace integration pending |
| Fingerprint / NFC / IR | Unverified | Fitted hardware and control paths need confirmation |

## Known bugs

- **The screen sometimes turns green when it should enter sleep mode.**
  Reported on the development phone; the cause is unresolved.
- **The GPU is locked at 266 MHz instead of scaling dynamically.** Live devfreq
  reports current, minimum and maximum frequency as `266000000`, with that same
  value as its only available operating point. The Linux device tree also
  defines only that operating point. The captured stock Android device tree
  contains speed-bin tables topping out at 700, 840 or 900 MHz; the applicable
  bin for this unit has not been confirmed. Dynamic scaling needs the correct
  bin, voltage and bandwidth handling plus stability testing. An 800 MHz maximum
  is not established by this evidence.
- Camera capture does not work.
- Call audio, microphone capture, earpiece routing and full fast charging are
  unfinished. Cellular data is not verified end to end.
- Only one SIM has been tested. The second SIM position shares the microSD
  slot, which is occupied by the Linux root filesystem, so dual-SIM operation
  cannot be tested with the current storage setup.

## Installation guide

See [the boot guide](docs/boot-guide.md) for prerequisites, kernel preparation,
microSD rootfs creation, boot image packaging, slot-A flashing and rollback.
The current workflow still requires an externally supplied verified Linux boot
template set. That dependency is explained before the installation steps.

## Kernel sources

Use the exact Linux release archive identified in the patch documentation.
`tools/prepare-kernel.py` verifies it and applies `patches/series`; `build.sh`
builds the kernel, DTB and modules using the captured configuration.

The [boot guide](docs/boot-guide.md) covers staging the minimal rootfs packages,
installing directly to microSD with `pmbootstrap install --disk`, packaging
images with `tools/package-boot.py`, and flashing slot A. Packaging requires
the pinned externally supplied Linux boot templates. Full-feature recipes that
refer to firmware or module bundles still require those inputs locally.

## Credits and AI involvement

**This project has been developed heavily with AI tools, including OpenAI
Codex, under the repository owner's direction.** AI tools contributed source
changes, investigation, debugging, build tooling and documentation. The owner
provides the hardware, directs development and performs device tests.

The project builds on Linux and work by its upstream maintainers, Qualcomm,
Xiaomi and the postmarketOS community. Device wiring was compared with captured
stock Android device-tree data and Qualcomm/Xiaomi downstream kernel sources.
Original copyright, authorship and SPDX notices are retained in the source.
The downstream Android port is not included.

See [LICENSE](LICENSE) and the [licensing and provenance review](LICENSING.md).
**Our original code, scripts and documentation use GPL-2.0-only.** Imported
source retains its existing license and attribution. GPL, MIT and
BSD license texts are included under `LICENSES/`. Firmware is not included or
licensed by this repository; redistribution rights for external firmware and
generated binary images remain unverified.
