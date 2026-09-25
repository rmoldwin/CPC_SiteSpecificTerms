import json, sys
sys.path.insert(0,'/home/user/workspace/icdo32_execution/scripts')
from ccode_map_gyn03 import lbl

batch = json.load(open('/home/user/workspace/icdo32_execution/batches/gyn_03.json'))
by_key = {(o['code'],o['term']):o for o in batch}

# FGT subset for 9110/3 ceiling (female genital tract, excluding peritoneum + urinary)
FGT_9110 = ["C529","C530","C531","C538","C539","C540","C541","C542","C543","C548","C549","C559","C569","C571","C572","C573","C574","C577"]
# FGT + placenta subset for 9100/3 ceiling (gestational: vulva/vagina/uterus/ovary/tube/ligaments/placenta)
FGT_9100 = ["C510","C511","C512","C518","C519","C529","C541","C549","C559","C569","C570","C571","C572","C573","C574","C577","C589"]
# Female genital subset for 9104/3 (uterine/ovary/FGT/placenta, exclude testis)
FGT_9104 = ["C540","C541","C542","C543","C548","C549","C559","C569","C578","C579","C589"]
TESTIS = ["C620","C621","C629"]
CTT_SITES = ["C620","C621","C629","C710","C711","C712","C713","C714","C716"]
ASKIN = ["C493"]  # connective tissue of thorax (chest wall)

def rec(code, term, ss, codes, rationale, source, sname):
    o = by_key[(code,term)]
    ceil = o['ceiling_codes']
    subset = codes if ss=="Yes" else []
    # validate subset
    if ss=="Yes":
        assert set(subset).issubset(set(ceil)) and len(subset)<len(ceil), f"bad subset {code} {term}: {set(subset)-set(ceil)}"
        assert len(subset)>0
    return {
        "code":code,"term":term,"site_specific":ss,
        "site_subset_codes":subset,
        "site_subset_labels": lbl(subset) if ss=="Yes" else [],
        "rationale":rationale,"source":source if ss=="Yes" else source,
        "source_name":sname
    }

R=[]
# --- Mesothelioma group: generic serosal, covers whole ceiling -> No ---
meso_src="https://www.ncbi.nlm.nih.gov/books/NBK563163/"
for code,term in [("9050/3","Mesothelioma, diffuse"),("9050/3","Mesothelioma, malignant"),
                  ("9052/3","Epithelioid mesothelioma, NOS"),("9052/3","Epithelioid mesothelioma, malignant"),
                  ("9053/3","Biphasic mesothelioma"),("9053/3","Mesothelioma, biphasic, NOS"),
                  ("9053/3","Mesothelioma, biphasic, malignant")]:
    R.append(rec(code,term,"No",[],
        "Generic/histologic descriptor of mesothelioma arising across all serosal-lined sites in the code ceiling (pleura, peritoneum, tunica vaginalis, ovarian/genital serosa); not restricted to a proper subset.",
        "https://www.who.int/","WHO"))

# --- 9071/3 yolk sac / germ cell group ---
# Embryonal carcinoma, infantile = testicular YST synonym
R.append(rec("9071/3","Embryonal carcinoma, infantile","Yes",TESTIS,
    "'Infantile embryonal carcinoma' is a historical synonym specifically for testicular yolk sac tumour of young children (under age 3), restricting it to the testis within the broad code ceiling.",
    "https://www.ncbi.nlm.nih.gov/books/NBK563163/","StatPearls (NCBI Bookshelf)"))
# Endodermal sinus tumor = multi-site YST synonym
R.append(rec("9071/3","Endodermal sinus tumor","No",[],
    "Synonym for yolk sac tumour, a germ cell tumour occurring in gonads (ovary, testis) and extragonadal midline sites; not restricted to a proper subset.",
    "https://www.ncbi.nlm.nih.gov/books/NBK563163/","StatPearls"))
R.append(rec("9071/3","Hepatoid yolk sac tumor","No",[],
    "Hepatoid pattern of yolk sac tumour reported in ovary and testis and other sites; a histologic variant, not site-restricted within the ceiling.",
    "https://pubmed.ncbi.nlm.nih.gov/7139531/","PubMed PMID7139531"))
# Orchioblastoma = testicular YST synonym
R.append(rec("9071/3","Orchioblastoma","Yes",TESTIS,
    "'Orchioblastoma' (orchi- = testis) is an established synonym exclusively for testicular yolk sac tumour, restricting it to the testis within the broad ceiling.",
    "https://www.ncbi.nlm.nih.gov/books/NBK13608/","BC Decker / Holland-Frei (NCBI)"))
R.append(rec("9071/3","Polyvesicular vitelline tumor","No",[],
    "Polyvesicular vitelline is a histologic pattern of yolk sac tumour reported in both ovary and testis; not restricted to a proper subset.",
    "https://gsconlinepress.com/journals/gscarr/content/yolk-sac-tumor-ovary-polyvesicular-vitelline-pattern-case-report-uncommon-tumor-and-brief","PubMed/GSC"))
