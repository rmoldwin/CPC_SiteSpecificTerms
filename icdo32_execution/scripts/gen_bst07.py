import json

batch = json.load(open('/home/user/workspace/icdo32_execution/batches/bone_soft_tissue_07.json'))
ceil = {}
for o in batch:
    ceil.setdefault(o['code'], o['ceiling_codes'])

LAB = {
"C340":"Main bronchus","C341":"Upper lobe lung","C342":"Middle lobe lung","C343":"Lower lobe lung","C348":"Overlapping lung","C349":"Lung, NOS",
"C400":"Long bones of limb","C401":"Short bones of upper limb","C402":"Long bones of lower limb","C403":"Short bones of lower limb","C408":"Overlapping bones of limbs","C409":"Bone of limb, NOS",
"C410":"Bones of skull and face","C411":"Mandible","C412":"Vertebral column","C413":"Rib, sternum, clavicle","C414":"Pelvic bones, sacrum, coccyx","C418":"Overlapping bone","C419":"Bone, NOS",
"C421":"Bone marrow","C424":"Hematopoietic system",
"C440":"Skin of lip","C441":"Skin of eyelid","C442":"Skin of ear","C443":"Skin of face","C444":"Skin of scalp and neck","C445":"Skin of trunk","C446":"Skin of upper limb","C447":"Skin of lower limb","C448":"Overlapping skin","C449":"Skin, NOS",
"C470":"Peripheral nerves head/neck","C471":"Peripheral nerves upper limb","C472":"Peripheral nerves lower limb","C473":"Peripheral nerves thorax","C474":"Peripheral nerves abdomen","C475":"Peripheral nerves pelvis","C476":"Peripheral nerves trunk","C478":"Overlapping peripheral nerves","C479":"Autonomic nervous system, NOS",
"C480":"Retroperitoneum","C481":"Peritoneum","C482":"Specified peritoneum","C488":"Overlapping retroperitoneum and peritoneum",
"C490":"Connective/soft tissue head/neck","C491":"Connective/soft tissue upper limb","C492":"Connective/soft tissue lower limb","C493":"Connective/soft tissue thorax","C494":"Connective/soft tissue abdomen","C495":"Connective/soft tissue pelvis","C496":"Connective/soft tissue trunk","C498":"Overlapping connective/soft tissue","C499":"Connective/soft tissue, NOS",
"C500":"Nipple","C501":"Central breast","C502":"Upper-inner breast","C503":"Lower-inner breast","C504":"Upper-outer breast","C505":"Lower-outer breast","C506":"Axillary tail breast","C508":"Overlapping breast","C509":"Breast, NOS",
"C510":"Labium majus","C511":"Labium minus","C512":"Clitoris","C518":"Overlapping vulva","C519":"Vulva, NOS","C529":"Vagina",
"C630":"Epididymis","C631":"Spermatic cord","C637":"Scrotum",
"C700":"Cerebral meninges","C701":"Spinal meninges","C709":"Meninges, NOS",
"C710":"Cerebrum","C711":"Frontal lobe","C712":"Temporal lobe","C713":"Parietal lobe","C714":"Occipital lobe","C715":"Ventricle","C716":"Cerebellum","C717":"Brain stem","C718":"Overlapping brain","C719":"Brain, NOS",
"C720":"Spinal cord","C721":"Cauda equina","C722":"Olfactory nerve","C723":"Optic nerve","C724":"Acoustic nerve","C725":"Cranial nerve, NOS","C728":"Overlapping CNS","C729":"Nervous system, NOS",
"C020":"Anterior tongue","C021":"Border of tongue","C022":"Ventral tongue","C023":"Posterior tongue","C028":"Overlapping tongue","C029":"Tongue, NOS",
"C040":"Anterior floor of mouth","C041":"Lateral floor of mouth","C048":"Overlapping floor of mouth","C049":"Floor of mouth, NOS",
"C050":"Hard palate","C058":"Overlapping palate","C059":"Palate, NOS",
"C060":"Cheek mucosa","C061":"Vestibule of mouth","C062":"Retromolar area","C068":"Overlapping mouth","C069":"Mouth, NOS",
}
def labs(codes):
    return [LAB.get(c, c) for c in codes]

