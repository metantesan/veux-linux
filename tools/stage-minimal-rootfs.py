#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Stage a kernel and minimal device aport without optional radio/audio inputs."""
import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aports', type=Path, required=True)
    parser.add_argument('--build', type=Path, default=ROOT / 'work/build')
    args = parser.parse_args()
    aports = args.aports.resolve()
    if not (aports / 'pmaports.cfg').is_file():
        raise SystemExit('Expected a pmaports checkout')
    build = args.build.resolve()
    kernel = 'linux-xiaomi-veux-mainline'
    device = 'device-xiaomi-veux-mainline'
    inputs = {
        'Image': build / 'arch/arm64/boot/Image',
        'kernel.config': build / '.config',
        'kernel.release': build / 'include/config/kernel.release',
        'modules.builtin': build / 'modules.builtin',
        'modules.builtin.modinfo': build / 'modules.builtin.modinfo',
        'sm6375-xiaomi-veux.dtb': build / 'arch/arm64/boot/dts/qcom/sm6375-xiaomi-veux.dtb',
    }
    payloads = {name: path.read_bytes() for name, path in inputs.items()}
    image = payloads['Image']
    if image[56:60] != b'ARMd':
        raise SystemExit('Expected an uncompressed ARM64 Image')
    for name in (kernel, device):
        target = aports / 'device/testing' / name
        if target.exists() and not (target / '.veux-public-stage').is_file():
            raise SystemExit(f'Refusing to overwrite an unrelated aport: {target}')
    for name in (kernel, device):
        source = ROOT / 'pmaports/device/testing' / name
        target = aports / 'device/testing' / name
        target.mkdir(parents=True, exist_ok=True)
        if name == kernel:
            files = payloads
            recipe = (source / 'APKBUILD').read_text()
        else:
            files = {'deviceinfo': (source / 'deviceinfo').read_bytes()}
            recipe = '''# SPDX-License-Identifier: GPL-2.0-only
maintainer="hikari <me@metantesan.com>"
pkgname=device-xiaomi-veux-mainline
pkgver=1
pkgrel=0
pkgdesc="Xiaomi veux minimal mainline SD-root development device"
url="https://postmarketos.org"
arch="aarch64"
license="GPL-2.0-only"
depends="linux-xiaomi-veux-mainline postmarketos-base openssh agetty unudhcpd kmod"
makedepends="devicepkg-dev"
source="deviceinfo"
options="!check !archcheck"
build() { devicepkg_build "$startdir" "$pkgname"; }
package() { devicepkg_package "$startdir" "$pkgname"; }
sha512sums=""
'''
        hashes = '\n'.join(f'{hashlib.sha512(data).hexdigest()}  {filename}'
                           for filename, data in files.items())
        recipe = recipe.replace('sha512sums=""', f'sha512sums="\n{hashes}\n"')
        for filename, data in files.items():
            (target / filename).write_bytes(data)
        (target / 'APKBUILD').write_text(recipe)
        (target / '.veux-public-stage').write_text('Staged minimal public source profile\n')
        print(f'Staged {target}')


if __name__ == '__main__':
    main()
