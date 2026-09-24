# Plan v2: Finding "Hidden" Site-Specific ICD-O-3.2 Terms

**Prepared:** 2026-07-09 (revised after anatomic/pathology review)
**Author:** Perplexity Computer + board-level pathology reasoning pass
**Status:** Ready to build on your approval. No token spend until you say go.

This v2 folds in the deep-knowledge answers to your four questions. The methodology
brief it draws from is saved at `hidden_methodology_answers.md` (full citations inside).

---

## 0. Your questions — resolved

| Your question | Resolution |
|---|---|
| **How is "organ system" defined? Use 2nd digit of C-code?** | **No** — the raw second digit (C0–C8, 9 buckets) miscombines unrelated anatomy (C4 lumps bone C40–41 + skin C43–44 + soft tissue C45–49). Use the **WHO/SEER ICD-O-3 topography *chapter* ranges** instead — the published registry-standard partition. 14 counting chapters (below). |
| **Why 4 systems, not 2 or 3?** | Pathology reasoning, not just counts: at **≥2 (395 codes)** and **≥3 (293)** the breadth is mostly *honest* — the tumor genuinely occurs in those systems (leiomyosarcoma etc.), so "broad ceiling" carries no signal and re-does Phase-1 work. **≥4 (235 codes)** is the inflection where SMVL breadth starts to *outrun* true biology for defined WHO entities with a molecular driver and a stereotyped anatomic home. At ≥5–6 you start losing genuinely tight positives (mesothelioma, Müllerian serous span only 2–3 chapters). **Recommended threshold: ≥4 chapters** as the recall gate. |
| **What defines a "hotspot" grouper — and can we auto-add more?** | Yes, fully auto-detected. A hotspot is a 3-digit family where a high *share* of its codes are broad-ceiling AND site-word-free. Rule: flag family F when **density HD_F ≥ 0.40 AND candidate count k_F ≥ 3**, rank by `HD_F × log(1+k_F)`. No family is hardcoded — 824–826, 880–899, 905, 906–909, 868–871, 872–879 surface automatically *because* they qualify. |
| **Anatomical-token list** | Drafted by the pathology agent (Section 3) — a paste-ready `SITE_BLOCKLIST` PLUS a `PATTERN_NOT_SITE` exclusion list that protects morphology words that merely *sound* anatomic (acinar, ductal, medullary, alveolar-as-pattern, small cell, clear cell, serous…). Ready for your review/edits. |
| **Fold-in vs separate deliverable** | **Separate deliverable** (your call), folded into the anatomic-site-in-term work later. |
| **Scope / budget — "whole catalog" = how many terms?** | "Whole catalog" = **3,256 candidate terms / 612 morphology codes** (full Phase-1 universe). The hidden pass is NOT that: the two deterministic filters cut it to **~90–120 codes / a few hundred terms** researched in **~3–6 grouper batches** — a small fraction of one Phase-1 wave. Comfortably inside ~$100/month. Recommendation: run filters over the **whole catalog at once** (it's cheap — deterministic, zero model tokens) so no hotspot family is missed, then research only what survives. |

---

## 1. Organ-system frame (the 14 counting chapters)

C76–C80 (ill-defined / nodal / metastatic / unknown primary) **excluded from all counting** — locked rule, and confirmed correct by review.

| # | Organ-system chapter | ICD-O-3 topography range |
|---|---|---|
| 1 | Lip / oral / pharynx | C00–C14 |
| 2 | Digestive (gut + hepatobiliary + pancreas) | C15–C26 |
| 3 | Respiratory / intrathoracic (incl. mediastinum, thymus C37) | C30–C39 |
| 4 | Bone & articular cartilage | C40–C41 |
| 5 | Skin | C43–C44 |
| 6 | Soft tissue + serosal cavities (nerve C47, connective C49, **peritoneum/retroperitoneum C48**, heart C38.0) | C47–C49 (+C48) |
| 7 | **Mesothelial / serosal lining — own system** | C45 |
| 8 | Breast | C50 |
| 9 | Female genital | C51–C58 |
| 10 | Male genital | C60–C63 |
| 11 | Urinary | C64–C68 |
| 12 | Eye & adnexa | C69 |
| 13 | Brain / CNS / meninges | C70–C72 |
| 14 | Endocrine (thyroid, adrenal, pituitary, parathyroid) | C73–C75 |

**Three review-driven refinements vs. my v1 draft:**
1. **C45 mesothelial split out** as its own system — coelomic serosal lining is embryologically distinct from mesenchymal soft tissue; merging destroys detection of mesothelial restriction.
2. **C48 peritoneum/retroperitoneum grouped with soft tissue (ch.6), NOT digestive** — matches SEER recode; it's the home cavity of DSRCT, peritoneal mesothelioma, PEComa, extragonadal GCT.
3. **Coelomic/Müllerian field flag** on C48 + C56–C57 (ovary/tube/peritoneum) — a *scoring annotation*, not a chapter, so an ovary+peritoneum serous tumor isn't misread as "pan-anatomic."

---

## 2. Breadth threshold: **≥4 organ-system chapters** (recall gate)

Applied as the candidate-*entry* filter, not the final classifier. Measured against real SMVL ceilings (C76/C80 excluded): **235 codes** clear ≥4. Token filter + biology adjudication then do the precision work.

Measured distribution (real data, `full_ceiling.json`):

| Threshold | Codes | Verdict |
|---|---:|---|
| ≥2 systems | 395 | Too loose — floods with honest-breadth codes |
| ≥3 systems | 293 | Still mostly genuine multi-site |
| **≥4 systems** | **235** | **Chosen — discordance signal peaks here** |
| ≥5 systems | 183 | Loses tight 3–4-system positives |
| ≥6 systems | 148 | Over-prunes |

---

## 3. Anatomical-token filter (drafted, for your review)

Two lists, in `hidden_methodology_answers.md` §3, ready to paste into Python:

- **`SITE_BLOCKLIST`** — organ adjectives + region words (gastric, pulmonary, ovarian, cutaneous, osseous, uveal, mediastinal, peritoneal, urothelial, …). If a term contains any → the site is named → **NOT hidden**, drop it.
- **`PATTERN_NOT_SITE`** — morphology words that *sound* anatomic but denote pattern/cell-of-origin and must **never** trigger a site block: acinar, ductal, lobular, follicular, papillary, cribriform, **alveolar** (nested pattern, not lung — critical for alveolar soft part sarcoma / alveolar RMS), **small cell** / **large cell** (cytology, not lung), **clear cell**, **serous** (Müllerian lineage), medullary (pattern unless phrase "medullary thyroid"), etc.
- **Phrase-only site words** (match full phrase): medullary thyroid, tunica vaginalis, base of tongue, small/large intestine, choroid plexus, ciliary body.

**Your action item:** review the two lists in §3 and add/remove tokens using your registry edge-case knowledge before I wire them in.

---

## 4. Positive-control anchor set (verified against YOUR official release)

25 exemplars proposed; **24 confirmed present** in the attached official ICDO32 release with exact preferred terms. Corrections I caught during verification:

| Correction | Detail |
|---|---|
| **8690/1 glomus jugulare — DROP** | Not present in the release. Removed from anchor set (24 anchors remain). |
| **8910/3 is "Embryonal rhabdomyosarcoma," not alveolar** | Release confirms 8910/3 = embryonal RMS. Alveolar RMS is **8920/3**. Both are valid hidden-class anchors; the *token filter* must treat "alveolar"/"embryonal" as pattern, not site. |
| **8693/3, 8714/3 — CONFIRMED** | Agent flagged these for verification; both present exactly ("Extra-adrenal paraganglioma, NOS"; "Perivascular epithelioid tumor, malignant"). |
| **8041/3** | Release term is "Small cell carcinoma, NOS" (agent said "small cell neuroendocrine carcinoma" — same code, note the exact string for filtering). |

The 24 confirmed anchors (with restricted-site subsets + WHO justification) live in `hidden_methodology_answers.md` §4. Highlights: alveolar soft part sarcoma (9581/3), DSRCT (8806/3, peritoneum-restricted), epithelioid hemangioendothelioma (9133/3, liver/lung/bone/soft tissue), PEComa (8714/3), paraganglioma family (neural-crest chains), germ-cell family (gonads + strict midline: mediastinum/retroperitoneum/pineal/sacrococcyx), mesothelioma (9050/3, serosal only), Merkel cell (8247/3, skin), NET/NEC (foregut + bronchopulmonary fields).

---

## 5. Hotspot grouper rule (auto, no hardcoding)

For each 3-digit family F: `broad_ceiling(c)` = ≥4 chapters; `no_site_hint(c)` = no SITE_BLOCKLIST token. Candidate = both true.
- Density `HD_F = k_F / n_F`; mass `k_F`.
- **Flag hotspot when `HD_F ≥ 0.40 AND k_F ≥ 3`; rank by `HD_F × log(1+k_F)`.**
- Recompute as SMVL / ICD-O-3.2 tables update — rule stable, inputs drift.

---

## 6. Pipeline additions (small, reuse Phase 1)

| Step | Script | Purpose | Output |
|---|---|---|---|
| 2b | `07_hidden_filter.py` | Filter A (≥4 chapters, 14-chapter map + C45/C48 refinements) + Filter B (SITE_BLOCKLIST, protecting PATTERN_NOT_SITE); attach 3-digit grouper family | `hidden_candidates.jsonl`, `hidden_dropped.jsonl`, `hidden_meta.json` |
| 3b | `08_make_grouper_batches.py` | Compute HD_F/k_F, flag hotspots, bucket candidates by grouper family, chunk | `batches_hidden/<family>_NN.json` |
| — | `research_brief_hidden.md` | Per-family brief: "term names no site — decide subset from tumor biology / WHO cell-of-origin; a 'Yes' must cite a source explicitly stating the site restriction, else Uncertain" | — |
| — | (research) | ~3–6 subagents (`claude_opus_4_8`, `preload_skills=["wide-search"]`), one grouper family each | `results_hidden/<family>_NN.json` |
| 4 | `04_validate_merge.py` (reuse) | Same strict-proper-subset + source enforcement vs. `effective_ceilings.json` | merged decisions |
| 6 | `06_build_workbook.py` (reuse) | Standalone "Hidden Site-Specific Terms" sheet with `Discovery method` = Hidden column | Excel (per locked Excel-only rule) |

Reuses locked rules 1–5, 7 verbatim. C76/C80 never researched. Excel-only output.

---

## 7. Execution & cost

1. **Deterministic pre-filter first** (07 → 08, zero model tokens): whole catalog → ~90–120 codes → a handful of grouper batches.
2. **Research the small set:** ~3–6 subagents, one grouper family each, ceiling + grouper label inline.
3. **Validate + merge** (script 4), tag `Hidden` / `Discovery method`.
4. **Anchor check:** each hotspot family should recover its §4 anchors; if not, revisit the token blocklist before trusting results.

**Cost:** filters cut the universe ~30× before any subagent → this whole phase ≈ cheaper than one Phase-1 organ wave (likely ≤ the head_neck batch). Well inside ~$100/month.

---

## 8. What I need from you (when you're back)

1. **Approve threshold ≥4 chapters** (or override).
2. **Review the two token lists** in `hidden_methodology_answers.md` §3 — add/remove any registry edge cases.
3. **Confirm the 14-chapter map** with the C45-split / C48-with-soft-tissue / Müllerian-flag refinements.
4. Then I build 07 + 08 (deterministic, no spend), show you the surviving candidate count + hotspot ranking, and you approve before any research subagent runs.
