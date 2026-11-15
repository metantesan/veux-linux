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
| 0009 | AW8624 continuous FF_RUMBLE haptics |
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
The AW8624 continuous FF_RUMBLE path now produces vibration on the
development device. Probe configures 24 kHz PWM while preserving and
checking the PWM output-enable bit; the previous full-register write had
cleared that bit. Each pulse is limited to one second. RAM and streamed
waveforms are not supported.

The complete ordered series applies cleanly to the pinned Linux 7.3 base.
The resulting source tree is `65d2738cbdfa562486fcd62db56154bc632f4784`.
This confirms patch applicability, not a kernel build. The AW8624 driver was
built and verified on the development phone: a maximum-strength, one-second
continuous pulse produced vibration.
