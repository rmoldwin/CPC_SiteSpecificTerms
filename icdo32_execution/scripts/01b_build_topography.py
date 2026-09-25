#!/usr/bin/env python3
"""
STEP 1b - Build / validate the 4-digit ICD-O-3.2 topography label map.

WHY THIS EXISTS
---------------
The workbook labels each subset C-code with a human-readable anatomic site. The
FIRST full-catalog run mislabeled 4-digit codes with their 3-char PARENT-GROUP
name (e.g. C221 shown as "Liver" instead of "Intrahepatic bile duct"), because
06_build_workbook.py only had a 3-char ORGAN prefix dict. This step supplies the
SPECIFIC 4-digit definitions so per-code subset labels are anatomically correct.

`icdo32_topography.json` maps every 4-digit code (e.g. "C221") to its official
ICD-O-3.2 topography term (e.g. "Intrahepatic bile duct").

PROVENANCE (refresh here when a new ICD-O version ships)
--------------------------------------------------------
The label text is the ICD-O-3.2 topographical (C-code) term list. Authoritative
sources used to build/verify the current map:
  - SEER ICD-O-3 site/histology recode & topography reference
    https://seer.cancer.gov/siterecode/icdo3_2023_expanded/  (confirms e.g.
    C220 = Liver, C221 = Intrahepatic bile duct)
  - IARC/WHO ICD-O-3.2 topography axis (WHO Blue Books 5th ed alignment)
  - Cross-check reference: CancerCenter.AI ICD-O-3 topographical codes list
    https://cancercenter.ai/icd-o-pathology-codes/topographical-codes-icd-o-3/

TO REFRESH FOR A NEW ICD-O / WHO BLUE BOOK VERSION
--------------------------------------------------
1. Obtain the new official ICD-O topography (C-code) term list from IARC/SEER.
2. Regenerate icdo32_topography.json as a flat {"Cxxx": "Site term", ...} map.
   (Keep 4-digit keys without the decimal point, matching the SMVL C_Site style.)
3. Run this script to VALIDATE coverage: it fails loudly if any code that appears
   in ceilings.json or decisions.jsonl is missing from the map.

Usage:
  # validate coverage of the existing map against the current run:
  python3 01b_build_topography.py --validate

Inputs (for --validate): icdo32_topography.json, ceilings.json, decisions.jsonl
Output: prints coverage report; non-zero exit if any used code is unmapped.
"""
import json, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")

def load(name):
    return json.load(open(os.path.join(ROOT, name), encoding="utf-8"))

def used_codes():
    """Every C-code referenced anywhere in the current run (ceilings + subsets)."""
    used = set()
    ceil = load("ceilings.json")
    for code, sites in ceil.items():
        if isinstance(sites, dict):
            for k in ("codes", "sites", "valid"):
                if k in sites:
                    sites = sites[k]; break
        used.update(sites)
    with open(os.path.join(ROOT, "decisions.jsonl"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            used.update(r.get("subset_codes", []))
    return used

def validate():
    topo = load("icdo32_topography.json")
    used = used_codes()
    missing = sorted(c for c in used if c not in topo)
    print(f"topography map codes : {len(topo)}")
    print(f"codes used in run    : {len(used)}")
    print(f"missing from map     : {len(missing)}")
    if missing:
        print("MISSING:", missing)
        sys.exit(1)
    print("OK: every used C-code has a specific 4-digit label.")

if __name__ == "__main__":
    if "--validate" in sys.argv:
        validate()
    else:
        print(__doc__)