def subset(code, keep):
    cc = ceil[code]
    return [c for c in cc if c in keep]
def exclude(code, drop):
    cc = ceil[code]
    return [c for c in cc if c not in drop]

# CNS parenchyma codes
CNS = {"C700","C701","C709","C710","C711","C712","C713","C714","C715","C716","C717","C718","C719","C720","C721","C722","C723","C724","C725","C728","C729"}

results = []
def add(code, term, ss, subset_codes=None, rat="", src="", srcname=""):
    o = {"code":code,"term":term,"site_specific":ss}
    if ss=="Yes":
        o["site_subset_codes"]=subset_codes
        o["site_subset_labels"]=labs(subset_codes)
    else:
        o["site_subset_codes"]=[]
        o["site_subset_labels"]=[]
    o["rationale"]=rat
    o["source"]=src
    o["source_name"]=srcname
    results.append(o)

# ---- 9368/3 BCOR family ----
# bone + soft tissue + retroperitoneum/peritoneum + marrow, excluding CNS (C70-C72)
bcor_bone_st = exclude("9368/3", CNS)  # keeps bone, C421/C424, C48, C49
SFA_BCOR = "https://curesarcoma.org/sarcoma-subtypes/sarcoma-with-bcor-genetic-alterations/"
CUREUS_BCOR = "https://pmc.ncbi.nlm.nih.gov/articles/PMC12417219/"
# soft-tissue-only subset for infantile / PMMTI (soft tissue + retroperitoneum, exclude bone & CNS)
st_only = [c for c in ceil["9368/3"] if c.startswith("C49") or c in ("C480","C481","C482","C488")]

add("9368/3","BCOR-rearranged sarcoma","Yes",bcor_bone_st,
    "BCOR-rearranged sarcoma is an undifferentiated round cell sarcoma arising in bone and soft tissue (pelvis, extremities, paraspinal, rarely kidney/lung); it does not arise as a primary CNS/meningeal tumor, so it is restricted to the bone/soft-tissue portion of the ceiling, excluding the meninges/brain/spinal-cord codes (C70-C72).",
    SFA_BCOR,"Sarcoma Foundation of America (WHO 5th ed. Soft Tissue & Bone)")
add("9368/3","BCOR::CCNB3 sarcoma","Yes",bcor_bone_st,
    "BCOR::CCNB3 sarcoma arises predominantly in bone and secondarily in soft tissue (pelvis, lower extremity, paraspinal region); it is not a primary CNS tumor, restricting it to the bone/soft-tissue portion of the ceiling and excluding CNS codes C70-C72.",
    CUREUS_BCOR,"Cureus 2025 (PMC12417219), citing WHO 5th ed.")
add("9368/3","Primitive myxoid mesenchymal tumor of infancy","Yes",st_only,
    "Primitive myxoid mesenchymal tumor of infancy arises mainly in the deep somatic soft tissues of the trunk, head/neck, extremities and rarely retroperitoneum; it is a soft-tissue neoplasm and is restricted to the soft-tissue/retroperitoneal portion of the ceiling.",
    SFA_BCOR,"Sarcoma Foundation of America (WHO 5th ed. Soft Tissue & Bone)")
add("9368/3","Round cell sarcoma, infantile undifferentiated","Yes",st_only,
    "Infantile undifferentiated round cell sarcoma (BCOR-ITD) arises mainly in the soft tissues of the trunk, retroperitoneum and head/neck, typically sparing bone and CNS; restricted to the soft-tissue/retroperitoneal portion of the ceiling.",
    SFA_BCOR,"Sarcoma Foundation of America (WHO 5th ed. Soft Tissue & Bone)")
add("9368/3","Sarcoma with BCOR genetic alterations","Yes",bcor_bone_st,
    "Sarcomas with BCOR genetic alterations arise in bone and soft tissue (and rarely kidney); they are not primary CNS tumors, restricting them to the bone/soft-tissue portion of the ceiling and excluding CNS codes C70-C72.",
    SFA_BCOR,"Sarcoma Foundation of America (WHO 5th ed. Soft Tissue & Bone)")

