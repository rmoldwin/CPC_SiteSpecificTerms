#!/usr/bin/env python3
"""
STEP 2 - Build the candidate universe of terms to research.

Scaling change vs. the digestive pilot:
  The pilot pre-filtered by digestive organ-name KEYWORDS. That was a shortcut
  appropriate to one organ system. For the FULL catalog we do NOT keyword-filter,
  because a term can be site-specific without an obvious organ word in its name.
  Instead we include EVERY term whose code is multi-site (ceiling > 1 site).
  Single-site codes are emitted separately as auto-"No" (no proper subset possible).

System-exclusion filter (locked with user):
  Sites in the 'ill_defined' (C76) and 'unknown_primary' (C80) systems are never researched.
  A code's ceiling is first stripped of those C-prefixes to form an EFFECTIVE (researchable)
  ceiling. Decisions about site-specificity are made against this effective ceiling, and any
  reported subset can only contain researchable sites.
    * If the effective ceiling has >1 site  -> candidate for research (multi-site).
    * If it has exactly 1 site              -> auto-"No" (no proper subset possible).
    * If it has 0 sites (code was ONLY C76/C80) -> excluded entirely; never researched.
  Edit EXCLUDE_PREFIXES below to change which systems are excluded.

Input : master_terms.tsv   (cols: ICDO32_Code, Term [, PrefTerm])
        ceilings.json       (from step 1)
Output: candidates.jsonl    one JSON object per term on a multi-site EFFECTIVE ceiling
                            { code, term, ceiling_count, ceiling_codes }  (ceiling = researchable)
        auto_no.jsonl       one object per term with a single-site effective ceiling (auto "No")
        excluded.jsonl      terms whose code is ONLY excluded systems (never researched)
        candidates_meta.json summary counts

Usage:
  python3 02_build_candidates.py <master_terms.tsv> <ceilings.json> [outdir=.]
"""
import csv, json, sys

# Topography prefixes whose sites are never researched.
# C76 = ill-defined sites; C80 = unknown primary.
EXCLUDE_PREFIXES = {"C76", "C80"}

def researchable(sites):
    return [s for s in sites if s[:3] not in EXCLUDE_PREFIXES]

def main():
    master = sys.argv[1] if len(sys.argv) > 1 else "master_terms.tsv"
    ceilings_path = sys.argv[2] if len(sys.argv) > 2 else "ceilings.json"
    outdir = sys.argv[3].rstrip("/") if len(sys.argv) > 3 else "."

    ceilings = json.load(open(ceilings_path))

    cand = open(f"{outdir}/candidates.jsonl", "w")
    autono = open(f"{outdir}/auto_no.jsonl", "w")
    excluded = open(f"{outdir}/excluded.jsonl", "w")
    eff_ceilings = {}   # code -> researchable ceiling (used by the validator, step 4)
    n_cand = n_auto = n_noceiling = n_excluded = 0

    with open(master, encoding="utf-8-sig") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            code = (row["ICDO32_Code"] or "").strip()
            term = (row["Term"] or "").strip()
            if not code or not term:
                continue
            sites = ceilings.get(code)
            if not sites:                       # code has no SMVL-valid site at all
                n_noceiling += 1
                continue
            eff = researchable(sites)           # strip excluded systems (C76/C80)
            eff_ceilings[code] = eff
            if len(eff) == 0:
                # code is valid ONLY at excluded sites -> never researched
                excluded.write(json.dumps(
                    {"code": code, "term": term, "ceiling_codes": sites}) + "\n")
                n_excluded += 1
                continue
            rec = {"code": code, "term": term,
                   "ceiling_count": len(eff), "ceiling_codes": eff}
            if len(eff) > 1:
                cand.write(json.dumps(rec) + "\n"); n_cand += 1
            else:
                autono.write(json.dumps(rec) + "\n"); n_auto += 1
    cand.close(); autono.close(); excluded.close()

    # Effective (researchable) ceilings for the validator, so strict-subset checks
    # never treat an excluded C76/C80 site as allowed. The workbook (step 6) still
    # reads the TRUE full ceiling from ceilings.json for its display columns.
    json.dump(eff_ceilings, open(f"{outdir}/effective_ceilings.json", "w"))

    meta = {
        "exclude_prefixes": sorted(EXCLUDE_PREFIXES),
        "candidates_multi_site": n_cand,
        "auto_no_single_site": n_auto,
        "excluded_only_excluded_systems": n_excluded,
        "terms_skipped_no_ceiling": n_noceiling,
    }
    json.dump(meta, open(f"{outdir}/candidates_meta.json", "w"), indent=2)
    print(json.dumps(meta, indent=2))

if __name__ == "__main__":
    main()
