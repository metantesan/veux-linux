# Kernel patch series

Base: Linux 7.3 release archive, SHA-256:
`87363c24f10e06321eb362765521094e94471f6bff8bce2d6b3e40f39f004953`.

Apply every patch in the order listed in `series`, from the kernel source root:

```sh
patch_dir=/absolute/path/to/veux-linux-public/patches
while IFS= read -r patch; do
    git apply --check "$patch_dir/$patch" || exit 1
    git apply "$patch_dir/$patch" || exit 1
done < "$patch_dir/series"
```

| Patch | Scope |
|---|---|
| 0001 | ARM64 boot entry and restricted TLMM pin control |
| 0002 | Shared display/IPA interconnect provider and IDs |
| 0003 | K6S display, DSI, DPU, display clocks and UBWC |
| 0004 | Goodix touchscreen |
| 0005 | Adreno GPU |
| 0006 | SYV690 charging |
| 0007 | Modem remoteproc, service domains and IPA |
| 0008 | Audio codecs, SoundWire and Q6AFE |
| 0009 | Experimental haptics |
| 0010 | Experimental camera controller and sensor ID probe |
| 0011 | Shared SoC definitions, board DTS and kernel configuration |

The series preserves the development source snapshot. Shared DRM code is in
0003; shared interconnect code is in 0002. The board integration patch contains
device nodes for several subsystems, so these are review boundaries rather than
independently selectable feature switches. Apply the complete series.

Camera capture does not work: the sensor identity read times out. The camera
patch retains failed diagnostic experiments, including GPIO-high precharge;
that experiment was based on an incorrect interpretation of downstream GPIO
flags and must not be treated as a verified Android initialization sequence.
Haptics registered an input device but produced no felt vibration.

The split was checked by applying both the original combined patch and this
ordered series to private Git indexes of the same pristine kernel base. Both
produced tree `d9b74afa3cb6198f95c680b5307693ad34fb0028`. This confirms source
equivalence; it is not a new kernel build or hardware test.

The subsequent license review restored a truncated Goodix author email address
in patch 0004 and selected GPL-2.0-only for the owner's original board DTS and
binding schemas. These attribution/license-only corrections change the source
tree hash from the initial split result above; executable driver behavior is
unchanged. Imported licenses and author notices are retained.
