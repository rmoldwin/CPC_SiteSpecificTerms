#!/usr/bin/env python3
"""
STEP 7 - Anatomic-correctness audit of assigned subset sites, and application of
confirmed corrections back into decisions.jsonl.

WHY THIS EXISTS
---------------
After the research waves assign each "Yes" term a subset of C-codes, a final
audit checks that every assigned site is the anatomic SITE OF ORIGIN of that
tumor term (not a site of secondary invasion, and not a naive substring/parent
mismatch). The first full run surfaced these systematic error classes:
  - parent-group vs specific-site confusion (labeling artifact, fixed in 06);
  - site of INVASION vs site of ORIGIN (e.g. retinoinvasive melanoma: retina
    C692 is invaded, origin is uvea C693/C694);
  - gland/tissue-distribution errors (e.g. ceruminous carcinoma 8420/3: glands
    exist only in external-ear skin C442, never middle ear C301);
  - wrong organ subsite (e.g. undifferentiated uterine sarcoma 8805/3 arises in
    corpus uteri, not cervix).

AUDIT PROCEDURE (reproducible)
------------------------------
1. Extract all "Yes" decisions with their subset_codes + 4-digit labels
   (yes_for_review.json).
2. Batch them (~90/batch) and, for each batch, spawn ONE research subagent with
   AUDIT_BRIEF.txt: for every (term, assigned sites) pair, judge OK / WRONG_SITE
   / UNSURE with a fetched source URL for any WRONG_SITE. Schema per record:
   {code, term, audit, corrected_codes, correction_reason, source}.
3. Collect audit_results/audit_NN.json.
4. Run this script with --apply to fold confirmed WRONG_SITE corrections into
   decisions.jsonl. IT ENFORCES THE LOCKED RULES:
     - corrected_codes must all be within the code's EFFECTIVE SMVL ceiling
       (effective_ceilings.json). Any correction proposing a site outside the
       ceiling is REJECTED (printed, not applied) — the ceiling is ground truth.
     - result must remain a STRICT proper subset, or the record is rejected.
   For a code whose true origin site is not SMVL-valid, keep only the ceiling-
   valid origin codes (this is what happened for 8805/3 -> C542 only).

CORRECTIONS APPLIED IN THE 2026-07-09 RUN (6 records)
-----------------------------------------------------
  8720/3 Retinoinvasive melanoma   C692,C694 -> C693,C694  (retina=invasion)
  8805/3 Undiff. uterine sarcoma   cervix    -> C542        (corpus uteri; only
                                                             C542 is SMVL-valid)
  8420/3 Ceruminous adenocarcinoma        C301 -> C442      (external ear skin)
  8420/3 Ceruminous adenoid cystic carc.  C301 -> C442
  8420/3 Ceruminous carcinoma             C301 -> C442
  8420/3 Ceruminous mucoepidermoid carc.  C301 -> C442
Cholangiocarcinomas needed NO data change — their subset_codes were already
correct (C221/C240/C248/C249); only the display label was wrong (fixed in 06).

Usage:
  python3 07_site_correction_audit.py --apply corrections.json
    corrections.json = list of {code, term, corrected_codes, reason, source,
    source_name}. See CORRECTIONS_2026_07_09 below for the canonical set.
"""
import json, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")

# Canonical corrections from the 2026-07-09 audit (re-applies idempotently).
CORRECTIONS_2026_07_09 = [
    {"code": "8720/3", "term": "Retinoinvasive melanoma",
     "corrected_codes": ["C693", "C694"],
     "reason": "retina C692 is site of secondary invasion, not origin; retinoinvasive uveal melanoma arises in choroid (C693)/ciliary body (C694).",
     "source": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5757583/",
     "source_name": "Ocul Oncol Pathol 2017, Retinoinvasive uveal melanoma, PMC5757583"},
    {"code": "8805/3", "term": "Undifferentiated uterine sarcoma",
     "corrected_codes": ["C542"],
     "reason": "arises in corpus uteri (endometrial stromal category), not cervix; cervix codes removed. Of corpus-uteri codes only C542 (myometrium) is SMVL-valid.",
     "source": "https://my.clevelandclinic.org/health/diseases/16408-uterine-sarcoma",
     "source_name": "Cleveland Clinic, Uterine Sarcoma; WHO 5th ed Female Genital Tumours 2020 (ICCR)"},
]
for _t in ("Ceruminous adenocarcinoma", "Ceruminous adenoid cystic carcinoma",
           "Ceruminous carcinoma", "Ceruminous mucoepidermoid carcinoma"):
    CORRECTIONS_2026_07_09.append({
        "code": "8420/3", "term": _t, "corrected_codes": ["C442"],
        "reason": "ceruminous glands occur only in skin of external auditory canal (C442 external ear), not middle ear (C301).",
        "source": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8294997/",
        "source_name": "Ceruminous gland tumours arise in external auditory canal skin; PMC8294997"})


def _norm(x):
    if isinstance(x, dict):
        for k in ("codes", "sites", "valid"):
            if k in x:
                return x[k]
    return x


def apply(corrections):
    eff = json.load(open(os.path.join(ROOT, "effective_ceilings.json"), encoding="utf-8"))
    corr_map = {(c["code"], c["term"]): c for c in corrections}
    applied, rejected = [], []
    out = []
    with open(os.path.join(ROOT, "decisions.jsonl"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            key = (r["code"], r["term"])
            c = corr_map.get(key)
            if c:
                effc = set(_norm(eff.get(r["code"], [])) or [])
                new = list(c["corrected_codes"])
                bad = [x for x in new if x not in effc]
                if bad:
                    rejected.append((key, "outside ceiling", bad)); out.append(r); continue
                if not (0 < len(new) < len(effc)):
                    rejected.append((key, "not a strict proper subset", (len(new), len(effc)))); out.append(r); continue
                r["subset_codes"] = new
                r["subset_count"] = len(new)
                note = f"Site corrected (audit): {c['reason']}"
                # Idempotent: only append if NO site-correction note is present yet
                # (dedupe on the marker, not exact wording).
                if "Site corrected" not in (r.get("rationale") or ""):
                    r["rationale"] = ((r.get("rationale", "") + " | ") if r.get("rationale") else "") + note
                r["source"] = c["source"]
                r["source_name"] = c["source_name"]
                applied.append(key)
            out.append(r)
    with open(os.path.join(ROOT, "decisions.jsonl"), "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"applied {len(applied)} corrections; rejected {len(rejected)}")
    for k in applied:
        print("  applied:", k)
    for k, why, det in rejected:
        print("  REJECTED:", k, why, det)


if __name__ == "__main__":
    if "--apply" in sys.argv:
        idx = sys.argv.index("--apply")
        if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith("--"):
            corrections = json.load(open(sys.argv[idx + 1], encoding="utf-8"))
        else:
            corrections = CORRECTIONS_2026_07_09
        apply(corrections)
    else:
        print(__doc__)
