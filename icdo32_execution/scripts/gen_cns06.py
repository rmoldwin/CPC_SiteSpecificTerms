import json

LABELS = {
    "C710":"Cerebrum","C711":"Frontal lobe","C712":"Temporal lobe","C713":"Parietal lobe",
    "C714":"Occipital lobe","C715":"Ventricle, NOS","C716":"Cerebellum","C717":"Brain stem",
    "C718":"Overlapping lesion of brain","C719":"Brain, NOS","C720":"Spinal cord",
    "C721":"Cauda equina","C722":"Olfactory nerve","C723":"Optic nerve","C724":"Acoustic nerve",
    "C725":"Cranial nerve, NOS","C728":"Overlapping lesion of brain and CNS"
}

def labs(codes):
    return [LABELS[c] for c in codes]

batch = json.load(open('/home/user/workspace/icdo32_execution/batches/cns_06.json'))
ceil = {d['code']: d['ceiling_codes'] for d in batch}

# subset used for supratentorial+brainstem pediatric-type diffuse LGG under 9421/1
peds_subset = ["C710","C711","C712","C713","C714","C717"]
# PLNTY subset (supratentorial cerebral, excludes brain stem C717) within 9413/0 ceiling
plnty_subset = ["C710","C711","C712","C713","C714","C719"]

MYB_SRC = "https://pmc.ncbi.nlm.nih.gov/articles/PMC10619148/"
MYB_NAME = "Chen et al., Front Pediatr 2023 (WHO CNS5 pediatric-type diffuse LGG neuroimaging review) PMC10619148"
PLNTY_SRC = "https://pmc.ncbi.nlm.nih.gov/articles/PMC8921648/"
PLNTY_NAME = "Johnson et al., J Neuropathol Exp Neurol 2021 (PLNTY series) PMC8921648"

results = []

def add(idx, ss, subset=None, rationale="", source="", source_name=""):
    d = batch[idx]
    code = d['code']; term = d['term']
    obj = {"code":code,"term":term,"site_specific":ss}
    if ss == "Yes":
        assert set(subset).issubset(set(ceil[code])), (term, subset, ceil[code])
        assert set(subset) != set(ceil[code]), ("not proper subset", term)
        obj["site_subset_codes"] = subset
        obj["site_subset_labels"] = labs(subset)
    else:
        obj["site_subset_codes"] = []
        obj["site_subset_labels"] = []
    obj["rationale"] = rationale
    obj["source"] = source
    obj["source_name"] = source_name
    results.append(obj)

# --- 9396/3 ependymoma molecular subtypes; ceiling is supratentorial-only C710-C715 ---
add(0, "Uncertain", rationale="Posterior fossa group B ependymoma is defined by obligatory posterior-fossa (cerebellum/4th-ventricle) localization, but the posterior fossa (C716/C717) is not among this code's SMVL-valid sites (ceiling is supratentorial C710-C715), so no valid proper subset within the ceiling can be asserted.",
    source="https://pmc.ncbi.nlm.nih.gov/articles/PMC9245931/", source_name="Kresbach et al., Brain Pathol 2022 (Updates in classification of ependymal neoplasms) PMC9245931")
add(1, "Uncertain", rationale="Spinal ependymoma, MYCN-amplified is defined by obligatory spinal-cord localization, but the spinal cord (C720) is not among this code's SMVL-valid sites (ceiling is supratentorial C710-C715), so no valid proper subset within the ceiling can be asserted.",
    source="https://pmc.ncbi.nlm.nih.gov/articles/PMC9245931/", source_name="Kresbach et al., Brain Pathol 2022 (Updates in classification of ependymal neoplasms) PMC9245931")
add(2, "No", rationale="Supratentorial location is obligatory; supratentorial (cerebrum, lobes, lateral/3rd ventricle) corresponds to the code's entire supratentorial ceiling (C710-C715), so the term is not restricted to a proper subset of its ceiling.")
add(3, "No", rationale="Supratentorial location is obligatory; supratentorial (cerebrum, lobes, lateral/3rd ventricle) corresponds to the code's entire supratentorial ceiling (C710-C715), so the term is not restricted to a proper subset of its ceiling.")

