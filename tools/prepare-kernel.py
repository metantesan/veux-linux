#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Prepare the pinned kernel in a fresh directory; never modify an existing tree."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SHA256 = '87363c24f10e06321eb362765521094e94471f6bff8bce2d6b3e40f39f004953'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--source', type=Path, default=ROOT / 'work/linux')
    args = parser.parse_args()
    with args.archive.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != SHA256:
            raise SystemExit('Wrong Linux archive: SHA-256 does not match the pinned base')
    target = args.source.resolve()
    if target.exists():
        raise SystemExit(f'Refusing to overwrite existing source: {target}')
    target.parent.mkdir(parents=True, exist_ok=True)
    series = (ROOT / 'patches/series').read_text().splitlines()
    with tempfile.TemporaryDirectory(prefix='extract-', dir=target.parent) as temporary:
        with tarfile.open(args.archive) as archive:
            archive.extractall(temporary, filter='data')
        source = Path(temporary) / 'linux-7.3'
        if not (source / 'Makefile').is_file():
            raise SystemExit('Unexpected kernel archive layout')
        env = {**os.environ, 'GIT_CEILING_DIRECTORIES': str(source.parent)}
        for name in series:
            if not name or name.startswith('#'):
                continue
            if Path(name).name != name:
                raise SystemExit(f'Invalid patch name: {name}')
            patch = ROOT / 'patches' / name
            subprocess.run(['git', 'apply', '--check', str(patch)], cwd=source,
                           env=env, check=True)
            subprocess.run(['git', 'apply', str(patch)], cwd=source, env=env, check=True)
        source.rename(target)
    print(f'Prepared {target}')


if __name__ == '__main__':
    main()
