#!/usr/bin/env python3
"""Build a research subagent objective for one batch. References the staged
batch file (which holds each term's ceiling_codes) instead of inlining the
large code lists, keeping the objective compact.

Usage: python3 build_objective.py <system> <NN>
Prints the objective to stdout.
"""
import json, sys, os

WORKDIR = os.path.dirname(os.path.abspath(__file__))

def main():
    system = sys.argv[1]
    nn = sys.argv[2]
    batch_id = f"{system}_{nn}"
    batch_path = os.path.join(WORKDIR, "batches", f"{batch_id}.json")
    out_path = os.path.join(WORKDIR, "results", f"{batch_id}.json")

    with open(os.path.join(WORKDIR, "BRIEF_HEADER.txt")) as f:
        template = f.read()
    template = template.replace("{SYSTEM}", system).replace("{BATCH_ID}", batch_id)

    with open(batch_path) as f:
        terms = json.load(f)
    n = len(terms)

    objective = f"""{template}

---
## Your batch: {batch_id} ({n} candidate terms)

STEP 1 — Load your batch. The workspace cwd is:
  {WORKDIR}
Read your batch file with the `read` tool (or python):
  batches/{batch_id}.json
It is a JSON array of {n} objects, each with: `code`, `term`, `ceiling_count`, and
`ceiling_codes` (the absolute SMVL-valid site ceiling for that code). NEVER expand a
term's sites beyond its own `ceiling_codes`.

STEP 2 — Research each of the {n} candidates per the decision rule above. Use wide-search /
authoritative sources (WHO Blue Books 5th ed, NCCN, UpToDate, CAP, PubMed). Site-specific
terms are RARE — default to "No". Only "Yes" with a real fetched source URL proving the
term is restricted to a PROPER SUBSET of its ceiling. Unverifiable restriction → "Uncertain".
Broad multi-site morphologic descriptors (e.g. "Adenocarcinoma, NOS") → "No".
Ignore ill_defined (C76*) and unknown_primary (C80*) as a basis for restriction.

STEP 3 — Save results. Write a JSON array (one object per candidate, exact schema from the
template: code, term, site_specific, site_subset_codes, site_subset_labels, rationale,
source, source_name) with the `write` tool to EXACTLY:
  {out_path}
The array length MUST equal {n}. Cover EVERY candidate; do not skip or summarize any away.
`site_subset_codes` MUST be a strict subset of that term's `ceiling_codes`.

STEP 4 — Report back ONLY a one-line summary: Yes/No/Uncertain counts and number of source
URLs fetched. Do NOT paste the full array into your reply.
"""
    print(objective)

if __name__ == "__main__":
    main()