# ---- 9370/3, 9371/3, 9372/3 Chordoma family ----
# axial skeleton bone only: skull/face (C410), vertebral column (C412), pelvis/sacrum/coccyx (C414); plus bone NOS (C419), overlapping bone (C418)
chordoma_sub = [c for c in ceil["9370/3"] if c in ("C410","C412","C414","C418","C419")]
CHORD_SRC = "https://pmc.ncbi.nlm.nih.gov/articles/PMC9479632/"
CHORD_NAME = "J Clin Imaging Sci 2022 (PMC9479632) / WHO 5th ed. Soft Tissue & Bone"
add("9370/3","Chordoma, NOS","Yes",chordoma_sub,
    "Chordoma arises from notochordal remnants restricted to the axial skeleton (skull base/clivus, mobile spine vertebrae, sacrococcyx); it does not arise in limb bones, adrenal (C74) or endocrine glands (C75), so it is restricted to the axial bone subset of the ceiling.",
    CHORD_SRC,CHORD_NAME)
add("9370/3","Conventional chordoma","Yes",chordoma_sub,
    "Conventional chordoma arises from notochordal remnants of the axial skeleton (skull base, vertebral column, sacrum); restricted to axial bone, excluding limb bones, adrenal and other endocrine sites in the ceiling.",
    CHORD_SRC,CHORD_NAME)
# poorly differentiated chordoma: skull base / clivus predominant, axial
pdc_src = "https://pubmed.ncbi.nlm.nih.gov/29483606/?dopt=Abstract"
add("9370/3","Poorly differentiated chordoma","Yes",chordoma_sub,
    "Poorly differentiated chordoma is a SMARCB1-deficient axial-skeleton chordoma arising predominantly in the skull base/clivus and cervical spine, occasionally sacrum; restricted to the axial bone subset of the ceiling.",
    pdc_src,"Am J Surg Pathol / PubMed 29483606 (WHO 5th ed.)")
add("9371/3","Chondroid chordoma","Yes",chordoma_sub,
    "Chondroid chordoma is a chordoma subtype of the axial skeleton, classically the skull base/clivus; restricted to the axial bone subset of the ceiling, excluding limb bones, adrenal and endocrine sites.",
    CHORD_SRC,CHORD_NAME)
add("9372/3","Dedifferentiated chordoma","Yes",chordoma_sub,
    "Dedifferentiated chordoma is a high-grade axial-skeleton chordoma (skull base, spine, sacrum); restricted to the axial bone subset of the ceiling, excluding limb bones, adrenal and endocrine sites.",
    CHORD_SRC,CHORD_NAME)

# ---- 9490/3 Ganglioneuroblastoma ----
cns_9490 = subset("9490/3", CNS)  # CNS codes present
periph_9490 = exclude("9490/3", CNS)  # peripheral sympathetic sites
NCI_NB = "https://www.cancer.gov/types/neuroblastoma/hp/neuroblastoma-treatment-pdq"
RAD_NB = "https://radiopaedia.org/articles/neuroblastoma?lang=us"
UPMC_GNB = "https://path.upmc.edu/divisions/neuropath/bpath/cases/case148/dx.html"
add("9490/3","CNS ganglioneuroblastoma","Yes",cns_9490,
    "CNS ganglioneuroblastoma is a central nervous system embryonal/neuronal tumor arising in the brain and spinal cord, distinct from peripheral (sympathetic) ganglioneuroblastoma; restricted to the CNS parenchyma codes of the ceiling.",
    UPMC_GNB,"UPMC Neuropathology case (central vs peripheral neuroblastic tumors)")