# generic YST subtype synonyms -> No
for term in ["Postpubertal (type II) yolk sac tumor","Prepubertal (type I) yolk sac tumor",
             "Yolk sac tumor, NOS","Yolk sac tumor, postpubertal (type II)","Yolk sac tumor, postpubertal-type",
             "Yolk sac tumor, pre-pubertal type","Yolk sac tumor, prepubertal (type I)","Yolk sac tumor, prepubertal-type"]:
    R.append(rec("9071/3",term,"No",[],
        "Yolk sac tumour subtype descriptor; YST (including pre/post-pubertal types) occurs in ovary, testis and extragonadal sites, so the named entity is not restricted to a proper subset of the ceiling.",
        "https://www.ncbi.nlm.nih.gov/books/NBK563163/","StatPearls"))

# --- 9100/3 choriocarcinoma ---
R.append(rec("9100/3","Choriocarcinoma (non-gestational)","No",[],
    "Non-gestational choriocarcinoma is a germ cell tumour arising in gonads (ovary/testis) and extragonadal midline sites (mediastinum, pineal, retroperitoneum); multi-site, not a proper subset.",
    "https://www.ncbi.nlm.nih.gov/books/NBK470267/","StatPearls"))
R.append(rec("9100/3","Choriocarcinoma, NOS","No",[],
    "Generic term encompassing both gestational and non-gestational choriocarcinoma across gonadal, genital and extragonadal midline sites; not site-restricted.",
    "https://www.ncbi.nlm.nih.gov/books/NBK470267/","StatPearls"))
R.append(rec("9100/3","Chorioepithelioma","No",[],
    "Obsolete generic synonym for choriocarcinoma; applies to gestational and germ-cell forms across multiple sites, not a proper subset.",
    "https://www.ncbi.nlm.nih.gov/books/NBK470267/","StatPearls"))
R.append(rec("9100/3","Chorionepithelioma","No",[],
    "Obsolete generic synonym for choriocarcinoma; applies across gestational and germ-cell forms and multiple sites, not a proper subset.",
    "https://www.ncbi.nlm.nih.gov/books/NBK470267/","StatPearls"))
R.append(rec("9100/3","Gestational choriocarcinoma","Yes",FGT_9100,
    "Gestational choriocarcinoma arises from placental/trophoblastic tissue of the female genital tract (uterus predominantly, also ovary/tube/vagina from ovarian pregnancy or metastasis); it does not arise in testis, mediastinum or CNS, restricting it to the female genital/placental subset.",
    "https://www.ncbi.nlm.nih.gov/books/NBK470267/","StatPearls (GTD)"))
R.append(rec("9100/3","Non-gestational choriocarcinoma","No",[],
    "Non-gestational choriocarcinoma is a germ cell tumour of gonads and extragonadal midline structures in both sexes; multi-site, not a proper subset.",
    "https://www.ncbi.nlm.nih.gov/books/NBK470267/","StatPearls"))

# --- 9101/3 combined choriocarcinoma (mixed germ cell) -> No ---
for term in ["Choriocarcinoma combined with embryonal carcinoma","Choriocarcinoma combined with other germ cell elements",
             "Choriocarcinoma combined with teratoma","Mixed trophoblastic tumor"]:
    R.append(rec("9101/3",term,"No",[],
        "Choriocarcinoma admixed with other germ cell elements denotes a mixed germ cell tumour, which occurs in gonads (testis/ovary) and extragonadal midline sites; not restricted to a proper subset.",
        "https://www.ncbi.nlm.nih.gov/books/NBK470267/","StatPearls"))

# --- 9104/3 PSTT ---
R.append(rec("9104/3","Placental site trophoblastic tumor of testis","Yes",TESTIS,
    "The term explicitly designates the testicular form of PSTT; primary testicular PSTT is confined to the testis within the ceiling.",
    "https://www.mjpath.org.my/2015/v37n2/testicular-tumour.pdf","Malaysian J Pathology (testicular PSTT)"))
