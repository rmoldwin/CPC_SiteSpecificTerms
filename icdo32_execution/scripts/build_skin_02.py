import json, os

batch = json.load(open('/home/user/workspace/icdo32_execution/batches/skin_02.json'))

# Ceiling lookup by code
ceil = {}
for o in batch:
    ceil[o['code']] = o['ceiling_codes']

LAB = {
    'C000':'External upper lip','C001':'External lower lip','C002':'External lip NOS',
    'C003':'Mucosa upper lip','C004':'Mucosa lower lip','C005':'Mucosa lip NOS',
    'C006':'Commissure of lip','C008':'Overlapping lip','C009':'Lip NOS',
    'C301':'External auditory canal',
    'C440':'Skin of lip','C441':'Eyelid','C442':'External ear (skin)','C443':'Skin of other/face',
    'C444':'Skin of scalp and neck','C445':'Skin of trunk','C446':'Skin of upper limb/shoulder',
    'C447':'Skin of lower limb/hip','C448':'Overlapping skin','C449':'Skin NOS',
    'C500':'Nipple','C501':'Central breast','C502':'Upper-inner breast','C503':'Lower-inner breast',
    'C504':'Upper-outer breast','C505':'Lower-outer breast','C506':'Axillary tail breast',
    'C508':'Overlapping breast','C509':'Breast NOS',
    'C510':'Labium majus','C511':'Labium minus','C512':'Clitoris','C518':'Overlapping vulva','C519':'Vulva NOS',
    'C600':'Prepuce','C601':'Glans penis','C602':'Body of penis','C608':'Overlapping penis','C609':'Penis NOS',
    'C632':'Scrotum',
}

# Decision map keyed by (code, term)
Y='Yes'; N='No'; U='Uncertain'

def skin_subset(code):
    return [c for c in ceil[code] if c.startswith('C44')]

