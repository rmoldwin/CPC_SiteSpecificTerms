#!/usr/bin/env python3
"""
STEP 0 (one-time) - Seed the completed digestive (GI) pilot decisions into the
fresh execution session so the validator (step 4) folds them in WITHOUT
re-running the digestive research wave.

The pilot's merged decisions live in `final_merged.json` with keys:
  code, term, decision, subset_codes, ceiling_count, subset_count,
  subset_labels, rationale, source, source_name

Step 4 (`04_validate_merge.py`) expects each raw result record to use:
  code, term, site_specific, site_subset_codes, rationale, source, source_name

This script converts the pilot decisions into that raw-result schema and writes
them to `results/digestive_seeded.json`, where step 4 will pick them up exactly
like a fresh research subagent's output (and re-validate them against the
effective ceiling, so they are held to the same rules).

Usage:
  python3 00_seed_digestive.py <final_merged.json> <results_dir>
"""
import json, sys, os

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "final_merged.json"
    results_dir = sys.argv[2] if len(sys.argv) > 2 else "results"
    os.makedirs(results_dir, exist_ok=True)

    pilot = json.load(open(src))
    out = []
    for r in pilot:
        out.append({
            "code": r["code"],
            "term": r["term"],
            "site_specific": r.get("decision", "Uncertain"),
            "site_subset_codes": r.get("subset_codes", []),
            "rationale": r.get("rationale", ""),
            "source": r.get("source", ""),
            "source_name": r.get("source_name", ""),
        })

    dest = os.path.join(results_dir, "digestive_seeded.json")
    json.dump(out, open(dest, "w"), indent=1)

    n_yes = sum(1 for r in out if r["site_specific"] == "Yes")
    n_no  = sum(1 for r in out if r["site_specific"] == "No")
    n_unc = sum(1 for r in out if r["site_specific"] == "Uncertain")
    print(f"seeded {len(out)} digestive decisions -> {dest}")
    print(f"  Yes={n_yes}  No={n_no}  Uncertain={n_unc}  (unique codes={len({r['code'] for r in out})})")

if __name__ == "__main__":
    main()
