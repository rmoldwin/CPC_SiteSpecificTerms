#!/usr/bin/env python3
"""
STEP 3 - Split the candidate universe into research batches for subagents.

Each batch is a self-contained JSON file a research subagent can consume.
Batching by ORGAN SYSTEM (code prefix) keeps each subagent focused on one
literature domain (better recall, fewer cross-domain mistakes) and lets you
run/refine one organ system at a time.

Input : candidates.jsonl (from step 2)
Output: batches/<system>_<nn>.json   list of {code, term, ceiling_count, ceiling_codes}
        batches_index.json           { file: n_terms, ... } + system mapping

Usage:
  python3 03_make_batches.py <candidates.jsonl> [batch_size=45] [outdir=.]
"""
import json, sys, os
from collections import defaultdict

# Topography prefix -> organ system bucket (for batching + focused research)
SYSTEM = {
    **{f"C0{n}": "head_neck" for n in range(0, 10)},
    "C10":"head_neck","C11":"head_neck","C12":"head_neck","C13":"head_neck","C14":"head_neck",
    "C15":"digestive","C16":"digestive","C17":"digestive","C18":"digestive","C19":"digestive",
    "C20":"digestive","C21":"digestive","C22":"digestive","C23":"digestive","C24":"digestive",
    "C25":"digestive","C26":"digestive",
    "C30":"respiratory","C31":"respiratory","C32":"respiratory","C33":"respiratory",
    "C34":"respiratory","C37":"respiratory","C38":"respiratory","C39":"respiratory",
    "C40":"bone_soft_tissue","C41":"bone_soft_tissue","C47":"bone_soft_tissue",
    "C48":"bone_soft_tissue","C49":"bone_soft_tissue",
    "C42":"heme","C77":"heme",
    "C44":"skin",
    "C50":"breast",
    "C51":"gyn","C52":"gyn","C53":"gyn","C54":"gyn","C55":"gyn","C56":"gyn","C57":"gyn","C58":"gyn",
    "C60":"male_genital","C61":"male_genital","C62":"male_genital","C63":"male_genital",
    "C64":"urinary","C65":"urinary","C66":"urinary","C67":"urinary","C68":"urinary",
    "C69":"eye",
    "C70":"cns","C71":"cns","C72":"cns",
    "C73":"endocrine","C74":"endocrine","C75":"endocrine",
    "C76":"ill_defined","C80":"unknown_primary",
}

def system_of(code):
    site_prefix = None
    return code  # placeholder; real mapping is by ceiling, see main()

def main():
    candfile = sys.argv[1] if len(sys.argv) > 1 else "candidates.jsonl"
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 45
    outdir = sys.argv[3].rstrip("/") if len(sys.argv) > 3 else "."
    bdir = f"{outdir}/batches"; os.makedirs(bdir, exist_ok=True)

    # Bucket each term by the organ system of the MAJORITY of its ceiling sites.
    buckets = defaultdict(list)
    with open(candfile) as f:
        for line in f:
            rec = json.loads(line)
            counts = defaultdict(int)
            for c in rec["ceiling_codes"]:
                counts[SYSTEM.get(c[:3], "other")] += 1
            # dominant system = most-represented; ties -> alphabetical for determinism
            sysname = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            buckets[sysname].append(rec)

    index = {}
    for sysname, recs in sorted(buckets.items()):
        recs.sort(key=lambda r: (r["code"], r["term"]))
        for i in range(0, len(recs), batch_size):
            chunk = recs[i:i+batch_size]
            fn = f"{bdir}/{sysname}_{i//batch_size+1:02d}.json"
            json.dump(chunk, open(fn, "w"), indent=1)
            index[os.path.relpath(fn, outdir)] = len(chunk)

    json.dump(index, open(f"{outdir}/batches_index.json", "w"), indent=2)
    total = sum(index.values())
    print(f"batches: {len(index)}  total terms: {total}")
    for k, v in sorted(index.items()):
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
