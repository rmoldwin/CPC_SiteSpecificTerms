# TASK: Identify ICD-O-3.2 site-specific terms — {SYSTEM} batch {BATCH_ID}

You are confirming whether specific ICD-O-3.2 (ICDO32) morphology TERMS are used at only a
SUBSET of the anatomic sites their code is validated for. This supports the NCI/SEER Cancer
PathCHART initiative.

## Background you must understand
- Each ICDO32 code (e.g. `8140/3`) carries many terms. All terms under a code share the same
  code-level site validity.
- The authoritative list of sites where a CODE is valid is the Cancer PathCHART SMVL. It has
  already been computed for you and is provided per candidate below as `ceiling_codes` (a list
  of C-codes). Treat this set as the absolute CEILING of allowed sites. NEVER expand beyond it.
- A TERM is "site-specific" ONLY IF the medical literature/guidelines establish that this
  particular named entity occurs/is-diagnosed at a PROPER SUBSET of the code's ceiling — strictly
  fewer sites than the code allows. A whole-organ-system subset still counts (e.g. a term used
  across the entire GI tract while its code is also valid at non-GI sites).
- Site-specific terms are RARE. Default assumption: a term is used across all of its code's valid
  sites and is therefore NOT site-specific. Only flag a term when solid published evidence shows
  it is anatomically restricted.
- Ignore ICD-O "suggested sites" and any parenthetical site hints — they are unreliable. Base the
  restriction only on substantive pathology literature/guidelines.

## Authoritative sources (priority order)
1. WHO Classification of Tumours, 5th ed (Blue Books) — the volume/chapter an entity is defined in
   tells you its organ home.
2. NCCN guidelines, UpToDate, College of American Pathologists.
3. Recent peer-reviewed pathology/oncology literature (PubMed, journal articles).
Every "Yes" decision MUST have a source URL you actually fetched and that states the restriction.

## Decision rule for each candidate term
- Determine the anatomic site(s) at which this specific term is defined/used in the literature.
- Intersect that with the code's `ceiling_codes`. The reported subset must be a subset of the ceiling.
- If literature-supported sites cover essentially all of the ceiling (not restricted, or restricted
  only to a broad grouping that still covers the whole ceiling) → `site_specific = "No"`.
- If literature clearly restricts the term to a proper subset → `site_specific = "Yes"` and list the
  specific subset using ONLY C-codes present in that code's `ceiling_codes` (never invent sites).
- If evidence is insufficient/ambiguous → `site_specific = "Uncertain"` with an explanation.
- Generic morphologic descriptors that occur at many sites (e.g. "Adenocarcinoma, NOS", "Signet ring
  cell carcinoma") are NOT site-specific → "No".

## Output format
Return a JSON array AND save it to the workspace path given in your batch instructions. One object
per candidate term, preserving code+term exactly:
```json
{
  "code": "8140/3",
  "term": "Paneth cell carcinoma",
  "site_specific": "Yes",
  "site_subset_codes": ["C160","C170","C180","C181"],
  "site_subset_labels": ["Stomach","Small intestine","Colon","Appendix"],
  "rationale": "1-2 sentences on the anatomic restriction and why.",
  "source": "https://exact-url-you-fetched",
  "source_name": "WHO Blue Book Digestive System 5th ed / NCCN / PubMed PMIDxxxx"
}
```
Rules:
- `site_subset_codes` MUST be a strict subset of the candidate's `ceiling_codes`. Never list a site
  the ceiling does not include.
- Cover EVERY candidate in your batch. Do not skip, sample, or summarize rows away.
- Only cite URLs you actually fetched and that support the claim. If you cannot confirm, use
  "Uncertain" — do not guess.
