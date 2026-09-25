---
name: icdo32-site-specific-terms
description: "Detect ICD-O-3.2 (ICDO32) morphology terms that are used at only a proper subset of the anatomic sites their code is validated for in the NCI/SEER Cancer PathCHART SMVL. Produces an Excel release listing each site-specific term, its code, preferred term, the specific site subset (codes + labels), the code's full SMVL-valid ceiling, and a literature source. Load when working on ICDO32 site-specific term detection, extending the digestive pilot to other organ systems, or refining this methodology."
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
8. **Site labels use SPECIFIC 4-digit topography, never the parent group.** Per-code subset sites
   are labeled from `icdo32_topography.json` (e.g. `C221 = Intrahepatic bile duct`, NOT the `C22`
   "Liver" parent group). The ceiling *organ-summary* column may group to parent organ for
   readability, but per-code subset labels must be the specific 4-digit definition. (First full run
   mislabeled 4-digit codes with the 3-char parent name — do not regress this.)
9. **Assigned sites must be the site of ORIGIN.** A subset code names where the tumor arises, not a
   site it secondarily invades, and not a naive substring/parent match. Enforced by the step-7
   anatomic-correctness audit before release.
10. **Keep every distinct RAW term as its own row; add a NORMALIZED-term column for joining.**
    (Supersedes the earlier "one row per normalized term" plan — maintainer decided 2026-07-09 to
    PRESERVE variants, not collapse them.) The workbook has both `ICDO32 Term` (verbatim, for display)
    and `Normalized Term` (= `clean(term)`, for joining/comparison). Rule 11 governs how normalization
    is used. Step 4 still collapses ONLY true exact-duplicate `(code, term)` rows that reach the merge
    from more than one organ-system batch (same code AND same exact term string); it uses the
    deterministic tie-break: stronger decision (`Yes`>`Uncertain`>`No`); for a `Yes`, the SMALLER
    (more specific, still sourced) proper subset = site of ORIGIN wins over a broader/organ-wide set;
    then better source (PMC/PubMed/IARC > other > Wikipedia > blank); then longer rationale. Variant
    spellings (`duodenal type` vs `duodenal-type`, `AIN III` vs `AIN 3`, `Oesophageal` vs `Esophageal`,
    `Adenocarcinoma, NOS` vs `Adenocarcinoma`) are DIFFERENT raw terms — they stay on separate rows and
    naturally share a `Normalized Term` value. Word order is NEVER normalized (distinct synonyms).
    Adjacent normalized-equal rows MAY legitimately carry different decisions/subsets — that is
    expected and is not re-researched.
11. **Normalization is a COMPARISON key, applied symmetrically — never a literature-search query.**
    Any time two terms are compared or joined (dedup, cross-walking to SEER/NAACCR/SQL tables, matching
    to another resource), run `clean()` on BOTH sides and compare normalized-to-normalized — never
    raw-vs-normalized. BUT the normalized form is a WORSE search string than the raw term: `clean()`
    strips `NOS`/`type`, turns dashes/`/`→space, drops parentheticals, forces American spelling
    (`Oesophageal`→`Esophageal`), and numeralizes Roman→Arabic (`III`→`3`). A PubMed/WHO/NCCN query
    built from the normalized string will MISS papers that use the original surface form. So for any
    FUTURE literature research: **group candidates by `(code, clean(term))` to research each group
    once, but issue the actual queries using the RAW surface variant(s)** in the group (query several
    spellings if they differ meaningfully), then key the finding back on the normalized term. See
    "Character variations that affect literature search" below. (No re-research of the current catalog:
    maintainer 2026-07-09 — existing decisions stand; discrepancies between normalized-equal rows are
    acceptable and surface naturally in the sheet.)

## Inputs required in the working dir
- `smvl.csv` — Cancer PathCHART SMVL (cols: Key, FullKey, C_Site, Hist, Behavior, CPC2024B,
  CPC2025B, CPC2026A). Source: seer.cancer.gov/cancerpathchart. Parse with `encoding='utf-8-sig'`.
- `master_terms.tsv` — authoritative ICDO32 term list. MUST include the `PrefTerm` column
  (cols: ICDO32_Code, Term, PrefTerm) or step 5 yields zero preferred terms. Use the maintainer's
  latest export; an older 2-column version will silently blank the Preferred Term column.