periph_rat = ("Peripheral ganglioneuroblastoma is a tumor of the sympathetic nervous system arising in the adrenal medulla and paraspinal/paravertebral sympathetic ganglia, mediastinum, retroperitoneum and neck; it is an extracranial tumor and does not arise in the CNS parenchyma, so it is restricted to the peripheral (non-CNS) portion of the ceiling.")
add("9490/3","Ganglioneuroblastoma","Yes",periph_9490,periph_rat,UPMC_GNB,"UPMC Neuropathology case / peripheral neuroblastic tumors")
add("9490/3","Ganglioneuroblastoma, intermixed","Yes",periph_9490,periph_rat,UPMC_GNB,"UPMC Neuropathology case / peripheral neuroblastic tumors")
add("9490/3","Ganglioneuroblastoma, nodular","Yes",periph_9490,periph_rat,UPMC_GNB,"UPMC Neuropathology case / peripheral neuroblastic tumors")
add("9490/3","Schwannian stroma-rich intermixed tumor","Yes",periph_9490,
    "Schwannian stroma-rich (intermixed) tumor is a synonym for intermixed ganglioneuroblastoma, a peripheral neuroblastic tumor of the sympathetic nervous system (adrenal medulla, paraspinal ganglia, mediastinum, retroperitoneum); restricted to the peripheral (non-CNS) portion of the ceiling.",
    UPMC_GNB,"UPMC Neuropathology case / peripheral neuroblastic tumors")

# ---- 9500/3 Neuroblastoma ----
cns_9500 = subset("9500/3", CNS)
periph_9500 = exclude("9500/3", CNS)
RAD_CNSNB = "https://radiopaedia.org/articles/cns-neuroblastoma-foxr2-activated-1"
cns_nb_rat = ("This is a central nervous system embryonal tumor entity (WHO CNS classification) arising intracranially (supratentorial brain); distinct from peripheral neuroblastoma, it is restricted to the CNS parenchyma codes of the ceiling.")
add("9500/3","CNS neuroblastoma, FOXR2-activated","Yes",cns_9500,
    "CNS neuroblastoma, FOXR2-activated is a supratentorial brain (CNS) embryonal tumor in the WHO CNS classification; restricted to the CNS parenchyma codes of the ceiling.",
    RAD_CNSNB,"Radiopaedia / WHO CNS5 classification")
add("9500/3","CNS neuroblastoma, NOS","Yes",cns_9500,cns_nb_rat,RAD_CNSNB,"Radiopaedia / WHO CNS5 classification")
add("9500/3","CNS tumor with BCCR internal tandem duplication","Yes",cns_9500,
    "This CNS tumor with BCOR internal tandem duplication (CNS HGNET-BCOR) is a central nervous system neuroepithelial tumor arising in the brain; restricted to the CNS parenchyma codes of the ceiling.",
    RAD_CNSNB,"Radiopaedia / WHO CNS5 classification")
add("9500/3","CNS tumor with BCOR internal tandem duplication","Yes",cns_9500,
    "CNS high-grade neuroepithelial tumor with BCOR internal tandem duplication is a central nervous system tumor arising in the brain; restricted to the CNS parenchyma codes of the ceiling.",
    RAD_CNSNB,"Radiopaedia / WHO CNS5 classification")
add("9500/3","Central neuroblastoma","Yes",cns_9500,
    "Central (CNS) neuroblastoma is a primary brain embryonal tumor, distinct from peripheral neuroblastoma; restricted to the CNS parenchyma codes of the ceiling.",
    RAD_CNSNB,"Radiopaedia / WHO CNS5 classification")
periph_nb_rat = ("Neuroblastoma is a tumor of the sympathetic nervous system arising from the adrenal medulla and sympathetic chain (extracranial); it is the most common extracranial solid childhood tumor and does not arise in the CNS parenchyma, so it is restricted to the peripheral (non-CNS) portion of the ceiling.")
for term in ["Differentiating neuroblastoma","Neuroblastoma, NOS","Neuroblastoma, differentiating","Neuroblastoma, poorly differentiated","Neuroblastoma, undifferentiated","Poorly differentiated neuroblastoma","Sympathicoblastoma","Undifferentiated neuroblastoma"]:
    add("9500/3",term,"Yes",periph_9500,periph_nb_rat,RAD_NB,"Radiopaedia neuroblastoma / NCI PDQ")

