import json

batch = json.load(open('/home/user/workspace/icdo32_execution/batches/cns_02.json'))

# Every decision in this CNS batch is "No":
#  - Generic CNS teratoma/GCT/hemangioma/cyst terms distribute broadly across the CNS ceiling
#    (pineal, suprasellar/pituitary, cerebral hemispheres/lobes, cerebellum, ventricles,
#     brainstem, spinal cord, meninges) -> not a proper subset -> No.
#  - Organ-named terms point to organs OUTSIDE the CNS ceiling (testis, lung, thymus, thyroid,
#    mediastinum, orbit/eye, bone, liver, spleen, placenta, skin, stomach). No valid ceiling
#    subset can be reported -> No.

RAD_GCT = "https://radiopaedia.org/articles/intracranial-germ-cell-tumours?lang=us"
SEER_BURNT = "https://seer.cancer.gov/seer-inquiry/inquiry-detail/20190029/"
RAD_EPI = "https://radiopaedia.org/articles/intracranial-epidermoid-cyst?lang=us"
RAD_DERM = "https://radiopaedia.org/articles/intracranial-dermoid-cyst-1?lang=us"

def entry(o, rationale, source="", source_name=""):
    return {
        "code": o["code"],
        "term": o["term"],
        "site_specific": "No",
        "site_subset_codes": [],
        "site_subset_labels": [],
        "rationale": rationale,
        "source": source,
        "source_name": source_name,
    }

# rationale text per term keyed by (code, term)
GEN_TER = ("Generic teratoma/germ-cell descriptor; intracranial teratomas/GCTs occur broadly "
           "across the CNS ceiling (pineal, suprasellar/pituitary region, cerebral hemispheres "
           "and lobes, ventricles, cerebellum, spinal cord), so the term is not restricted to a "
           "proper subset of its ceiling.")

results = []
for o in batch:
    code, term = o["code"], o["term"]
    key = (code, term)
    tl = term.lower()

    if code in ("9080/0", "9080/1") and ("teratoma" in tl or "germ cell" in tl) and \
       not any(x in tl for x in ["lung", "mediastinum", "orbit", "eye", "thymus", "thyroid",
                                 "burnt", "regressed"]):
        results.append(entry(o, GEN_TER, RAD_GCT, "Radiopaedia: Intracranial germ cell tumors"))
    elif code == "9080/1" and any(x in tl for x in ["lung", "mediastinum", "orbit", "eye",
                                                    "thymus", "thyroid"]):
        organ = "the named non-CNS organ (lung/mediastinum/thymus/thyroid/orbit)"
        results.append(entry(o,
            "This is an organ-of-origin synonym naming a non-CNS site "
            "(lung, mediastinum, thymus, thyroid, or orbit/eye) that is not among the code's CNS "
            "ceiling C-codes; no valid proper subset of the CNS ceiling can be reported.",
            "", ""))
    elif code == "9080/1" and ("burnt" in tl or "regressed" in tl):
        results.append(entry(o,
            "Burnt-out/regressed germ cell tumor (9080/1) is defined by WHO/SEER as a "
            "spontaneously regressed germ cell tumor of the TESTIS; the testis is not in this "
            "code's CNS ceiling, so no valid ceiling subset can be reported.",
            SEER_BURNT, "SEER Inquiry 20190029 / WHO Urinary & Male Genital Organs"))
    else:
        # 9084/0, 9102/3, 9120/0 handled below
        results.append(None)

