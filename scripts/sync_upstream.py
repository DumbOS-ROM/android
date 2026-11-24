#!/usr/bin/env python3
"""Optional maintainer helper: fast-forwards unmodified DumbOS-ROM mirrors from upstream
LineageOS / LineageOS-UL ONLY when run manually. Never modifies custom DumbOS forks
automatically so upstream pushes cannot silently alter DumbOS builds."""
import argparse
import pathlib
import subprocess
import sys
import xml.etree.ElementTree as ET

PROTECTED_REPOS = {
    "android",
    "android_vendor_dumbos",
    "android_frameworks_base",
    "android_frameworks_base-ul",
    "android_vendor_lineage",
    "android_vendor_lineage-ul",
}

def main():
    ap = argparse.ArgumentParser(description="Manually sync upstream LineageOS mirrors into DumbOS-ROM")
    ap.add_argument("--branch", default="lineage-21.0", choices=["lineage-20.0", "lineage-21.0", "lineage-22.2"])
    ap.add_argument("--dry-run", action="store_true", help="List upstream vs DumbOS-ROM drift without syncing")
    args = ap.parse_args()

    root = pathlib.Path(__file__).resolve().parent.parent
    repos = set()
    for fname in ("default.xml", "snippets/lineage.xml"):
        fpath = root / fname
        if not fpath.exists():
            continue
        for proj in ET.parse(fpath).getroot().findall("project"):
            rem = proj.attrib.get("remote", "dumbos")
            name = proj.attrib.get("name", "")
            if rem == "dumbos" and name not in PROTECTED_REPOS and name.startswith("android"):
                repos.add(name)

    print(f"Found {len(repos)} unmodified mirror repos for {args.branch}. Protected forks: {sorted(PROTECTED_REPOS)}")
    if args.dry_run:
        for r in sorted(repos):
            print(f"  [DRY-RUN] gh api -X POST repos/DumbOS-ROM/{r}/merge-upstream -f branch={args.branch}")
        return

    ok = err = 0
    for r in sorted(repos):
        p = subprocess.run(
            ["gh", "api", "-X", "POST", f"repos/DumbOS-ROM/{r}/merge-upstream", "-f", f"branch={args.branch}"],
            text=True, capture_output=True,
        )
        if p.returncode == 0:
            ok += 1
        else:
            err += 1
            print(f"  [WARN] {r}: {p.stderr.strip()}")
    print(f"Upstream sync finished: ok={ok}, errors={err}")
    if err:
        sys.exit(1)

if __name__ == "__main__":
    main()
