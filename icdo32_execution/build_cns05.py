import json

# Source URLs actually fetched this session
SRC_SEGA = "https://radiopaedia.org/articles/subependymal-giant-cell-astrocytoma?lang=us"
SRC_DIPG = "https://www.ncbi.nlm.nih.gov/sites/books/NBK560640/"
SRC_DMG = "https://en.wikipedia.org/wiki/Diffuse_midline_glioma"
SRC_PHGG = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9763979/"
SRC_CPT = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10552314/"
SRC_EPEND = "https://pmc.ncbi.nlm.nih.gov/articles/PMC10242666/"
SRC_MPE = "https://radiopaedia.org/articles/myxopapillary-ependymoma-1?lang=us"

LAB = {
 "C710":"Cerebrum","C711":"Frontal lobe","C712":"Temporal lobe","C713":"Parietal lobe",
 "C714":"Occipital lobe","C715":"Ventricle, NOS","C716":"Cerebellum, NOS","C717":"Brain stem",
 "C718":"Overlapping lesion of brain","C719":"Brain, NOS","C720":"Spinal cord","C721":"Cauda equina",
 "C729":"Nervous system, NOS",
}
def labels(codes): return [LAB[c] for c in codes]

# batch
with open("batches/cns_05.json") as f:
    batch = json.load(f)

# decisions keyed by (code, term)
D = {}

def yes(code, term, subset, rationale, src, src_name):
    D[(code,term)] = ("Yes", subset, rationale, src, src_name)
def no(code, term, rationale):
    D[(code,term)] = ("No", [], rationale, "", "")
def unc(code, term, rationale):
    D[(code,term)] = ("Uncertain", [], rationale, "", "")

# ---- 9384/1 (ceiling C710-C715) ----
unc("9384/1","Giant cell astrocytoma of retina",
    "This entity is retinal (an ocular/retinal astrocytic lesion), but the code's ceiling (C710-C715) contains only brain subsites and no retina/eye code, so no valid site subset can be expressed within the ceiling.")
unc("9384/1","Retinal astrocytic hamartoma",
    "A retinal lesion by definition, but the ceiling (C710-C715) has no retina/eye code, so no in-ceiling subset can be assigned.")
yes("9384/1","Subependymal giant cell astrocytoma",["C715"],
    "SEGA arises almost exclusively from the wall of the lateral ventricle near the foramen of Monro (intraventricular), a proper subset (ventricle, C715) of the C710-C715 ceiling.",
    SRC_SEGA,"Radiopaedia - Subependymal giant cell astrocytoma")

# ---- 9385/3 (ceiling C710-C721, 12 codes) ----
HEMISPHERE = ["C710","C711","C712","C713","C714"]
MIDLINE = ["C710","C717","C720"]

yes("9385/3","Diffuse hemispheric glioma, H3 G34-mutant",HEMISPHERE,
    "WHO 5th ed defines this as a CNS grade 4 astrocytoma arising in the cerebral hemispheres (mainly temporal/parietal lobes); restricted to hemispheric subsites, excluding ventricle, cerebellum, brainstem and spinal cord.",
    SRC_PHGG,"Pathologica - Paediatric-type diffuse HGG in 5th CNS WHO Classification")
yes("9385/3","Diffuse intrinsic pontine glioma, H3 K27M-mutant",["C717"],
    "DIPG by definition arises within the pons of the brainstem (C717), a proper subset of the brain/spinal ceiling.",
    SRC_DIPG,"StatPearls - Diffuse intrinsic pontine glioma")
yes("9385/3","Diffuse intrinsic pontine glioma, NOS",["C717"],
    "DIPG arises within the pons of the brainstem (C717) by definition, a proper subset of the ceiling.",
    SRC_DIPG,"StatPearls - Diffuse intrinsic pontine glioma")
# DMG variants -> midline (thalamus=C710 cerebrum, pons/brainstem=C717, spinal cord=C720)
DMG_RAT = "Diffuse midline gliomas arise in CNS midline structures (thalamus, pons/brainstem, spinal cord); mapped to cerebrum/thalamus (C710), brain stem (C717) and spinal cord (C720), a proper subset excluding the lateral lobes, ventricle, cerebellum and cauda equina."
for t in ["Diffuse midline glioma, EGFR-mutant",
          "Diffuse midline glioma, H3 K27-altered",
          "Diffuse midline glioma, H3 K27M-mutant",
          "Diffuse midline glioma, H3-wildtype with EZHIP overexpression",
          "Diffuse midline glioma, H3.1 or H3.2 K27\u2013mutant",
          "Diffuse midline glioma, H3.3 K27\u2013mutant",
          "Diffuse midline glioma, NOS"]:
    yes("9385/3",t,MIDLINE,DMG_RAT,SRC_DMG,"Wikipedia (WHO-based) - Diffuse midline glioma")

