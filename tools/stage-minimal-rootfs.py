#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Stage a minimal device aport and selected optional hardware packages."""
import argparse
import hashlib
import io
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aports', type=Path, required=True)
    parser.add_argument('--build', type=Path, default=ROOT / 'work/build')
    parser.add_argument('--extra-package', action='append', default=[],
                        choices=('veux-usbc-pd', 'veux-aw8624-feedbackd'),
                        help='also stage this optional hardware package (repeatable)')
    args = parser.parse_args()
    args.extra_package = list(dict.fromkeys(args.extra_package))
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
    for name in args.extra_package:
        target = aports / 'main' / name
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
            extra_dependencies = ' '.join(args.extra_package)
            recipe = '''# SPDX-License-Identifier: GPL-2.0-only
maintainer="hikari <me@metantesan.com>"
pkgname=device-xiaomi-veux-mainline
pkgver=1
pkgrel=1
pkgdesc="Xiaomi veux minimal mainline SD-root development device"
url="https://postmarketos.org"
arch="aarch64"
license="GPL-2.0-only"
depends="linux-xiaomi-veux-mainline postmarketos-base openssh agetty unudhcpd kmod ''' + extra_dependencies + '''"
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

    for name in args.extra_package:
        source = ROOT / 'pmaports/main' / name
        target = aports / 'main' / name
        if name == 'veux-usbc-pd':
            archive = io.BytesIO()
            release = (build / 'include/config/kernel.release').read_text().strip()
            with tarfile.open(fileobj=archive, mode='w') as bundle:
                for module in ('tcpm', 'tcpci', 'tcpci_rt1711h'):
                    path = build / 'drivers/usb/typec/tcpm' / f'{module}.ko'
                    if not path.is_file():
                        raise SystemExit(f'Missing USB-PD module: {path}')
                    vermagic = subprocess.check_output(
                        ['modinfo', '-F', 'vermagic', str(path)], text=True).strip()
                    if not vermagic.startswith(release + ' '):
                        raise SystemExit(
                            f'{module} was built for {vermagic}, expected {release}')
                    data = path.read_bytes()
                    entry = tarfile.TarInfo(f'{module}.ko')
                    entry.size, entry.mode = len(data), 0o644
                    bundle.addfile(entry, io.BytesIO(data))
            files = {
                'veux-usbc-pd-modules.tar': archive.getvalue(),
                **{filename: (source / filename).read_bytes() for filename in (
                    'veux-usbc-pd-start', 'veux-usbc-pd.service',
                    '60-veux-usbc-pd.preset')},
            }
        else:
            files = {
                '72-veux-aw8624-feedbackd.rules':
                    (source / '72-veux-aw8624-feedbackd.rules').read_bytes(),
            }
        recipe = (source / 'APKBUILD').read_text()
        hashes = '\n'.join(
            f'{hashlib.sha512(data).hexdigest()}  {filename}'
            for filename, data in files.items())
        recipe = recipe.replace('sha512sums=""', f'sha512sums="\n{hashes}\n"')
        target.mkdir(parents=True, exist_ok=True)
        for filename, data in files.items():
            (target / filename).write_bytes(data)
        (target / 'APKBUILD').write_text(recipe)
        (target / '.veux-public-stage').write_text('Staged optional public package\n')
        print(f'Staged {target}')


if __name__ == '__main__':
    main()
