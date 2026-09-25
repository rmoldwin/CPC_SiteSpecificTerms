#!/usr/bin/env python3
"""
STEP 6 - Build the final Excel workbook (and optional CSVs) from decisions.

Columns (locked with user):
  ICDO32 Code | ICDO32 Term | Normalized Term | ICDO32 Preferred Term | Site-Specific? |
  Site Subset (C-codes) | Site Subset (Labels) | Subset Site Count |
  Code's SMVL-Valid Site Count | Code's SMVL-Valid Sites (organ summary) |
  Code's SMVL-Valid Sites (all C-codes) | Rationale | Source (URL) | Source Reference

Sheets: README | Site-Specific Terms (Yes only) | All Screened Terms (all).
Styling: Calibri; teal header #20808D; layout starts at B2; data header row 5.

Input : decisions.jsonl, ceilings.json, pref_map.json
Output: <out.xlsx>   (CSVs optional via --csv)

Usage:
  python3 06_build_workbook.py decisions.jsonl ceilings.json pref_map.json OUT.xlsx [--csv]
"""
import json, sys, csv, os
from collections import defaultdict

# ---------------------------------------------------------------------------
# 4-digit ICD-O-3.2 topography label map (SPECIFIC site definitions, NOT the
# parent-group prefix). Loaded from icdo32_topography.json which lives beside
# the data files. This fixes the prior bug where per-code subset sites were
# labeled with the 3-char parent group (e.g. C221 mislabeled "Liver" instead
# of "Intrahepatic bile duct").
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
def _load_topo():
    for cand in (os.path.join(_HERE, "..", "icdo32_topography.json"),
                 os.path.join(os.getcwd(), "icdo32_topography.json")):
        if os.path.exists(cand):
            return json.load(open(cand, encoding="utf-8"))
    raise SystemExit("icdo32_topography.json not found (required for 4-digit site labels)")
TOPO = _load_topo()

# Parent-organ grouping (3-char prefix) used ONLY for the readable ceiling
# organ-summary column, never for per-code subset site labels.
ORGAN = {
 'C00':'Lip','C01':'Tongue','C02':'Tongue','C03':'Gum','C04':'Mouth','C05':'Palate','C06':'Mouth',
 'C07':'Salivary','C08':'Salivary','C09':'Tonsil','C10':'Oropharynx','C11':'Nasopharynx',
 'C12':'Pyriform sinus','C13':'Hypopharynx','C14':'Pharynx','C15':'Esophagus','C16':'Stomach',
 'C17':'Small intestine','C18':'Colon','C19':'Rectosigmoid','C20':'Rectum','C21':'Anus',
 'C22':'Liver & intrahepatic bile ducts','C23':'Gallbladder','C24':'Biliary tract','C25':'Pancreas','C26':'GI tract',
 'C30':'Nasal cavity/middle ear','C31':'Sinuses','C32':'Larynx','C33':'Trachea','C34':'Lung',
 'C37':'Thymus','C38':'Heart/mediastinum','C39':'Respiratory','C40':'Bone-limbs','C41':'Bone-other',
 'C42':'Blood/marrow','C44':'Skin','C47':'Peripheral nerves','C48':'Peritoneum/retroperitoneum',
 'C49':'Soft tissue','C50':'Breast','C51':'Vulva','C52':'Vagina','C53':'Cervix','C54':'Corpus uteri',
 'C55':'Uterus NOS','C56':'Ovary','C57':'Female genital','C58':'Placenta','C60':'Penis','C61':'Prostate',
 'C62':'Testis','C63':'Male genital','C64':'Kidney','C65':'Renal pelvis','C66':'Ureter','C67':'Bladder',
 'C68':'Urinary','C69':'Eye','C70':'Meninges','C71':'Brain','C72':'CNS','C73':'Thyroid','C74':'Adrenal',
 'C75':'Endocrine','C76':'Ill-defined','C77':'Lymph nodes','C80':'Unknown primary',
}
def organ(code): return ORGAN.get(code[:3], code[:3])
def site_label(code): return TOPO.get(code, organ(code))
# Per-code subset labels use SPECIFIC 4-digit definitions.
def labelize(codes): return '; '.join(f'{c}={site_label(c)}' for c in codes)
# Ceiling organ-summary groups to parent organ for readability.
def summarize(codes):
    g = defaultdict(list)
    for c in codes: g[organ(c)].append(c)
    return '; '.join(f'{k} ({len(v)})' for k, v in sorted(g.items()))

