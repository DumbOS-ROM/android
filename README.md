# DumbOS (lineage-22.2 — Android 15)

**DumbOS** is a standalone, ultra-lightweight, pure **Black & White (`#000000` / `#FFFFFF`)** Android ROM distribution mirrored and forked under [`github.com/DumbOS-ROM`](https://github.com/DumbOS-ROM).

Built to be **completely isolated from upstream LineageOS pushes**, while preserving **100% compatibility with standard LineageOS device trees & kernels** — just drop your device's `.repo/local_manifests/` and run `brunch <codename>`.

---

## Supported Branches

| Android | Branch | Alias | Ultra-Legacy Manifest |
| :--- | :--- | :--- | :--- |
| **Android 13** | [`lineage-20.0`](https://github.com/DumbOS-ROM/android/tree/lineage-20.0) | `android-13` | `lineage-ul.xml` |
| **Android 14** | [`lineage-21.0`](https://github.com/DumbOS-ROM/android/tree/lineage-21.0) (`main`) | `android-14` | `lineage-ul.xml` |
| **Android 15** | [`lineage-22.2`](https://github.com/DumbOS-ROM/android/tree/lineage-22.2) | `android-15` | — |

---

## How to Build (Same Workflow as LineageOS)

```bash
mkdir -p ~/dumbos-15 && cd ~/dumbos-15

# 1. Initialize DumbOS standalone manifest (lineage-22.2)
repo init -u https://github.com/DumbOS-ROM/android.git -b lineage-22.2 --git-lfs --depth=1

# 2. Drop any LineageOS-compatible device tree manifest into .repo/local_manifests/
#    (remote="github" works directly with your existing device manifests!)
cp /path/to/your_device.xml .repo/local_manifests/device.xml

# 3. Sync sources (100% served from DumbOS-ROM mirrors; WebView LFS prebuilts pinned by SHA-1)
repo sync -c -j$(nproc) --force-sync --no-clone-bundle --no-tags

# 4. Build (outputs DumbOS-*.zip with zero device-tree edits needed)
source build/envsetup.sh
brunch <device_codename>
```

---

## Key Features & Optimizations
- **100% Isolated Distribution**: All ROM repos live under `DumbOS-ROM/*` (`default.xml` defaults to `remote="dumbos"`). Upstream LineageOS commits will not alter your ROM builds unless you explicitly merge them.
- **Custom Pure Black & White `DumbLauncher`** (`vendor/dumbos/apps/DumbLauncher`): Built natively in Java (~80 KB, zero Kotlin/AndroidX bloat) matching the OLED mockup — `#000000` canvas, clock + date, clickable `Mode: Normal` pill (`Normal`, `Fokus (DND)`, `Hanya Telepon & SMS`, `Malam (Hitam-Putih)`), `[Kunci]` instant sleep, pure-text favorites, and instant A–Z drawer + native Quick Settings Tile (`DumbModeTileService`).
- **SystemUI Lockscreen & Monochrome Engine**: `ThemeOverlayController` defaults to zero-chroma `Style.MONOCHROMATIC`, `DumbModeBadgeView` displays live mode on the Lockscreen, and notification cards render with `#070707` fill, `8dp` corners, and `1dp #1D1D1D` hairline borders.
- **Ultra-Light Debloat & Font Trim**: Strips ~75 MB CJK fonts, ~20 MB ML TextClassifier models, `ThemePicker`, `IconPack*`, `IconShape*`, `AudioFX`, `Eleven`/`Twelve`, `Etar`, `Recorder`, `Seedvault`, `Jelly`, and `LineageSetupWizard` via Soong `overrides`, while retaining `TrebuchetQuickStep`/`Go` for native Recents, `Aperture`, `DeskClock`, `ExactCalculator`, `DocumentsUI`, and `microG` (working cleanly in both `-userdebug` and `-user`).
- **Device Kernel Untouched**: Uses each device's own kernel as-is (`ro.lmk.use_psi` is never forced). Maintainers looking for extra low-RAM defconfig tweaks can consult `vendor/dumbos/docs/KERNEL_RECOMMENDATIONS.md`.