# Diffuse pediatric-type HGG variants -> occur both supratentorial AND brainstem/midline -> No
PHGG_RAT = "Diffuse paediatric-type high-grade glioma, H3-/IDH-wildtype (and its MYCN/RTK1/RTK2 methylation subtypes) occurs in both the supratentorial hemispheres and infratentorial/brainstem-midline sites, so it is not restricted to a proper subset of the ceiling."
for t in ["Diffuse pediatric-type high-grade glioma MYCN",
          "Diffuse pediatric-type high-grade glioma RTK1",
          "Diffuse pediatric-type high-grade glioma RTK2",
          "Diffuse pediatric-type high-grade glioma, H3-wildtype and IDH-wildtype"]:
    no("9385/3",t,PHGG_RAT)

# Infant-type hemispheric glioma variants -> hemispheric
IHG_RAT = "Infant-type hemispheric glioma arises in the cerebral hemispheres (supratentorial) by definition; restricted to hemispheric subsites, a proper subset excluding ventricle, cerebellum, brainstem and spinal cord."
for t in ["Infant-type hemispheric glioma",
          "Infant-type hemispheric glioma, ALK-altered",
          "Infant-type hemispheric glioma, MET-altered",
          "Infant-type hemispheric glioma, NTRK-altered",
          "Infant-type hemispheric glioma, ROS1-altered"]:
    yes("9385/3",t,HEMISPHERE,IHG_RAT,SRC_PHGG,"Pathologica - Paediatric-type diffuse HGG in 5th CNS WHO Classification")

# ---- 9390 choroid plexus tumors ----
CPT_RAT = "Choroid plexus tumors are intraventricular neoplasms of choroid plexus epithelium arising within the lateral/third/fourth ventricles; restricted to the ventricle (C715), a proper subset of the ceiling."
yes("9390/0","Choroid plexus papilloma, NOS",["C715"],CPT_RAT,SRC_CPT,"World J Oncol / PMC - Choroid plexus tumors spectrum")
yes("9390/1","Atypical choroid plexus papilloma",["C715"],CPT_RAT,SRC_CPT,"PMC - Choroid plexus tumors spectrum")
yes("9390/3","Choroid plexus carcinoma",["C715"],CPT_RAT,SRC_CPT,"PMC - Choroid plexus tumors spectrum")
yes("9390/3","Choroid plexus papilloma, anaplastic",["C715"],CPT_RAT,SRC_CPT,"PMC - Choroid plexus tumors spectrum")
yes("9390/3","Choroid plexus papilloma, malignant",["C715"],CPT_RAT,SRC_CPT,"PMC - Choroid plexus tumors spectrum")

# ---- 9391/3 ependymoma (broad ceiling incl female genital C569,C571-574,C577 + CNS) ----
# generic morphologic variants -> No
for t in ["Cellular ependymoma","Clear cell ependymoma","Ependymoma, NOS",
          "Epithelial ependymoma","Tanycytic ependymoma"]:
    no("9391/3",t,"Generic/morphologic ependymoma variant occurring throughout the neuraxis (and validated at extraneural sites in this code's ceiling); not restricted to a proper subset.")

PF = ["C716","C717"]
SPINAL = ["C720","C721"]
SUPRA = ["C710","C711","C712","C713","C714","C715"]

yes("9391/3","Ependymoma, posterior fossa",PF,
    "By name a posterior-fossa tumor (cerebellum/fourth-ventricle/brainstem region); mapped to cerebellum (C716) and brain stem (C717), a proper subset of the ceiling.",
    SRC_EPEND,"Front Pediatr / PMC - Classification and neuroimaging of ependymal tumors")
yes("9391/3","Posterior fossa ependymoma, NOS",PF,
    "Posterior-fossa ependymoma by name; mapped to cerebellum (C716) and brain stem (C717), a proper subset of the ceiling.",
    SRC_EPEND,"Front Pediatr / PMC - Classification and neuroimaging of ependymal tumors")
yes("9391/3","Ependymoma, spinal",SPINAL,
    "Spinal ependymoma arises from ependymal remnants of the spinal cord central canal; mapped to spinal cord (C720) and cauda equina (C721), a proper subset of the ceiling.",
    SRC_EPEND,"PMC - Classification and neuroimaging of ependymal tumors")
