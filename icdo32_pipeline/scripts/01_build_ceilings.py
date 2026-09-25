#!/usr/bin/env python3
"""
STEP 1 - Build code-level site ceilings from the Cancer PathCHART SMVL.

Input : SMVL CSV (columns: Key, FullKey, C_Site, Hist, Behavior, CPC2024B, CPC2025B, CPC2026A)
Output: ceilings.json  { "8140/3": ["C000","C001", ...], ... }   (SMVL-valid sites only)
        ceilings_meta.json  { "release": ..., "status_col": ..., "n_codes": ..., "n_multi": ..., "n_single": ... }

Rule (locked with user):
  Allowed site  = SMVL row whose chosen status column == "1" (Valid).
  "Unlikely" (2) and "Impossible" (3) are BOTH excluded (Unlikely treated as impossible).
  A code is eligible for a site-specific term ONLY if it has >1 valid site
  (single-site codes can never have a proper subset -> always "No").

Usage:
  python3 01_build_ceilings.py <smvl.csv> [status_col=CPC2026A] [outdir=.]
"""
import csv, json, sys
from collections import defaultdict

def main():
    smvl = sys.argv[1] if len(sys.argv) > 1 else "smvl.csv"
    status_col = sys.argv[2] if len(sys.argv) > 2 else "CPC2026A"
    outdir = sys.argv[3].rstrip("/") if len(sys.argv) > 3 else "."

    ceiling = defaultdict(set)
    with open(smvl, encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        if status_col not in r.fieldnames:
            raise SystemExit(f"status_col {status_col!r} not in {r.fieldnames}")
        for row in r:
            if (row[status_col] or "").strip() == "1":  # Valid only
                code = f"{row['Hist'].strip()}/{row['Behavior'].strip()}"
                ceiling[code].add(row["C_Site"].strip())

    out = {c: sorted(s) for c, s in ceiling.items()}
    multi = {c: v for c, v in out.items() if len(v) > 1}
    single = {c: v for c, v in out.items() if len(v) == 1}

    json.dump(out, open(f"{outdir}/ceilings.json", "w"))
    meta = {
        "smvl_file": smvl,
        "status_col": status_col,
        "rule": "status==1 (Valid) only; Unlikely(2)+Impossible(3) excluded",
        "n_codes_with_valid_sites": len(out),
        "n_multi_site_codes": len(multi),
        "n_single_site_codes": len(single),
    }
    json.dump(meta, open(f"{outdir}/ceilings_meta.json", "w"), indent=2)
    print(json.dumps(meta, indent=2))

if __name__ == "__main__":
    main()
