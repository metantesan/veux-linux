#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Replace the kernel/DTB in pinned Linux boot templates. No device access."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = {
    'boot.img': 'a00dfeb4109699e5372c921200960a457fb4727ba6c3b4fb86421bc7c4341592',
    'vendor_boot.img': '9782f9f05d092dcf31fa9930efdc6f60da0cfd19b81ece621a4e261f6b077231',
    'dtbo.img': '4662db06238627d1a14c61f4f11f800d5898a0263ee1ef3e981b7ac43206ce44',
    'sm6375-xiaomi-veux.dtb': '72353e6c6249e283d8fdfffc2c42631aba0b1713891be486236fbfac5e8a106e',
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def align(data):
    return data + b'\0' * (-len(data) % 4096)


def u32(data, offset):
    return struct.unpack_from('<I', data, offset)[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--build', type=Path, default=ROOT / 'work/build')
    parser.add_argument('--output', type=Path, default=ROOT / 'out/boot')
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Output already exists; choose a fresh directory')
    templates = {}
    for name, expected in TEMPLATES.items():
        data = (args.baseline / name).read_bytes()
        if digest(data) != expected:
            raise SystemExit(f'Wrong verified Linux template: {name}')
        templates[name] = data
    boot, vendor = templates['boot.img'], templates['vendor_boot.img']
    if (boot[:8] != b'ANDROID!' or u32(boot, 40) != 4 or u32(boot, 1580) != 0
            or vendor[:8] != b'VNDRBOOT' or u32(vendor, 8) != 3
            or u32(vendor, 12) != 4096):
        raise SystemExit('Unsupported boot image headers')
    image = (args.build / 'arch/arm64/boot/Image').read_bytes()
    if image[56:60] != b'ARMd' or struct.unpack_from('<Q', image, 8)[0] != 0x80000:
        raise SystemExit('Expected an uncompressed ARM64 Image with text offset 0x80000')
    ramdisk_start = 4096 + ((u32(boot, 8) + 4095) // 4096 * 4096)
    ramdisk = boot[ramdisk_start:ramdisk_start + u32(boot, 12)]
    vendor_ramdisk = vendor[4096:4096 + u32(vendor, 24)]
    if len(ramdisk) != u32(boot, 12) or len(vendor_ramdisk) != u32(vendor, 24):
        raise SystemExit('Truncated template ramdisk')
    with tempfile.TemporaryDirectory(prefix='veux-dtb-') as temporary:
        dtb = Path(temporary) / 'veux.dtb'
        dtb.write_bytes((args.build / 'arch/arm64/boot/dts/qcom/sm6375-xiaomi-veux.dtb').read_bytes())
        baseline = args.baseline / 'sm6375-xiaomi-veux.dtb'
        props = subprocess.check_output(['fdtget', '-p', str(baseline), '/'], text=True).splitlines()
        for prop in ('qcom,msm-id', 'qcom,board-id', 'qcom,pmic-id',
                     'qcom,pmic-id-size', 'qcom,softsku-id'):
            if prop in props:
                values = subprocess.check_output(
                    ['fdtget', '-t', 'x', str(baseline), '/', prop], text=True).split()
                subprocess.run(['fdtput', '-t', 'x', str(dtb), '/', prop, *values], check=True)
        for prop, value in (('console-size', '100000'), ('pmsg-size', '0')):
            subprocess.run(['fdtput', '-t', 'x', str(dtb),
                            '/reserved-memory/ramoops@d0000000', prop, value], check=True)
        blob = dtb.read_bytes()
    boot_header = bytearray(boot[:4096])
    struct.pack_into('<II', boot_header, 8, len(image), len(ramdisk))
    boot_image = bytes(boot_header) + align(image) + align(ramdisk)
    vendor_header = bytearray(vendor[:4096])
    struct.pack_into('<I', vendor_header, 2100, len(blob))
    vendor_image = bytes(vendor_header) + align(vendor_ramdisk) + align(blob)
    if len(boot_image) >= 128 * 1024**2 - 65536 or len(vendor_image) >= 96 * 1024**2 - 65536:
        raise SystemExit('Image exceeds the development partition size limit')
    files = {'boot.img': boot_image, 'vendor_boot.img': vendor_image,
             'dtbo.img': templates['dtbo.img'], 'sm6375-xiaomi-veux.dtb': blob}
    args.output.mkdir(parents=True)
    for name, data in files.items():
        (args.output / name).write_bytes(data)
    (args.output / 'SHA256SUMS').write_text(''.join(
        f'{digest(data)}  {name}\n' for name, data in sorted(files.items())))
    (args.output / 'manifest.json').write_text(json.dumps({
        'templates': TEMPLATES,
        'kernel_release': (args.build / 'include/config/kernel.release').read_text().strip(),
        'ramdisk_sha256': digest(ramdisk),
        'vendor_ramdisk_sha256': digest(vendor_ramdisk),
        'config_sha256': digest((args.build / '.config').read_bytes()),
        'hardware_tested': False,
        'note': 'Preserves verified template ramdisks and command line; no firmware is distributed.'
    }, indent=2) + '\n')
    print(f'Packaged {args.output}; no phone writes performed')


if __name__ == '__main__':
    main()
