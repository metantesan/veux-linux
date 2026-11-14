# Licensing and attribution

The owner's chosen license for **all original project code, scripts,
documentation and packaging recipes is GPL-2.0-only**, as provided in
`LICENSE`. Original service/configuration files and package payloads also use
GPL-2.0-only. This default does not
replace the licenses of imported code, package payloads, device-tree sources
or firmware. Preserve individual SPDX identifiers and copyright notices.

License texts are included under `LICENSES/` for GPL-2.0-only,
GPL-2.0-or-later, MIT, BSD-2-Clause and BSD-3-Clause. The texts were taken from
the pinned kernel archive's `LICENSES/preferred/` files, without its explanatory
metadata. Generic copyright placeholders in license templates do not replace
the actual notices retained in source files.

## Source inventory

| Material | License / attribution |
|---|---|
| Original host tools, build script, initramfs scripts and documentation | GPL-2.0-only |
| Original package recipes, service units, configurations and Wi-Fi/SIM helpers | GPL-2.0-only; original MIT selections replaced at the owner's request |
| Linux driver modifications | Existing source-file license; predominantly GPL-2.0-only, including the kernel's legacy `GPL-2.0` spelling |
| Goodix GTX8 driver/header | GPL-2.0-only; Goodix, Linaro and Aelin Reidel notices retained |
| K6S panel, SYV690 and shared ICC drivers | GPL-2.0-only; downstream/reference provenance listed below |
| AW8624 driver | GPL-2.0-only adaptation; AWINIC/Joseph attribution retained; downstream reference permits GPL version 2 or later |
| Original K6S, SYV690 and AW8624 binding schemas | GPL-2.0-only, selected by the owner |
| Imported Goodix binding schema | GPL-2.0-only OR BSD-2-Clause; upstream notice retained |
| Original veux board device tree | GPL-2.0-only, selected by the owner |
| Upstream SM6375 SoC device tree | BSD-3-Clause; existing source notices retained |
| Plasma startup/prepare helpers | GPL-2.0-or-later; adapted from KDE's `startplasmamobile`, with original author notices restored |
| RMTFS changes | BSD-3-Clause context; source is upstream linux-msm/rmtfs, not a project-owned replacement |
| External firmware | Not included; no license or redistribution permission is granted by this repository |

The `license=` field of an APKBUILD describes the built package's contents; it
does not relicense third-party files or establish permission to redistribute
an external binary. `MODULE_LICENSE()` likewise is not a substitute for the
source's actual license notice. See the
[Linux kernel licensing rules](https://docs.kernel.org/process/license-rules.html).

The Plasma helper sources retain KDE's GPL-2.0-or-later grant. The combined
project package selects GPL version 2, which that grant permits, and declares
GPL-2.0-only for the package containing the project's original GPLv2-only files.
That package declaration does not remove the upstream authors' broader grant
on their own source files. Likewise, existing BSD/dual-licensed kernel files
remain under their original notices; the project-wide choice does not
relicense third-party material.

Patches carry changes to differently licensed files. Do not apply a blanket
GPL label over a BSD device tree or remove an upstream notice just because
the file is distributed inside a patch. Files not present in a diff retain
their upstream notices in the exact kernel base required by the series.

## Provenance

- **Linux:** the exact Linux 7.3 archive hash and patch order are in
  [patches/README.md](patches/README.md). Existing Linux authorship is retained.
- **Goodix:** Aelin Reidel's GTX8 submission, derived from Goodix's vendor
  driver and the upstream Goodix Berlin driver. The source was imported from
  the [v2 driver submission](https://lists.openwall.net/linux-kernel/2026/02/28/91).
  The canonical thread is
  [on lore](https://lore.kernel.org/linux-input/20260228-gtx8-v2-0-3a408c365f6c@mainlining.org/).
  Local changes include veux integration and transport/reset handling. The
  imported copyright address had been truncated by a mailing-list mirror;
  it has been restored to `aelin@mainlining.org`, matching the author's address
  already present in the imported binding and module metadata.
- **Qualcomm/Xiaomi downstream references:** the inspected trees were
  [dereference23/kernel_xiaomi_sm6375](https://github.com/dereference23/kernel_xiaomi_sm6375)
  at `494122af9e9875662d3113496b437652af466f7d` and
  [sm6375-devs/android_kernel_xiaomi_sm6375](https://github.com/sm6375-devs/android_kernel_xiaomi_sm6375)
  at local checkout revision `980ca57c802c509c43c9658145e704459d589150`.
  These identify reference checkouts, not proof that every local source came
  verbatim from those upstream revisions. The inspected AW8624 source credits
  AWINIC Technology (2019) and Joseph, and explicitly permits GPL v2 or later.
  The SYV690/BQ2589x reference credits Texas Instruments (2013) and specifies
  GPL v2. K6S command/timing and board wiring were compared with downstream
  device-tree data and a captured Android FDT; the binary capture is excluded.
- **KDE Plasma Mobile:** `veux-plasma-start` and `veux-plasma-prepare` adapt
  `startplasmamobile`. The installed source inspected during this review has
  GPL-2.0-or-later notices for Aleix Pol, Bhushan Shah and Jonah Brüchert.
  Those notices are retained in both helpers. Upstream project:
  [KDE Plasma Mobile](https://invent.kde.org/plasma/plasma-mobile).
- **RMTFS:** [linux-msm/rmtfs](https://github.com/linux-msm/rmtfs), version 1.3;
  the recipe records the expected source archive checksum. The source archive
  is not bundled here.

## Firmware and binary release limits

The source repository excludes firmware, boot templates, APKs and compiled
modules. Some recipes refer to local modem/GPU/IPA/ADSP/amp firmware, and the
boot guide requires a verified Linux template set whose ramdisk contains
firmware. Source licensing does not establish permission to distribute those
inputs or any resulting image/APK.

The amplifier firmware `aw882xx_pid_2113_acf.bin` has not been reviewed for
redistribution rights. The audio APKBUILD now marks the package as including
proprietary material alongside GPL source components, rather than calling the
entire result GPL-only. This metadata is **not** a redistribution grant. Keep
firmware and generated audio packages out of a public binary release until
their actual terms and required notices are established. Apply the same
review to all firmware embedded in the required boot templates.

## Review result and limits

This source review added missing license texts, restored upstream KDE notices
and the Goodix author address, corrected package metadata, and checked that
binary artifacts remain excluded. It did not establish redistribution rights
for external firmware or certify every historical import's provenance. Do not
describe this as legal certification or full REUSE compliance.

Further binary release work remains: identify every firmware input and its
terms, preserve corresponding notices/source obligations for compiled code,
and review the complete contents of each artifact before distributing it.
