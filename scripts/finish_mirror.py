#!/usr/bin/env python3
"""Resumable mirror completer for DumbOS-ROM.
Forks any missing LineageOS / LineageOS-UL repositories referenced by this manifest
(across lineage-20.0, lineage-21.0, lineage-22.2) into github.com/DumbOS-ROM."""
import json, pathlib, subprocess, sys, time, xml.etree.ElementTree as ET

ORG = "DumbOS-ROM"
EXCLUDE_PREFIXES = ("LineageOS/", "LineageOS-UL/", "platform/")
PROTECTED = {"android", "android_vendor_dumbos", "android_vendor_partner_gms"}

def gh_api(method, ep, data=None):
    cmd = ["gh", "api", "-X", method, ep]
    if data is not None:
        cmd += ["--input", "-"]
    return subprocess.run(cmd, input=json.dumps(data) if data is not None else None, text=True, capture_output=True)

def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    existing = set(subprocess.check_output(
        ["gh", "api", f"orgs/{ORG}/repos?per_page=100", "--paginate", "--jq", ".[].name"], text=True
    ).splitlines())

    needed = {}
    branches = subprocess.check_output(["git", "-C", str(root), "for-each-ref", "--format=%(refname:short)", "refs/heads/", "refs/remotes/"], text=True).splitlines()
    target_branches = [b for b in ("lineage-20.0", "lineage-21.0", "lineage-22.2") if any(b in x for x in branches)]
    for br in (target_branches or ["HEAD"]):
        for fn in ("default.xml", "snippets/lineage.xml", "lineage-ul.xml", "snippets/lineage-ul.xml", "snippets/losul.xml"):
            p = subprocess.run(["git", "-C", str(root), "show", f"{br}:{fn}"], text=True, capture_output=True)
            if p.returncode != 0:
                continue
            for el in ET.fromstring(p.stdout).findall("project"):
                name = el.attrib.get("name", "")
                if name.startswith(EXCLUDE_PREFIXES) or name in PROTECTED:
                    continue
                if name.endswith("-ul"):
                    src = f"LineageOS-UL/{name[:-3]}"
                elif "losul" in fn and el.attrib.get("remote") == "dumbos":
                    # Check whether repo lives in LineageOS-UL or LineageOS
                    src = f"LineageOS-UL/{name}" if name not in existing else None
                else:
                    src = f"LineageOS/{name}"
                if src:
                    needed[name] = src

    pending = [(dst, src) for dst, src in sorted(needed.items()) if dst not in existing]
    print(f"Existing in {ORG}: {len(existing)} | Missing from manifest: {len(pending)}")
    if not pending:
        print("All manifest repositories are already mirrored in DumbOS-ROM!")
        return

    for idx, (dst, src) in enumerate(pending, 1):
        payload = {"organization": ORG, "default_branch_only": False}
        if dst != src.split("/", 1)[1]:
            payload["name"] = dst
        while True:
            r = gh_api("POST", f"repos/{src}/forks", payload)
            if r.returncode == 0:
                print(f"[{idx}/{len(pending)}] Forked {src} -> {ORG}/{dst}", flush=True)
                break
            err = (r.stderr + " " + r.stdout).lower()
            if any(k in err for k in ("403", "429", "too quickly", "rate limit")):
                print("[RATE LIMIT] GitHub secondary fork limit active; sleeping 15 minutes before resuming...", flush=True)
                time.sleep(900)
            elif "404" in err and src.startswith("LineageOS-UL/"):
                src = f"LineageOS/{src.split('/', 1)[1]}"
            else:
                print(f"[ERROR] {src} -> {dst}: {r.stderr.strip()}", file=sys.stderr)
                sys.exit(1)
        time.sleep(2.5)

if __name__ == "__main__":
    main()
