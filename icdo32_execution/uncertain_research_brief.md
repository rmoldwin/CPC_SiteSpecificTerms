# Uncertain-row site research — BATCH {BATCH_ID}

You are a pathology/oncology anatomic-site researcher. For each ICD-O-3.2 morphology term below,
determine the BEST POSSIBLE list of appropriate PRIMARY anatomic site(s) of ORIGIN, expressed as
ICD-O topography **C-codes** (4-digit where a specific subsite is definitive; 3-digit parent only
when the entity genuinely spans a whole organ group).

## Background (why these are "Uncertain")
These terms were previously marked "Uncertain" in a site-specificity screen. Most commonly the
literature-confirmed site of origin is NOT inside the code's SMVL-valid "ceiling", so it could not be
recorded under the old strict-subset rule. **That constraint is now LIFTED for this task.** We want
the true site(s) of origin regardless of whether they fall inside the SMVL ceiling.

## What each term row gives you
- `code` — ICD-O-3.2 morphology code (e.g. 8802/3)
- `term` — the exact RAW surface term. **USE THIS RAW STRING for your literature queries** (WHO 5th
  ed Blue Books, PubMed/PMC, NCCN, CAP protocols, ESMO). Query several spellings if a term has
  hyphen/spelling variants; never search a "normalized" form.
- `full_ceiling_codes` / `full_ceiling_labels` — the code's SMVL-valid ceiling (for reference only —
  you may propose sites OUTSIDE it).

## Rules (STRICT)
1. **Site of ORIGIN only.** Name where the tumor ARISES, not where it spreads/invades. No naive
   substring or parent-code guessing.
2. **Prefer specific 4-digit C-codes.** E.g. kidney parenchyma = C649; lung sites C340-C349; skin of
   a specific region (skin of finger = C444? — use the correct ICD-O skin subsite). If an entity is
   defined for an entire organ without a single subsite, a 3-digit parent (e.g. C56 ovary) is
   acceptable — say so.
3. **Multiple sites allowed.** If an entity genuinely arises at 2-4 sites, list them all.
4. **Flag in/out of ceiling.** For each proposed C-code, note whether it is IN the code's
   `full_ceiling_codes` ("in_ceiling") or NOT ("outside_ceiling / not SMVL-valid for this code").
5. **Every proposed site needs a real, fetched source URL** — WHO Blue Books, PMC/PubMed (preferred,
   use real PMCID/PMID URLs you actually retrieved), NCCN, CAP, ESMO. Quote the defining sentence.
   NEVER fabricate a URL or PMCID. If you cannot verify a site, mark it `unresolved` with a short
   reason — do NOT guess.
6. **Accuracy over completeness.** A well-sourced "unresolved" is better than a wrong site.

## Output — write ONLY this JSON array to `uncertain_results/{BATCH_ID}.json`
```json
[
  {
    "code": "8802/3",
    "term": "Anaplastic sarcoma of the kidney",
    "proposed_codes": ["C649"],
    "proposed_labels": ["Kidney, NOS"],
    "site_status": "outside_ceiling",
    "resolution": "resolved",
    "rationale": "WHO Urinary/Male Genital 5th ed and Vujanic et al define anaplastic sarcoma of kidney as a renal parenchymal tumor of childhood arising in the kidney.",
    "source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMCxxxxxxx/",
    "source_ref": "Vujanić GM et al. ... (year)"
  }
]
```
- `site_status`: "in_ceiling" | "outside_ceiling" | "mixed" (some in, some out)
- `resolution`: "resolved" | "unresolved"
- For `unresolved`, set `proposed_codes`/`proposed_labels` to [] and explain in `rationale`.
- One object per term (keep the exact raw `term` string so we can join back).

Write the file, then reply with a one-line summary: N resolved / M unresolved.
