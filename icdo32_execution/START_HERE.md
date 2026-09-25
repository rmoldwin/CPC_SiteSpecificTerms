# ICDO32 Full-Catalog Execution — Fresh Session Kickoff

**This directory is a self-contained handoff.** Start a NEW Perplexity Computer
session, attach this folder (or the `icdo32_execution.zip`), and follow the steps
below. The digestive/GI wave is already done and pre-loaded — you do **not**
re-research it.

---

## What is already done (folded in)

- **Digestive (GI) wave: COMPLETE.** 216 decisions (119 site-specific "Yes",
  97 "No", 0 Uncertain) across 45 codes are seeded into
  `results/digestive_seeded.json`. Step 4 re-validates them against the effective
  ceiling and merges them exactly like fresh research output — verified with
  **0 violations**. Do not re-run the digestive wave.
- **All deterministic build artifacts are pre-generated** in this directory
  (`ceilings.json`, `candidates.jsonl`, `effective_ceilings.json`, `auto_no.jsonl`,
  `pref_map.json`, `batches_index.json`, `batches/`). You can rebuild them any time
  (they are deterministic), but you don't have to.

## What remains to research

**57 batches / 2,297 candidate terms** across 12 organ systems (digestive removed,
`ill_defined`/`unknown_primary` never researched per locked rule 7):

| System            | Batches | Terms | Expected cost |
|-------------------|--------:|------:|---------------|
| head_neck         | 13      | 559   | HIGHEST (broadest ceilings) |
| cns               | 11      | 464   | LOW (narrow ceilings) |
| bone_soft_tissue  | 8       | 319   | MEDIUM |
| skin              | 4       | 177   | MEDIUM |
| gyn               | 4       | 162   | MEDIUM |
| endocrine         | 4       | 155   | LOW |
| breast            | 3       | 127   | LOW |
| respiratory       | 3       | 116   | LOW |
| heme              | 2       | 81    | LOW |
| male_genital      | 2       | 68    | LOW |
| urinary           | 2       | 49    | MEDIUM-HIGH (broad per-term) |
| eye               | 1       | 20    | LOW |
| **TOTAL**         | **57**  | **2,297** | |

## Recommended run order (cost-calibrated)

Front-load **head_neck** first — it is the worst-case cost bucket (89% of terms have
ceilings spanning ≥4 organ systems), so it calibrates the true per-wave spend before
committing the rest:

`head_neck → urinary → gyn → bone_soft_tissue → skin → breast → respiratory → endocrine → cns → male_genital → heme → eye`

(If you prefer to confirm the cheap end first, run `heme`/`eye`/`male_genital` as a
quick warm-up, then head_neck.)

---

## Steps for the fresh session

1. **Load the skill by name:** the methodology is saved in the **User** library as
   `icdo32-site-specific-terms` (skill_id `0cd59950-cfa6-475b-8e22-1e07c818bef6`) — just
   `load_skill(name="icdo32-site-specific-terms", scope="user")`. This loads the current scripts
   and the 7 locked rules. The `SKILL.md` in this folder is a fallback copy if the library skill
   isn't available. Either way, keep this folder attached for the staged data (`smvl.csv`,
   `master_terms.tsv`, seeded GI results, prebuilt artifacts) — the library skill holds the method
   and scripts, not the bulky input data.
2. **(Optional) rebuild** the deterministic layer to confirm inputs:
   ```
   python3 scripts/01_build_ceilings.py smvl.csv
   python3 scripts/02_build_candidates.py
   python3 scripts/03_make_batches.py candidates.jsonl 45 .
   python3 scripts/00_seed_digestive.py final_merged.json results
   python3 scripts/05_build_pref_map.py
   ```
   `03_make_batches.py` skips `digestive` by default (env `ICDO32_SKIP_SYSTEMS`,
   default `"digestive"`) and never emits `ill_defined`/`unknown_primary`.
3. **Research in waves.** For each batch file in the order above, spawn ONE research
   subagent: `subagent_type="research"`, `model="claude_opus_4_8"`,
   `preload_skills=["wide-search"]`, objective = `research_brief_template.md` with
   `{SYSTEM}`/`{BATCH_ID}` filled and the batch's terms (each with `ceiling_codes`)
   inlined, output path `results/<system>_NN.json`. Run 3–5 at a time,
   `wait_for_subagents`, repeat. **Meter cost after the first head_neck wave** and
   report actuals before continuing.
4. **Validate + merge** after each wave (safe to re-run; seeded digestive stays in):
   ```
   python3 scripts/04_validate_merge.py results effective_ceilings.json auto_no.jsonl .
   ```
   Check `validation_report.json` — `violations_fixed` should stay low; any
   bogus "Yes" is auto-demoted to "Uncertain".
5. **Build the final workbook** once all systems merge cleanly:
   ```
   python3 scripts/06_build_workbook.py
   ```
   Spot-check the Paneth anchor (`8140/3` → "Yes", GI-only subset). Share the xlsx
   (no CSVs — per user).

## Anchor / regression check
`8140/3 Paneth cell carcinoma` must resolve to **"Yes"** (GI-only subset of a 186-site
ceiling). Already true in the seeded digestive results.

## Cost expectation
Full remaining run ≈ **8–10× the GI pilot** (digestive already banked). head_neck +
urinary drive most of the cost; cns/respiratory/heme/male_genital/breast/endocrine are
cheap (narrow ceilings, few real subsets). Meter after wave 1 and adjust.
