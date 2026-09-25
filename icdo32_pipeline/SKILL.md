---
name: icdo32-site-specific-terms
description: Detect ICD-O-3.2 (ICDO32) morphology terms that are used at only a proper subset of the anatomic sites their code is validated for in the NCI/SEER Cancer PathCHART SMVL. Produces a CSV/Excel release listing each site-specific term, its code, preferred term, the specific site subset (codes + labels), the code's full SMVL-valid ceiling, and a literature source. Load when working on ICDO32 site-specific term detection, extending the digestive pilot to other organ systems, or refining this methodology.
---

# ICD-O-3.2 Site-Specific Term Detection

Reusable pipeline for finding ICDO32 morphology **terms** that occur at only a **proper subset**
of the anatomic sites their **code** is SMVL-valid for. Built and validated on a digestive-tract
pilot (216 terms → 119 site-specific); designed to scale to the full ~816-code / ~3,263-term catalog.

## Locked rules (do not deviate without user sign-off)
1. **Ceiling = SMVL Valid only.** Allowed sites for a code = SMVL rows whose chosen status column
   (default `CPC2026A`) == `1` (Valid). "Unlikely" (2) and "Impossible" (3) are BOTH excluded
   ("treat Unlikely as impossible").
2. **Terms come from the master ICDO32 list** (code + term). Term **level** and ICD-O
   **suggested/parenthetical sites** are NOT used for validity — only the SMVL.
3. **Candidate universe = every term on a multi-site code.** Single-site codes can never have a
   proper subset → auto "No". (No organ-name keyword pre-filter at full scale; the pilot's
   keyword shortlist was a digestive-only shortcut.)
4. **Site-specific = strict proper subset (Option A).** A term is "Yes" when its literature-confirmed
   sites are strictly fewer than the code's ceiling — a whole-organ-system subset still counts.
5. **Every "Yes" needs a source URL** (WHO Blue Books 5th ed, NCCN, UpToDate, CAP, PubMed).
   Unverifiable → "Uncertain", never a guess. Site-specific terms are RARE.
6. **Preferred Term column:** master `PrefTerm=1` flag; a `/2` code lacking a preferred term falls
   back to the `/3` preferred term marked `(for /3)`; otherwise left blank.
7. **System exclusion:** sites in `ill_defined` (C76) and `unknown_primary` (C80) are NEVER
   researched. Step 2 strips them to form an EFFECTIVE ceiling; site-specificity is judged against
   that. Codes valid ONLY at C76/C80 are dropped to `excluded.jsonl`. Edit `EXCLUDE_PREFIXES` in
   `02_build_candidates.py` to change the excluded systems. The workbook still displays each code's
   TRUE full ceiling; only the researchable subset is ever evaluated.

## Inputs required in the working dir
- `smvl.csv` — Cancer PathCHART SMVL (cols: Key, FullKey, C_Site, Hist, Behavior, CPC2024B,
  CPC2025B, CPC2026A). Source: seer.cancer.gov/cancerpathchart. Parse with `encoding='utf-8-sig'`.
- `master_terms.tsv` — authoritative ICDO32 term list. MUST include the `PrefTerm` column
  (cols: ICDO32_Code, Term, PrefTerm) or step 5 yields zero preferred terms. Use the maintainer's
  latest export; an older 2-column version will silently blank the Preferred Term column.

## Pipeline (scripts/ — run in order)
| Step | Script | Purpose | Output |
|------|--------|---------|--------|
| 1 | `01_build_ceilings.py` | SMVL → per-code Valid-site ceilings; classify multi/single | `ceilings.json`, `ceilings_meta.json` |
| 2 | `02_build_candidates.py` | Split terms into multi-site candidates vs single-site auto-No; strip excluded systems (C76/C80) | `candidates.jsonl`, `auto_no.jsonl`, `excluded.jsonl`, `effective_ceilings.json` |
| 3 | `03_make_batches.py` | Bucket candidates by organ system, chunk into batch files | `batches/<system>_NN.json`, `batches_index.json` |
| — | (research) | One `run_subagent` per batch, using `research_brief_template.md` | `results/<system>_NN.json` |
| 4 | `04_validate_merge.py` | Enforce subset rules (against `effective_ceilings.json`), merge results + auto-No | `decisions.jsonl`, `validation_report.json` |
| 5 | `05_build_pref_map.py` | Code → preferred term (with /3 fallback) | `pref_map.json` |
| 6 | `06_build_workbook.py` | Final Excel (README + 2 sheets); reads TRUE full `ceilings.json` for display; `--csv` optional | `<out>.xlsx` |

## Research step (the token-heavy part — delegate)
For each batch file, spawn ONE research subagent:
- `subagent_type="research"`, `model="claude_opus_4_8"`, `preload_skills=["wide-search"]`.
- Objective = contents of `research_brief_template.md` with `{SYSTEM}`/`{BATCH_ID}` filled, the batch's
  term list (each with its `ceiling_codes`) inlined, and the exact output path
  `results/<system>_NN.json`.
- Run organ systems in waves (e.g. 3-5 subagents at a time), `wait_for_subagents`, then validate.
- Keep raw result JSON in files; never pull full batch results back into the orchestrator context.

## Token / context discipline
- Orchestrator should read only `*_meta.json`, `validation_report.json`, and `batches_index.json` —
  never the large `candidates.jsonl` / `decisions.jsonl` / result files in full (grep or head).
- Each research subagent holds only its own batch (~45 terms), so its context stays bounded.
- Because full-catalog volume is ~15× the pilot, run in a FRESH session dedicated to execution.

## Anchor / regression check
`8140/3 Paneth cell carcinoma` must resolve to "Yes" (GI-only subset of a 186-site ceiling), sourced
to Zhang et al., Diagnostic Pathology 2019 (PMC6323739). Use this as a smoke test after any refactor.
