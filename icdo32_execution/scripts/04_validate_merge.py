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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # find clean_term.py
from clean_term import clean as _clean_term  # normalize term for dedup key

def main():
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "results"
    ceilings = json.load(open(sys.argv[2] if len(sys.argv) > 2 else "ceilings.json"))
    autono_path = sys.argv[3] if len(sys.argv) > 3 else "auto_no.jsonl"
    outdir = sys.argv[4].rstrip("/") if len(sys.argv) > 4 else "."

    violations = []
    # merged[(code, EXACT term)] -> best surviving record. We keep EVERY distinct
    # original term (the maintainer wants punctuation/spelling variants such as
    # 'duodenal type' vs 'duodenal-type' or 'AIN III' vs 'AIN 3' preserved as their
    # own rows). The only records collapsed here are TRUE duplicates: the exact same
    # (code, term) reaching us from more than one organ-system batch file. Each row
    # also carries a `normalized_term` (scripts/clean_term.py, a Python port of
    # dbo.Clean) exposed as its own column so downstream resources can join on it.
    merged = {}
    dedup_events = []
    seen = set()

    # ---- Deterministic winner selection for duplicate (code,term) records ----
    _DEC_RANK = {"Yes": 3, "Uncertain": 2, "No": 1}
    def _src_rank(url):
        u = (url or "").lower()
        if not u.strip():
            return 0                      # blank source is weakest
        if "pmc.ncbi" in u or "pubmed" in u or "iarc.who" in u or "whobluebooks" in u:
            return 3                      # primary / authoritative
        if "wikipedia" in u:
            return 1                      # weakest non-blank
        return 2
    def _better(new, cur):
        """Return True if `new` should replace `cur` for the same (code,term).
        Priority: stronger decision (Yes>Uncertain>No) -> for Yes, the more
        SPECIFIC (smaller, still-sourced) proper subset = site of origin, not
        organ-wide spread -> better-sourced -> longer rationale. Fully
        deterministic so re-runs are stable."""
        nk = (
            _DEC_RANK.get(new["decision"], 0),
            # for a Yes, prefer the SMALLER subset (negate count); non-Yes -> 0
            -(new["subset_count"]) if new["decision"] == "Yes" else 0,
            _src_rank(new["source"]),
            len(new["rationale"] or ""),
        )
        ck = (
            _DEC_RANK.get(cur["decision"], 0),
            -(cur["subset_count"]) if cur["decision"] == "Yes" else 0,
            _src_rank(cur["source"]),
            len(cur["rationale"] or ""),
        )
        return nk > ck

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

            rec = {
                "code": code, "term": term, "normalized_term": _clean_term(term),
                "decision": decision,
                "subset_codes": subset if decision == "Yes" else [],
                "subset_count": len(subset) if decision == "Yes" else 0,
                "ceiling_count": len(ceil),
                "rationale": r.get("rationale", ""),
                "source": r.get("source", ""),
                "source_name": r.get("source_name", ""),
            }
            if key in merged:
                # TRUE duplicate: same exact (code, term) from >1 batch. Keep better.
                kept, dropped = (rec, merged[key]) if _better(rec, merged[key]) else (merged[key], rec)
                merged[key] = kept
                dedup_events.append({
                    "code": code, "term": term,
                    "kept_decision": kept["decision"], "kept_subset": kept["subset_codes"],
                    "kept_source": kept["source"],
                    "dropped_decision": dropped["decision"], "dropped_subset": dropped["subset_codes"],
                    "dropped_source": dropped["source"],
                })
            else:
                merged[key] = rec
            seen.add(key)

    # merge auto-No single-site terms (keyed on the EXACT term; only true
    # exact-duplicate (code, term) rows are skipped).
    n_auto = 0
    if os.path.exists(autono_path):
        with open(autono_path) as f:
            for line in f:
                rec = json.loads(line)
                key = (rec["code"], rec["term"])
                if key in seen:      # already covered by research or a prior auto-No
                    continue
                merged[key] = {
                    "code": rec["code"], "term": rec["term"],
                    "normalized_term": _clean_term(rec["term"]),
                    "decision": "No",
                    "subset_codes": [], "subset_count": 0,
                    "ceiling_count": rec["ceiling_count"],
                    "rationale": "Code is SMVL-valid at only one site; a proper site subset is impossible.",
                    "source": "", "source_name": "SMVL (single-site code)",
                }
                seen.add(key); n_auto += 1

    out = list(merged.values())

    with open(f"{outdir}/decisions.jsonl", "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")

    counts = {"Yes":0,"No":0,"Uncertain":0}
    for r in out:
        counts[r["decision"]] = counts.get(r["decision"],0)+1
    report = {"total": len(out), "by_decision": counts,
              "auto_no_merged": n_auto, "violations_fixed": len(violations),
              "duplicates_collapsed": len(dedup_events),
              "dedup_events": dedup_events[:200],
              "violations": violations[:200]}
    json.dump(report, open(f"{outdir}/validation_report.json", "w"), indent=2)
    print(json.dumps({k:v for k,v in report.items() if k!="violations"}, indent=2))

if __name__ == "__main__":
    main()