- `scripts/clean_term.py` — Python port of the maintainer's `dbo.Clean` T-SQL UDF used to normalize
  term strings for the step-4 dedup key. Faithful to the SQL, with THREE agreed, clearly-commented
  deviations that fix SQL bugs (see "Known SQL-source bugs" below). Refresh this port if the
  maintainer edits `dbo.Clean`.
- `icdo32_topography.json` — flat `{"Cxxx": "Specific 4-digit site term", ...}` map covering every
  C-code that appears in any ceiling or subset. Source = official ICD-O topography (C-code) term
  list (IARC/SEER). Used by step 6 for per-code subset labels. Refresh it when the ICD-O version
  changes (see "Version refresh" below), then run `01b_build_topography.py --validate` to confirm
  0 codes are unmapped.

## Pipeline (scripts/ — run in order)
| Step | Script | Purpose | Output |
|------|--------|---------|--------|
| 0 | `00_seed_digestive.py` | (one-time) Convert the completed GI pilot decisions (`final_merged.json`) into the raw-result schema so step 4 folds them in without re-research | `results/digestive_seeded.json` |
| 1 | `01_build_ceilings.py` | SMVL → per-code Valid-site ceilings; classify multi/single | `ceilings.json`, `ceilings_meta.json` |
| 1b | `01b_build_topography.py --validate` | Validate that `icdo32_topography.json` covers every used C-code (fails loudly on any gap). Provenance + refresh notes in the script header. | (report; exit≠0 on gaps) |
| 2 | `02_build_candidates.py` | Split terms into multi-site candidates vs single-site auto-No; strip excluded systems (C76/C80) | `candidates.jsonl`, `auto_no.jsonl`, `excluded.jsonl`, `effective_ceilings.json` |
| 3 | `03_make_batches.py` | Bucket candidates by organ system, chunk into batch files; SKIPS already-done systems (env `ICDO32_SKIP_SYSTEMS`, default `digestive`) and NEVER emits `ill_defined`/`unknown_primary` | `batches/<system>_NN.json`, `batches_index.json` |
| — | (research) | One `run_subagent` per batch, using `research_brief_template.md` | `results/<system>_NN.json` |
| 4 | `04_validate_merge.py` | Enforce subset rules (against `effective_ceilings.json`), merge results + auto-No, and **de-duplicate to one row per (code, NORMALIZED term)** via `clean_term.py` (variants collapse; best decision/subset/source wins; display term = preferred-or-longest) | `decisions.jsonl`, `validation_report.json` |
| 5 | `05_build_pref_map.py` | Code → preferred term (with /3 fallback) | `pref_map.json` |
| 6 | `06_build_workbook.py` | Final Excel (README + 2 sheets); reads TRUE full `ceilings.json` for display + `icdo32_topography.json` for 4-digit labels; `--csv` optional | `<out>.xlsx` |
| 7 | `07_site_correction_audit.py` | Anatomic-correctness audit of every "Yes" subset (site-of-origin vs invasion, gland distribution, wrong subsite). `--apply` folds confirmed corrections back into `decisions.jsonl`, enforcing ceiling + strict-subset rules; idempotent. | corrected `decisions.jsonl` |

After step 7, re-run step 6 to rebuild the workbook from the corrected decisions.

**Critical re-run ordering:** step 4 rebuilds `decisions.jsonl` FROM the raw `results/` + `auto_no`,
so it WIPES the step-7 site corrections (which live only in `decisions.jsonl`). Any time you re-run
step 4 (e.g. to pick up the dedup fix or new research), you MUST re-run `07_site_correction_audit.py
--apply` afterward (its `CORRECTIONS_2026_07_09` list is idempotent), then rebuild with step 6.
Correct order after a step-4 re-run: **4 → 7 (--apply) → 6**.

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

## Full-catalog extension plan
The end-to-end plan for scaling this pilot to the whole ICDO32 catalog (measured scope, reuse
strategy, execution waves, cost/risk, fresh-session recommendation) is in
`references/ICDO32_FullCatalog_Plan.md`. Read it when planning or resuming the full-catalog run.

