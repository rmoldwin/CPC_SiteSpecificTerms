# Plan: Applying the Site-Specific Term Methodology to the Full ICD-O-3.2 Catalog

**Prepared:** 2026-07-08
**Author:** Perplexity Computer
**Scope:** Extend the validated digestive-tract pilot (216 terms → 119 site-specific) to the entire ICDO32 morphology catalog.

---

## 1. What we proved in the pilot

The digestive pilot established and locked a repeatable method:

- **Ceiling** for each code = Cancer PathCHART SMVL rows with `CPC2026A = Valid (1)`; Unlikely and Impossible both excluded.
- **Terms** taken verbatim from the maintained master ICDO32 list (code + term only). Level and ICD-O suggested sites are not used.
- **Site-specific = strict proper subset (Option A):** a term is "Yes" when its literature-confirmed sites are strictly fewer than the code's SMVL ceiling — a whole-organ-system subset still counts.
- **Every "Yes" carries a source URL** (WHO Blue Books 5th ed, NCCN, UpToDate, CAP, PubMed). Unverifiable → "Uncertain". Site-specific terms are rare.
- **Preferred Term** per code from the master `PrefTerm` flag, with a `/2 → /3 (for /3)` fallback and blanks for codes IARC hasn't yet leveled.
- **Output:** README + "Site-Specific Terms" + "All Screened Terms" sheets, 13 columns, Calibri, teal header.

Anchor/regression check: **8140/3 Paneth cell carcinoma → "Yes"** (GI-only subset of a 186-site ceiling), sourced to Zhang et al., Diagnostic Pathology 2019 (PMC6323739).

---

## 2. Full-catalog scope (measured from the real SMVL + master list)

| Quantity | Pilot (digestive) | Full catalog |
|---|---|---|
| Codes with ≥1 SMVL-valid site | — | **816** |
| — multi-site codes (subset possible) | — | **686** |
| — single-site codes (auto "No") | — | **130** |
| Master terms total | 5,616 | 5,616 |
| Terms on multi-site codes = **candidate universe to research** | 216 | **3,263** |
| Terms on single-site codes (auto "No", no research) | — | **574** |
| Terms whose code has no SMVL-valid site (skipped) | — | 1,779 |
| Ceiling size of multi-site codes (min / median / max) | — | 2 / 16 / 327 |

The research workload is roughly **15× the pilot** (3,263 vs 216 terms). This is the cost driver and the reason for delegation + a fresh session.

**System exclusion (locked):** sites in `ill_defined` (C76) and `unknown_primary` (C80) are never researched. Step 2 strips them from each code's ceiling to form an *effective* researchable ceiling, so those sites can never appear in a reported subset. Codes valid *only* at C76/C80 (10 terms) are dropped entirely to `excluded.jsonl`. After exclusion the candidate universe is **3,256 terms** (309 codes had their ceiling shrink). The workbook still displays each code's true full SMVL ceiling; only the researchable subset is ever evaluated.

---

## 3. Reuse strategy — methodology captured as an editable skill + tools

To cut token usage and make the process refinable, the methodology is now externalized into files under `icdo32_pipeline/` instead of living in conversation. All are plain, editable `.py`/`.md` files.

```
icdo32_pipeline/
  SKILL.md                       # orchestration guide + locked rules (loadable skill)
  research_brief_template.md     # the per-batch research prompt (generalized from the pilot brief)
  scripts/
    01_build_ceilings.py         # SMVL -> per-code Valid-site ceilings; multi/single split
    02_build_candidates.py       # terms -> multi-site candidates + single-site auto-No; excludes C76/C80 systems
    03_make_batches.py           # bucket candidates by organ system, chunk into batch files
    04_validate_merge.py         # enforce strict-subset + source rules; merge results
    05_build_pref_map.py         # code -> preferred term (with /3 fallback)
    06_build_workbook.py         # final Excel (README + 2 sheets); optional CSVs
  data/                          # working copies of smvl.csv-derived + master_terms.tsv
```

