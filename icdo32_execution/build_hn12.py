import json, os
from collections import Counter

d = json.load(open('batches/head_neck_12.json'))
ceil99 = set(d[2]['ceiling_codes'])
skin = sorted([x for x in ceil99 if x.startswith('C44')])
skin_lab = ["Skin of lip","Skin of eyelid","Skin of ear/external canal","Skin of face other/NOS",
            "Skin of scalp and neck","Skin of trunk","Skin of upper limb/shoulder","Skin of lower limb/hip",
            "Overlapping lesion of skin","Skin NOS"]
eye = sorted([x for x in ceil99 if x.startswith('C69')])
eye_lab = ["Eye NOS","Conjunctiva","Cornea NOS","Retina","Choroid","Ciliary body",
           "Lacrimal gland","Overlapping lesion of eye","Eye NOS"]
men = sorted([x for x in ceil99 if x.startswith('C70')])
men_lab = ["Cerebral meninges","Spinal meninges","Meninges NOS"]
ln = sorted([x for x in ceil99 if x.startswith('C77')])
# ln codes: C770 C771 C772 C773 C774 C775 C778 C779 (8)
ln_lab = ["LN of head/face/neck","Intrathoracic LN","Intra-abdominal LN","LN of axilla/arm",
          "LN of inguinal/leg","LN of pelvis","Overlapping LN","LN NOS"]

URL_PCMZL_WHO = "https://www.nature.com/articles/s41375-022-01620-2"
NAME_PCMZL_WHO = "WHO-HAEM5 (Alaggio et al., Leukemia 2022) - PCMZL designated a separate skin-restricted entity"
URL_PCMZL_ICC = "https://www.nature.com/articles/s41375-022-01764-1"
NAME_PCMZL_ICC = "ICC vs WHO-HAEM5 (Zamo et al., Leukemia 2022) - EMZL not classified by site except cutaneous"
URL_DURA = "https://pmc.ncbi.nlm.nih.gov/articles/PMC9217145/"
NAME_DURA = "NMC Case Rep J 2022 (PMC9217145) - CNS MALT lymphoma arises in dura mater"
URL_CHOROID = "https://pubmed.ncbi.nlm.nih.gov/15586289/"
NAME_CHOROID = "Coupland et al., Graefes Arch Clin Exp Ophthalmol 2005 (PMID15586289) - primary uveal EMZL"
URL_NMZL = "https://www.cancernetwork.com/view/nodal-marginal-zone-b-cell-lymphoma-diagnostic-and-therapeutic-dilemma"
NAME_NMZL = "CancerNetwork/WHO - NMZL is a primary nodal lymphoma localized to lymph nodes"
URL_ENKTL = "https://www.nature.com/articles/s41375-022-01620-2"
NAME_ENKTL = "WHO-HAEM5 (Alaggio et al., Leukemia 2022) - extranodal NK/T-cell lymphoma"
URL_MONO = "https://pubmed.ncbi.nlm.nih.gov/10319381/"
NAME_MONO = "Nathwani et al. (PMID10319381) - nodal monocytoid B-cell lymphoma = nodal MZL"