## Site-correction audit (step 7 — run before release)
After the research waves, audit every "Yes" subset for anatomic correctness. Extract all Yes rows
with their 4-digit labels, batch (~90/batch), and spawn ONE research subagent per batch using
`AUDIT_BRIEF.txt`: for each (term, assigned sites) pair, judge `OK` / `WRONG_SITE` / `UNSURE` with a
fetched source URL for any `WRONG_SITE` (schema: `{code, term, audit, corrected_codes,
correction_reason, source}`). Then `07_site_correction_audit.py --apply <corrections.json>` folds
confirmed corrections in — it REJECTS any corrected site outside the code's effective ceiling and any
that is not a strict proper subset. The 2026-07-09 run's canonical corrections are baked into the
script (`CORRECTIONS_2026_07_09`, applied with a bare `--apply`): cholangiocarcinoma was a
label-only fix (subset codes were already correct); ceruminous carcinoma 8420/3 → C442 (external
ear skin, not middle ear C301); retinoinvasive melanoma 8720/3 → C693/C694 (uvea, not retina C692);
undifferentiated uterine sarcoma 8805/3 → C542 (corpus uteri myometrium — the only SMVL-valid
corpus code — not cervix).

## Version refresh (new ICD-O and/or WHO Blue Book editions)
When the maintainer ships a new ICDO32 / SMVL / WHO Blue Book version, reproduce the release with:
1. Replace `smvl.csv` (new Cancer PathCHART SMVL) and set the status column if it changes from
   `CPC2026A` (rule 1). Replace `master_terms.tsv` (new term list, keep the `PrefTerm` column).
2. Refresh `icdo32_topography.json` if the ICD-O topography axis changed, then run
   `01b_build_topography.py --validate` (must report 0 missing).
3. Re-run steps 1 → 2 → 3 → 5, research the changed/new systems (waves), then 4 → 6 → 7 → 6.
4. Re-check the anchor below and re-run the step-7 audit; update the WHO/NCCN source URLs on any
   "Yes" whose classification changed in the new Blue Book.

## Anchor / regression check
`8140/3 Paneth cell carcinoma` must resolve to "Yes" (GI-only subset of a 186-site ceiling), sourced
to Zhang et al., Diagnostic Pathology 2019 (PMC6323739). Use this as a smoke test after any refactor.
Label smoke test: `C221` must render as "Intrahepatic bile duct" (NOT "Liver") in cholangiocarcinoma
rows.
Dedup smoke test: no `(code, term)` pair may appear on more than one row in either data tab; e.g.
`8020/3 Undifferentiated primary liver carcinoma` must be a single row with subset `C220` (liver
parenchyma), not the broader `C220+C221` that added bile duct.
Normalization smoke test: `clean('Follicular lymphoma, duodenal type') == clean('Follicular
lymphoma, duodenal-type')` (both -> `Follicular lymphoma duodenal`), and `clean('AIN III') ==
clean('AIN 3')`. A bare trailing capital `I` NOT preceded by type/grade/an all-caps acronym must be
left untouched (`clean('Type I germ cell tumor of testis')` and `clean('MEN I syndrome')` unchanged).

## Known SQL-source bugs in `dbo.Clean` (fixed in the Python port; tell maintainer to fix in SQL)
The Python port `scripts/clean_term.py` intentionally deviates from the literal T-SQL in three
places to fix bugs; each deviation is commented in the code. When the maintainer updates the SQL,
these should be fixed there too:
1. **Rule ordering (Bug A).** SQL removes `' NOS'`/`' type'` BEFORE converting dashes to spaces, so a
   hyphenated `X-type`/`X-NOS` keeps its word while the spaced `X type` loses it — the two forms then
   don't match. Fix: convert `-`, en/em dashes, and `/` to spaces FIRST, then strip `NOS`/`type`.
2. **Roman-numeral `type` guard (Bug B).** The `' type II'`/`' type I'` lines are guarded on
   `LIKE '% grade II'`/`'% grade I'` (copy/paste slip), so `type` numerals almost never convert. Fix:
   guard each on the matching `'% type II'`/`'% type I'` suffix. (Maintainer's chosen behavior: drop
   the word `type` and keep the digit, e.g. `Type II` -> `2`.)