# Second pass for 9084/0, 9102/3, 9120/0
for i, o in enumerate(batch):
    if results[i] is not None:
        continue
    code, term = o["code"], o["term"]
    tl = term.lower()

    if code == "9084/0":
        if "testicular" in tl or "testis" in tl:
            results[i] = entry(o,
                "Explicitly a testicular germ-cell/teratoma entity (prepubertal-type / "
                "postpubertal testicular teratoma / type I GCT of testis); the testis is not in "
                "the code's CNS ceiling, so no valid ceiling subset can be reported.")
        elif "epidermoid" in tl:
            results[i] = entry(o,
                "Intracranial epidermoid cysts occur across multiple CNS ceiling sites "
                "(cerebellopontine-angle region, parasellar, cerebral hemispheres/lobes, "
                "ventricle, spinal cord, meninges); not restricted to a proper subset of the "
                "ceiling.",
                RAD_EPI, "Radiopaedia: Intracranial epidermoid cyst")
        elif "dermoid" in tl:
            results[i] = entry(o,
                "Intracranial dermoid cysts, while midline-predilected, occur across CNS ceiling "
                "sites (suprasellar/parasellar, frontal, posterior fossa/cerebellum, spinal "
                "cord); the term is not restricted to a proper subset of its CNS ceiling.",
                RAD_DERM, "Radiopaedia: Intracranial dermoid cyst")
        else:  # generic prepubertal-type teratoma synonyms
            results[i] = entry(o,
                "Prepubertal-type teratoma is a germ-cell entity defined primarily for the "
                "testis/gonad; as a generic teratoma synonym under a CNS ceiling it is not "
                "supported as restricted to a proper subset of the CNS ceiling.",
                RAD_GCT, "Radiopaedia: Intracranial germ cell tumors")

    elif code == "9102/3":  # Malignant teratoma, trophoblastic
        results[i] = entry(o,
            "Generic malignant/trophoblastic teratoma descriptor; intracranial germ cell tumors "
            "with these elements occur broadly across brain ceiling sites (pineal, "
            "suprasellar region, cerebral hemispheres/lobes, cerebellum), so not restricted to a "
            "proper subset of the ceiling.",
            RAD_GCT, "Radiopaedia: Intracranial germ cell tumors")

    elif code == "9120/0":  # hemangioma family
        organ_named = any(x in tl for x in ["bone", "hepatic", "littoral", "chorioangioma",
                                            "cherry", "gastric antral", "dieulafoy",
                                            "glomeruloid", "hobnail", "acquired elastotic"])
        if "bone" in tl or "osteolysis" in tl or "gorham" in tl:
            results[i] = entry(o,
                "Names a bone/skeletal vascular entity (hemangioma of bone / massive osteolysis / "
                "Gorham-Stout); bone (C40/C41) is not in this code's CNS ceiling, so no valid "
                "ceiling subset can be reported.")
        elif "hepatic" in tl:
            results[i] = entry(o,
                "Hepatic vascular lesion; the liver (C22) is not in this code's CNS ceiling, so "
                "no valid ceiling subset can be reported.")
        elif "littoral" in tl:
            results[i] = entry(o,
                "Littoral cell angioma is a splenic vascular tumor; the spleen (C42.2) is not in "
                "this code's CNS ceiling, so no valid ceiling subset can be reported.")
        elif "chorioangioma" in tl:
            results[i] = entry(o,
                "Chorioangioma is a placental vascular tumor; the placenta (C58) is not in this "
                "code's CNS ceiling, so no valid ceiling subset can be reported.")
        elif "cherry" in tl:
            results[i] = entry(o,
                "Cherry hemangioma is a cutaneous vascular lesion; skin (C44) is not in this "
                "code's CNS ceiling, so no valid ceiling subset can be reported.")
        elif "gastric antral" in tl or "dieulafoy" in tl:
            results[i] = entry(o,
                "Gastrointestinal vascular lesion (gastric antral vascular ectasia / Dieulafoy "
                "lesion); the stomach/GI tract is not in this code's CNS ceiling, so no valid "
                "ceiling subset can be reported.")
        elif any(x in tl for x in ["anastomos", "hobnail", "glomeruloid", "acquired elastotic"]):
            results[i] = entry(o,
                "Named benign hemangioma variant that is not anatomically restricted within the "
                "CNS ceiling; described across cutaneous/soft-tissue/visceral sites rather than a "
                "specific proper subset of the CNS ceiling.")
        else:  # generic: angioma NOS, angiomatosis, hemangioma NOS, angiodysplasia, cystic angiomatosis, hepatic small vessel neoplasm
            results[i] = entry(o,
                "Generic benign vascular descriptor (angioma/hemangioma/angiomatosis/vascular "
                "malformation) that occurs at many sites and is not restricted to a proper subset "
                "of this code's CNS ceiling.")

# validate none left None and subset rule
assert all(r is not None for r in results), "unfilled entries"
ceil_by = {(o['code'], o['term']): set(o['ceiling_codes']) for o in batch}
for r in results:
    sub = set(r['site_subset_codes'])
    cc = ceil_by[(r['code'], r['term'])]
    assert sub <= cc, f"subset not in ceiling: {r['term']}"
    if r['site_specific'] == 'Yes':
        assert sub and sub < cc, f"Yes must be proper non-empty subset: {r['term']}"
        assert r['source'].startswith('http'), f"Yes needs source: {r['term']}"

assert len(results) == 45, len(results)
from collections import Counter
print(Counter(r['site_specific'] for r in results))
srcs = set(r['source'] for r in results if r['source'])
print("distinct source urls used:", len(srcs))
for s in srcs:
    print("  ", s)

json.dump(results, open('/home/user/workspace/icdo32_execution/results/cns_02.json', 'w'), indent=2)
print("WROTE results/cns_02.json  len", len(results))
