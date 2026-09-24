# Hidden Site-Specific ICD-O-3.2 Morphology Terms — Methodology Brief

**Audience:** cancer-registry informatics + molecular pathology pipeline team
**Scope:** ICD-O-3.2 (ICDO32) morphology axis; Cancer PathCHART Site-Morphology Validity List (SMVL) as the site-validity backbone; WHO Classification of Tumours (5th series, "Blue Books") as the biology authority.
**Goal:** define the anatomic frame, breadth threshold, token filters, positive-control anchors, and an auto-hotspot rule for isolating morphology terms that are **SMVL-valid across many topography sites, contain no site word in the term string, yet are biologically confined to a proper subset of sites.**

A note on sourcing: the SMVL is the current definitive standard for the validity of site–morphology code combinations for U.S. registries (it replaced the SEER Site/Histology Validation List for 2024+), per [SEER's ICD-O-3 materials page](https://seer.cancer.gov/icd-o-3/) and the [Cancer PathCHART edits overview](https://seer.cancer.gov/cancerpathchart/CancerPathchartEdits.pdf). Topography-chapter definitions below are grounded in the official [SEER COD-to-Site Recode (ICD-O-3, 2023 revision)](https://seer.cancer.gov/codrecode/icdo3_d2023expanded/index.html) and the [SEER Site Recode ICD-O-3/WHO 2008](https://seer.cancer.gov/siterecode/icdo3_dwhoheme/index.html), which enumerate the C-code ranges by organ group.

---

## 1. ORGAN-SYSTEM DEFINITION

### 1.1 The proposed chapter mapping is anatomically sound, with two refinements

Your working map (C00-14 lip/oral/pharynx; C15-26 digestive; C30-39 respiratory/intrathoracic; C40-41 bone/joint; C43-44 skin; C45-49 mesothelial+soft tissue; C50 breast; C51-58 female genital; C60-63 male genital; C64-68 urinary; C69 eye/adnexa; C70-72 brain/CNS; C73-75 endocrine; C76-80 excluded) tracks the official SEER organ-system grouping closely. The [SEER Site Recode](https://seer.cancer.gov/siterecode/icdo3_dwhoheme/index.html) groups sites into: Oral Cavity & Pharynx (C00–C14), Digestive (C15–C26), Respiratory (C30–C39), Bones & Joints (C40–C41), Soft Tissue incl. heart (C38.0, C47, C49) + Mesothelium (C45) + Kaposi vessels (C46), Skin (C43–C44), Breast (C50), Female Genital (C51–C58), Male Genital (C60–C63), Urinary (C64–C68), Eye/Orbit (C69), Brain/CNS (C70–C72), Endocrine (C73–C75), and ill-defined/unknown (C76–C80). This is a legitimate, published, registry-standard partition and is the correct anatomic definition of "organ system" for this purpose.

**Excluding C76–C80 from all counting is correct and important.** C76 (other/ill-defined), C77 (lymph nodes), C78–C79 (metastatic/secondary sites), and C80 (unknown primary) are not primary organ systems; they are "wastebasket," nodal, and metastatic buckets. Counting them would inflate ceiling-breadth for essentially every disseminating tumor and defeat the purpose. Keep them out of the denominator and the numerator.

### 1.2 Refinement A — C45 (mesothelial) must be its own system, NOT merged with soft tissue

On embryologic and biologic grounds, **do not** treat C45 (mesothelioma / serosal mesothelium) as one system with C47/C49 (peripheral nerves / connective-soft tissue). The mesothelium is a coelomic-derived (mesodermal serosal) lining of the pleural, peritoneal, pericardial, and tunica-vaginalis cavities; mesothelioma is confined to these serosal surfaces — pleura (~90%), peritoneum (~10–20%), pericardium and tunica vaginalis rarely — per the [MSD Manual on mesothelioma](https://www.msdmanuals.com/professional/pulmonary-disorders/environmental-and-occupational-pulmonary-diseases/mesothelioma) and documented multi-serosal cases in the [tunica vaginalis/pleura/peritoneum literature](https://pubmed.ncbi.nlm.nih.gov/8732655/). Soft-tissue sarcomas (C47/C49) are a biologically unrelated mesenchymal compartment. If you merge C45 into C47-49 you will (a) destroy the ability to detect mesothelial morphologies as "restricted," and (b) mis-score germ-cell/serous tumors. **Recommendation: C45 = its own organ-system chapter ("mesothelial/serosal").**

### 1.3 Refinement B — the coelomic/Müllerian "serosal field" is a cross-chapter biology, not a chapter

Do **not** create a physical chapter for it, but the pipeline must be aware that several restricted entities live on the **coelomic epithelial / Müllerian field**, which spans anatomic chapters:
- Ovary (C56, female-genital chapter), fallopian tube (C57), and peritoneum (C48, within your digestive C15-26 range) form the tubo-ovarian–peritoneal serous carcinoma continuum. High-grade serous carcinoma is now understood to arise predominantly from the fallopian-tube fimbria and secondarily involve ovary and peritoneum; this is one developmental field split across two of your chapters (female genital + digestive/peritoneum).
- The peritoneum (C48) is coded inside the digestive range in the SEER recode ([SEER recode](https://seer.cancer.gov/codrecode/icdo3_d2023expanded/index.html) places C48 Retroperitoneum & Peritoneum under "Bones and Soft Tissue"), while the ovary/tube sit in female genital. So a Müllerian serous tumor will legitimately look like it spans ≥2 systems even though it is one embryologic field.

**Recommendation:** keep the physical chapter list as below, but tag C48 (peritoneum/retroperitoneum) and C56–C57 (ovary/tube) with a **"coelomic/Müllerian field" flag** so the scoring layer does not misinterpret an ovary+peritoneum restricted tumor as "pan-anatomic." This is a scoring annotation, not a new chapter.

### 1.4 Refinement C — where does C48 live?

Note a genuine ambiguity: your map places digestive as C15–C26, but C48 (retroperitoneum, peritoneum, omentum, mesentery) is grouped by SEER **with soft tissue / bones-and-soft-tissue**, not with the tubular digestive organs ([SEER recode](https://seer.cancer.gov/codrecode/icdo3_d2023expanded/index.html)). Peritoneal/retroperitoneal is the home cavity of DSRCT, peritoneal mesothelioma, PEComa, and extragonadal germ-cell/retroperitoneal tumors. **Recommendation: assign C47–C49 AND C48 to the "soft tissue / mesenchymal + serosal-cavity" system (with C45 separate), and explicitly document that peritoneum (C48) is NOT in the digestive chapter.** This materially changes breadth counts for abdominal-cavity-restricted entities.

### 1.5 Recommended exact chapter list to use

Use these **14 counting chapters** (C76–C80 excluded entirely; hematolymphoid C81–C96 out of scope for solid-tumor morphology work):

| # | Organ-system chapter | ICD-O-3 topography range |
|---|----------------------|--------------------------|
| 1 | Lip / oral cavity / pharynx | C00–C14 |
| 2 | Digestive (tubular gut + hepatobiliary + pancreas) | C15–C26 (peritoneum C48 handled in ch. 6) |
| 3 | Respiratory / intrathoracic (incl. mediastinum, thymus C37) | C30–C39 |
| 4 | Bone & articular cartilage | C40–C41 |
| 5 | Skin | C43–C44 |
| 6 | Soft tissue + serosal cavities (nerve C47, connective C49, retroperitoneum/peritoneum C48, heart C38.0) | C47–C49 (+C48) |
| 7 | **Mesothelial / serosal lining (own system)** | C45 (C46 Kaposi vessels adjacent) |
| 8 | Breast | C50 |
| 9 | Female genital (with coelomic/Müllerian flag on C56–C57) | C51–C58 |
| 10 | Male genital | C60–C63 |
| 11 | Urinary | C64–C68 |
| 12 | Eye & adnexa | C69 |
| 13 | Brain / CNS / meninges | C70–C72 |
| 14 | Endocrine (thyroid, adrenal, pituitary, parathyroid) | C73–C75 |

Changes vs. your draft: (a) C45 split out from soft tissue as its own system; (b) C48 peritoneum explicitly grouped with soft tissue/serosal cavities, not digestive; (c) coelomic/Müllerian cross-chapter flag on C48 + C56–C57. Everything else stands.

---

## 2. BREADTH THRESHOLD

### 2.1 Recommended single number: **≥4 organ-system chapters**

Recommendation: **require an SMVL ceiling of ≥4 distinct organ-system chapters (C76/C80 excluded) for a code to enter the hidden-term candidate pool.**

### 2.2 Pathology reasoning (not just the count distribution)

The class you are hunting — "looks pan-anatomic but is biologically restricted" — is defined by a *tension*: SMVL says "valid almost anywhere," biology says "really only these few." That tension only becomes diagnostic when the SMVL ceiling is genuinely broad. Consider what each threshold captures:

- **≥2 chapters (395 codes):** This floods the pool with the ordinary situation, not the hidden one. Almost every mesenchymal, neuroendocrine, melanocytic, and epithelial NOS morphology is legitimately valid in ≥2 chapters *because it genuinely occurs in ≥2 chapters* (e.g., leiomyosarcoma truly arises in uterus, GI, soft tissue, vessels). At ≥2, "broad ceiling" carries almost no information — you are mostly re-deriving Phase-1-handled generic codes. Reject.
- **≥3 chapters (293 codes):** Still dominated by genuinely multi-site mesenchymal/epithelial entities. A tumor valid in exactly 3 systems is usually valid *because* it occurs in 3 systems; the SMVL is not overclaiming. The "hidden" signal is weak here.
- **≥4 chapters (235 codes):** This is the inflection where SMVL breadth starts to **outrun true biology** for the target families. Once a code is declared valid in ≥4 of 14 organ systems, the a priori expectation for a *biologically specific* entity (a defined WHO diagnosis with a driver fusion and a stereotyped anatomic home) is that the SMVL is being permissive — it is licensing sites the tumor does not actually originate in. That gap is exactly the "hidden site-specific" phenomenon. Entities like alveolar soft part sarcoma, PEComa, paraganglioma, extragonadal germ-cell tumors, DSRCT, and epithelioid hemangioendothelioma will clear ≥4 (their SMVL ceilings are wide) yet each is confined by embryology to a definable subset. Accept.
- **≥5 (183) / ≥6 (148):** Cleaner still, but you begin losing true positives that are restricted to exactly 3–4 real systems (e.g., mesothelioma across pleura+peritoneum+pericardium+tunica vaginalis maps to only 2–3 of your chapters; a Müllerian serous tumor to 2). Setting the bar at 5–6 sacrifices recall on precisely the tightest, most valuable positives.

The decisive argument is **specificity of the biological claim vs. breadth of the coding license.** A well-defined WHO entity with a molecular driver has a *narrow* natural history; when its SMVL ceiling nonetheless spans ≥4 systems, the discordance is real and worth flagging. Below 4, most breadth is honest breadth. At/above 5, you start excluding genuinely tight positives. **≥4 is the sweet spot that maximizes the discordance signal without either flooding (from generic NOS/pan-mesenchymal codes at ≥2–3) or over-pruning (losing 2–3-system restricted entities at ≥5–6).**

### 2.3 Operational note

Apply ≥4 as the *entry filter* to the candidate pool, then let the anatomical-token blocklist (Section 3) and the biology adjudication (Sections 4–5) do the precision work. The threshold is a recall gate, not the final classifier.

---

## 3. ANATOMICAL-TOKEN BLOCKLIST

Rule: if a term string contains any BLOCKLIST token (word-boundary, case-insensitive, including the listed adjectival/combining forms), the site is *named in the term* and the term is **NOT hidden** — exclude it. Then apply the EXCLUSION list: tokens that *sound* anatomic but denote histologic pattern/cell-of-origin, which must **never** trigger the site filter.

### 3.1 BLOCKLIST — organ / region words and adjectival forms (paste-ready)

```python
# --- ANATOMICAL SITE BLOCKLIST (term is NOT "hidden" if any token matches, word-boundary, case-insensitive) ---
SITE_BLOCKLIST = [
    # Oral / pharynx / head & neck
    "oral", "buccal", "gingival", "lingual", "tongue", "palatal", "palate", "tonsil", "tonsillar",
    "pharyngeal", "pharynx", "nasopharyngeal", "nasopharynx", "oropharyngeal", "oropharynx",
    "hypopharyngeal", "hypopharynx", "laryngeal", "larynx", "glottic", "supraglottic", "salivary",
    "parotid", "sublingual", "submandibular", "sinonasal", "nasal", "paranasal", "labial",
    # Digestive
    "esophageal", "esophagus", "oesophageal", "gastric", "gastro", "stomach", "intestinal",
    "duodenal", "jejunal", "ileal", "colonic", "colon", "colorectal", "rectal", "rectum", "anal",
    "appendiceal", "appendix", "hepatic", "hepato", "liver", "hepatocellular", "biliary", "cholangio",
    "gallbladder", "pancreatic", "pancreas", "ampullary", "small intestine", "large intestine",
    # Respiratory / intrathoracic
    "pulmonary", "lung", "bronchial", "bronchi", "broncho", "bronchus", "tracheal", "trachea",
    "pleural", "pleura", "mediastinal", "mediastinum", "thymic", "thymus", "pericardial", "pericardium",
    # Bone / joint
    "osseous", "osteo", "bone", "skeletal", "intraosseous", "periosteal", "juxtacortical",
    "chondro-skeletal", "vertebral", "articular",
    # Skin / cutaneous
    "cutaneous", "dermal", "dermato", "epidermal", "skin", "subcutaneous", "acral", "subungual",
    # Breast
    "mammary", "breast",
    # Female genital
    "ovarian", "ovary", "uterine", "uterus", "endometrial", "endometrium", "endometrioid",
    "myometrial", "cervical", "cervix", "vulvar", "vulva", "vaginal", "vagina",
    "fallopian", "tubal", "salpingeal", "placental", "gestational", "trophoblastic",
    # Male genital
    "prostatic", "prostate", "testicular", "testis", "penile", "penis", "scrotal", "epididymal",
    "seminal", "tunica vaginalis",
    # Urinary
    "renal", "kidney", "nephro", "nephrogenic", "urothelial", "urothelium", "bladder", "vesical",
    "ureteral", "ureter", "urethral", "urethra", "urinary", "pelvicalyceal",
    # Eye / adnexa
    "ocular", "orbital", "orbit", "uveal", "uvea", "choroidal", "choroid", "ciliary body",
    "retinal", "retina", "conjunctival", "conjunctiva", "lacrimal", "iris",
    # CNS
    "cerebral", "cerebellar", "cerebrum", "cerebello", "intracranial", "brain", "meningeal",
    "meninges", "spinal", "pineal", "pituitary", "sellar", "hypothalamic", "ventricular",
    "choroid plexus", "ependymal", "leptomeningeal",
    # Endocrine
    "thyroid", "thyroidal", "parathyroid", "adrenal", "adrenocortical", "medullary thyroid",
    "pituitary",  # (also CNS)
    # Serosal / cavity / region
    "peritoneal", "peritoneum", "retroperitoneal", "retroperitoneum", "omental", "mesenteric",
    "mesothelial", "mesothelium", "serosal",
    # Soft-tissue anatomic regions (region words, not pattern words)
    "cardiac",  # heart
]
```

Notes on deliberately included/excluded edge cases:
- `"medullary thyroid"` is blocklisted as a **phrase** (site-committed) while bare `"medullary"` is on the EXCLUSION list (pattern) — see below. Implement medullary as: block only when followed by "thyroid"/"kidney"/"renal".
- `"pituitary"` appears once; it is both endocrine and CNS-adjacent — either mapping is fine.
- `"acral"`, `"subungual"` are skin-region words → block.
- Serosal words (`peritoneal`, `pleural`, `pericardial`, `mesothelial`) are blocked: if the *term itself* says "peritoneal mesothelioma," the site is named and it is not hidden.

### 3.2 EXCLUSION list — morphology words that SOUND anatomic but are PATTERN / CELL-OF-ORIGIN (never treat as site hints)

```python
# --- PATTERN / CELL-OF-ORIGIN ALLOWLIST (must NOT count as site hints) ---
PATTERN_NOT_SITE = [
    "acinar",       # glandular growth pattern (acini); NOT pancreas/lung site
    "acinic",       # cell type (salivary-associated by convention but denotes cell, keep as pattern)
    "ductal",       # duct-forming pattern; NOT breast/pancreas site per se
    "lobular",      # growth architecture; NOT breast site
    "medullary",    # soft/cellular growth pattern (breast, colon, thyroid all use it) -> pattern
    "follicular",   # follicle-forming pattern (thyroid, lymphoid, ovarian) -> pattern
    "papillary",    # frond/papilla architecture; site-agnostic
    "cribriform",   # sieve-like architecture; site-agnostic
    "glandular",    # gland-forming; site-agnostic
    "alveolar",     # nested/alveolar PATTERN (alveolar RMS, ASPS) -> NOT lung when it means pattern
    "acinic",       # (dup guard)
    "trabecular",   # cord/trabecula architecture
    "solid",        # architecture
    "insular",      # nested/island architecture
    "basal",        # basal/basaloid cell phenotype; NOT "base of" a site
    "basaloid",     # phenotype
    "squamous",     # epithelial differentiation; site-agnostic
    "transitional", # (urothelial synonym historically, BUT also "transitional" pattern) -> see note
    "spindle",      # cell shape
    "epithelioid",  # cell shape
    "clear cell",   # cytoplasm phenotype (NOT a site; occurs kidney/ovary/etc.)
    "signet ring",  # cytology
    "mucinous",     # secretion phenotype
    "serous",       # Müllerian/coelomic differentiation phenotype (see biology flag)
    "sebaceous",    # differentiation phenotype (though skin-associated) -> treat as pattern
    "oncocytic",    # mitochondria-rich phenotype
    "oxyphilic",    # phenotype
    "chromophobe",  # phenotype
    "granular cell",# cell type
    "small cell",   # cell size phenotype (NOT lung)
    "large cell",   # cell size phenotype
    "giant cell",   # cell type
    "round cell",   # cell shape
    "plasmacytoid", # cytology
    "rhabdoid",     # cytology
    "myoid",        # differentiation
    "neuroendocrine", # lineage, not a site
    "endocrine",    # lineage descriptor (careful: "endocrine" alone = lineage; site is the organ)
    "germ cell",    # lineage, not a site
    "sarcomatoid",  # differentiation
    "desmoplastic", # stromal reaction
    "myxoid",       # matrix phenotype
    "pleomorphic",  # cytology
    "anaplastic",   # grade/differentiation (NOT "anaplastic thyroid" unless 'thyroid' present)
]
```

One-line notes on the genuinely ambiguous ones:
- **acinar** — means gland/acinus growth pattern; used in lung "acinar adenocarcinoma" and prostate "acinar adenocarcinoma," so it is a pattern, not a site. Do not block.
- **ductal** — duct-forming architecture; appears in breast and pancreatic ductal carcinoma but the word encodes pattern, not location. Do not block.
- **lobular** — architectural (breast lobular, hepatic "lobular") → pattern. Do not block.
- **medullary** — a soft/cellular growth pattern shared by breast, colon, and thyroid carcinomas; block only in the fixed phrases "medullary thyroid"/"medullary (renal/kidney)."
- **follicular** — follicle architecture (thyroid follicular, lymphoid follicular, ovarian) → pattern. Do not block.
- **papillary / cribriform / glandular / trabecular / insular / solid** — pure architecture terms, site-agnostic. Do not block.
- **alveolar** — CRITICAL: "alveolar" in "alveolar rhabdomyosarcoma" and "alveolar soft part sarcoma" is a *nested growth pattern*, NOT the pulmonary alveolus. Do not block. (These are top positive controls — see Section 4.)
- **basal / basaloid** — cell phenotype ("basal cell," "basaloid squamous"), not "base of tongue." Do not block; block "base of" as a phrase if needed.
- **transitional** — historically synonymous with urothelial, but also a nonspecific "transitional" architecture. Treat as pattern (do not auto-block); rely on the separate hard blocklist token `urothelial` to catch true urothelial terms.
- **serous** — denotes Müllerian/coelomic serous differentiation (ovary/tube/peritoneum/endometrium), a lineage phenotype, not a single site; keep as pattern but pair with the Müllerian flag from Section 1.3.
- **small cell** — "small cell carcinoma" is a cytologic class occurring in lung, bladder, cervix, prostate, etc.; NOT a lung-site word. Do not block.
- **clear cell** — cytoplasm phenotype (kidney, ovary, endometrium, soft tissue "clear cell sarcoma"); not a site. Do not block.

Implementation guidance: run BLOCKLIST first (any hit → not hidden). Never let a PATTERN_NOT_SITE token override into a block. For the handful of "phrase-only" site words (medullary thyroid, tunica vaginalis, base of tongue, small intestine, large intestine, choroid plexus, ciliary body), match the full phrase, not the component word.

---

## 4. HIDDEN-TERM EXEMPLARS (positive-control anchor set)

These are morphology terms whose SMVL ceiling is broad and whose term string carries no site word, yet whose biology (WHO / embryology) confines them to a proper subset of chapters. Chapter numbers refer to the Section 1.5 list. Codes are ICD-O-3.2 4-digit morphology; behavior shown where standard. Where a specific code cannot be verified with certainty I flag it.

| # | Code | Term (no site word) | True restricted site subset (by chapter) | Biology / WHO justification |
|---|------|---------------------|------------------------------------------|-----------------------------|
| 1 | 9581/3 | Alveolar soft part sarcoma | Ch.6 soft tissue (deep extremity/trunk); ch.1 head&neck & ch.9 uterus in special subsets | ASPSCR1::TFE3 fusion; deep somatic soft tissue of extremities predominates; H&N (orbit/tongue) in children — per [Oxford JJCO ASPS review](https://academic.oup.com/jjco/article/53/11/1009/7251339) and [SFA subtype page](https://curesarcoma.org/sarcoma-subtypes/alveolar-soft-part-sarcoma/). "Alveolar" = nested pattern, not lung. |
| 2 | 8806/3 | Desmoplastic small round cell tumour | Ch.6 (abdominal/pelvic peritoneum C48) almost exclusively | EWSR1::WT1 fusion; arises on abdominopelvic peritoneal/serosal surfaces of young males — per [DSRCT peritoneal review](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7099158/) and [Cancers DSRCT review](https://pmc.ncbi.nlm.nih.gov/articles/PMC7865637/). |
| 3 | 9133/3 | Epithelioid haemangioendothelioma | Ch.2 liver, ch.3 lung, ch.4 bone, ch.6 soft tissue | Vascular tumour (WWTR1::CAMTA1) with a stereotyped liver/lung/bone/soft-tissue distribution — per [AJR EHE imaging review](https://ajronline.org/doi/10.2214/AJR.20.22876) and [ESMO Open EHE review](https://pmc.ncbi.nlm.nih.gov/articles/PMC8182432/). |
| 4 | 8714/3 | Perivascular epithelioid cell tumour, malignant (PEComa) | Ch.9 uterus/female genital, ch.6 retroperitoneum/soft tissue, ch.2 GI/liver, ch.11 kidney | Perivascular epithelioid (melanocytic-myoid) lineage; most common at uterus, retroperitoneum, abdominopelvic/GI — per [Oxford JJCO PEComa review](https://academic.oup.com/jjco/article/55/7/691/8126755) and [AJR malignant PEComa series](https://ajronline.org/doi/10.2214/AJR.13.10909). |
| 5 | 8693/3 | Extra-adrenal paraganglioma, malignant | Ch.1 head&neck (carotid/jugulotympanic), ch.3 mediastinum/aortopulmonary, ch.6 retroperitoneum/organ of Zuckerkandl, ch.14 adrenal-adjacent | Neural-crest paraganglia along sympathetic/parasympathetic chains; distribution follows neural-crest migration — per [StatPearls paraganglioma](https://www.ncbi.nlm.nih.gov/books/NBK549834/) and [CAP paraganglioma protocol](https://documents.cap.org/documents/New-Cancer-Protocols-March-2025/Paragang_Pheochrom_1.0.0.0.REL.CAPCP.docx). |
| 6 | 8680/3 | Paraganglioma, malignant (NOS) | Same neural-crest paraganglial distribution as #5 | Same neural-crest paraganglia biology; not a random pan-anatomic tumour — per [2022 WHO paraganglioma overview](https://pubmed.ncbi.nlm.nih.gov/35285002/). |
| 7 | 8690/1 | Glomus jugulare / jugulotympanic paraganglioma | Ch.1 head&neck (temporal bone/jugular foramen) | Parasympathetic paraganglion of the head & neck; anatomically fixed. Per [StatPearls paraganglioma](https://www.ncbi.nlm.nih.gov/books/NBK549834/). |
| 8 | 9071/3 | Yolk sac tumour | Ch.10 testis + ch.9 ovary (gonadal) + midline extragonadal: ch.3 mediastinum, ch.6 retroperitoneum/sacrococcyx, ch.13 pineal/CNS | Germ-cell lineage; extragonadal forms restricted to body midline (germ-cell migration path) — per [NCI extragonadal GCT PDQ](https://www.cancer.gov/types/extragonadal-germ-cell/hp/extragonadal-treatment-pdq) and [extragonadal GCT review](https://pmc.ncbi.nlm.nih.gov/articles/PMC4503148/). |
| 9 | 9070/3 | Embryonal carcinoma | Gonads (ch.9/10) + midline extragonadal (ch.3 mediastinum, ch.6 retroperitoneum, ch.13 CNS) | Germ-cell; same midline-restricted extragonadal biology — per [NCI PDQ](https://www.cancer.gov/types/extragonadal-germ-cell/hp/extragonadal-treatment-pdq). |
| 10 | 9085/3 | Mixed germ cell tumour | Gonads + midline extragonadal (as #8/#9) | Germ-cell mixture; confined to gonads + body midline — per [extragonadal GCT review](https://pmc.ncbi.nlm.nih.gov/articles/PMC4503148/). |
| 11 | 9080/3 | Teratoma, malignant / postpubertal-type | Gonads (ch.9/10) + midline: ch.3 mediastinum, ch.6 sacrococcyx/retroperitoneum, ch.13 pineal | Germ-cell derivative along embryonic germ ridge/midline — per [CAP extragonadal GCT protocol](https://documents.cap.org/protocols/cp-extragonadal-germ-cell-2016-v3101.pdf). |
| 12 | 9064/3 | Germinoma / seminoma-type (extragonadal germinoma) | Ch.13 CNS (pineal/suprasellar), ch.3 mediastinum, gonads | Germ-cell; germinoma is the dominant CNS/mediastinal midline extragonadal GCT — per [extragonadal GCT review](https://pmc.ncbi.nlm.nih.gov/articles/PMC4503148/). |
| 13 | 9050/3 | Mesothelioma, malignant | Ch.7 mesothelial serosa: pleura, and via serosa peritoneum (ch.6 C48), pericardium, tunica vaginalis | Coelomic mesothelium only; ~90% pleura, rest peritoneum, rare pericardium/tunica vaginalis — per [MSD Manual mesothelioma](https://www.msdmanuals.com/professional/pulmonary-disorders/environmental-and-occupational-pulmonary-diseases/mesothelioma). |
| 14 | 9051/3 | Mesothelioma, biphasic (sarcomatoid/fibrous) | Same serosal surfaces as #13 | Same mesothelial-lining restriction — per [multi-serosal mesothelioma case](https://pubmed.ncbi.nlm.nih.gov/8732655/). |
| 15 | 8720/3 | Melanoma, malignant (NOS) | Ch.5 skin predominates; mucosal (ch.1 sinonasal/oral, ch.9 vulvovaginal, ch.2 anorectal); ch.12 uveal | Melanocytes are neural-crest-derived; occur in skin, mucosal surfaces, and uveal tract — a defined set of melanocyte-bearing sites, not truly pan-anatomic. (Melanoma variants family 872–879.) |
| 16 | 8728/1 | Meningeal melanocytoma / melanocytic tumour | Ch.13 CNS leptomeninges | Neural-crest melanocytes of the leptomeninges; CNS-restricted despite generic melanocytic code. |
| 17 | 8247/3 | Merkel cell carcinoma | Ch.5 skin (rare mucosal ch.1) | Cutaneous neuroendocrine (Merkel cell) carcinoma; skin-restricted, though code is broadly SMVL-valid. (NE family 824–826.) |
| 18 | 8240/3 | Neuroendocrine tumour, NOS (well-diff NET) | GI/pancreas (ch.2), lung/bronchus & thymus (ch.3) dominate; genito-urinary rarely | Diffuse neuroendocrine system tumour; concentrated in GI-pancreatic and bronchopulmonary/thymic neuroendocrine cells — biologically NOT uniform across all 14 systems. |
| 19 | 8013/3 | Large cell neuroendocrine carcinoma | Ch.3 lung/thymus, ch.2 GI-pancreas, some genito-urinary | High-grade NE carcinoma concentrated in foregut-derived and bronchopulmonary neuroendocrine fields. "Large cell" = cytology, not site. |
| 20 | 8041/3 | Small cell neuroendocrine carcinoma | Ch.3 lung dominant; extrapulmonary in ch.11 bladder, ch.9 cervix, ch.10 prostate, ch.2 GI | High-grade NE carcinoma; extrapulmonary confined to specific epithelial fields, not truly ubiquitous. "Small cell" = cytology, not lung. |
| 21 | 9040/3 | Synovial sarcoma (spindle/biphasic) | Ch.6 deep soft tissue (para-articular extremity), ch.3 thorax/lung, ch.1 head&neck | SS18::SSX fusion; despite the name it does NOT arise from synovium — a soft-tissue sarcoma of defined mesenchymal distribution. Per [ESMO Open synovial sarcoma review](https://pmc.ncbi.nlm.nih.gov/articles/PMC10470271/). |
| 22 | 8815/3 | Solitary fibrous tumour, malignant | Ch.3 pleura (classic), ch.13 meninges, ch.6 soft tissue/retroperitoneum, ch.9 pelvis | NAB2::STAT6 fusion; serosal/meningeal/deep-soft-tissue distribution, not pan-organ. |
| 23 | 8830/3 | Undifferentiated pleomorphic sarcoma / MFH | Ch.6 deep soft tissue (extremity/trunk), ch.4 bone | Mesenchymal; deep somatic soft tissue and bone — a mesenchymal-compartment restriction, not epithelial organs. |
| 24 | 9364/3 | Ewing sarcoma / round cell (EWSR1::ETS) | Ch.4 bone (classic) + ch.6 extraskeletal soft tissue | FET::ETS fusion sarcoma; bone + soft tissue only, both skeletal and extraskeletal — per [WHO small round cell sarcoma update](https://pmc.ncbi.nlm.nih.gov/articles/PMC11738087/). |
| 25 | 8910/3 | Alveolar rhabdomyosarcoma | Ch.6 soft tissue (extremity/trunk/paratesticular), ch.1 head&neck | PAX3/7::FOXO1 fusion skeletal-muscle sarcoma. "Alveolar" = nested pattern, NOT lung — a canonical false-anatomic token. |

Adjudication caveats for the pipeline team:
- Codes above are the standard ICD-O-3.2 assignments; a few (e.g., 8714/3 for malignant PEComa, 8693/3 for extra-adrenal paraganglioma) should be **verified against the current NAACCR/IARC ICD-O-3.2 numeric table** ([NAACCR ICD-O-3.2 page](https://www.naaccr.org/icdo3/)) before hardcoding, because 3.2 updates have reshuffled behavior/terms in the germ-cell, urinary, and male-genital families ([2024 ICD-O-3.2 alpha update](https://www.alabamapublichealth.gov/ASCR/assets/ascr-2024-icd-o-3.2-update-codes-and-terms-alpha.pdf)). I flag these rather than assert them as final.
- The germ-cell entries (#8–#12) are the strongest positive controls: gonadal + strictly midline extragonadal (mediastinum, retroperitoneum, pineal/CNS, sacrococcyx), a distribution driven by the primordial-germ-cell migration path — repeatedly documented ([NCI PDQ](https://www.cancer.gov/types/extragonadal-germ-cell/hp/extragonadal-treatment-pdq), [extragonadal GCT review](https://pmc.ncbi.nlm.nih.gov/articles/PMC4503148/)).
- Melanoma (#15) is a "restricted to melanocyte-bearing sites" case rather than a single-chapter case — useful as a boundary control (broad but principled).

---

## 5. GROUPER HOTSPOT RULE

Goal: auto-rank 3-digit morphology grouper families (the ICD-O 3-digit code blocks, e.g., 824–826 NET, 880–899 soft-tissue sarcoma, 906–909 germ cell) by their likelihood of harboring hidden site-specific terms — **without hardcoding any family.**

### 5.1 Definitions (per 3-digit family F)

For each morphology code c in family F, compute two booleans from data already available:
- `broad_ceiling(c)` = SMVL ceiling spans **≥4 organ-system chapters** (Section 2, C76/C80 excluded).
- `no_site_hint(c)` = none of the code's associated term strings contains a BLOCKLIST token (Section 3), after applying the PATTERN_NOT_SITE exclusion.

A code is a **candidate** if `broad_ceiling(c) AND no_site_hint(c)`.

### 5.2 Hotspot score (rate-based, not count-based)

Let n_F = number of distinct member codes in family F, and k_F = number of candidate codes in F.

- **Hotspot density:** `HD_F = k_F / n_F` (share of the family that is broad-ceiling + no-hint).
- **Hotspot mass:** `k_F` (absolute count, to avoid promoting tiny families where 1/1 = 100%).

**Rule:** flag family F as a hotspot when **`HD_F ≥ 0.40` AND `k_F ≥ 3`.** Rank hotspots by a combined score `score_F = HD_F * log(1 + k_F)` so that families that are both proportionally enriched and absolutely sizeable rise to the top. This is fully data-driven: it will surface 824–826 (neuroendocrine), 880–899 (soft-tissue sarcoma), 905 (mesothelial), 906–909 (germ cell), 868–871 (paraganglioma), and 872–879 (melanoma) automatically **because** those families are densely populated with broad-ceiling, no-site-word codes — not because they were named.

### 5.3 Threshold rationale

- `HD_F ≥ 0.40`: a family where ≥40% of members are simultaneously broad-ceiling AND site-word-free is behaving abnormally — most epithelial families (adenocarcinoma 814–838 subsets, squamous 805–808) either name their site or are genuinely broad, so they fall below 0.40. The soft-tissue, germ-cell, NE, paraganglioma, and mesothelial families cluster high because their defining feature is a molecular/lineage identity decoupled from a site word.
- `k_F ≥ 3`: prevents a 1- or 2-member family from being crowned a hotspot on a fluke.
- Log weighting on mass: rewards families with many candidates without letting one huge generic family dominate purely by size.

### 5.4 Operational loop

1. Tag every code with `broad_ceiling` and `no_site_hint`.
2. Aggregate to 3-digit families; compute HD_F, k_F, score_F.
3. Rank descending by score_F; take families above the HD/k gates as the priority worklist.
4. Within each hotspot family, route candidate codes to biology adjudication using the Section-4 anchor set as positive controls (precision check) — a hotspot family should recover most of its Section-4 anchors; if it does not, revisit the token blocklist.
5. Recompute periodically as the SMVL and ICD-O-3.2 tables update ([NAACCR ICD-O-3.2 page](https://www.naaccr.org/icdo3/), [SEER ICD-O-3](https://seer.cancer.gov/icd-o-3/)); the rule is stable, the inputs drift.

---

## Summary of recommendations

1. **Organ-system frame:** use the 14-chapter list in Section 1.5. Split **C45 mesothelial into its own system**; group **C48 peritoneum with soft tissue (not digestive)**; flag **C48 + C56–C57 as a coelomic/Müllerian field**; keep C76–C80 excluded.
2. **Breadth threshold:** **≥4 organ-system chapters** as the candidate-entry gate — the inflection where SMVL breadth outruns true biology without flooding (≥2–3) or over-pruning (≥5–6).
3. **Token filter:** apply the paste-ready `SITE_BLOCKLIST` (block → not hidden) and protect the `PATTERN_NOT_SITE` list (acinar/ductal/lobular/medullary/follicular/papillary/alveolar/basal/squamous/transitional/small-cell/clear-cell etc.) from ever triggering a site block; handle phrase-only site words (medullary thyroid, tunica vaginalis, base of tongue) as phrases.
4. **Positive controls:** the 25 anchors in Section 4 — prioritizing neuroendocrine, soft-tissue sarcoma, germ cell, paraganglioma, mesothelial, melanoma, and Müllerian/serous families — with codes flagged for verification against the current ICD-O-3.2 numeric table.
5. **Hotspot rule:** flag 3-digit families with `HD_F ≥ 0.40 AND k_F ≥ 3`, rank by `HD_F * log(1+k_F)`; families surface themselves, nothing hardcoded.

Where a specific ICD-O-3.2 code could not be confirmed with certainty (e.g., exact 4-digit assignment for malignant PEComa and extra-adrenal paraganglioma under the latest 3.2 revision), that is flagged in Section 4 rather than asserted — verify against the [official NAACCR/IARC ICD-O-3.2 tables](https://www.naaccr.org/icdo3/) before hardcoding.
