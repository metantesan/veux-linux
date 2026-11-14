# Booting mainline Linux on Xiaomi veux

This guide prepares a minimal systemd rootfs on microSD and Linux boot images
for slot A. The initial goal is a booted kernel, serial console and SSH over
USB. It does not install a complete phone desktop or make unfinished hardware
work. The device is **Xiaomi Redmi Note 11 Pro 5G, codename `veux`, SM6375**;
do not use these images on a different Redmi Note 11 variant.

All host commands below run from the **root of this repository** unless a
command explicitly says it runs on the phone. Keep that terminal in this
directory. No command in the provided build tools flashes the phone.

## 1. Required inputs and current release limitation

You need:

- A Linux PC, a reliable USB data cable, a microSD card and card reader.
- An already unlocked bootloader and working access to fastboot. Unlocking can
  erase user data and is outside this guide. Back up personal data beforehand.
- A verified slot-B Android fallback and saved original boot-related images
  for your own device. Confirm your slot layout; do not assume another phone
  has the development phone's setup.
- Python 3.12 or newer, Git, GNU make, LLVM/Clang/LLD with AArch64 support,
  flex, bison, bc, pkg-config, OpenSSL and ELF development headers, tar/xz,
  `dtc`, `fdtget`, `fdtput`, Android platform-tools (`fastboot`, `adb`), kmod,
  and the usual host C build tools. The captured build used Clang 23.1.4.