COLS = ["ICDO32 Code","ICDO32 Term","Normalized Term","ICDO32 Preferred Term","Site-Specific?",
        "Site Subset (C-codes)","Site Subset (Labels)","Subset Site Count",
        "Code's SMVL-Valid Site Count","Code's SMVL-Valid Sites (organ summary)",
        "Code's SMVL-Valid Sites (all C-codes)","Rationale","Source (URL)","Source Reference"]

def rows_from(decisions, ceilings, pref):
    for r in sorted(decisions, key=lambda x: (x["code"], x["term"])):
        code = r["code"]; ceil = sorted(ceilings.get(code, []))
        subset = r.get("subset_codes", [])
        yield {
            "ICDO32 Code": code,
            "ICDO32 Term": r["term"],
            "Normalized Term": r.get("normalized_term", ""),
            "ICDO32 Preferred Term": pref.get(code, ""),
            "Site-Specific?": r["decision"],
            "Site Subset (C-codes)": ', '.join(subset),
            "Site Subset (Labels)": labelize(subset),
            "Subset Site Count": r.get("subset_count", 0),
            "Code's SMVL-Valid Site Count": len(ceil),
            "Code's SMVL-Valid Sites (organ summary)": summarize(ceil),
            "Code's SMVL-Valid Sites (all C-codes)": ', '.join(ceil),
            "Rationale": r.get("rationale", ""),
            "Source (URL)": r.get("source", ""),
            "Source Reference": r.get("source_name", ""),
        }

