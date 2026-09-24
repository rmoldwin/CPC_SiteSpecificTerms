USE [pathchartprd]
GO

/****** Object:  UserDefinedFunction [dbo].[Clean]    Script Date: 7/9/2026 10:29:10 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE OR ALTER FUNCTION [dbo].[Clean]
-- =============================================
-- Author:      Moldwin, Richard
-- Create Date: 2022 Aug 29; Edited 4/30/2023
--   RM 10/2024 : filters for aem, paed, aen
--   RM Jan/Feb 2026 : Roman-numeral normalization; remove invisible Unicode;
--                     NVARCHAR for Unicode comparisons
--   2026-07-09 : FIX 1 ordering, FIX 2 type-numeral WHERE, FIX 3 acronym Roman,
--                FIX 4 case-preserving spelling (regenerated to match clean_term.py)
-- Description: Normalize characters/spacing that interfere with string comparison.
-- =============================================
/* ============================================================================
   dbo.Clean  —  CORRECTED VERSION  (regenerated 2026-07-09)

   Normalizes ICD-O term strings so variant spellings compare equal.
   This is the SQL counterpart of scripts/clean_term.py and produces the SAME
   normalized value. Use it ONLY as a comparison / join key — never as a
   literature-search query string (the normalized form drops NOS/type,
   Americanizes spelling, and numeralizes Roman numerals, which makes it a
   poor search term). See the ICDO32 skill, rules 10 & 11.

   ----------------------------------------------------------------------------
   FIXES vs. the previous version (each marked  ***FIX n***  inline):

   FIX 1  (Bug A — rule ordering)
       Dashes ( -  – (0x2013)  — (0x2014) ) and '/' are converted to spaces
       BEFORE ' NOS' / ' (NOS)' / ' type' are removed. In the old code these
       removals ran first, so a HYPHENATED 'X-type' / 'X-NOS' kept its word
       while the spaced 'X type' lost it, and the two forms failed to match
       (e.g. 'duodenal-type' vs 'duodenal type').

   FIX 2  (Bug B — type-numeral WHERE clauses)
       The old ' type II' / ' type I' lines guarded on
       WHERE ... LIKE '% grade II' / '% grade I'  (copy/paste slip), so they
       almost never fired. They now guard on the matching '% type II'/'% type I'.
       Per maintainer, a 'type <roman>' collapses to just the DIGIT (the word
       'type' is dropped by the later blanket ' type' removal), so we convert
       to ' <digit>' rather than ' type <digit>'.

   FIX 3  (acronym Roman numerals — new)
       Handles the cases the old code flagged as "best handled manually"
       (RAEB I/II, CMML I/II, AIN/CIN/PIN/VAIN/VIN III, etc.): an ALL-CAPS
       acronym followed by a trailing Roman numeral is converted to the digit
       so 'AIN III' == 'AIN 3'. Only fires on a TRAILING numeral (anchored),
       and only after ' NOS' is removed so 'CIN III, NOS' -> 'CIN III' -> 'CIN 3'.

   FIX 4  (case-preserving British-spelling replacement)
       Old CI REPLACE adopted the replacement's lower-case, so 'Oesophageal'
       -> 'esophageal' (leading capital lost) and 'Tumour' -> 'tumor'. Each
       spelling fix is now done with BOTH a capitalized and a lower-case
       pattern (case-sensitive collation) so 'Oesophageal' -> 'Esophageal'
       and 'oesophageal' -> 'esophageal'. A trailing standalone capital 'I'
       is never touched (only type/grade/ACRONYM-prefixed numerals convert).

   NOT changed (intentional, per maintainer):
     * grade/type/acronym numeral conversion is ANCHORED at end of string, so
       only a TRAILING numeral converts (mid-string 'CIN III with dysplasia'
       is left as-is).
     * word order is NEVER reordered — different word orders are distinct
       synonyms.
   ============================================================================ */

