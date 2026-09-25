#!/usr/bin/env python3
"""
STEP 4 - Validate subagent results and merge into one decisions file.

Enforces the locked rules on every returned record:
  * site_subset_codes MUST be a STRICT proper subset of the code's ceiling.
    - Any code not in the ceiling -> rule violation (drop that stray code, log it).
    - subset == full ceiling -> NOT site-specific; force decision "No".
    - subset empty but decision "Yes" -> demote to "Uncertain" (needs sites).
  * decision "Yes" REQUIRES a source URL. Missing -> demote to "Uncertain".
Auto-"No" single-site terms (from step 2) are merged in as decision "No".

Input : batches results dir (*.json, each a list of decision objects),
        effective_ceilings.json (from step 2 - excludes C76/C80), auto_no.jsonl
        NOTE: pass effective_ceilings.json here, NOT the raw ceilings.json, so the
        strict-subset check never treats an excluded C76/C80 site as allowed.
Output: decisions.jsonl  merged, validated, one object per term
        validation_report.json  counts + list of violations fixed

Usage:
  python3 04_validate_merge.py <results_dir> <effective_ceilings.json> <auto_no.jsonl> [outdir=.]
"""
import json, sys, os, glob

def main():
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "results"
    ceilings = json.load(open(sys.argv[2] if len(sys.argv) > 2 else "ceilings.json"))
    autono_path = sys.argv[3] if len(sys.argv) > 3 else "auto_no.jsonl"
    outdir = sys.argv[4].rstrip("/") if len(sys.argv) > 4 else "."

    violations = []
    out = []
    seen = set()

    for fn in sorted(glob.glob(f"{results_dir}/*.json")):
        try:
            recs = json.load(open(fn))
        except Exception as e:
            violations.append({"file": fn, "error": f"unreadable: {e}"}); continue
        if isinstance(recs, dict):
            recs = [recs]
        for r in recs:
            code = str(r.get("code", "")).strip()
            term = str(r.get("term", "")).strip()
            key = (code, term)
            ceil = set(ceilings.get(code, []))
            subset = [c for c in (r.get("site_subset_codes") or []) if c]
            decision = (r.get("site_specific") or "").strip() or "Uncertain"

            # drop stray codes outside ceiling
            stray = [c for c in subset if c not in ceil]
            if stray:
                violations.append({"code": code, "term": term, "stray_codes": stray})
                subset = [c for c in subset if c in ceil]

            # subset == full ceiling => not site-specific
            if decision == "Yes" and ceil and set(subset) == ceil:
                violations.append({"code": code, "term": term, "issue": "subset==ceiling -> No"})
                decision = "No"; subset = []
            # Yes needs a proper non-empty subset
            if decision == "Yes" and (not subset or len(subset) >= len(ceil)):
                violations.append({"code": code, "term": term, "issue": "Yes without proper subset -> Uncertain"})
                decision = "Uncertain"
            # Yes needs a source
            if decision == "Yes" and not (r.get("source") or "").strip():
                violations.append({"code": code, "term": term, "issue": "Yes without source -> Uncertain"})
                decision = "Uncertain"

            out.append({
                "code": code, "term": term, "decision": decision,
                "subset_codes": subset if decision == "Yes" else [],
                "subset_count": len(subset) if decision == "Yes" else 0,
                "ceiling_count": len(ceil),
                "rationale": r.get("rationale", ""),
                "source": r.get("source", ""),
                "source_name": r.get("source_name", ""),
            })
            seen.add(key)

    # merge auto-No single-site terms
    n_auto = 0
    if os.path.exists(autono_path):
        with open(autono_path) as f:
            for line in f:
                rec = json.loads(line)
                key = (rec["code"], rec["term"])
                if key in seen:
                    continue
                out.append({
                    "code": rec["code"], "term": rec["term"], "decision": "No",
                    "subset_codes": [], "subset_count": 0,
                    "ceiling_count": rec["ceiling_count"],
                    "rationale": "Code is SMVL-valid at only one site; a proper site subset is impossible.",
                    "source": "", "source_name": "SMVL (single-site code)",
                })
                seen.add(key); n_auto += 1

    with open(f"{outdir}/decisions.jsonl", "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")

    counts = {"Yes":0,"No":0,"Uncertain":0}
    for r in out:
        counts[r["decision"]] = counts.get(r["decision"],0)+1
    report = {"total": len(out), "by_decision": counts,
              "auto_no_merged": n_auto, "violations_fixed": len(violations),
              "violations": violations[:200]}
    json.dump(report, open(f"{outdir}/validation_report.json", "w"), indent=2)
    print(json.dumps({k:v for k,v in report.items() if k!="violations"}, indent=2))

if __name__ == "__main__":
    main()