**Why this saves tokens:** the orchestrator reads only small summary files (`*_meta.json`, `validation_report.json`, `batches_index.json`) — never the large candidate/result JSON. Each research subagent holds only its own ~45-term batch. The deterministic scripts do all the heavy data shaping locally with zero model tokens.

These files are **already smoke-tested on the real data** (step 1 → 816 codes; step 2 → 3,263 candidates; step 3 → 80 batches; step 5 → 1,124 preferred terms). They can be edited between waves as we refine wording, sources, or the batch size.

---

## 4. Execution workflow (per organ system, in waves)

1. **Build once:** run scripts 1, 2, 3, 5 (deterministic, cheap). Produces 80 batch files bucketed by organ system, each ~45 terms.
2. **Research in waves:** for each batch, spawn ONE research subagent — `subagent_type="research"`, `model="claude_opus_4_8"`, `preload_skills=["wide-search"]`, objective = the brief template with the batch's terms + ceilings inlined and an output path `results/<system>_NN.json`. Run 3–5 subagents at a time, `wait_for_subagents`, repeat.
3. **Validate + merge:** run script 4 across the accumulated `results/` — it rejects any site outside the ceiling, demotes bogus "Yes" (no proper subset / no source) to "Uncertain", and merges the single-site auto-"No" terms.
4. **Build workbook:** run script 6 → final Excel. Spot-check the Paneth anchor and skim the validation report.
5. **Refine loop:** if a wave's results look weak (too many "Uncertain", thin sources), edit `research_brief_template.md` or re-batch and re-run just that system.

**Suggested order (start where signal is richest / most auditable):**
`digestive` (already validated) → `gyn` → `urinary` → `male_genital` → `head_neck` → `respiratory` → `breast` → `skin` → `endocrine` → `bone_soft_tissue` → `cns` → `eye` → `heme`.

---

## 5. Cost, quality, and risk controls

- **Cost:** 80 research subagents is the main spend. Running by system in waves lets us checkpoint quality and stop/adjust before committing the whole catalog. I will request confirmation before launching large subagent waves.
- **Quality:** script 4 mechanically enforces the strict-subset and source rules, so no bad "Yes" reaches the workbook. "Uncertain" is a first-class outcome for later human review.
- **Consistency:** ceilings and preferred terms are computed once, deterministically, so every batch shares an identical ground truth.
- **Refinability:** because the brief and scripts are files, any rule change is a one-line edit + re-run, not a re-explanation.

---

## 6. Context / compaction assessment — recommendation

This session has already undergone one compaction and still carries the full pilot state (SMVL parsing, four research batches, a re-review pass, the workbook build, and the preferred-term addition). The full-catalog run will spawn ~80 research subagents emitting large JSON, which would repeatedly reload and bloat this context.

**Recommendation: run execution in a FRESH session dedicated to the full catalog.** The new session needs almost nothing from this one because the method is fully externalized:

- Load the skill: `icdo32_pipeline/SKILL.md`.
- Inputs already staged: `smvl.csv`, `icdo32_pipeline/data/master_terms.tsv` (the version with the `PrefTerm` column).
- Everything else regenerates deterministically from the scripts.

The pilot deliverable (`ICDO32_Site_Specific_Terms.xlsx`) stays valid and can be folded in as the `digestive` results, or regenerated by the new pipeline for full consistency.

---

## 7. Immediate next actions (for the new session)

1. Load `icdo32_pipeline/SKILL.md`; confirm the two input files are present.
2. Run scripts 1 → 2 → 3 → 5; review `ceilings_meta.json`, `candidates_meta.json`, `batches_index.json`.
3. Launch the `digestive` wave first as a re-validation against the known pilot result (Paneth anchor).
4. On a clean anchor + validation report, proceed system-by-system through the order in §4.
5. After all systems merge cleanly, run script 6 for the full-catalog Excel and share it.