# ---- 9561/3 MPNST with rhabdomyoblastic differentiation (Triton tumor) ----
MTT_SRC = "https://pmc.ncbi.nlm.nih.gov/articles/PMC3693303/"
mtt_rat = ("Malignant Triton tumor (MPNST with rhabdomyoblastic differentiation) arises along peripheral nerves in the head/neck, extremities, trunk, retroperitoneum and mediastinum, i.e. across the skin/soft-tissue/peripheral-nerve sites that make up essentially the whole ceiling; no literature-supported restriction to a proper subset was found.")
for term in ["MPNST with rhabdomyoblastic differentiation","Malignant Schwannoma with rhabdomyoblastic differentiation","Malignant peripheral nerve sheath tumor with rhabdomyoblastic differentiation","Triton tumor, malignant"]:
    add("9561/3",term,"No",None,mtt_rat,MTT_SRC,"Indian J Surg 2012 (PMC3693303)")

# ---- 9571/3 Malignant perineurioma ----
PER_SRC = "https://oap-onlinejournals.org/clinical-and-diagnostic-pathology/article/the-neoplastic-whorls-soft-tissue-perineurioma-1339"
per_rat = ("Malignant perineurioma (perineurial MPNST) arises from peripheral nerves and extraneural soft tissue across body regions; the code ceiling is already confined to peripheral-nerve and peritoneal soft-tissue codes and no literature clearly restricts it to a proper subset of those.")
for term in ["Malignant perineurioma","Perineurial MPNST","Perineurioma, malignant"]:
    add("9571/3",term,"No",None,per_rat,PER_SRC,"Open Access Pub, Clin Diagn Pathol 2020")

# ---- 9580/3 Malignant granular cell tumor ----
GCT_SRC = "https://academic.oup.com/ajcp/article/148/2/161/3976046"
gct_rat = ("Malignant granular cell tumor occurs at many anatomic sites, including the tongue/oral cavity, skin, soft tissue, breast, respiratory and reproductive tracts and peripheral nerves, spanning essentially all sites in the ceiling; it is a generic multi-site entity, not anatomically restricted.")
for term in ["Granular cell myoblastoma, malignant","Granular cell tumor, malignant"]:
    add("9580/3",term,"No",None,gct_rat,GCT_SRC,"Am J Clin Pathol 2017 (typical/atypical GCT of soft tissue)")

# ---- 9731/3 Plasmacytoma (ceiling is all bone) ----
PLAS_SRC = "https://emedicine.medscape.com/article/207233-overview"
plas_rat = ("The 9731/3 code ceiling comprises only bone topography codes. Solitary bone plasmacytoma occurs across the bony skeleton (most often vertebrae, but also ribs, skull and other bones); within an all-bone ceiling there is no literature-supported restriction to a proper subset.")
for term in ["Plasma cell tumor","Plasmacytoma of bone","Plasmacytoma, NOS","Solitary myeloma","Solitary plasmacytoma","Solitary plasmacytoma of bone"]:
    add("9731/3",term,"No",None,plas_rat,PLAS_SRC,"Medscape Solitary Plasmacytoma")

# ---- 9751/3 Langerhans cell histiocytosis (Histiocytosis X) ----
LCH_SRC = "https://pmc.ncbi.nlm.nih.gov/articles/PMC8891995/"
lch_rat = ("Langerhans cell histiocytosis (histiocytosis X) is a multisystem disorder affecting bone, skin, lung, lymph nodes and other sites, spanning essentially all systems in the ceiling; it is not restricted to a proper subset of sites.")
for term in ["Acute progressive histiocytosis X","Histiocytosis X, NOS"]:
    add("9751/3",term,"No",None,lch_rat,LCH_SRC,"Radiology Case Reports 2022 (PMC8891995)")

print("total", len(results))
json.dump(results, open('/home/user/workspace/icdo32_execution/results/bone_soft_tissue_07.json','w'), indent=1)
from collections import Counter
print(Counter(r['site_specific'] for r in results))
