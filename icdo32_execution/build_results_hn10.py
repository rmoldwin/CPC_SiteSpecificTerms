import json, os

data = json.load(open('/home/user/workspace/icdo32_execution/batches/head_neck_10.json'))
ceil = {o['code']: set(o['ceiling_codes']) for o in data}

LBL = {
    'C421': 'Bone marrow',
    'C422': 'Spleen',
    'C379': 'Thymus',
    'C381': 'Anterior mediastinum',
    'C382': 'Posterior mediastinum',
    'C383': 'Mediastinum, NOS',
    'C388': 'Overlapping lesion of heart, mediastinum and pleura',
    'C160': 'Stomach, cardia', 'C161': 'Stomach, fundus', 'C162': 'Stomach, body',
    'C163': 'Stomach, antrum', 'C164': 'Stomach, pylorus', 'C165': 'Stomach, lesser curvature',
    'C166': 'Stomach, greater curvature', 'C168': 'Stomach, overlapping', 'C169': 'Stomach, NOS',
    'C170': 'Duodenum', 'C171': 'Jejunum', 'C172': 'Ileum', 'C173': 'Meckel diverticulum',
    'C178': 'Small intestine, overlapping', 'C179': 'Small intestine, NOS',
    'C180': 'Cecum', 'C181': 'Appendix', 'C182': 'Ascending colon', 'C183': 'Hepatic flexure',
    'C184': 'Transverse colon', 'C185': 'Splenic flexure', 'C186': 'Descending colon',
    'C187': 'Sigmoid colon', 'C188': 'Colon, overlapping', 'C189': 'Colon, NOS',
    'C199': 'Rectosigmoid junction', 'C209': 'Rectum, NOS',
}

def sub(codes, code):
    codes = [c for c in codes if c in ceil[code]]
    return codes, [LBL[c] for c in codes]

GI = ['C160','C161','C162','C163','C164','C165','C166','C168','C169',
      'C170','C171','C172','C173','C178','C179',
      'C180','C181','C182','C183','C184','C185','C186','C187','C188','C189','C199','C209']
SPLEEN = ['C421','C422']
MGZL = ['C379','C381','C382','C383','C388']

results = []
def add(code, term, ss, codes=None, labels=None, rationale='', src='', srcname=''):
    results.append({"code": code, "term": term, "site_specific": ss,
                    "site_subset_codes": codes or [], "site_subset_labels": labels or [],
                    "rationale": rationale, "source": src, "source_name": srcname})