(
    @StringIn NVARCHAR(MAX)
)
RETURNS NVARCHAR(MAX)
AS
BEGIN
    IF @StringIn IS NULL RETURN NULL;
    IF TRIM(@StringIn) = '' RETURN '';

    DECLARE @StringOut NVARCHAR(MAX) = @StringIn;

    -- [unchanged] &nbsp; (NCHAR 160) and '/' -> space. Same as original lines 41-42.
    SELECT @StringOut = REPLACE(@StringOut, NCHAR(160), ' ');
    SELECT @StringOut = REPLACE(@StringOut, '/', ' ');
    -- [moved] The original collapsed double-spaces HERE (its lines 44-47). That
    -- collapse is now deferred to just after the dash->space step below, because
    -- converting dashes can create new double-spaces that also need collapsing.
    -- Doing it once, after dashes, covers both the '/' and dash cases.

    -- [unchanged] Remove invisible Unicode characters (original lines 50-52).
    SELECT @StringOut = REPLACE(@StringOut, NCHAR(0x200B), '');   -- zero-width space
    SELECT @StringOut = REPLACE(@StringOut, NCHAR(0x00AD), '');   -- soft hyphen
    SELECT @StringOut = REPLACE(@StringOut, NCHAR(0xFEFF), '');   -- zero-width no-break space

    -- [unchanged] strip commas, leading '+'/'?', and '#' (original lines 54-57).
    SELECT @StringOut = REPLACE(@StringOut, ',', '');
    SELECT @StringOut = TRIM(LEADING '+' FROM @StringOut);
    SELECT @StringOut = TRIM(LEADING '?' FROM @StringOut);
    SELECT @StringOut = REPLACE(@StringOut, '#', '');

    -- =====================================================================
    -- ***FIX 1 (Bug A: rule ordering)***
    -- CHANGE: dashes are converted to spaces HERE, i.e. BEFORE the ' NOS' /
    --   ' (NOS)' / ' type' removals below.
    -- ORIGINAL BEHAVIOR: the original removed ' NOS'/' type' at lines 58-60 and
    --   only converted dashes later at lines 75-77. Consequence: a hyphenated
    --   'duodenal-type' still read as one token when ' type' was removed, so it
    --   was NOT stripped, while the spaced 'duodenal type' WAS stripped -> the
    --   two spellings normalized differently and failed to match.
    -- EFFECT OF FIX: 'X-type' first becomes 'X type', so the later ' type'
    --   removal treats both spellings identically ('duodenal-type' ==
    --   'duodenal type'). Same reasoning for 'X-NOS' vs 'X NOS'.
    -- =====================================================================
    SELECT @StringOut = REPLACE(@StringOut, '-', ' ');            -- hyphen (orig line 75)
    SELECT @StringOut = REPLACE(@StringOut, NCHAR(0x2013), ' ');  -- en dash – (orig line 76)
    SELECT @StringOut = REPLACE(@StringOut, NCHAR(0x2014), ' ');  -- em dash — (orig line 77)

    -- [moved here] collapse duplicate spaces. Original did this at lines 44-47
    -- before removing dashes; moved after the dash step so the spaces introduced
    -- by dash->space (and by '/'->space above) are all collapsed in one pass.
    WHILE CHARINDEX('  ', @StringOut) > 0
        SELECT @StringOut = REPLACE(@StringOut, '  ', ' ');

    -- =====================================================================
    -- ***FIX 1 (cont.)*** Remove ' NOS' / ' (NOS)' now (was original lines 58-59),
    -- AND do it BEFORE the numeral rules below.
    -- WHY BEFORE THE NUMERALS: a term like 'CIN III, NOS' has its comma removed
    --   earlier, leaving 'CIN III NOS'. If NOS were removed AFTER the numeral
    --   step, 'III' would not be at the end (NOS would be), the acronym rule
    --   would not fire, and it would fail to match its sibling 'CIN 3, NOS'.
    --   Removing NOS first makes the string end in the numeral: 'CIN III'.
    -- =====================================================================
    SELECT @StringOut = REPLACE(@StringOut, ' NOS', '');
    SELECT @StringOut = REPLACE(@StringOut, ' (NOS)', '');

    -- =====================================================================
    -- Trailing Roman-numeral normalization. ALL THREE blocks below share two
    -- deliberate properties carried over from the original design:
    --   (a) ANCHORED AT END ('% ... III', not '% ... III%'): only a numeral at
    --       the very end of the string converts. A mid-string 'CIN III with
    --       dysplasia' is intentionally left alone. (Original intent, kept.)
    --   (b) longest-first (III before II before I) via IF/ELSE IF, so 'III' is
    --       never partially matched as 'II' then 'I'.
    -- IMPLEMENTATION NOTE: the original used
    --       REPLACE(@s,' grade III',' grade 3') WHERE @s LIKE '% grade III'.
    --   REPLACE is global, so if ' grade III' ever appeared twice it would
    --   convert both. Here we instead rebuild the string as LEFT(head) + digit,
    --   which converts ONLY the trailing occurrence and makes the anchoring
    --   explicit. The LEN()-N math is annotated on each line.
    -- =====================================================================

    -- grade <roman> -> grade <digit>   (UNCHANGED semantics from original lines
    --   63-65: keep the word 'grade', replace only the trailing numeral).
    --   ' grade III' ends in 'III' (3 chars) -> drop 3, append '3'; likewise
    --   'II' -> drop 2 append '2'; 'I' -> drop 1 append '1'.
    IF @StringOut LIKE '% grade III' SELECT @StringOut = LEFT(@StringOut, LEN(@StringOut)-3) + '3';
    ELSE IF @StringOut LIKE '% grade II' SELECT @StringOut = LEFT(@StringOut, LEN(@StringOut)-2) + '2';
    ELSE IF @StringOut LIKE '% grade I'  SELECT @StringOut = LEFT(@StringOut, LEN(@StringOut)-1) + '1';

    -- =====================================================================
    -- ***FIX 2 (Bug B: wrong WHERE guard on type numerals)***
    -- ORIGINAL BEHAVIOR (lines 67-69): the ' type II' and ' type I' lines were
    --   guarded on  WHERE @s LIKE '% grade II'  and  '% grade I'  (a copy/paste
    --   slip -- they checked 'grade', not 'type'). As a result 'type II' and
    --   'type I' almost never converted, so 'CMML type II' and 'CMML II' did
    --   not match. (Only ' type III' had the correct guard.)
    -- CHANGE: guard each on the matching '% type III'/'% type II'/'% type I'.
    -- MAINTAINER DECISION: for 'type', DROP the word 'type' and keep just the
    --   DIGIT (unlike 'grade', which keeps the word). So we remove the whole
    --   ' type <roman>' tail and append only the digit:
    --     ' type III' = 8 chars -> drop 8, append '3'
    --     ' type II'  = 7 chars -> drop 7, append '2'
    --     ' type I'   = 6 chars -> drop 6, append '1'
    --   e.g. 'CMML type II' -> 'CMML 2'  (matches 'CMML II' after FIX 3).
    -- =====================================================================
    IF @StringOut LIKE '% type III' SELECT @StringOut = LEFT(@StringOut, LEN(@StringOut)-8) + '3';
    ELSE IF @StringOut LIKE '% type II' SELECT @StringOut = LEFT(@StringOut, LEN(@StringOut)-7) + '2';
    ELSE IF @StringOut LIKE '% type I'  SELECT @StringOut = LEFT(@StringOut, LEN(@StringOut)-6) + '1';

    -- =====================================================================
    -- ***FIX 3 (acronym Roman numerals -- NEW)***
    -- ADDED: the original had none of this; comment line 73 explicitly said
    --   'there are types like RAEB I/II and CMML I/II ... best handled manually.'
    --   This block handles them automatically so the Roman and Arabic siblings
    --   collapse together (e.g. 'AIN III' == 'AIN 3', 'RAEB II' == 'RAEB 2').
    -- RULE: an ALL-CAPS acronym (>=2 capital letters) immediately followed by a
    --   trailing Roman numeral -> keep the acronym, replace the numeral with a
    --   digit. Same anchored / longest-first / LEFT()+digit approach as above
    --   (numeral 'III'=3 chars, 'II'=2, 'I'=1).
    -- CASE-SENSITIVITY (addresses your 'do not remove capital I' concern):
    --   the pattern is matched under Latin1_General_CS_AS and REQUIRES two
    --   trailing capitals before the numeral ('%[A-Z][A-Z] I'). Therefore:
    --     - a lone Title-case word ending in 'I' (e.g. an ordinary word) will
    --       NOT match, and
    --     - a MID-string 'Type I ...' or 'MEN I syndrome' is not at the end, so
    --       it will NOT match either.
    --   A genuine standalone capital 'I' that is part of a word is preserved.
    -- =====================================================================
    IF @StringOut COLLATE Latin1_General_CS_AS LIKE '%[A-Z][A-Z] III'
        SELECT @StringOut = LEFT(@StringOut, LEN(@StringOut)-3) + '3';
    ELSE IF @StringOut COLLATE Latin1_General_CS_AS LIKE '%[A-Z][A-Z] II'
        SELECT @StringOut = LEFT(@StringOut, LEN(@StringOut)-2) + '2';
    ELSE IF @StringOut COLLATE Latin1_General_CS_AS LIKE '%[A-Z][A-Z] I'
        SELECT @StringOut = LEFT(@StringOut, LEN(@StringOut)-1) + '1';

    -- [unchanged] blanket ' type' removal (original line 60). Kept, but now runs
    -- AFTER the type-numeral rule (FIX 2) so 'type <roman>' is converted to a
    -- digit first; any remaining plain ' type' (e.g. 'intestinal type') is then
    -- stripped as before.
    SELECT @StringOut = REPLACE(@StringOut, ' type', '');

    -- [unchanged] "non abc"/"Non abc" -> "nonabc"/"Nonabc" (original lines 80-81).
    -- Case-sensitive collation is intentional so the two capitalizations are
    -- handled separately and each keeps its own case.
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'non ', 'non');
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'Non ', 'Non');

    -- [unchanged] Naevus -> nevus (original lines 85-86). Already case-sensitive
    -- with both capitalizations in the original, so no fix was needed here; kept
    -- as the model for how the FIX 4 spelling replacements below are done.
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'Naev', 'Nev');
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'naev', 'nev');

    -- =====================================================================
    -- ***FIX 4 (British -> American spelling: preserve original case)***
    -- ORIGINAL BEHAVIOR (lines 88-113): these used a plain REPLACE under the
    --   default (case-insensitive) collation, e.g.
    --       REPLACE(@s, 'oesophag', 'esophag')
    --   SQL Server's CI REPLACE MATCHES case-insensitively but SUBSTITUTES the
    --   replacement string verbatim -- so 'Oesophageal' became 'esophageal'
    --   (leading capital LOST) and 'Tumour' became 'tumor'. That silently
    --   changed the case of the first letter of many terms.
    -- CHANGE: each replacement is now done under a CASE-SENSITIVE collation
    --   (Latin1_General_CS_AS) with TWO explicit patterns -- a Capitalized one
    --   and a lower-case one -- each substituting a replacement of matching
    --   case. So 'Oesophageal' -> 'Esophageal' and 'oesophageal' ->
    --   'esophageal'; the original letter case is preserved in every position.
    --   (Where the original had only a lower-case pattern, a Capitalized twin
    --   line has been ADDED; these additions are marked 'FIX 4 add'.)
    -- =====================================================================
    -- 'ou' family. Original (lines 88-92) had ONE line each ('tumour','colour',
    -- 'Grey','grey','mould'); FIX 4 keeps the original as the lower-case (or
    -- given-case) pattern and ADDS the Capitalized twin where the term can begin
    -- a string. Each line notes 'orig' or 'FIX 4 add'.
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'Tumour', 'Tumor');   -- FIX 4 add (Tumour->Tumor, capital kept)
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'tumour', 'tumor');   -- orig line 88
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'Colour', 'Color');   -- FIX 4 add
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'colour', 'color');   -- orig line 89
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'Grey', 'Gray');      -- orig line 90 (was CI, now CS)
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'grey', 'gray');      -- orig line 91
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'Mould', 'Mold');     -- FIX 4 add
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'mould', 'mold');     -- orig line 92 (smouldering)
    -- [unchanged] 'of the ' -> 'of ' (original line 94). Case-insensitive is fine
    -- here -- there is no leading-letter to preserve in the lowercase 'of the'.
    SELECT @StringOut = REPLACE(@StringOut, 'of the ', 'of ');
    -- 'ae' family (original lines 96-102). CI->CS + added Capitalized twins.
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'aem', 'em');     -- orig line 96 (haematology, leukaemia)
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'Aem', 'Em');     -- FIX 4 add (rare, but preserves capital)
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'paed', 'ped');   -- orig line 97
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'Paed', 'Ped');   -- orig line 98 (was CI; kept, now CS)
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'paen', 'pen');   -- orig line 99 (cytopaenia)
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'Paen', 'Pen');   -- FIX 4 add
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'phaeo', 'pheo'); -- orig line 100 (phaeochromocytoma)
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'Phaeo', 'Pheo'); -- orig line 101
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'melaen', 'melen'); -- orig line 102 (melaena->melena)
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'Melaen', 'Melen'); -- FIX 4 add
    -- 'tre' family (original lines 104-105). CI->CS + added Capitalized twins.
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'Goitre', 'Goiter'); -- FIX 4 add
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'goitre', 'goiter'); -- orig line 104
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'Centre', 'Center'); -- FIX 4 add
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'centre', 'center'); -- orig line 105
    -- 'oe' family (original lines 107-113). CI->CS + added Capitalized twins.
    -- NOTE: the original listed 'oedema' TWICE (lines 107 and 109); collapsed to
    -- one pair here (harmless de-duplication, same result).
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'Oedema', 'Edema');   -- FIX 4 add
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'oedema', 'edema');   -- orig lines 107/109
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'Oesophag', 'Esophag'); -- FIX 4 add (THE key case: Oesophageal->Esophageal)
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'oesophag', 'esophag'); -- orig line 108
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'Coeli', 'Celi');     -- FIX 4 add (Coeliac->Celiac)
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'coeli', 'celi');     -- orig line 110
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'rhoea', 'rhea');     -- orig line 111 (never starts a term -> no capital twin needed)
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'Oestr', 'Estr');     -- FIX 4 add (Oestrogen->Estrogen)
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'oestr', 'estr');     -- orig line 112
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'Foet', 'Fet');       -- FIX 4 add (Foetal->Fetal)
    SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'foet', 'fet');       -- orig line 113

    -- [unchanged] remove possessive 's (original lines 116-117): straight quote
    -- ('s) and curly apostrophe (U+2019 s). CI is fine; nothing case-bearing is
    -- lost. NCHAR(0x2019)+'s' reproduces the original curly-apostrophe rule.
    SELECT @StringOut = REPLACE(@StringOut, '''s', '');
    SELECT @StringOut = REPLACE(@StringOut, NCHAR(0x2019) + 's', '');

    -- [unchanged] truncate everything from '(specify' onward (original line 118).
    -- CHARINDEX-1 keeps the text BEFORE '(specify'; guarded so it only fires when
    -- '(specify' is present (CHARINDEX > 0).
    SELECT @StringOut = SUBSTRING(@StringOut, 1, (CHARINDEX('(specify', @StringOut, 1) - 1))
        WHERE CHARINDEX('(specify', @StringOut, 1) > 0;

    -- [added] final tidy. The original ended with a single TRIM (line 120). We
    -- also collapse any residual double spaces first, because the extra dash and
    -- '(specify' edits above can leave a stray double space near the end. This is
    -- a safety net; it does not change any single-spaced result.
    WHILE CHARINDEX('  ', @StringOut) > 0
        SELECT @StringOut = REPLACE(@StringOut, '  ', ' ');
    SELECT @StringOut = TRIM(@StringOut);   -- orig line 120

    RETURN @StringOut;
END
GO