results = []
for o in d:
    code = o['code']; term = o['term']; cc = o['ceiling_codes']
    tl = term.lower()
    rec = {"code":code,"term":term,"site_specific":"No","site_subset_codes":[],
           "site_subset_labels":[],"rationale":"","source":"","source_name":""}

    if code == '9698/3':
        rec.update({"site_specific":"No",
            "rationale":"Legacy Rappaport/Working-Formulation synonym for follicular lymphoma, a systemic nodal and extranodal B-cell lymphoma that occurs across essentially all of the code's valid sites; not restricted to a proper subset.",
            "source":"https://www.nature.com/articles/s41375-022-01620-2",
            "source_name":"WHO-HAEM5 (Alaggio et al., Leukemia 2022) - follicular lymphoma"})

    elif code == '9719/3':
        rec.update({"site_specific":"No",
            "rationale":"The code's SMVL ceiling is already limited to nasal/upper-aerodigestive sites (palate, nasopharynx, nasal cavity/sinuses/middle ear); this term does not restrict further to a proper subset. Non-nasal/extranasal variants involve skin/GI/testis/soft tissue that lie outside the ceiling, so no in-ceiling subset applies.",
            "source":URL_ENKTL,"source_name":NAME_ENKTL})

    elif code == '9699/3':
        is_cut = ('cutaneous' in tl) or ('salt' in tl) or ('skin-associated' in tl) or ('skin associated' in tl)
        if is_cut:
            rec.update({"site_specific":"Yes","site_subset_codes":skin,"site_subset_labels":skin_lab,
                "rationale":"Primary cutaneous marginal zone lymphoma (including its heavy-chain class-switched, non-class-switched/IgM subtypes and the SALT synonym) is recognized in WHO-HAEM5 as a distinct entity confined to the skin, restricted to skin at diagnosis with rare extracutaneous spread.",
                "source":URL_PCMZL_WHO,"source_name":NAME_PCMZL_WHO})
        elif 'dura' in tl:
            rec.update({"site_specific":"Yes","site_subset_codes":men,"site_subset_labels":men_lab,
                "rationale":"MALT lymphoma of the dura is a primary CNS marginal zone lymphoma arising in the dura mater/meninges; restricted to the meninges, a proper subset of the code ceiling.",
                "source":URL_DURA,"source_name":NAME_DURA})
        elif 'choroidal' in tl:
            rec.update({"site_specific":"Yes","site_subset_codes":eye,"site_subset_labels":eye_lab,
                "rationale":"Primary choroidal (uveal) lymphoma is an intraocular MALT/marginal zone lymphoma of the eye; restricted to ocular sites, a proper subset of the ceiling.",
                "source":URL_CHOROID,"source_name":NAME_CHOROID})
        elif ('nodal' in tl) and ('extranodal' not in tl) and ('extra-nodal' not in tl):
            rec.update({"site_specific":"Yes","site_subset_codes":ln,"site_subset_labels":ln_lab,
                "rationale":"Nodal marginal zone lymphoma (and its pediatric variant) is defined by WHO as a primary NODAL B-cell lymphoma presenting in lymph nodes without extranodal or splenic disease; restricted to lymph nodes, a proper subset of the ceiling.",
                "source":URL_NMZL,"source_name":NAME_NMZL})
        elif 'monocytoid' in tl:
            rec.update({"site_specific":"Uncertain","site_subset_codes":[],"site_subset_labels":[],
                "rationale":"Historically 'monocytoid B-cell lymphoma' equated with nodal MZL, but monocytoid morphology is also a defining feature of extranodal MALT lymphomas at many sites; literature does not cleanly restrict this term to one anatomic subset.",
                "source":URL_MONO,"source_name":NAME_MONO})
        else:
            rec.update({"site_specific":"No",
                "rationale":"Generic marginal zone / MALT (mucosa-associated / bronchus-associated lymphoid tissue) descriptor occurring across essentially all extranodal/mucosal sites in the ceiling; not restricted to a proper subset.",
                "source":URL_PCMZL_ICC,"source_name":NAME_PCMZL_ICC})

    if rec["site_subset_codes"]:
        assert set(rec["site_subset_codes"]).issubset(set(cc)), (term, rec["site_subset_codes"])
        assert set(rec["site_subset_codes"]) != set(cc)
        assert len(rec["site_subset_codes"]) == len(rec["site_subset_labels"])
    results.append(rec)

os.makedirs('results', exist_ok=True)
json.dump(results, open('results/head_neck_12.json','w'), indent=1)
cnt = Counter(r['site_specific'] for r in results)
print('len', len(results))
print(dict(cnt))
for r in results:
    if r['site_specific']!='No':
        print(r['site_specific'], '|', r['term'], '->', r['site_subset_codes'][:3])