yes("9391/3","Spinal ependymoma, NOS",SPINAL,
    "Spinal ependymoma arises in the spinal cord; mapped to spinal cord (C720) and cauda equina (C721), a proper subset of the ceiling.",
    SRC_EPEND,"PMC - Classification and neuroimaging of ependymal tumors")
yes("9391/3","Ependymoma, supratentorial",SUPRA,
    "Supratentorial ependymoma is intra-/paraventricular or hemispheric above the tentorium; mapped to cerebral hemisphere lobes (C710-C714) and ventricle (C715), a proper subset excluding cerebellum, brainstem and spinal cord.",
    SRC_EPEND,"PMC - Classification and neuroimaging of ependymal tumors")
yes("9391/3","Supratentorial ependymoma, NOS",SUPRA,
    "Supratentorial ependymoma occupies the supratentorial compartment (hemispheres/lateral ventricle); mapped to C710-C715, a proper subset of the ceiling.",
    SRC_EPEND,"PMC - Classification and neuroimaging of ependymal tumors")
unc("9391/3","Sellar ependymoma",
    "\"Sellar ependymoma\" is not a standard WHO CNS site subtype; the sellar region has no dedicated C-code within this ceiling, so a valid in-ceiling subset cannot be assigned.")

# ---- 9392/3 (ceiling C710-715,C717-721) ----
unc("9392/3","Ependymoblastoma",
    "Ependymoblastoma is an obsolete embryonal-tumor term (now within ETMR); its historic supratentorial/periventricular association is not reliably mappable to a defined in-ceiling subset.")
no("9392/3","Ependymoma, anaplastic",
    "Anaplastic (grade 3) ependymoma occurs throughout the neuraxis (supratentorial, posterior fossa, spinal); not restricted to a proper subset.")

# ---- 9393/3 papillary ependymoma (ceiling C715,C717,C720,C721) ----
no("9393/3","Papillary ependymoma",
    "Papillary ependymoma is a morphologic pattern reported along ventricular walls and within the spinal cord (i.e., across its ceiling sites); not restricted to a proper subset.")

# ---- 9394/1 myxopapillary ependymoma (ceiling C717,C719,C720,C721,C729) ----
yes("9394/1","Myxopapillary ependymoma",["C720","C721"],
    "Myxopapillary ependymoma occurs almost exclusively in the filum terminale/conus medullaris/cauda equina of the lumbosacral spine; mapped to spinal cord (C720) and cauda equina (C721), a proper subset excluding brain stem/brain NOS/nervous system NOS.",
    SRC_MPE,"Radiopaedia - Myxopapillary ependymoma")

# ---- 9396/3 (ceiling C710-C715, supratentorial subsites) ----
no("9396/3","Ependymoma, RELA fusion positive",
    "ZFTA(RELA)-fusion ependymomas are supratentorial; the ceiling (C710-C715) is already entirely supratentorial, and these tumors occur across the cerebral hemispheres and lateral ventricle, so there is no proper subset within the ceiling.")
unc("9396/3","Posterior fossa group A (PFA) ependymoma",
    "PFA ependymoma is by definition a posterior-fossa (cerebellum/brainstem) tumor, but the provided ceiling (C710-C715) contains only supratentorial subsites; the tumor's true site is not represented in the ceiling, so no valid in-ceiling subset can be assigned.")

# ---- assemble in batch order ----
out = []
for item in batch:
    key = (item["code"], item["term"])
    ss, subset, rat, src, src_name = D[key]
    obj = {"code":item["code"],"term":item["term"],"site_specific":ss}
    if ss == "Yes":
        assert set(subset).issubset(set(item["ceiling_codes"])), f"subset violation {key}: {subset} not in {item['ceiling_codes']}"
        assert len(subset) < len(item["ceiling_codes"]), f"not proper subset {key}"
        obj["site_subset_codes"] = subset
        obj["site_subset_labels"] = labels(subset)
        obj["rationale"] = rat
        obj["source"] = src
        obj["source_name"] = src_name
    else:
        obj["site_subset_codes"] = []
        obj["site_subset_labels"] = []
        obj["rationale"] = rat
        obj["source"] = ""
        obj["source_name"] = ""
    out.append(obj)

assert len(out) == 45, len(out)
import os
os.makedirs("results", exist_ok=True)
with open("results/cns_05.json","w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)

from collections import Counter
c = Counter(o["site_specific"] for o in out)
srcs = set(o["source"] for o in out if o["source"])
print("counts", dict(c), "len", len(out))
print("unique source urls used:", len(srcs))
for s in sorted(srcs): print("  ", s)