# --- 9400/3 (indices 4-17): generic diffuse/adult astrocytoma terms, occur throughout CNS ---
for i in range(4, 18):
    add(i, "No", rationale="Generic diffuse astrocytic entity; astrocytoma (IDH-mutant/wildtype/NOS, grade 2, diffuse) can arise anywhere in the brain or spinal cord (frontal-lobe predilection is a preference, not a restriction), spanning essentially the full CNS ceiling.")

# --- 9401/3 (18-22): anaplastic/grade 3 astrocytoma; same reasoning ---
for i in range(18, 23):
    add(i, "No", rationale="Generic higher-grade diffuse astrocytic entity; anaplastic/grade 3 astrocytoma occurs throughout the CNS (cerebral hemispheres predominantly, also brainstem/cerebellum/spinal cord), not restricted to a proper subset of its ceiling.")

# --- 9411/3 (23-25): gemistocytic astrocytoma; ceiling is spinal/cranial-nerve only, generic within it ---
for i in range(23, 26):
    add(i, "No", rationale="Gemistocytic astrocytoma is a morphologic pattern of diffuse (IDH-mutant) astrocytoma, not an anatomically restricted entity; within this code's ceiling it is a generic descriptor and not confined to a proper subset.")

# --- 9412/1 (26-27): desmoplastic infantile astrocytoma / ganglioglioma; ceiling already all supratentorial ---
add(26, "No", rationale="Desmoplastic infantile astrocytoma invariably arises in the supratentorial compartment (cerebral cortex, most often frontal/parietal lobes); this equals the code's entirely supratentorial ceiling (C710-C714), so it is not restricted to a proper subset.")
add(27, "No", rationale="Desmoplastic infantile ganglioglioma invariably arises in the supratentorial cerebral hemispheres; this equals the code's entirely supratentorial ceiling (C710-C714), so it is not restricted to a proper subset.")

# --- 9413/0 (28-30): DNET / PLNTY ---
add(28, "No", rationale="DNET arises in the cerebral cortex with a temporal-lobe predilection but occurs across cerebral lobes and rarely in the brain stem/cerebellum; it spans the code's ceiling and is not confined to a proper subset.")
add(29, "Yes", subset=plnty_subset, rationale="PLNTY is reported as an exclusively supratentorial cortical/subcortical tumor (temporal lobe predominant); series show all cases supratentorial with no brain-stem (infratentorial) involvement, so it is restricted to the supratentorial cerebral subset of its ceiling (excludes brain stem C717).",
    source=PLNTY_SRC, source_name=PLNTY_NAME)
add(30, "Yes", subset=plnty_subset, rationale="PLNTY (polymorphous low-grade neuroepithelial tumor of the young) is an exclusively supratentorial cortical/subcortical tumor; published series report all cases supratentorial with no brain-stem involvement, restricting it to the supratentorial cerebral subset of its ceiling (excludes brain stem C717).",
    source=PLNTY_SRC, source_name=PLNTY_NAME)

# --- 9421/1 (31-43) ---
add(31, "Yes", subset=peds_subset, rationale="Diffuse astrocytoma, MYB-/MYBL1-altered primarily affects the cerebral hemispheres with less common brain-stem/diencephalic involvement; it is not reported in the cerebellum or spinal cord, restricting it to the cerebral + brain-stem subset of its ceiling.",
    source=MYB_SRC, source_name=MYB_NAME)
add(32, "Yes", subset=peds_subset, rationale="MYB-altered pediatric-type diffuse low-grade glioma occurs in the cerebral hemispheres (cortical/subcortical) and occasionally brain stem, without cerebellar or spinal-cord involvement, restricting it to the cerebral + brain-stem subset of its ceiling.",
    source=MYB_SRC, source_name=MYB_NAME)
