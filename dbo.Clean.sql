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
-- Create Date: 2022 Aug 29, Edited 4/30/2023, 
--				RM Edited 10/2024: added filters for: aem, paed, aen
--				RM Edited Jan/Feb 2026: added additional cases for normalizing Roman numerals,
--							Remove invisible Unicode characters - 2026Feb15
--							Converted strings to use NVARCHAR instead of VARCHAR to allow unicode comparisons, etc.
-- Description: Normalize some characters and extra spaces that can interfere with string comparisions
-- =============================================
(
@StringIn NVARCHAR(MAX)  -- Changed from VARCHAR
)
RETURNS NVARCHAR(MAX)    -- Changed from VARCHAR
AS
BEGIN
IF @StringIn IS NULL Return NULL;  --RM: changed from '' to NULL 2026Feb24
IF TRIM(@StringIn) = '' RETURN '';

DECLARE @StringOut NVARCHAR(MAX) = @StringIn;  -- Changed from VARCHAR

SELECT @StringOut = REPLACE(@StringOut, NCHAR(160), ' '); --replace every &nbsp; with a regular space
SELECT @StringOut = REPLACE(@StringOut, '/', ' ');
-- remove duplicate spaces
WHILE CHARINDEX('  ', @StringOut) >0  
BEGIN
	SELECT @StringOut = REPLACE(@StringOut, '  ', ' ');
END

--Remove invisible Unicode characters - RM added 2026Feb15
SELECT @StringOut = REPLACE(@StringOut, NCHAR(0x200B), ''); -- Remove zero-width spaces
SELECT @StringOut = REPLACE(@StringOut, NCHAR(0x00AD), ''); -- soft hyphen
SELECT @StringOut = REPLACE(@StringOut, NCHAR(0xFEFF), ''); -- zero-width no-break space

SELECT @StringOut = REPLACE(@StringOut, ',', '');
SELECT @StringOut = TRIM(LEADING '+' FROM @StringOut);
SELECT @StringOut = TRIM(LEADING '?' FROM @StringOut);
SELECT @StringOut = REPLACE(@StringOut, '#', '');
SELECT @StringOut = REPLACE(@StringOut, ' NOS', '');
SELECT @StringOut = REPLACE(@StringOut, ' (NOS)', '');
SELECT @StringOut = REPLACE(@StringOut, ' type', '');

-- Roman numeral grades to number (case-sensitive)
SELECT @StringOut = REPLACE(@StringOut, ' grade III', ' grade 3') WHERE @StringOut LIKE '% grade III';
SELECT @StringOut = REPLACE(@StringOut, ' grade II', ' grade 2') WHERE @StringOut LIKE '% grade II';
SELECT @StringOut = REPLACE(@StringOut, ' grade I', ' grade 1') WHERE @StringOut LIKE '% grade I';
-- Roman numeral types to number (case-sensitive)
SELECT @StringOut = REPLACE(@StringOut, ' type III', ' type 3') WHERE @StringOut LIKE '% type III';
SELECT @StringOut = REPLACE(@StringOut, ' type II', ' type 2') WHERE @StringOut LIKE '% grade II';
SELECT @StringOut = REPLACE(@StringOut, ' type I', ' type 1') WHERE @StringOut LIKE '% grade I';



-->>>>Also there are types like RAEB I/II and CMML I/II, but there may be others that are best handled manually.

SELECT @StringOut = REPLACE(@StringOut, '-', ' '); -- hyphen
SELECT @StringOut = REPLACE(@StringOut, '–', ' '); -- em dash
SELECT @StringOut = REPLACE(@StringOut, '—', ' '); -- long em dash

--Remove spaces for terms like "non-abc" vs "non abc" vs "nonabc", and adjust capitalization at start or middle of the term
SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'non ', 'non');
SELECT @StringOut = REPLACE(@StringOut COLLATE Latin1_General_CS_AS, 'Non ', 'Non');

--Fix common British spellings
-- Naevus to nevus (case-sensitive): many terms like this, and adjust capitalization at start or middle of the term
SELECT @StringOut = Replace(@StringOut COLLATE Latin1_General_CS_AS, 'Naev', 'Nev')
SELECT @StringOut = Replace(@StringOut COLLATE Latin1_General_CS_AS, 'naev', 'nev')
--ou--
SELECT @StringOut = REPLACE(@StringOut, 'tumour', 'tumor'); --  fix 'Tumour' or 'tumor'
SELECT @StringOut = REPLACE(@StringOut, 'colour', 'color'); --  fix 'Tumour' or 'tumor'
SELECT @StringOut = REPLACE(@StringOut, 'Grey', 'Gray');
SELECT @StringOut = REPLACE(@StringOut, 'grey', 'gray');
SELECT @StringOut = REPLACE(@StringOut, 'mould', 'mold'); --smouldering
--
SELECT @StringOut = REPLACE(@StringOut, 'of the ', 'of ');
--ae--
SELECT @StringOut = REPLACE(@StringOut, 'aem', 'em'); --like haematology; leukaemia
SELECT @StringOut = REPLACE(@StringOut, 'paed', 'ped'); --paediatric
SELECT @StringOut = REPLACE(@StringOut, 'Paed', 'Ped'); --Paediatric
SELECT @StringOut = REPLACE(@StringOut, 'paen', 'pen'); --cytoPAENia
SELECT @StringOut = REPLACE(@StringOut, 'phaeo', 'pheo'); --phAeochromocytoma
SELECT @StringOut = REPLACE(@StringOut, 'Phaeo', 'Pheo'); --phAeochromocytoma
SELECT @StringOut = REPLACE(@StringOut, 'melaen', 'melen'); -- melaena → melena
--tre--
SELECT @StringOut = REPLACE(@StringOut, 'goitre', 'goiter'); 
SELECT @StringOut = REPLACE(@StringOut, 'centre', 'center'); 
--oe--
SELECT @StringOut = REPLACE(@StringOut, 'oedema', 'edema'); 
SELECT @StringOut = REPLACE(@StringOut, 'oesophag', 'esophag');   -- oesophageal → esophageal
SELECT @StringOut = REPLACE(@StringOut, 'oedema', 'edema');       -- oedema → edema
SELECT @StringOut = REPLACE(@StringOut, 'coeli', 'celi');         -- coeliac → celiac
SELECT @StringOut = REPLACE(@StringOut, 'rhoea', 'rhea');         -- diarrhoea → diarrhea, gonorrhoea, amenorrhoea
SELECT @StringOut = REPLACE(@StringOut, 'oestr', 'estr');         -- oestrogen → estrogen
SELECT @StringOut = REPLACE(@StringOut, 'foet', 'fet');           -- foetal → fetal, foetus → fetus
---------------------------

SELECT @StringOut = REPLACE(@StringOut, '''s', ''); --remove 's (single quote [escaped as ''])
SELECT @StringOut = REPLACE(@StringOut, '’s', ''); --remove 's (real apostrophe [’])
SELECT @StringOut = SUBSTRING(@StringOut, 1, (CHARINDEX('(specify', @StringOut, 1)-1)	) WHERE CHARINDEX('(specify', @StringOut, 1) >0;

SELECT @StringOut = TRIM(@StringOut);

RETURN @StringOut;
END
GO