for o in data:
    code, term = o['code'], o['term']
    t = term.lower()
    if code == '9591/3':
        if term in ('Reticulosarcoma, diffuse', 'Reticulum cell sarcoma, NOS', 'Reticulum cell sarcoma, diffuse'):
            add(code, term, "No", rationale=(
                "Obsolete synonym for diffuse large B-cell lymphoma, a generic aggressive B-cell lymphoma arising "
                "across nodal and virtually all extranodal sites; not anatomically restricted."),
                src='https://www.nature.com/articles/s41375-022-01620-2',
                srcname='WHO-HAEM5 (2022) Lymphoid Neoplasms, Leukemia 2022 (Alaggio et al.)')
        elif 'splenic diffuse red pulp' in t:
            c,l = sub(SPLEEN, code)
            add(code, term, "Yes", c, l, rationale=(
                "Splenic diffuse red pulp small B-cell lymphoma is defined by diffuse infiltration of the splenic red "
                "pulp with bone marrow and peripheral blood involvement; a spleen/marrow-based entity forming a proper "
                "subset of the code ceiling."),
                src='https://pmc.ncbi.nlm.nih.gov/articles/PMC12205484/',
                srcname='Cureus 2025 review of splenic diffuse red pulp small B-cell lymphoma')
        elif 'splenic b-cell lymphoma/leukemia' in t or 'splenic b-cell lymphoma/leukaemia' in t or 'prominent nucleoli' in t or 'prominent nuclei' in t:
            c,l = sub(SPLEEN, code)
            add(code, term, "Yes", c, l, rationale=(
                "WHO-HAEM5 splenic B-cell lymphoma/leukaemia entities (SBLPN and the unclassifiable category) are "
                "primary splenic neoplasms involving spleen, bone marrow and blood; restricted to a proper subset of the ceiling."),
                src='https://www.nature.com/articles/s41375-022-01620-2',
                srcname='WHO-HAEM5 (2022) Lymphoid Neoplasms, Leukemia 2022 (Alaggio et al.)')
        else:
            add(code, term, "No", rationale="Not anatomically restricted.",
                src='https://www.nature.com/articles/s41375-022-01620-2', srcname='WHO-HAEM5 (2022)')
    elif code == '9596/3':
        if term == 'Mediastinal gray zone lymphoma':
            c,l = sub(MGZL, code)
            add(code, term, "Yes", c, l, rationale=(
                "WHO-HAEM5 (2022) restricts the diagnosis of mediastinal gray zone lymphoma to EBV-negative lymphomas "
                "arising in the mediastinum from thymic B cells, explicitly excluding extramediastinal cases."),
                src='https://pmc.ncbi.nlm.nih.gov/articles/PMC12821469/',
                srcname='Hematology Reports 2025 (Zorlu et al.); WHO-HAEM5 2022')
        else:
            add(code, term, "No", rationale=(
                "The generic B-cell lymphoma unclassifiable (DLBCL/CHL) and composite Hodgkin/non-Hodgkin lymphoma occur "
                "across lymph node groups and other sites (per SEER/WHO), so not restricted to a proper subset."),
                src='https://seer.cancer.gov/seertools/hemelymph/51f6cf57e3e27c3994bd5333/',
                srcname='SEER Hematopoietic Project (B-cell lymphoma unclassifiable, DLBCL/CHL)')
    elif code == '9671/3':
        add(code, term, "No", rationale=(
            "Lymphoplasmacytic lymphoma/immunocytoma is a systemic small B-cell neoplasm that, although marrow-predominant, "
            "also involves lymph nodes, spleen and other tissues and is coded wherever biopsied; not restricted to a proper subset."),
            src='https://pubmed.ncbi.nlm.nih.gov/23544948/',
            srcname='PubMed PMID 23544948 (lymphoplasmacytic lymphoma / Waldenstrom macroglobulinemia)')
    elif code == '9673/3':
        if term == 'Leukemic non-nodal mantle cell lymphoma':
            c,l = sub(SPLEEN, code)
            add(code, term, "Yes", c, l, rationale=(
                "Leukemic non-nodal MCL is defined by peripheral blood, bone marrow and sometimes splenic involvement "
                "without significant adenopathy; restricted to a non-nodal marrow/spleen subset."),
                src='https://seer.cancer.gov/seertools/hemelymph/51f6cf57e3e27c3994bd5357/',
                srcname='SEER Hematopoietic Project / WHO definition of leukemic non-nodal MCL')
        elif term == 'Malignant lymphomatous polyposis':
            c,l = sub(GI, code)
            add(code, term, "Yes", c, l, rationale=(
                "Multiple/malignant lymphomatous polyposis is the gastrointestinal-tract manifestation of mantle cell "
                "lymphoma, presenting as polypoid lesions along the digestive tract (stomach, small intestine, colon, rectum)."),
                src='https://pubmed.ncbi.nlm.nih.gov/20206107/',
                srcname='PubMed PMID 20206107 (primary GI MCL as multiple lymphomatous polyposis)')
        else:
            add(code, term, "No", rationale=(
                "Mantle cell lymphoma and its cyclin D1 / centrocytic / mantle-zone synonyms form a disseminated neoplasm "
                "involving lymph nodes, bone marrow, blood, spleen, Waldeyer ring and GI tract; not restricted to a proper subset."),
                src='https://seer.cancer.gov/seertools/hemelymph/51f6cf57e3e27c3994bd5357/',
                srcname='SEER Hematopoietic Project (mantle cell lymphoma)')
    elif code == '9687/3':
        add(code, term, "No", rationale=(
            "Burkitt lymphoma (all clinical/molecular variants and synonyms) arises across many sites - jaw/facial bones, "
            "abdomen (ileocecum), ovaries, kidneys, breast, lymph nodes, bone marrow and CNS - so not anatomically restricted "
            "to a proper subset of the code ceiling."),
            src='https://seer.cancer.gov/seertools/hemelymph/51f6cf57e3e27c3994bd5324/',
            srcname='SEER Hematopoietic Project (Burkitt lymphoma, NOS)')
    else:
        add(code, term, "Uncertain", rationale="Unhandled category.", src='', srcname='')

assert len(results) == 45, len(results)
for r in results:
    if r['site_specific'] == 'Yes':
        assert set(r['site_subset_codes']).issubset(ceil[r['code']]), r['term']
        assert len(r['site_subset_codes']) < len(ceil[r['code']])
        assert len(r['site_subset_codes']) == len(r['site_subset_labels'])

os.makedirs('/home/user/workspace/icdo32_execution/results', exist_ok=True)
json.dump(results, open('/home/user/workspace/icdo32_execution/results/head_neck_10.json','w'), indent=1)

from collections import Counter
print('counts', dict(Counter(r['site_specific'] for r in results)), 'total', len(results))
for r in results:
    if r['site_specific'] == 'Yes':
        print('YES |', r['term'][:55], '->', r['site_subset_codes'])