- pmbootstrap; commands were inspected with version 3.12.1. See its
  [official installation instructions](https://docs.postmarketos.org/pmbootstrap/installation.html).
  The systemd-capable pmaports checkout below requires pmbootstrap >= 3.11.0.
- The exact `linux-7.3.tar.xz` used by this snapshot. Its SHA-256 is
  `87363c24f10e06321eb362765521094e94471f6bff8bce2d6b3e40f39f004953`.
- The externally supplied **verified Linux template set** listed below.

**The public repository alone is not yet a complete fresh-phone installer.**
Boot image packaging still requires four files from the maintainer's booted
Linux candidate 69. They include a working ramdisk, firmware, vendor ramdisk,
loader selection metadata and no-op DTBO. They are not shipped in this source
repository. Obtain this exact set separately from the maintainer before trying
to install. A stock Android `boot.img` is not an equivalent substitute.

Place the archive at `inputs/linux-7.3.tar.xz` and these files in
`inputs/baseline/`:

| File | Required SHA-256 |
|---|---|
| `boot.img` | `a00dfeb4109699e5372c921200960a457fb4727ba6c3b4fb86421bc7c4341592` |
| `vendor_boot.img` | `9782f9f05d092dcf31fa9930efdc6f60da0cfd19b81ece621a4e261f6b077231` |
| `dtbo.img` | `4662db06238627d1a14c61f4f11f800d5898a0263ee1ef3e981b7ac43206ce44` |
| `sm6375-xiaomi-veux.dtb` | `72353e6c6249e283d8fdfffc2c42631aba0b1713891be486236fbfac5e8a106e` |

The packager checks these hashes and refuses other templates. Do not bypass
that check to use an arbitrary dump. If these inputs are unavailable, you can
build the kernel and review the source, but the documented image packaging
and phone boot steps are blocked.

## 2. Prepare the source and build

```sh
mkdir -p inputs/baseline
python3 tools/prepare-kernel.py inputs/linux-7.3.tar.xz
JOBS=8 bash build.sh
```

The preparation tool checks the archive hash and applies `patches/series` in
order into `work/linux`. It refuses to overwrite an existing source tree.
The build uses `work/build`, seeds it with `configs/veux.config` on the first
run, resolves the configuration, and builds the kernel, board DTB and modules.
Change `JOBS` to suit the PC. Keep substantial free disk space for a complete
kernel source/build tree and the pmbootstrap chroots.

Expected outputs:

```text
work/build/arch/arm64/boot/Image
work/build/arch/arm64/boot/dts/qcom/sm6375-xiaomi-veux.dtb
work/build/include/config/kernel.release
work/build/modules.builtin
work/build/modules.builtin.modinfo
```

Read the actual release with:

```sh
cat work/build/include/config/kernel.release
```

The release must also match any separately built loadable modules. The minimal
rootfs below packages the built-in driver metadata only. Although `build.sh`
builds modules, they are not automatically installed or loaded in that profile.
Do not substitute modules built for another release.

## 3. Prepare isolated minimal rootfs packages

Use a separate pmaports checkout and pmbootstrap work directory. This avoids
overwriting an existing device configuration, chroots or local signing keys.

```sh
git clone https://gitlab.postmarketos.org/postmarketOS/pmaports.git work/pmaports
git -C work/pmaports checkout f3f926903c1be144b0f92e1a8f3b88383911ad80
python3 tools/stage-minimal-rootfs.py --aports work/pmaports --build work/build
```

The staging tool supplies the locally built kernel/config/DTB and module
metadata, then calculates APK source checksums. It creates a minimal device
recipe in that checkout. This minimal recipe omits the full device template's
mandatory radio, firmware, audio and USB-PD packages and their startup hooks.
It requires only the kernel, base OS, OpenSSH, agetty, unudhcpd and kmod.
The full templates under `pmaports/` are preserved for later integration.

Define this shell function in the same terminal:

```sh
pmb() {
    pmbootstrap -c "$PWD/work/pmbootstrap-systemd.cfg" \
        -w "$PWD/work/pmbootstrap" -p "$PWD/work/pmaports" "$@"
}
pmb init
```

During initialization select the edge channel, vendor `xiaomi`, device
`veux-mainline`, UI `none` and service manager `systemd`. Choose your own
username, timezone and locale. Do not select the downstream `veux` device.
The username in the SSH examples below must match the one you choose.

Set/check the essential settings and build:

```sh
pmb config device xiaomi-veux-mainline
pmb config service_manager systemd
pmb config ui none
pmb config extra_packages openssh,agetty,unudhcpd,iproute2,kmod
pmb config ssh_keys True
pmb build linux-xiaomi-veux-mainline device-xiaomi-veux-mainline
```

Enter host sudo and phone account passwords interactively when prompted; do
not put passwords in commands. `ssh_keys=True` uses the host keys selected by
pmbootstrap; check the prompts if you want a particular public key installed.
Do not install `veux-development-sudo` for this minimal profile: that optional
package gives every phone user passwordless sudo.

Package download availability and the upstream repositories can change. The
rootfs steps above are a prepared workflow, not a completed clean-machine
installation test of this public repository. If a package fails, inspect
`pmb log` before proceeding. Do not flash a phone with an unfinished rootfs.

## 4. Write the removable microSD

The initramfs expects an **unencrypted ext4 root on partition 2 of an MMC
device**, with `/usr/lib/systemd/systemd` or `/sbin/init` present. Let
pmbootstrap create the normal two-partition layout. Do not use
`--single-partition`, full-disk encryption, or an internal-UFS installation.

Identify the removable card by model, size and transport:

```sh
lsblk -o NAME,PATH,SIZE,MODEL,TRAN,MOUNTPOINTS
```

On the development PC the card is `/dev/mmcblk0`. This name is **not universal**;
confirm it on your own PC. Use the whole disk, not `/dev/mmcblk0p1` or `p2`.
Unmount any card partitions shown as mounted before continuing; for example,
run `sudo umount /dev/mmcblk0p1` and `sudo umount /dev/mmcblk0p2` if those
partitions are mounted. Do not unmount unrelated disks.

**The next command erases and repartitions the selected card.** With the
confirmed removable card at `/dev/mmcblk0`, build the rootfs and install it
directly using the systemd configuration prepared above:

```sh
pmbootstrap -c "$PWD/work/pmbootstrap-systemd.cfg" \
    -w "$PWD/work/pmbootstrap" -p "$PWD/work/pmaports" \
    install --disk /dev/mmcblk0 --no-recommends --filesystem ext4
sync
lsblk -f /dev/mmcblk0
```

In the terminal where you defined `pmb`, the equivalent shorter command is:

```sh
pmb install --disk /dev/mmcblk0 --no-recommends --filesystem ext4
```

pmbootstrap handles partitioning, formatting and installing the rootfs. There
is no separate `dd` step with this method. It may request host sudo and the
phone account password interactively. Confirm that the finished card has a
second partition containing the ext4 root, then eject it cleanly and insert
it into the phone. Installing the card does not flash the phone's kernel;
continue with the boot-image steps below.

If you already have a separate systemd pmbootstrap profile outside this repo,
the same operation has this form (replace the config path):

```sh
pmbootstrap -c /path/to/pmbootstrap-systemd.cfg install --disk /dev/mmcblk0
```

That existing config must already select the correct device, kernel, systemd
and package inputs. Keep its APK cache if desired; avoid sharing built-package
repositories with different signing keys. Do not accidentally use the default
pmbootstrap profile or a downstream device profile.

For an image file instead of writing the card directly, use this alternative:

```sh
pmb install --no-recommends --no-split --no-sparse --filesystem ext4
mkdir -p out/rootfs
pmb export --no-install "$PWD/out/rootfs"
```

This alternative only creates/exports an image; it does not install the card.
The direct `--disk` method above is the recommended path in this guide.

## 5. Package Linux boot images

```sh
python3 tools/package-boot.py --baseline inputs/baseline \
    --build work/build --output out/boot
(cd out/boot && sha256sum -c SHA256SUMS)
```

This produces `boot.img`, `vendor_boot.img`, `dtbo.img`, the packaged DTB,
`SHA256SUMS` and a manifest. It preserves the verified Linux template's
ramdisks and command line, replaces its kernel and DTB, copies the bootloader
board-selection metadata, and preserves the DTBO bytes/order. It also applies
the same ramoops console/pmsg allocation used by the verified template.

Changing scripts under `initramfs/` does **not** change this packager's ramdisk.
There is currently no source-only ramdisk/firmware construction path in the
public tooling. The binary template dependency must be removed before claiming
a fully reproducible installation from source alone.

The packager refuses to overwrite an existing output directory; choose another
`--output` path for a later build. Its structural checks do not prove that a
new kernel boots.

## 6. Flash slot A

Have the original images and a known-good slot-B Android installation available
before starting. Enter the bootloader manually using your established device
method. If Android and ADB are available, `adb reboot bootloader` is another
option. Check the connection and current slot:

```sh
fastboot devices
fastboot getvar product
fastboot getvar current-slot
```

Confirm this is your `veux` device and slot B is the preserved fallback. Only
then run these commands yourself, checking each command succeeds:

```sh
fastboot flash boot_a out/boot/boot.img
fastboot flash vendor_boot_a out/boot/vendor_boot.img
fastboot flash dtbo_a out/boot/dtbo.img
fastboot set_active a
fastboot reboot
```

Do not flash `super`, `userdata`, modem partitions or slot B. Do not use a
generic `pmbootstrap flasher flash_rootfs` command: this workflow boots the
rootfs from microSD. Do not relock the bootloader with development images.

The phone should start the kernel, create USB serial/NCM networking, wait for
the microSD root and enter systemd automatically. The minimal profile does not
start Plasma. A blank display alone does not establish whether boot failed;
check USB serial and SSH.

## 7. Connect and confirm boot

The phone's USB address is `172.16.42.1`; the host normally receives
`172.16.42.2`. Find the host's USB interface with `ip -br link`. If DHCP did not
configure it, replace the placeholder and configure the host side:

```sh
USB_IF=REPLACE_WITH_HOST_USB_INTERFACE
sudo ip link set "$USB_IF" up
sudo ip address replace 172.16.42.2/24 dev "$USB_IF"
ssh user@172.16.42.1
```

Replace `user` with the account created by pmbootstrap. Verify the host-key
fingerprint when connecting; after an intentional reinstall, remove a stale
entry with `ssh-keygen -R 172.16.42.1` only after confirming the device identity.

Run **on the phone**:

```sh
uname -a
cat /etc/os-release
findmnt /
ip -br address
systemctl --failed
sudo journalctl -b -p warning
```

The root filesystem should be on the card. Preserve the actual kernel release
and journal when diagnosing problems. A matching kernel release and successful
SSH connection verify the minimal boot, not Wi-Fi, camera or call audio.

If SSH is unavailable but USB serial appears, open `/dev/ttyACM0` using a serial
terminal at 115200 baud. Use the actual device name reported by the host.
Only one terminal should read the serial port at a time. The initramfs keeps a
recovery shell when it cannot mount the card; inspect `/run/mainline-init.log`,
`dmesg`, `/dev/mmcblk*p2` and `/sys/kernel/debug/devices_deferred` there.

## 8. Desktop and other hardware

First establish the minimal boot above. The README table describes results on
the configured development image; it is not a list of features installed by
this minimal recipe.

- Plasma needs its OS packages, Mesa/Turnip, session setup and the
  `veux-plasma-autostart` package. Its copied unit currently uses `User=user`;
  adapt that to your chosen account. It relies on an existing desktop setup.
- Wi-Fi/modem need matching device firmware, ath10k assets, QRTR,
  RMTFS/TFTP, NetworkManager/ModemManager and their service configuration.
- Audio needs modules built for the running kernel, amplifier firmware,
  routing/UCM and DSP setup. The full audio APKBUILD refers to external inputs.
- USB-PD uses separately packaged TCPM/TCPCI modules. The minimal profile does
  not promise charging behavior identical to the configured development image.

The package sources are included, but source recipes with missing generated
inputs and empty `sha512sums` are not ready for direct `pmbootstrap build`.
Do not add every full-profile package to `extra_packages` and expect it to
build. Full desktop/radio/audio provisioning needs additional public staging
and firmware-extraction tooling; that part of the installation is unfinished.

## 9. Troubleshooting and rollback

| Symptom | First action |
|---|---|
| Wrong archive/template hash | Obtain the pinned input; do not bypass validation |
| Patch fails | Use a fresh directory and exact archive; do not apply on a downstream kernel |
| APKBUILD missing local source | Use the minimal staging tool; do not select full firmware/audio templates |
| No USB device after boot | Return to fastboot; check all three slot-A images came from the same output |
| Initramfs shell / no root mount | Check the card has ext4 root on partition 2 and an init executable |
| SSH refuses connection | Check USB IP configuration, account keys and serial/journal output |
| Screen turns green on sleep | Known unresolved display/sleep bug; collect logs after recovery |
| No Plasma | Expected for UI `none`; desktop setup is separate |
| Boot loop | Stop retrying new changes and restore the verified slot-A image set |

To return to the preserved Android installation, enter fastboot and run:

```sh
fastboot set_active b
fastboot reboot
```

This assumes you confirmed a working Android slot B before installation. It
does not repair an overwritten slot. To restore a known-good Linux slot A,
flash its matching saved `boot.img`, `vendor_boot.img` and `dtbo.img` to their
`*_a` partitions, then select A. Keep each image set together.

## Validation of this guide's tooling

The 11-patch series was checked against the pinned kernel base and recreates
the captured development source. Python/shell syntax checks pass. Using the
existing development build, the new packager reproduced all four verified
candidate-69 files byte for byte. A newly compiled public-checkout kernel,
freshly generated minimal rootfs and full phone installation have not yet been
tested together. No phone flashing was performed while writing this guide.
