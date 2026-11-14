#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
set -euo pipefail
repo=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
source_dir=${SOURCE_DIR:-"$repo/work/linux"}
build_dir=${BUILD_DIR:-"$repo/work/build"}
test -f "$source_dir/Makefile" || { echo 'Run tools/prepare-kernel.py first' >&2; exit 1; }
mkdir -p "$build_dir"
build_dir=$(CDPATH= cd -- "$build_dir" && pwd)
if [ ! -f "$build_dir/.config" ]; then
    cp "$repo/configs/veux.config" "$build_dir/.config"
fi
make -C "$source_dir" ARCH=arm64 LLVM=1 O="$build_dir" olddefconfig
make -C "$source_dir" ARCH=arm64 LLVM=1 O="$build_dir" -j"${JOBS:-8}" Image qcom/sm6375-xiaomi-veux.dtb modules
echo "Kernel, DTB and modules built in $build_dir. No device writes performed."
