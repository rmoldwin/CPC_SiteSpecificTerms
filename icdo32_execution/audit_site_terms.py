#!/usr/bin/env python3
"""Audit: find Yes-decisions where the term names a specific organ but the assigned
subset_codes point to a DIFFERENT organ (potential site misapplication).

Uses the authoritative 4-digit ICD-O-3.2 topography map for correct organ grouping.
"""
import json, re

topo = json.load(open('icdo32_topography.json'))

# Map each 4-digit code to a coarse ORGAN concept for consistency checking.
# (label text -> organ keyword the term might contain)
def organ_of(code):
    d = topo.get(code, '').lower()
    return d

# term-keyword -> set of code-prefixes (3-char) that are ANATOMICALLY consistent
# If a term contains the keyword, at least one subset code should map to a consistent site.
KEYWORD_SITES = {
    'cholangio': ['C221', 'C240', 'C241', 'C248', 'C249'],
    'bile duct': ['C221', 'C240', 'C241', 'C248', 'C249'],
    'biliary': ['C221', 'C239', 'C240', 'C241', 'C248', 'C249'],
    'gallbladder': ['C239'],
    'hepatocellular': ['C220'],
    'hepatoblast': ['C220'],
    'hepatic': ['C220', 'C221'],
    'pancrea': ['C250','C251','C252','C253','C254','C257','C258','C259'],
    'gastric': ['C160','C161','C162','C163','C164','C165','C166','C168','C169'],
    'stomach': ['C160','C161','C162','C163','C164','C165','C166','C168','C169'],
    'esophag': ['C150','C151','C152','C153','C154','C155','C158','C159'],
    'colon': ['C180','C181','C182','C183','C184','C185','C186','C187','C188','C189'],
    'colorectal': ['C180','C181','C182','C183','C184','C185','C186','C187','C188','C189','C199','C209'],
    'rectal': ['C199','C209','C210','C211','C212','C218'],
    'rectum': ['C199','C209'],
    'anal': ['C210','C211','C212','C218'],
    'anus': ['C210','C211','C212','C218'],
    'appendix': ['C181'],
    'appendiceal': ['C181'],
    'duoden': ['C170'],
    'ileal': ['C172'],
    'jejun': ['C171'],
    'small intestin': ['C170','C171','C172','C173','C178','C179'],
    'renal': ['C649','C659'],
    'kidney': ['C649'],
    'renal pelvis': ['C659'],
    'ureter': ['C669'],
    'bladder': ['C670','C671','C672','C673','C674','C675','C676','C677','C678','C679'],
    'urethra': ['C680','C681'],
    'prostat': ['C619'],
    'testic': ['C620','C621','C629'],
    'testis': ['C620','C621','C629'],
    'penile': ['C600','C601','C602','C608','C609'],
    'penis': ['C600','C601','C602','C608','C609'],
    'scrotal': ['C632'],
    'ovar': ['C569'],
    'fallopian': ['C570'],
    'endometri': ['C540','C541','C542','C543','C548','C549','C559'],
    'cervic': ['C530','C531','C538','C539'],
    'cervix': ['C530','C531','C538','C539'],
    'vulv': ['C510','C511','C512','C518','C519'],
    'vagin': ['C529'],
    'uter': ['C540','C541','C542','C543','C548','C549','C559'],
    'breast': ['C500','C501','C502','C503','C504','C505','C506','C508','C509'],
    'lung': ['C340','C341','C342','C343','C348','C349'],
    'pulmonary': ['C340','C341','C342','C343','C348','C349'],
    'bronch': ['C340','C349'],
    'pleural': ['C384'],
    'thymic': ['C379'],
    'thymus': ['C379'],
    'laryn': ['C320','C321','C322','C323','C328','C329'],
    'trachea': ['C339'],
    'nasophary': ['C110','C111','C112','C113','C118','C119'],
    'orophary': ['C100','C101','C102','C103','C104','C108','C109'],
    'hypophary': ['C129','C130','C131','C132','C138','C139'],
    'sinonasal': ['C300','C301','C310','C311','C312','C313','C318','C319'],
    'nasal': ['C300','C301'],
    'salivary': ['C079','C080','C081','C088','C089'],
    'parotid': ['C079'],
    'tonsil': ['C090','C091','C098','C099'],
    'thyroid': ['C739'],
    'parathyroid': ['C750'],
    'adrenal': ['C740','C741','C749'],
    'pituitary': ['C751'],
    'pineal': ['C753'],
    'retina': ['C692'],
    'retinoblast': ['C692'],
    'uveal': ['C693','C694'],
    'choroid': ['C693'],
    'conjunctiv': ['C690'],
    'corneal': ['C691'],
    'orbit': ['C696'],
    'meningi': ['C700','C701','C709'],
    'cerebell': ['C716'],
    'skin': ['C440','C441','C442','C443','C444','C445','C446','C447','C448','C449'],
    'cutaneous': ['C440','C441','C442','C443','C444','C445','C446','C447','C448','C449'],
    'liver': ['C220','C221'],
    'peritone': ['C481','C482'],
    'retroperiton': ['C480'],
}

decisions = [json.loads(l) for l in open('decisions.jsonl')]
flags = []
for d in decisions:
    if d['decision'] != 'Yes':
        continue
    term = d['term'].lower()
    sub = set(d.get('subset_codes', []))
    if not sub:
        continue
    for kw, allowed in KEYWORD_SITES.items():
        if kw in term:
            allowed_set = set(allowed)
            # is there any overlap between the subset and the anatomically-allowed codes?
            overlap = sub & allowed_set
            if not overlap:
                # potential misapplication: term names organ X but subset points elsewhere
                flags.append({
                    'code': d['code'], 'term': d['term'], 'keyword': kw,
                    'subset': sorted(sub),
                    'subset_labels': [f'{c}={topo.get(c,"?")}' for c in sorted(sub)],
                    'expected_any_of': allowed,
                    'source_name': d.get('source_name','')[:60],
                })
            break  # only first matching keyword

print(f'Total Yes decisions audited: {sum(1 for d in decisions if d["decision"]=="Yes")}')
print(f'Potential site-misapplication flags: {len(flags)}')
print()
for f in flags:
    print(f"[{f['code']}] {f['term']}")
    print(f"   keyword '{f['keyword']}' -> subset assigned: {f['subset_labels']}")
    print(f"   expected at least one of: {f['expected_any_of']}")
    print(f"   src: {f['source_name']}")
    print()

json.dump(flags, open('audit_flags.json','w'), indent=1)