def main():
    decisions = [json.loads(l) for l in open(sys.argv[1])]
    ceilings = json.load(open(sys.argv[2]))
    pref = json.load(open(sys.argv[3]))
    out = sys.argv[4]
    want_csv = "--csv" in sys.argv

    all_rows = list(rows_from(decisions, ceilings, pref))
    yes_rows = [r for r in all_rows if r["Site-Specific?"] == "Yes"]

    if want_csv:
        for fn, rows in [("ICDO32_All_Screened_Terms.csv", all_rows),
                         ("ICDO32_SiteSpecific_Terms.csv", yes_rows)]:
            with open(fn, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)

    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = openpyxl.Workbook()
    TEAL = "20808D"
    hdr_fill = PatternFill("solid", fgColor=TEAL)
    hdr_font = Font(name="Calibri", bold=True, color="FFFFFF")
    base_font = Font(name="Calibri")
    center = Alignment(horizontal="center", vertical="top", wrap_text=True)
    left = Alignment(horizontal="left", vertical="top", wrap_text=True)

    # ---- README sheet ----
    ws = wb.active; ws.title = "README"

    # ---- Counts for the README narrative (computed from the actual data) ----
    n_all = len(all_rows)
    n_yes = len(yes_rows)
    n_no = sum(1 for r in all_rows if r["Site-Specific?"] == "No")
    n_unc = sum(1 for r in all_rows if r["Site-Specific?"] == "Uncertain")

    # ---- README ----
    # README lines are (text, style) tuples. style in:
    #   'title'   -> 16pt bold
    #   'h'       -> 12pt bold section header
    #   'body'    -> 11pt normal (wrapped)
    #   'bodyb'   -> 11pt, first run bold-ish via full bold (used for labeled defs)
    #   ''        -> blank spacer
    readme = [
        ("ICD-O-3.2 Site-Specific Term Detection \u2014 Full Catalog", "title"),
        ("A catalog of cancer histology (morphology) terms that, although their code is "
         "officially allowed at many anatomic sites, in real-world pathology occur at only a "
         "narrow subset of those sites.", "body"),
        ("", ""),

        ("What question this answers", "h"),
        ("In ICD-O-3.2, a morphology code (e.g. 8140/3 Adenocarcinoma) can be paired with a wide "
         "range of topography (anatomic-site) codes. The NCI/SEER Cancer PathCHART project publishes, "
         "for every morphology code, which sites that code is VALID at. But many specific NAMED terms "
         "under a code are, by their biology or WHO definition, restricted to far fewer sites than the "
         "code as a whole. This workbook identifies exactly those terms \u2014 the 'site-specific' ones \u2014 "
         "and, for each, records the specific sites where it actually arises, with a literature source.", "body"),
        ("", ""),

        ("Key vocabulary", "h"),
        ("\u2022 Morphology code / term: the histology type, e.g. 8160/3 = 'Cholangiocarcinoma'. One code "
         "can carry many named terms (subtypes, synonyms).", "body"),
        ("\u2022 Topography (site) code: the anatomic location, e.g. C221 = 'Intrahepatic bile duct'. "
         "4-digit C-codes are specific sites; the first 3 characters (C22) are the broad parent organ group.", "body"),
        ("\u2022 SMVL: the NCI/SEER Cancer PathCHART 'Site-Morphology Validation List', which marks each "
         "code-site pairing as Valid, Unlikely, or Impossible.", "body"),
        ("\u2022 Ceiling: the full set of sites a code is allowed at = every SMVL pairing marked Valid. This "
         "is the baseline we compare each term against.", "body"),
        ("\u2022 Site-specific: a term is 'site-specific' when the sites where it actually occurs are a STRICT "
         "SUBSET of (fewer than) its code's ceiling.", "body"),
        ("", ""),

        ("How the analysis was done (high level)", "h"),
        ("Step 1 \u2013 Build each code's ceiling. From the SMVL, for every morphology code we collect all "
         "sites marked Valid (status column CPC2026A = 1). Sites marked Unlikely or Impossible are "
         "excluded \u2014 we treat 'Unlikely' as effectively impossible.", "body"),
        ("Step 2 \u2013 Decide which terms to research. Terms sit under codes taken verbatim from the master "
         "ICDO32 term list. A term can only be site-specific if its code is valid at MORE THAN ONE site, so "
         "single-site codes are automatically 'No' (no research needed). Two site systems are never "
         "researched and never appear in a reported subset: C76 (ill-defined) and C80 (unknown primary).", "body"),
        ("Step 3 \u2013 Literature research, per term. Working organ system by organ system, each candidate "
         "term is checked against authoritative oncology references \u2014 WHO Blue Books (5th ed.), NCCN, "
         "UpToDate, CAP protocols, and peer-reviewed literature (PubMed/PMC) \u2014 to establish the actual "
         "site(s) of origin for that specific term.", "body"),
        ("Step 4 \u2013 Apply the decision rule. If the term's literature-confirmed sites are a strict subset of "
         "its code's ceiling, it is 'Yes' (site-specific). If it can occur across the whole ceiling, it is "
         "'No'. If the evidence is insufficient, it is 'Uncertain' \u2014 never a guess. Every 'Yes' carries a "
         "source URL; any proposed site outside the code's SMVL ceiling is rejected automatically. "
         "Every distinct original code+term appears on its own row; if the exact same code+term was "
         "researched in more than one organ-system batch, the single best-supported result is kept (a "
         "sourced 'Yes' with the most specific site of origin outranks a broader or weaker one). A "
         "'Normalized Term' column is provided so variant spellings can be joined to other resources.", "body"),
        ("Step 5 \u2013 Anatomic-correctness audit. Every 'Yes' was independently re-checked so that each "
         "assigned site is the term's true site of ORIGIN \u2014 not a site it merely spreads to, and not a "
         "naive name match. Confirmed errors were corrected against fetched sources (see 'Corrections' below).", "body"),
        ("Step 6 \u2013 Assemble this workbook, labeling every site with its specific 4-digit ICD-O-3.2 "
         "definition.", "body"),
        ("", ""),

        ("What is in each sheet", "h"),
        (f"\u2022 'Site-Specific Terms' \u2014 the {n_yes:,} terms judged site-specific ('Yes'). This is the main deliverable.", "body"),
        (f"\u2022 'All Screened Terms' \u2014 all {n_all:,} screened terms with their decision and rationale "
         f"({n_yes:,} Yes / {n_no:,} No / {n_unc:,} Uncertain), for full transparency and audit.", "body"),
        ("", ""),

        ("How to read the columns", "h"),
        ("\u2022 ICDO32 Code / Term: the morphology code and the specific named term being evaluated. Every "
         "distinct original term is kept on its own row (punctuation and spelling variants are preserved).", "body"),
        ("\u2022 Normalized Term: the term after applying the maintainer's normalization routine (dbo.Clean). "
         "Use this column as the join key to other resources; variant spellings of the same entity "
         "(e.g. 'duodenal type' vs 'duodenal-type', 'AIN III' vs 'AIN 3') share one normalized value.", "body"),
        ("\u2022 ICDO32 Preferred Term: IARC's preferred term for the code (a /2 code with no preferred term "
         "falls back to the /3 preferred term, marked '(for /3)'); blank if none is assigned.", "body"),
        ("\u2022 Site-Specific?: the decision \u2014 Yes, No, or Uncertain.", "body"),
        ("\u2022 Site Subset (C-codes) / (Labels): the specific sites where this term arises (only populated for "
         "'Yes'), as codes and as 4-digit site names.", "body"),
        ("\u2022 Subset Site Count: how many sites are in that subset.", "body"),
        ("\u2022 Code's SMVL-Valid Site Count / (organ summary) / (all C-codes): the code's full ceiling \u2014 how "
         "many sites it is allowed at, grouped by parent organ for readability, and the complete code list. "
         "'Yes' means the subset is strictly smaller than this ceiling.", "body"),
        ("\u2022 Rationale: why the term received its decision.", "body"),
        ("\u2022 Source (URL) / Source Reference: the citation supporting a 'Yes'.", "body"),
        ("", ""),

        ("Site labeling note", "h"),
        ("Per-code subset sites use SPECIFIC 4-digit ICD-O-3.2 topography definitions "
         "(e.g. C221 = Intrahepatic bile duct, NOT the broad C22 'Liver' group). The ceiling "
         "'organ summary' column groups to the parent organ for readability only.", "body"),
        ("", ""),

        ("Corrections applied in the 2026-07-09 anatomic audit", "h"),
        ("\u2022 Cholangiocarcinomas \u2014 relabeled to the biliary system (e.g. C221 Intrahepatic bile duct, "
         "C240 Extrahepatic bile duct); these arise in bile ducts, not liver parenchyma. (Underlying site "
         "codes were already correct; this was a display-label fix.)", "body"),
        ("\u2022 Ceruminous carcinomas (8420/3) \u2014 corrected to external ear skin (C442); ceruminous glands "
         "exist only in the external auditory canal, not the middle ear (C301).", "body"),
        ("\u2022 Retinoinvasive melanoma (8720/3) \u2014 corrected to choroid / ciliary body (C693 / C694); the "
         "retina (C692) is invaded, but the tumor originates in the uvea.", "body"),
        ("\u2022 Undifferentiated uterine sarcoma (8805/3) \u2014 corrected to corpus uteri (C542); it arises in "
         "the uterine body, not the cervix.", "body"),
        ("", ""),

        ("Important caveats", "h"),
        ("\u2022 'Uncertain' means the literature was insufficient to decide \u2014 not that the term is site-specific.", "body"),
        ("\u2022 Ceilings reflect the SMVL status column CPC2026A. A different SMVL version may shift some ceilings.", "body"),
        ("\u2022 This is a decision-support reference, not a coding rule set; clinical/registry coding should "
         "follow the current official ICD-O and registry standards.", "body"),
    ]
    README_COL_W = 110
    # ~ chars that fit per line at Calibri 11 in a width-110 column
    CHARS_PER_LINE = 118
    r = 2
    for text, style in readme:
        c = ws.cell(row=r, column=2, value=text)
        if style == "title":
            c.font = Font(name="Calibri", bold=True, size=16)
        elif style == "h":
            c.font = Font(name="Calibri", bold=True, size=12, color="20808D")
        else:
            c.font = Font(name="Calibri", size=11)
        c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        # Set an explicit row height so wrapped text is never clipped.
        if text == "":
            ws.row_dimensions[r].height = 6
        else:
            lines = max(1, -(-len(text) // CHARS_PER_LINE))  # ceil division
            per = 21 if style == "title" else (16 if style == "h" else 15)
            ws.row_dimensions[r].height = lines * per + 2
        r += 1
    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = README_COL_W

    def build_sheet(title, subtitle, rows):
        ws = wb.create_sheet(title)
        ws.column_dimensions["A"].width = 3
        ws.cell(row=2, column=2, value=title).font = Font(name="Calibri", bold=True, size=14)
        ws.cell(row=3, column=2, value=subtitle).font = Font(name="Calibri", italic=True, size=10)
        for j, col in enumerate(COLS):
            c = ws.cell(row=5, column=2+j, value=col)
            c.fill = hdr_fill; c.font = hdr_font; c.alignment = center
        for i, row in enumerate(rows):
            for j, col in enumerate(COLS):
                c = ws.cell(row=6+i, column=2+j, value=row[col])
                c.font = base_font
                c.alignment = center if col in ("ICDO32 Code","Site-Specific?","Subset Site Count","Code's SMVL-Valid Site Count") else left
        widths = [12,34,30,30,12,26,30,10,14,34,40,50,40,34]
        from openpyxl.utils import get_column_letter
        for j, w in enumerate(widths):
            ws.column_dimensions[get_column_letter(2+j)].width = w
        ws.freeze_panes = "B6"
        ws.auto_filter.ref = f"B5:{get_column_letter(1+len(COLS))}{5+len(rows)}"

    build_sheet("Site-Specific Terms", "Terms used at only a proper subset of their code's SMVL-valid sites.", yes_rows)
    build_sheet("All Screened Terms", "All screened terms with Yes/No/Uncertain decision and rationale.", all_rows)

    wb.save(out)
    print(f"wrote {out}: all={len(all_rows)} yes={len(yes_rows)}")

if __name__ == "__main__":
    main()