results = []
for o in batch:
    code=o['code']; term=o['term']; cc=o['ceiling_codes']
    ss=N; subset=[]; rat=''; src=''; sname=''

    # --- 8403/3 spiradenocarcinoma group: skin adnexal, any body site -> No
    if code=='8403/3':
        ss=N
        rat='Spiradenocarcinoma/malignant spiradenoma is a skin adnexal sweat-gland tumour that can arise at essentially any cutaneous site (head/neck/scalp, trunk, extremities), spanning the code\'s skin ceiling; not restricted to a proper subset.'
        src='https://pmc.ncbi.nlm.nih.gov/articles/PMC8151110/'
        sname='Cutaneous Adnexal Neoplasms review, Int J Mol Sci 2021 (PMC8151110)'

    # --- 8408/3 digital papillary group: classically acral but disputed/non-acral cases -> Uncertain
    elif code=='8408/3':
        ss=U
        rat='Classically defined as an acral (fingers/toes) eccrine tumour, but documented non-acral cases and published expert dispute over whether it is truly digit-restricted preclude a confident proper-subset assignment.'
        src='https://www.nature.com/articles/s41379-022-01094-8'
        sname='HPV42 and digital papillary adenocarcinoma incl. non-acral sites, Mod Pathol 2022'

    # --- 8409/3 porocarcinoma: eccrine glands everywhere -> No
    elif code=='8409/3':
        ss=N
        rat='Eccrine porocarcinoma arises from eccrine sweat-gland ducts distributed over essentially all skin (lower/upper limbs, trunk, head & neck, and vulva), covering the code ceiling; not a proper subset.'
        src='https://pmc.ncbi.nlm.nih.gov/articles/PMC10137440/'
        sname='Eccrine Porocarcinoma review, Diagnostics 2023 (PMC10137440)'

    # --- 8413/3 eccrine adenocarcinoma: widely distributed -> No
    elif code=='8413/3':
        ss=N
        rat='Eccrine adenocarcinoma derives from eccrine sweat glands, which are present throughout the skin and genital skin; the term is not anatomically restricted to a proper subset of the ceiling.'
        src='https://pmc.ncbi.nlm.nih.gov/articles/PMC3633551/'
        sname='Sweat-gland carcinomas review, OncoTargets Ther 2013 (PMC3633551)'

    # --- 8420/3 ceruminous carcinomas: external auditory canal ONLY -> Yes C301
    elif code=='8420/3':
        ss=Y
        subset=['C301']
        rat='Ceruminous carcinomas arise from ceruminous glands, which exist only in the outer external auditory canal; the tumour by definition affects only that site (diagnosis is questioned if the EAC is uninvolved), a proper subset of the ceiling (EAC + skin).'
        src='https://en.wikipedia.org/wiki/Ceruminous_adenocarcinoma'
        sname='Ceruminous adenocarcinoma (external auditory canal only); corroborated by Head & Neck Pathol 2018 PMC6081286'

    # --- 8440/3 cystadenocarcinoma NOS: generic multi-site -> No
    elif code=='8440/3':
        ss=N
        rat='Cystadenocarcinoma, NOS is a generic morphologic descriptor applied across many organs (salivary glands, pancreas, skin, etc.); not restricted to a proper subset.'
        src='https://www.ncbi.nlm.nih.gov/books/NBK493224/'
        sname='General pathology reference (generic descriptor)'

    # --- 8542/3 Paget/EMPD: ceiling already = extramammary apocrine distribution -> No
    elif code=='8542/3':
        ss=N
        rat='Extramammary Paget disease occurs on apocrine-bearing anogenital/perianal skin (vulva, perianal, scrotum, penis) plus rare ectopic cutaneous sites; the code ceiling already encompasses exactly this extramammary distribution (breast is excluded), so no further proper-subset restriction applies.'
        src='https://www.ncbi.nlm.nih.gov/books/NBK493224/'
        sname='Extramammary Paget Disease, StatPearls (NBK493224)'

    # --- 8572/3
    elif code=='8572/3':
        if term=='Fibromatosis-like metaplastic carcinoma':
            ss=Y
            subset=[c for c in cc if c.startswith('C50')]
            rat='Fibromatosis-like metaplastic carcinoma is a WHO Classification of Breast Tumours (5th ed) entity defined exclusively in the breast; it is restricted to the breast, a proper subset of the code ceiling.'
            src='https://pmc.ncbi.nlm.nih.gov/articles/PMC10336999/'
            sname='Fibromatosis-like metaplastic carcinoma of the breast, WHO 5th ed (World J Clin Cases 2023, PMC10336999)'
        else:
            ss=U
            rat='Sarcomatoid/spindle-cell metaplastic acinar adenocarcinoma variants are strongly associated with breast but analogous metaplastic/sarcomatoid change is described in other organs of the ceiling; evidence is insufficient to fix a single proper subset.'
            src='https://pmc.ncbi.nlm.nih.gov/articles/PMC7640663/'
            sname='Metaplastic breast cancer overview, Breast Cancer Res 2020 (PMC7640663)'

    # --- 8573/3 apocrine metaplasia: breast + apocrine skin -> Uncertain
    elif code=='8573/3':
        ss=U
        rat='Carcinoma/adenocarcinoma with apocrine metaplasia is classically a breast entity but apocrine differentiation also occurs in apocrine-bearing skin/genital sites within the ceiling; a single proper subset cannot be firmly established.'
        src='https://pmc.ncbi.nlm.nih.gov/articles/PMC7640663/'
        sname='Metaplastic/apocrine breast carcinoma overview (PMC7640663)'

    # --- 8575/3 metaplastic carcinoma NOS group: predominantly breast but generic -> Uncertain
    elif code=='8575/3':
        ss=U
        rat='Metaplastic carcinoma (NST/NOS, or with mesenchymal differentiation) is predominantly a WHO breast entity but the same terminology is applied to metaplastic carcinomas of skin and other ceiling sites; evidence is insufficient to confine it to a single proper subset.'
        src='https://pmc.ncbi.nlm.nih.gov/articles/PMC7640663/'
        sname='Metaplastic breast cancer overview, Breast Cancer Res 2020 (PMC7640663)'

    # --- 8722/3 balloon cell melanoma: skin + mucosa + eye -> No
    elif code=='8722/3':
        ss=N
        rat='Balloon cell melanoma is a histologic variant that arises across cutaneous, mucosal (anus, genital) and ocular/choroidal sites, spanning the code ceiling; not a proper subset.'
        src='https://pmc.ncbi.nlm.nih.gov/articles/PMC9036264/'
        sname='Balloon Cell Melanoma case series/review, Dermatopathology 2022 (PMC9036264)'

    # --- 8723/3 regressing melanoma: generic -> No
    elif code=='8723/3':
        ss=N
        rat='"Regressing melanoma" is a generic descriptor of tumour regression applicable to melanomas at any site in the ceiling; not anatomically restricted.'
        src='https://www.ncbi.nlm.nih.gov/books/NBK470409/'
        sname='Malignant Melanoma, StatPearls (NBK470409)'

    # --- 8740/3 melanoma in junctional nevus: generic -> No
    elif code=='8740/3':
        ss=N
        rat='Melanoma arising in a junctional nevus is a generic descriptor; junctional nevi and melanomas occur across cutaneous and mucosal/genital sites of the ceiling, so no proper-subset restriction is established.'
        src='https://www.ncbi.nlm.nih.gov/books/NBK470409/'
        sname='Malignant Melanoma, StatPearls (NBK470409)'

    # --- 8741/2, 8741/3 precancerous melanosis: archaic term, uncertain -> Uncertain
    elif code in ('8741/2','8741/3'):
        ss=U
        rat='"Precancerous melanosis" (Dubreuilh) is an archaic synonym historically overlapping lentigo maligna (facial sun-damaged skin), but the term is ambiguous and the code ceiling includes non-cutaneous (meningeal) sites, so a reliable proper-subset cannot be assigned.'
        src='https://www.ncbi.nlm.nih.gov/books/NBK482163/'
        sname='Lentigo Maligna Melanoma / precancerous melanosis, StatPearls (NBK482163)'

    # --- 8742/2 lentigo maligna group: chronically sun-damaged skin -> Yes skin codes
    elif code=='8742/2':
        ss=Y
        subset=skin_subset(code)
        rat='Lentigo maligna / Hutchinson melanotic freckle is by definition melanoma in situ on chronically sun-damaged skin (86% head & neck, predilection for face); it is confined to cutaneous sites and does not arise on the lip mucosa, vulva, penis or scrotum included in the ceiling, so it is restricted to the skin subset.'
        src='https://www.ncbi.nlm.nih.gov/books/NBK482163/'
        sname='Lentigo Maligna Melanoma, StatPearls (NBK482163)'

    # --- 8742/3 high-CSD melanoma: chronically sun-exposed skin -> Yes skin codes
    elif code=='8742/3':
        ss=Y
        subset=skin_subset(code)
        rat='High cumulative sun damage (high-CSD) melanoma is the WHO 5th-ed pathway defined on chronically sun-exposed skin (head/neck and dorsal extremities); it is a cutaneous entity and does not arise on the lip mucosa, vulva, penis or scrotum in the ceiling, so it is restricted to the skin subset.'
        src='https://pubmed.ncbi.nlm.nih.gov/32057276/'
        sname='WHO 2018 Classification of Melanoma (high-CSD), PMID 32057276'

    # validate subset
    subset=[c for c in subset if c in cc]
    labels=[LAB.get(c,c) for c in subset]
    if ss=='Yes':
        assert subset and set(subset).issubset(set(cc)) and set(subset)!=set(cc), f'bad subset {code} {term}'

    results.append({
        'code':code,'term':term,'site_specific':ss,
        'site_subset_codes':subset,'site_subset_labels':labels,
        'rationale':rat,'source':src,'source_name':sname
    })

os.makedirs('/home/user/workspace/icdo32_execution/results',exist_ok=True)
json.dump(results, open('/home/user/workspace/icdo32_execution/results/skin_02.json','w'), indent=2, ensure_ascii=False)

from collections import Counter
c=Counter(r['site_specific'] for r in results)
print('LEN',len(results))
print(dict(c))
srcs=set(r['source'] for r in results if r['site_specific']=='Yes')
print('Yes sources:',srcs)