add(33, "Yes", subset=peds_subset, rationale="MYBL1-altered pediatric-type diffuse low-grade glioma occurs in the cerebral hemispheres and occasionally brain stem, without cerebellar or spinal-cord involvement, restricting it to the cerebral + brain-stem subset of its ceiling.",
    source=MYB_SRC, source_name=MYB_NAME)
add(34, "Yes", subset=peds_subset, rationale="Diffuse low-grade glioma, BRAF p.V600E-mutant (MAPK pathway-altered pediatric-type diffuse LGG) is located in the cerebral cortical region and diencephalon/brain stem, without reported cerebellar or spinal-cord involvement, restricting it to the cerebral + brain-stem subset of its ceiling.",
    source=MYB_SRC, source_name=MYB_NAME)
add(35, "Yes", subset=peds_subset, rationale="FGFR1 tyrosine-kinase-domain-duplicated diffuse low-grade glioma (MAPK pathway-altered pediatric-type diffuse LGG) arises in the cerebral cortical region and diencephalon/brain stem, without reported cerebellar or spinal-cord involvement, restricting it to the cerebral + brain-stem subset of its ceiling.",
    source=MYB_SRC, source_name=MYB_NAME)
add(36, "Yes", subset=peds_subset, rationale="FGFR1-mutant diffuse low-grade glioma (MAPK pathway-altered pediatric-type diffuse LGG) arises in the cerebral cortical region and diencephalon/brain stem, without reported cerebellar or spinal-cord involvement, restricting it to the cerebral + brain-stem subset of its ceiling.",
    source=MYB_SRC, source_name=MYB_NAME)
add(37, "Yes", subset=peds_subset, rationale="Diffuse low-grade glioma, MAPK pathway-altered is a pediatric-type diffuse LGG located in the cerebral cortical region and diencephalon/brain stem; it is not reported in the cerebellum or spinal cord, restricting it to the cerebral + brain-stem subset of its ceiling.",
    source=MYB_SRC, source_name=MYB_NAME)
add(38, "No", rationale="Juvenile astrocytoma is a synonym for pilocytic astrocytoma, which arises throughout the neuraxis (cerebellum, optic pathway/cranial nerves, brain stem, cerebral hemispheres, spinal cord); it spans the code's ceiling and is not confined to a proper subset.")
add(39, "No", rationale="Pediatric-type oligodendroglioma, though usually hemispheric, is documented to also arise in the cerebellum, brain stem and spinal cord more often than adult forms; it spans the code's ceiling and is not confined to a proper subset.")
add(40, "No", rationale="Pilocytic astrocytoma can arise anywhere in the CNS (cerebellum ~42%, supratentorial, optic pathway/cranial nerves, brain stem, spinal cord); the cerebellar predominance is a preference, not a restriction, so it spans the ceiling.")
add(41, "No", rationale="Pilocytic astrocytoma with anaplasia is a grade variant of pilocytic astrocytoma; it occurs across the same broad neuraxial distribution and is not confined to a proper subset of the ceiling.")
add(42, "No", rationale="Piloid astrocytoma is a synonym/variant of pilocytic astrocytoma and shares its broad neuraxial distribution (cerebellum, optic/cranial nerves, brain stem, cerebrum, spinal cord); not confined to a proper subset.")
add(43, "No", rationale="Spongioblastoma, NOS is an obsolete, ambiguous historical term reported in the cerebral hemispheres, posterior fossa/cerebellum and upper spinal cord; it is not a well-defined anatomically restricted entity.")

# --- 9421/3 (44): HGAP ---
add(44, "No", rationale="High-grade astrocytoma with piloid features is preferentially located in the posterior fossa (cerebellum ~63%) but also occurs supratentorially (~17%) and in the spinal cord; the posterior-fossa preference is not a strict restriction, so it spans multiple compartments of its ceiling.")

assert len(results) == 45, len(results)
json.dump(results, open('/home/user/workspace/icdo32_execution/results/cns_06.json','w'), indent=2)

from collections import Counter
c = Counter(r['site_specific'] for r in results)
print("counts:", dict(c))
print("len:", len(results))
