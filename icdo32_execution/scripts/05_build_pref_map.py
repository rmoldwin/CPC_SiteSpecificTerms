#!/usr/bin/env python3
"""
STEP 5 - Build the code -> preferred-term map from the master list.

Preferred term = the row whose PrefTerm flag == "1" for that code.
Fallback rule (locked with user): if a /2 (in situ) code has NO preferred term,
use the /3 counterpart's preferred term and append " (for /3)".
Codes still lacking any preferred term are left blank (e.g. new Blue Book
entries IARC has not yet leveled, such as 8148/2).

Input : master_terms.tsv  (cols: ICDO32_Code, Term, PrefTerm)
Output: pref_map.json      { code: "preferred term" or "X (for /3)" or "" }

Usage:
  python3 05_build_pref_map.py <master_terms.tsv> [outdir=.]
"""
import csv, json, sys

def main():
    master = sys.argv[1] if len(sys.argv) > 1 else "master_terms.tsv"
    outdir = sys.argv[2].rstrip("/") if len(sys.argv) > 2 else "."

    pref = {}
    all_codes = set()
    with open(master, encoding="utf-8-sig") as f:
        r = csv.DictReader(f, delimiter="\t")
        has_flag = "PrefTerm" in r.fieldnames
        for row in r:
            code = (row["ICDO32_Code"] or "").strip()
            term = (row["Term"] or "").strip()
            if not code:
                continue
            all_codes.add(code)
            if has_flag and (row.get("PrefTerm") or "").strip() == "1":
                pref.setdefault(code, term)

    final = {}
    for code in sorted(all_codes):
        if code in pref:
            final[code] = pref[code]
        else:
            hist = code.split("/")[0]
            c3 = f"{hist}/3"
            final[code] = f"{pref[c3]} (for /3)" if c3 in pref else ""

    json.dump(final, open(f"{outdir}/pref_map.json", "w"), indent=1)
    blanks = [c for c, v in final.items() if not v]
    print(f"codes: {len(final)}  with_preferred: {sum(1 for v in final.values() if v)}  blank: {len(blanks)}")
    print("blank sample:", blanks[:15])

if __name__ == "__main__":
    main()
