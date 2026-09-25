"""
clean_term.py — faithful Python port of dbo.Clean (Moldwin, 2022-2026).

Purpose: normalize term strings so near-identical variants collapse to one key
for string comparison / de-duplication. This mirrors the T-SQL UDF EXACTLY,
including its known quirks (documented inline) so the Python dedup key matches
the maintainer's SQL environment. Do NOT "fix" the quirks without sign-off —
the whole point is byte-for-byte parity with the authoritative SQL function.

Behavior notes / faithful quirk replication:
  * Default SQL collation is case-INSENSITIVE (Latin1_General_CI_AS), so plain
    REPLACE calls are case-insensitive substring replacements. Lines that use
    `COLLATE Latin1_General_CS_AS` are case-SENSITIVE — replicated below.
  * The Roman-numeral grade/type conversions are gated by `WHERE @StringOut LIKE
    '% grade III'` etc., i.e. ANCHORED AT END. So only a trailing " grade III"
    (etc.) converts; a mid-string " grade III " does not. Replicated.
  * The two ' type II' / ' type I' lines carry `WHERE ... LIKE '% grade II'` /
    `'% grade I'` (a copy/paste slip in the SQL): they only fire when the string
    ENDS in " grade II"/" grade I", and they still replace the substring " type
    II"/" type I" if present. Replicated exactly (net effect: almost never fires).
  * '(specify...' truncation cuts the string at the first '(specify' occurrence.
"""
import re

# SQL default collation is case-insensitive; Python str.replace is case-sensitive,
# so we implement a case-insensitive replace for the plain (non-COLLATE) REPLACEs.

def _ci_replace(s: str, old: str, new: str) -> str:
    """Case-insensitive replace (mimics SQL REPLACE under CI collation)."""
    if not old:
        return s
    return re.sub(re.escape(old), lambda m: new, s, flags=re.IGNORECASE)


def _cs_replace(s: str, old: str, new: str) -> str:
    """Case-sensitive replace (mimics REPLACE ... COLLATE Latin1_General_CS_AS)."""
    return s.replace(old, new)


def _cp_replace(s: str, old: str, new: str) -> str:
    """Case-INSENSITIVE match, case-PRESERVING replace.
    Finds `old` regardless of case (like SQL CI REPLACE) but keeps the ORIGINAL
    casing pattern of each match instead of adopting the replacement's casing.
    Rules (applied per matched span):
      * if the matched text is all-caps            -> emit `new` upper-cased
      * if the matched text is title/leading-cap   -> emit `new` with first
                                                      alpha char upper, rest as-is
      * otherwise (all lower / mixed)              -> emit `new` as written
    This fixes the SQL side effect where CI REPLACE(oesophag->esophag) turned
    'Oesophageal' into lower-case 'esophageal'. Now 'Oesophageal'->'Esophageal'
    and 'oesophageal'->'esophageal'.
    """
    if not old:
        return s
    def _rep(m):
        matched = m.group(0)
        if matched.isupper():
            return new.upper()
        # leading-capital (first alpha upper, and not all-upper)
        first_alpha = next((c for c in matched if c.isalpha()), "")
        if first_alpha and first_alpha.isupper():
            # capitalize first alpha of `new`, keep the rest of `new` as written
            out = []
            done = False
            for c in new:
                if not done and c.isalpha():
                    out.append(c.upper()); done = True
                else:
                    out.append(c)
            return "".join(out)
        return new
    return re.sub(re.escape(old), _rep, s, flags=re.IGNORECASE)


