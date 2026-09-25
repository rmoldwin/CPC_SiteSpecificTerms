import json

with open('/home/user/workspace/icdo32_execution/batches/cns_03.json') as f:
    batch = json.load(f)

# All terms in this batch are generic vascular tumor/malformation morphology
# descriptors. Their code ceilings are entirely CNS sites (C70x meninges,
# C71x brain, C72x spinal cord/other CNS). Literature shows these vascular
# entities (cavernomas, AVMs, capillary/infantile hemangiomas, venous
# malformations, etc.) are NOT restricted to a proper subset of CNS sites:
# cavernous malformations, AVMs, and capillary hemangiomas all occur throughout
# the CNS (brain, brainstem, spinal cord, meninges). The cutaneous/soft-tissue
# predominant variants (microvenular, papillary, spindle cell hemangioma,
# angiomatosis) are primarily non-CNS lesions with no published evidence
# restricting them to a proper subset of the CNS ceiling. Per the brief,
# generic multi-site vascular descriptors and terms covering essentially all
# valid sites -> "No". None qualify as site-specific within the CNS ceiling.

sources = {
    "9120/0": ("https://en.wikipedia.org/wiki/Microvenular_hemangioma",
               "Microvenular hemangioma / spindle cell hemangioma literature (Wikipedia; PubMed PMID 36206448)"),
    "9121/0": ("https://www.ncbi.nlm.nih.gov/books/NBK538144/",
               "StatPearls: Cerebral Cavernous Malformations"),
    "9122/0": ("https://www.ahajournals.org/doi/10.1161/strokeaha.117.017074",
               "Stroke: Cranial Cavernous Malformations (venous vascular malformations of brain and spinal cord)"),
    "9123/0": ("https://pubmed.ncbi.nlm.nih.gov/30285374/",
               "PubMed/StatPearls: Arteriovenous Malformations of the Central Nervous System"),
    "9131/0": ("https://pubmed.ncbi.nlm.nih.gov/15255254/",
               "PubMed PMID 15255254: Capillary hemangioma of the central nervous system"),
}

rationale_map = {
 "9120/0": "Generic hemangioma-variant descriptor; these vascular lesions are not restricted to a proper subset of the code's CNS ceiling sites, and the cutaneous/soft-tissue variants (microvenular, papillary, spindle cell) have no literature confining them to specific CNS locations.",
 "9121/0": "Cavernous malformation/cavernoma occurs throughout the CNS (cerebral hemispheres, brainstem, cerebellum, basal ganglia, and spinal cord/meninges), not confined to a proper subset of the ceiling sites.",
 "9122/0": "Venous hemangioma/malformation is a generic vascular descriptor occurring throughout CNS parenchyma and meninges, not restricted to a proper subset of the ceiling sites.",
 "9123/0": "Arteriovenous malformations occur throughout the CNS (cerebral cortex, brainstem, cerebellum, spinal cord and meninges); the syndromic/cutaneous/deep-seated qualifiers do not confine the entity to a proper subset of the CNS ceiling sites.",
 "9131/0": "Capillary/infantile/congenital hemangioma is a generic vascular lesion; within its CNS ceiling it is reported in both brain and spinal cord and is not restricted to a proper subset of the ceiling sites.",
}

results = []
for obj in batch:
    code = obj["code"]
    src, srcname = sources[code]
    results.append({
        "code": code,
        "term": obj["term"],
        "site_specific": "No",
        "site_subset_codes": [],
        "site_subset_labels": [],
        "rationale": rationale_map[code],
        "source": src,
        "source_name": srcname,
    })

assert len(results) == 45, len(results)

with open('/home/user/workspace/icdo32_execution/results/cns_03.json','w') as f:
    json.dump(results, f, indent=1)

print("count:", len(results))
from collections import Counter
print(Counter(r["site_specific"] for r in results))
