import json

d = json.load(open('batches/head_neck_08.json'))
cc = {o['code']: o['ceiling_codes'] for o in d}

LBL = {
 'C530':'Endocervix','C531':'Exocervix','C538':'Overlapping cervix','C539':'Cervix uteri NOS',
 'C540':'Isthmus uteri','C541':'Endometrium','C542':'Myometrium','C543':'Fundus uteri',
 'C548':'Overlapping corpus uteri','C549':'Corpus uteri NOS','C559':'Uterus NOS',
 'C529':'Vagina','C300':'Nasal cavity','C301':'Middle ear',
 'C310':'Maxillary sinus','C311':'Ethmoid sinus','C312':'Frontal sinus','C313':'Sphenoid sinus',
 'C318':'Overlapping accessory sinuses','C319':'Accessory sinus NOS',
 'C320':'Glottis','C321':'Supraglottis','C322':'Subglottis','C323':'Laryngeal cartilage',
 'C328':'Overlapping larynx','C329':'Larynx NOS','C339':'Trachea',
 'C110':'Superior wall nasopharynx','C111':'Posterior wall nasopharynx','C112':'Lateral wall nasopharynx',
 'C113':'Anterior wall nasopharynx','C118':'Overlapping nasopharynx','C119':'Nasopharynx NOS',
 'C670':'Trigone bladder','C671':'Dome bladder','C672':'Lateral wall bladder','C673':'Anterior wall bladder',
 'C674':'Posterior wall bladder','C675':'Bladder neck','C676':'Ureteric orifice','C677':'Urachus',
 'C678':'Overlapping bladder','C679':'Bladder NOS',
 'C410':'Bones of skull and face','C411':'Mandible','C414':'Pelvic bones/sacrum/coccyx',
 'C412':'Vertebral column','C413':'Rib/sternum/clavicle','C400':'Long bones upper limb',
 'C401':'Short bones upper limb','C402':'Long bones lower limb','C403':'Short bones lower limb',
 'C408':'Overlapping bones limb','C409':'Bone of limb NOS','C418':'Overlapping bone','C419':'Bone NOS',
}

def labels(codes):
    return [LBL.get(c, c) for c in codes]

# ---- precompute subsets ----
c8805 = cc['8805/3']
uterine_8805 = [x for x in c8805 if x in ('C530','C531','C538','C539','C542')]

# botryoid mucosal hollow-organ subset (8910)
c8910 = cc['8910/3']
muc_prefix = ('C00','C01','C02','C03','C04','C05','C06','C09','C10','C11','C13','C14',
              'C30','C31','C32','C33','C52','C53','C54','C55','C67')
botryoid_8910 = [x for x in c8910 if x[:3] in muc_prefix]

# TFCP2 under 8900: head/neck mucosal + salivary + sinonasal + larynx + trachea (+ HN soft tissue C491)
c8900 = cc['8900/3']
hn_prefix = ('C00','C01','C02','C03','C04','C05','C06','C07','C08','C09','C10','C11','C12','C13','C14',
             'C30','C31','C32','C33')
tfcp2_8900 = [x for x in c8900 if x[:3] in hn_prefix]

# intraosseous RMS under 8912: bone codes (craniofacial + pelvic + other bone)
c8912 = cc['8912/3']
bone_8912 = [x for x in c8912 if x.startswith('C40') or x.startswith('C41')]