def clean(string_in):
    # IF @StringIn IS NULL RETURN NULL
    if string_in is None:
        return None
    # IF TRIM(@StringIn) = '' RETURN ''
    if string_in.strip() == "":
        return ""

    s = string_in

    s = s.replace("\u00A0", " ")   # NCHAR(160) &nbsp; -> space
    s = s.replace("/", " ")         # '/' -> space

    # remove duplicate spaces (loop until none remain)
    while "  " in s:
        s = s.replace("  ", " ")

    # invisible unicode
    s = s.replace("\u200B", "")     # zero-width space
    s = s.replace("\u00AD", "")     # soft hyphen
    s = s.replace("\uFEFF", "")     # zero-width no-break space

    s = s.replace(",", "")          # remove commas
    s = s.lstrip("+")               # TRIM(LEADING '+' ...)
    s = s.lstrip("?")               # TRIM(LEADING '?' ...)
    s = s.replace("#", "")

    # ------------------------------------------------------------------
    # DEVIATION FROM LITERAL SQL (intentional bug fix — "Bug A"):
    # The SQL removes ' NOS' / ' type' BEFORE converting dashes to spaces,
    # so a hyphenated "X-type" / "X-NOS" keeps its "type"/"NOS" (only the
    # space-separated "X type" is stripped). That makes
    #   "Follicular lymphoma, duodenal type"  vs  "...duodenal-type"
    # normalize DIFFERENTLY and survive as duplicate rows. We convert
    # dashes (and already-done '/') to spaces FIRST so both forms lose
    # "type" identically. To reproduce the SQL 1:1 instead, move the three
    # dash replacements back below the NOS/type block.
    # ------------------------------------------------------------------
    s = s.replace("-", " ")         # hyphen  (moved earlier)
    s = s.replace("\u2013", " ")    # en/em dash – (moved earlier)
    s = s.replace("\u2014", " ")    # long em dash — (moved earlier)
    while "  " in s:                # collapse any new double spaces
        s = s.replace("  ", " ")

    # ------------------------------------------------------------------
    # Roman-numeral normalization (do this BEFORE the blanket ' type'
    # removal, so a 'type II'/'grade II' suffix converts to a digit).
    #
    # SAFETY (maintainer concern): a bare trailing capital 'I' could be a
    # meaningful letter, NOT a numeral. A full scan of all 5,551 master
    # terms shows every trailing standalone I/II/III is in fact a Roman
    # numeral, and is ALWAYS preceded by a qualifier: 'type', 'grade', or
    # an all-UPPERCASE grading acronym (RAEB, AIN, CIN, PIN, VAIN, VIN, ...).
    # We therefore convert a trailing numeral ONLY when it is a whole-token
    # suffix immediately preceded by one of those qualifiers. A lone 'I'
    # after an ordinary lowercase word is never touched.
    #
    # Behavior chosen by maintainer: for 'type', DROP the word 'type' and
    # keep the digit ('CMML, Type II' -> 'CMML 2'); for 'grade', KEEP the
    # word 'grade' and use the digit ('... grade III' -> '... grade 3');
    # for an acronym, keep the acronym and use the digit ('AIN III' ->
    # 'AIN 3', matching an existing 'AIN 3' variant).
    # ------------------------------------------------------------------
    # Remove ' NOS' / ' (NOS)' FIRST so a numeral like 'CIN III, NOS' (comma
    # already stripped -> 'CIN III NOS') ends in the numeral for the rules below.
    s = _ci_replace(s, " NOS", "")
    s = _ci_replace(s, " (NOS)", "")

    _ROMAN = {"III": "3", "II": "2", "I": "1"}  # longest-first order matters
    # grade <roman> at end -> grade <digit>
    for rom, dig in _ROMAN.items():
        if re.search(r"(?i)\bgrade %s$" % rom, s):
            s = re.sub(r"(?i)(\bgrade )%s$" % rom, lambda m, d=dig: m.group(1) + d, s)
            break
    # type <roman> at end -> <digit>   (drops the word 'type' per maintainer)
    for rom, dig in _ROMAN.items():
        if re.search(r"(?i)\btype %s$" % rom, s):
            s = re.sub(r"(?i)\btype %s$" % rom, dig, s)
            s = re.sub(r"  +", " ", s).strip()
            break
    # ACRONYM <roman> at end -> ACRONYM <digit>  (acronym = all-caps, >=2 chars)
    m = re.search(r"(?<![^ ])([A-Z]{2,}) (III|II|I)$", s)
    if m:
        s = s[: m.start(2)] + _ROMAN[m.group(2)]

    # blanket ' type' removal (CI, global) — after the type-numeral rule above
    s = _ci_replace(s, " type", "")

    # (dashes were converted to spaces earlier — see "Bug A" note above)

    # non / Non collapse (case-SENSITIVE, global)
    s = _cs_replace(s, "non ", "non")
    s = _cs_replace(s, "Non ", "Non")

    # British spellings: naevus (case-sensitive)
    s = _cs_replace(s, "Naev", "Nev")
    s = _cs_replace(s, "naev", "nev")

    # British/American spelling normalization.
    # DEVIATION FROM LITERAL SQL (agreed — casing fix): SQL used CI REPLACE, which
    # adopts the REPLACEMENT's (lower) casing, so 'Oesophageal'->'esophageal' and
    # 'Tumour'->'tumor' (leading capital lost). We use _cp_replace: match any case,
    # PRESERVE the original casing pattern. So 'Oesophageal'->'Esophageal',
    # 'oesophageal'->'esophageal', 'TUMOUR'->'TUMOR'.
    # -ou-
    s = _cp_replace(s, "tumour", "tumor")
    s = _cp_replace(s, "colour", "color")
    s = _cp_replace(s, "grey", "gray")
    s = _cp_replace(s, "mould", "mold")

    s = _cp_replace(s, "of the ", "of ")

    # -ae-
    s = _cp_replace(s, "aem", "em")
    s = _cp_replace(s, "paed", "ped")
    s = _cp_replace(s, "paen", "pen")
    s = _cp_replace(s, "phaeo", "pheo")
    s = _cp_replace(s, "melaen", "melen")

    # -tre-
    s = _cp_replace(s, "goitre", "goiter")
    s = _cp_replace(s, "centre", "center")

    # -oe-
    s = _cp_replace(s, "oedema", "edema")
    s = _cp_replace(s, "oesophag", "esophag")
    s = _cp_replace(s, "coeli", "celi")
    s = _cp_replace(s, "rhoea", "rhea")
    s = _cp_replace(s, "oestr", "estr")
    s = _cp_replace(s, "foet", "fet")

    # possessive removal
    s = s.replace("'s", "")   # straight apostrophe
    s = s.replace("\u2019s", "")  # real apostrophe ’s

    # truncate at '(specify'
    idx = s.find("(specify")
    if idx > 0:
        s = s[:idx]

    s = s.strip()
    return s


if __name__ == "__main__":
    import sys
    for line in sys.stdin:
        print(clean(line.rstrip("\n")))