3. **Case-preserving spelling replacement (casing fix).** CI `REPLACE(oesophag->esophag)` etc. adopts
   the replacement's lower case, so `Oesophageal` -> `esophageal` (leading capital lost). The port
   matches case-insensitively but PRESERVES the original casing (`Oesophageal` -> `Esophageal`).

NOT changed (agreed intentional): the grade/type Roman-numeral conversions are anchored at end
(`WHERE ... LIKE '% grade III'`), so only a TRAILING numeral converts; and word order is never
normalized (different word orders are distinct synonyms).

## Folding in the completed GI (digestive) wave
The digestive pilot is DONE (216 decisions: 119 Yes / 97 No). In a fresh execution session:
1. Run `00_seed_digestive.py final_merged.json results` to write `results/digestive_seeded.json`.
2. Leave `ICDO32_SKIP_SYSTEMS=digestive` (default) so step 3 does not re-batch digestive.
3. Step 4 re-validates the seeded decisions against the effective ceiling and merges them exactly
   like fresh research output (verified: 0 violations). Never re-run the digestive research wave.

## Uncertain-row "Proposed Valid Sites" enrichment (2026-07-10)
A follow-on task filled best-possible primary site(s) of ORIGIN for the 95 "Uncertain" rows and
added a dedicated tab. Key rule change for THIS enrichment ONLY:

- **The strict-subset rule is LIFTED for Uncertain rows.** Proposed sites are the term's true
  literature-confirmed site(s) of ORIGIN and need NOT be a subset of (or even inside) the code's
  SMVL ceiling. Each row is FLAGGED in its rationale as `[within ceiling / SMVL-valid]`,
  `[outside ceiling / not SMVL-valid for this code]`, `[mixed: ...]`, or `[unresolved]`.
- Still enforced: site of ORIGIN only (not invasion); prefer specific 4-digit topography labels;
  every resolved row carries a real fetched source URL; unverifiable → left `[unresolved]` (never a
  guess). Result: 94/95 resolved, 1 unresolved (9504/3 Spongioneuroblastoma — obsolete glial/CNS
  label on a neuroepithelioma code with an unrestricted ICCC topography range; no defensible single
  site). Split 48 outside / 46 within / 1 unresolved.
- **Workbook changes:** (a) `All Screened Terms` Uncertain rows now populate G/H/I (Site Subset
  C-codes/Labels/Count) + M (flag+rationale) + N/O (source URL/ref); Site-Specific? stays
  "Uncertain". (b) New **`Uncertain Items`** tab = the 95 Uncertain rows with the two site columns
  RENAMED to **"Proposed Valid Sites (C-codes)"** / **"Proposed Valid Sites (Labels)"**; teal
  #20808D header, frozen panes, auto-filter. Counts unchanged (608 Yes / 2309 No / 95 Uncertain).
- **Provenance:** `decisions.jsonl` Uncertain rows gained `proposed_site_codes`,
  `proposed_site_labels`, `proposed_site_status`, `proposed_site_resolution`,
  `proposed_site_rationale`, `proposed_site_source`, `proposed_site_source_name`. These are
  ADDITIVE; the pipeline's validated `subset_codes`/`decision` were NOT altered, so re-running
  step 4 will not disturb Yes/No logic. The workbook Uncertain-site fill was applied DIRECTLY in
  openpyxl (not via `06_build_workbook.py`) precisely because the builder/step-4 reject
  outside-ceiling sites — to reproduce, re-apply from `uncertain_merged.json` after any rebuild.
- Working files: `uncertain_work.json` (95 extracted), `uncertain_batches/`, `uncertain_results/`,
  `uncertain_merged.json` (final, includes the C083→dropped Sialolipoma fix and the corrected
  Spongioneuroblastoma record), `uncertain_research_brief.md` (the research brief).
- **Source access note:** WHO Blue Books / NCCN / UpToDate / AJCC were NOT usable via custom-cred
  injection (cookie-login sites, not per-request-auth APIs) and local Comet handoff was unavailable
  in the execution session; all proposed sites came from open citable literature (WHO-aligned
  PMC/PubMed, NCCN, CAP, SEER). AJCC chapter-text API remains wired-up-able IF the maintainer
  supplies the real backend base URL + a sample endpoint from the 3scale portal API Spec.
