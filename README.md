# CPC_SiteSpecificTerms

Research files from Perplexity Computer for finding ICD-O-3.2 morphology terms that apply at only some of the anatomic sites where the Cancer PathCHART site–morphology validation list allows their code.

| Term | Meaning |
|---|---|
| ICD-O-3.2 | International Classification of Diseases for Oncology, third edition, revision 2 |
| CPC | Cancer PathCHART, the NCI/SEER project that publishes the site–morphology validation list |
| SMVL | Site–Morphology Validation List: which morphology codes are valid at which topography (site) codes |
| Site-specific term | A term used for only part of the set of sites where its code is valid |

## Layout

| Path | Contents |
|---|---|
| `START_HERE.md` | Kick-off note for a new research session (a copy of `icdo32_execution/START_HERE.md`) |
| `ICDO32_FullCatalog_Plan (1).md`, `ICDO32_HiddenSiteSpecific_Plan_v2.md`, `hidden_methodology_answers.md` | Plans and method answers |
| `ICDO32_SiteSpecific_Terms.csv`, `ICDO32_Site_Specific_Terms.xlsx` | Results |
| `master_terms.csv`, `dbo.Clean.sql`, `dbo.Clean_fixed.sql` | Term list and SQL Server term-cleaning function |
| `icdo32_execution/` | Unpacked from `icdo32_execution.zip`: full run, including batches, results, audits, scripts and `SKILL.md` |
| `icdo32_pipeline/` | Unpacked from `icdo32_pipeline.zip`: the reusable pipeline scripts and `SKILL.md` |

The two zip files are kept alongside their unpacked folders for now.

## Origin

Copied on 2026-09-24 from `CancerPathCHART\Terms\Perplexity Research`, where the original remains. Issues are tracked in [rmoldwin/AI_Organize](https://github.com/rmoldwin/AI_Organize) with the label `project:perplexity-research`.