results = []
for o in d:
    code = o['code']; term = o['term']
    ceil = o['ceiling_codes']
    entry = {"code": code, "term": term}

    tl = term.lower()

    if code == '8804/3':
        entry.update({
            "site_specific":"No","site_subset_codes":[],"site_subset_labels":[],
            "rationale":"Epithelioid sarcoma and its distal/proximal/large-cell/undifferentiated subtypes are soft-tissue/skin tumors; while the distal type favors distal limbs and the proximal type favors pelvic/perineal/axial regions, both variants occur across the skin, superficial/deep soft tissue and head-and-neck sites that make up the code ceiling, so the term is not confined to a definable proper C-code subset of this ceiling.",
            "source":"https://pmc.ncbi.nlm.nih.gov/articles/PMC2924131/",
            "source_name":"J Clin Aesthet Dermatol - Epithelioid Sarcoma: A Review and Update (PMC2924131)"})
    elif code == '8805/3' and 'uterine' in tl:
        entry.update({
            "site_specific":"Yes","site_subset_codes":uterine_8805,"site_subset_labels":labels(uterine_8805),
            "rationale":"Undifferentiated uterine sarcoma is defined in the WHO 5th ed Female Genital Tumours as a uterine (endometrial/myometrial) high-grade sarcoma of exclusion; within this code's ceiling the only uterine-region sites are the cervix and myometrium codes, so the term is restricted to those uterine sites and not the broad soft-tissue/head-neck ceiling.",
            "source":"https://www.iccr-cancer.org/wp-content/uploads/2023/11/ICCR-Uterine-sarcoma-1st-edn-v1-bookmark.pdf",
            "source_name":"ICCR Uterine Sarcoma dataset (WHO 5th ed Female Genital Tumours 2020)"})
    elif code == '8805/3':
        entry.update({
            "site_specific":"No","site_subset_codes":[],"site_subset_labels":[],
            "rationale":"Undifferentiated sarcoma (NOS) is a diagnosis-of-exclusion, high-grade soft-tissue sarcoma with no line of differentiation that arises at essentially any soft-tissue site; it is a broad morphologic descriptor and not anatomically restricted within the code ceiling.",
            "source":"https://pmc.ncbi.nlm.nih.gov/articles/PMC8167394/",
            "source_name":"Pathologica - The 2020 WHO Classification of Soft Tissue Tumours (PMC8167394)"})
    elif code == '8815/3':
        entry.update({
            "site_specific":"No","site_subset_codes":[],"site_subset_labels":[],
            "rationale":"Solitary fibrous tumor (including its malignant/dedifferentiated/anaplastic/grade-3 and legacy 'malignant hemangiopericytoma' designations) is a ubiquitous fibroblastic neoplasm reported across meninges, pleura, deep and superficial soft tissue, viscera and head-and-neck; these terms are grade/differentiation descriptors, not anatomically restricted subsets of the ceiling.",
            "source":"https://pmc.ncbi.nlm.nih.gov/articles/PMC8167394/",
            "source_name":"Pathologica - The 2020 WHO Classification of Soft Tissue Tumours (PMC8167394)"})
    elif code == '8900/3' and 'tfcp2' in tl:
        entry.update({
            "site_specific":"Yes","site_subset_codes":tfcp2_8900,"site_subset_labels":labels(tfcp2_8900),
            "rationale":"Rhabdomyosarcoma with TFCP2/FET-TFCP2 rearrangement has a striking predilection for the craniofacial skeleton (mandible, maxilla, skull); the rare extraosseous cases have been reported only in head-and-neck soft tissue and the oral cavity, so within this non-bone code ceiling the term is confined to head-and-neck mucosal/salivary/sinonasal/laryngeal sites rather than the many distant/genitourinary ceiling sites.",
            "source":"https://pmc.ncbi.nlm.nih.gov/articles/PMC8243398/",
            "source_name":"Histopathology - Head and Neck RMS Harboring TFCP2 Fusions (PMC8243398)"})
    elif code == '8900/3':
        entry.update({
            "site_specific":"No","site_subset_codes":[],"site_subset_labels":[],
            "rationale":"Rhabdomyosarcoma NOS (and the synonym rhabdosarcoma) is a generic skeletal-muscle sarcoma that can arise at essentially any body site; it is a broad morphologic descriptor and not anatomically restricted within the code ceiling.",
            "source":"https://www.cancer.gov/types/soft-tissue-sarcoma/hp/rhabdomyosarcoma-treatment-pdq",
            "source_name":"NCI PDQ Childhood Rhabdomyosarcoma Treatment"})
    elif code == '8910/3' and ('botryoid' in tl or 'botryoides' in tl):
        entry.update({
            "site_specific":"Yes","site_subset_codes":botryoid_8910,"site_subset_labels":labels(botryoid_8910),
            "rationale":"Botryoid-type embryonal rhabdomyosarcoma (sarcoma botryoides) by definition arises beneath the mucosal surface of hollow, epithelium-lined organs (nasal cavity/sinuses, nasopharynx, oral cavity/palate, larynx, and the genitourinary tract - vagina, cervix, uterus, bladder); it does not arise in skin, non-luminal soft tissue or bone, so it is confined to the mucosa-lined hollow-organ subset of the ceiling.",
            "source":"https://pmc.ncbi.nlm.nih.gov/articles/PMC12117734/",
            "source_name":"Am J Surg Pathol - Botryoid-Type Embryonal Rhabdomyosarcoma (PMC12117734)"})
    elif code == '8910/3':
        entry.update({
            "site_specific":"No","site_subset_codes":[],"site_subset_labels":[],
            "rationale":"Embryonal rhabdomyosarcoma (NOS and its anaplastic/pleomorphic/'embryonal type'/rhabdopoietic designations) arises broadly across head-and-neck, genitourinary, orbit, extremity, trunk and other soft-tissue sites; these are morphologic/grade descriptors, not anatomically restricted subsets of the ceiling.",
            "source":"https://pmc.ncbi.nlm.nih.gov/articles/PMC12117734/",
            "source_name":"Am J Surg Pathol - Botryoid-Type Embryonal Rhabdomyosarcoma (PMC12117734)"})
    elif code == '8912/3' and 'intraosseous' in tl:
        entry.update({
            "site_specific":"Yes","site_subset_codes":bone_8912,"site_subset_labels":labels(bone_8912),
            "rationale":"Intraosseous spindle cell rhabdomyosarcoma (with TFCP2/NCOA2 or MEIS1-NCOA2 rearrangements) is by definition a primary bone tumor with predilection for craniofacial (mandible/maxilla/skull) and pelvic bones; it is confined to the bone-site subset of the ceiling and excludes the soft-tissue/mucosal/skin ceiling sites.",
            "source":"https://www.nature.com/articles/s41379-019-0323-8",
            "source_name":"Modern Pathology - Epithelioid/spindle cell RMS with TFCP2 fusions (bone predilection)"})
    elif code == '8912/3':
        entry.update({
            "site_specific":"No","site_subset_codes":[],"site_subset_labels":[],
            "rationale":"Spindle cell/sclerosing rhabdomyosarcoma and its congenital/infantile (VGLL2/NCOA2/CITED2) and MYOD1-mutant soft-tissue variants arise across head-and-neck, paratesticular, extremity and trunk soft-tissue sites; these terms are not confined to a definable proper C-code subset of this ceiling.",
            "source":"https://curesarcoma.org/sarcoma-subtypes/spindle-cell-sclerosing-rhabdomyosarcoma/",
            "source_name":"Sarcoma Foundation of America - Spindle Cell/Sclerosing Rhabdomyosarcoma (WHO 5th ed)"})
    elif code == '8920/3':
        entry.update({
            "site_specific":"No","site_subset_codes":[],"site_subset_labels":[],
            "rationale":"Alveolar rhabdomyosarcoma (and its monomorphous round cell designation) arises across extremity, trunk, head-and-neck, perineal and other soft-tissue sites; it is a broad histologic subtype, not anatomically restricted within the code ceiling.",
            "source":"https://curesarcoma.org/sarcoma-subtypes/alveolar-rhabdomyosarcoma/",
            "source_name":"Sarcoma Foundation of America - Alveolar Rhabdomyosarcoma (WHO 5th ed)"})
    elif code == '8941/3':
        entry.update({
            "site_specific":"No","site_subset_codes":[],"site_subset_labels":[],
            "rationale":"Carcinoma ex pleomorphic adenoma (and its adenocarcinoma-ex / basal-cell-ex / carcinoma ex benign mixed tumor synonyms) arises in pleomorphic adenomas of major and minor salivary/seromucous glands, which are distributed throughout the oral cavity, palate, sinonasal tract, larynx, and lacrimal gland; it therefore occurs across essentially all sites in this salivary-type ceiling and is not restricted to a proper subset.",
            "source":"https://seer.cancer.gov/seer-inquiry/inquiry-detail/20140072/",
            "source_name":"SEER Inquiry 20140072 / WHO Classification of Head and Neck Tumours"})
    else:
        entry.update({"site_specific":"Uncertain","site_subset_codes":[],"site_subset_labels":[],
            "rationale":"No specific rule matched.","source":"","source_name":""})

    # safety: subset must be strict subset of ceiling
    ss = entry["site_subset_codes"]
    assert set(ss) <= set(ceil), (code, term, set(ss)-set(ceil))
    if ss:
        assert set(ss) != set(ceil), (code, term, "not proper subset")
    results.append(entry)

assert len(results) == 45, len(results)
import os
os.makedirs('results', exist_ok=True)
json.dump(results, open('results/head_neck_08.json','w'), indent=1)

from collections import Counter
cnt = Counter(r['site_specific'] for r in results)
print('counts:', dict(cnt))
print('total:', len(results))