R.append(rec("9104/3","Placental site trophoblastic tumor, malignant","Yes",FGT_9104,
    "PSTT is a gestational trophoblastic neoplasm arising from the placental implantation site, nearly always in the uterine corpus/fundus (rarely other female genital sites); it does not arise in the testis, restricting it to the female genital/uterine subset.",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC6893905/","PMC (PSTT review)"))

# --- 9105/3 trophoblastic tumors ---
R.append(rec("9105/3","Cystic trophoblastic tumor","Yes",CTT_SITES,
    "Cystic trophoblastic tumour is described almost exclusively in testicular germ cell tumours (post-chemotherapy/retroperitoneal) and rarely in primary CNS germ cell tumours; it is a germ-cell-derived lesion not occurring at gynaecologic sites, restricting it to testis and CNS within the ceiling.",
    "https://pubmed.ncbi.nlm.nih.gov/15316321/","PubMed PMID15316321"))
R.append(rec("9105/3","Epithelioid trophoblastic tumor","No",[],
    "Epithelioid trophoblastic tumour is a trophoblastic neoplasm reported both as gestational disease of the uterus/cervix and, by analogy, in the testis; spanning female genital and testicular sites it is not confined to a single clean proper subset (marked conservatively).",
    "https://pure.johnshopkins.edu/en/publications/nonchoriocarcinomatous-trophoblastic-tumors-of-the-testis-the-wid-3","PubMed/Johns Hopkins"))
R.append(rec("9105/3","Trophoblastic tumor, epithelioid","No",[],
    "Synonym of epithelioid trophoblastic tumour; reported in both uterine/cervical (gestational) and testicular settings, so not confined to a single clean proper subset (marked conservatively).",
    "https://pure.johnshopkins.edu/en/publications/nonchoriocarcinomatous-trophoblastic-tumors-of-the-testis-the-wid-3","PubMed/Johns Hopkins"))

# --- 9110/3 mesonephric group ---
R.append(rec("9110/3","Adenocarcinoma of rete ovarii","Yes",["C569"],
    "Adenocarcinoma of the rete ovarii arises from the rete ovarii in the ovarian hilus, i.e. the ovary only, a strict subset of the broad code ceiling.",
    "https://www.medsci.cn/article/show_article.do?id=4cf1856930f4","WHO Female Genital Tumours (summary)"))
R.append(rec("9110/3","Adenocarcinoma, HPV-independent, mesonephric type","Yes",FGT_9110,
    "Mesonephric adenocarcinoma (HPV-independent) arises from Wolffian/mesonephric remnants of the female genital tract (cervix predominant, also vagina, uterine corpus, ovary, broad ligament, tube); it does not occur in the urinary tract sites of the ceiling.",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC8416001/","PMC (MNAC in FGT)"))
R.append(rec("9110/3","Mesonephric adenocarcinoma","Yes",FGT_9110,
    "Mesonephric adenocarcinoma arises from mesonephric (Wolffian) remnants confined to the female genital tract (cervix, vagina, uterine corpus, ovary, broad ligament, tube); not the urinary sites in the ceiling.",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC8416001/","PMC (MNAC in FGT)"))
R.append(rec("9110/3","Mesonephroma, NOS","No",[],
    "'Mesonephroma' is a historical/generic term applied broadly (including clear cell tumours of the kidney/urinary tract and female genital tract); not restricted to a proper subset.",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC8416001/","PMC"))
R.append(rec("9110/3","Mesonephroma, malignant","No",[],
    "'Malignant mesonephroma' is a historical/generic designation applied across female genital and urinary tract sites; not restricted to a proper subset.",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC8416001/","PMC"))
R.append(rec("9110/3","Wolffian duct carcinoma","Yes",FGT_9110,
    "Wolffian (mesonephric) duct carcinoma arises from Wolffian duct remnants of the female genital tract (cervix, vagina, uterine corpus, ovary, broad ligament, tube); not the urinary tract sites in the ceiling.",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC8416001/","PMC (MNAC in FGT)"))

# --- 9111/3 mesonephric-like ---
for term in ["Mesonephric-like adenocarcinoma","Mesonephric-like carcinoma"]:
    R.append(rec("9111/3",term,"No",[],
        "WHO 2020 mesonephric-like adenocarcinoma arises in the uterine corpus (endometrium) and ovary (rarely fallopian tube) - essentially the entire narrow code ceiling of corpus/uterus/ovary/tube; not a proper subset.",
        "https://pubmed.ncbi.nlm.nih.gov/35384888/","PubMed PMID35384888 / WHO 2020"))

# --- 9364/3 Ewing family ---
R.append(rec("9364/3","Adamantinoma-like Ewing sarcoma","No",[],
    "Adamantinoma-like Ewing sarcoma has a head-and-neck predilection but is also reported in long bones, extremities and thorax; it spans multiple bone/soft-tissue regions and is not confined to a single clean proper subset (marked conservatively).",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC9424385/","PMC (ALES head & neck)"))
R.append(rec("9364/3","Askin tumor","Yes",ASKIN,
    "Askin tumour is by definition the Ewing/PNET of the thoracopulmonary region, arising from the soft tissues of the chest wall; it is restricted to the thorax (connective/soft tissue of thorax) within the broad ceiling.",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC3266582/","PMC (Askin tumour, thoracopulmonary)"))

print("total:",len(R))
# order to match batch
order = [(o['code'],o['term']) for o in batch]
Rmap = {(r['code'],r['term']):r for r in R}
missing=[k for k in order if k not in Rmap]
extra=[k for k in Rmap if k not in set(order)]
print("missing:",missing)
print("extra:",extra)
final=[Rmap[k] for k in order]
assert len(final)==45
json.dump(final, open('/home/user/workspace/icdo32_execution/results/gyn_03.json','w'), indent=2)
ys=sum(1 for r in final if r['site_specific']=="Yes")
no=sum(1 for r in final if r['site_specific']=="No")
un=sum(1 for r in final if r['site_specific']=="Uncertain")
print("Yes",ys,"No",no,"Uncertain",un)
