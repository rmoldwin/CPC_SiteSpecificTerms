import json

with open('/home/user/workspace/icdo32_execution/batches/skin_03.json') as f:
    batch = json.load(f)

LAB = {
    "C000":"External upper lip","C001":"External lower lip","C002":"External lip NOS",
    "C003":"Mucosa of upper lip","C004":"Mucosa of lower lip","C005":"Mucosa of lip NOS",
    "C006":"Commissure of lip","C008":"Overlapping lesion of lip","C009":"Lip NOS",
    "C440":"Skin of lip NOS","C441":"Eyelid","C442":"External ear skin","C443":"Skin of face",
    "C444":"Skin of scalp and neck","C445":"Skin of trunk","C446":"Skin of upper limb and shoulder",
    "C447":"Skin of lower limb and hip","C448":"Overlapping lesion of skin","C449":"Skin NOS",
    "C481":"Specified parts of peritoneum","C482":"Peritoneum NOS",
    "C510":"Labium majus","C511":"Labium minus","C512":"Clitoris","C518":"Overlapping lesion of vulva","C519":"Vulva NOS",
    "C529":"Vagina NOS","C578":"Overlapping lesion of female genital organs","C579":"Female genital tract NOS",
    "C600":"Prepuce","C609":"Penis NOS","C632":"Scrotum NOS",
    "C690":"Conjunctiva","C691":"Cornea NOS","C692":"Retina","C693":"Choroid","C694":"Ciliary body",
    "C695":"Lacrimal gland","C696":"Orbit NOS","C698":"Overlapping lesion of eye","C699":"Eye NOS",
    "C490":"Connective tissue of head/face/neck","C491":"Connective tissue of upper limb","C492":"Connective tissue of lower limb",
    "C493":"Connective tissue of thorax","C494":"Connective tissue of abdomen","C495":"Connective tissue of pelvis",
    "C496":"Connective tissue of trunk NOS","C498":"Overlapping lesion of connective tissue","C499":"Connective tissue NOS",
    "C500":"Nipple","C501":"Central portion of breast","C502":"Upper-inner quadrant of breast","C503":"Lower-inner quadrant of breast",
    "C504":"Upper-outer quadrant of breast","C505":"Lower-outer quadrant of breast","C506":"Axillary tail of breast",
    "C508":"Overlapping lesion of breast","C509":"Breast NOS",
}

def lbl(codes):
    return [LAB.get(c, c) for c in codes]

# Cutaneous skin codes
SKIN = ["C440","C441","C442","C443","C444","C445","C446","C447","C448","C449"]

# Source refs
SRC_ACRAL = ("https://pmc.ncbi.nlm.nih.gov/articles/PMC8503895/",
             "J Pathol Clin Res 2021 (PMC8503895) - WHO defines acral melanoma as glabrous skin of the extremities: palms, soles, nail apparatus")
SRC_LMM = ("https://www.ncbi.nlm.nih.gov/books/NBK482163/",
           "StatPearls: Lentigo Maligna Melanoma - chronically sun-damaged skin, ~86% head and neck")
SRC_LOWCSD = ("https://pmc.ncbi.nlm.nih.gov/articles/PMC9292921/",
              "Br J Dermatol 2021 (PMC9292921) Melanoma Pathology 2.0 - low-CSD/superficial spreading melanoma arises on trunk and extremities")
SRC_UVEAL = ("https://www.cancer.gov/types/eye/patient/intraocular-melanoma-treatment-pdq",
             "NCI PDQ Intraocular (Uveal) Melanoma - uvea (iris, ciliary body, choroid) middle layer of the eye")

results = []
for b in batch:
    code = b['code']; term = b['term']; ceil = b['ceiling_codes']
    ss = "No"; sub = []; rationale = ""; source = ""; sname = ""

    tlow = term.lower()

    if code == "8742/3":
        # Lentigo maligna melanoma / Hutchinson melanotic freckle synonyms -> chronically sun-damaged skin (cutaneous), not genital sites/lip mucosa
        sub = [c for c in SKIN if c in ceil]
        ss = "Yes"
        rationale = ("Lentigo maligna melanoma (Hutchinson melanotic freckle) is by definition a melanoma of chronically sun-damaged CUTANEOUS skin, "
                     "overwhelmingly on the head and neck; it does not arise on the lip mucosa or on the sun-shielded genital sites (vulva, penis, scrotum) that the code ceiling also spans, so it is restricted to the cutaneous (C44) subset.")
        source, sname = SRC_LMM

    elif code == "8743/2":
        # Low-CSD MIS / SSM in situ -> intermittently sun-exposed cutaneous skin (trunk/extremities), not vulvar/vaginal/female-genital mucosa
        sub = [c for c in SKIN if c in ceil]
        ss = "Yes"
        rationale = ("Low-CSD (superficial spreading) melanoma in situ is a CUTANEOUS melanoma of intermittently sun-exposed skin (trunk and extremities); "
                     "it does not arise on the vaginal or female-genital-tract mucosa included in the code ceiling (those are mucosal lentiginous melanomas), so it is restricted to the cutaneous (C44) subset.")
        source, sname = SRC_LOWCSD

    elif code == "8744/3":
        # Acral melanoma group -> glabrous acral skin: palms/soles/nails = C446 (upper limb/hand) + C447 (lower limb/foot)
        sub = [c for c in ["C446","C447"] if c in ceil]
        ss = "Yes"
        rationale = ("Acral (lentiginous/subungual/nail-apparatus) melanoma is defined by the WHO as melanoma of glabrous skin of the extremities - palms, soles and nail units of the hands and feet; "
                     "it does not occur on lip, eyelid, ear, face, scalp/neck or trunk skin, so it is restricted to the skin of the upper limb/hand (C446) and lower limb/foot (C447).")
        source, sname = SRC_ACRAL

    elif code == "8761/3":
        # Melanoma in congenital nevus -> CMN occur anywhere on skin; not a proper subset
        ss = "No"
        rationale = ("Congenital-nevus-associated melanoma arises within congenital melanocytic nevi, which can occur on any skin surface (trunk predominant but head/neck, extremities and genital skin all involved); it is not restricted to a proper subset of the cutaneous ceiling.")

    elif code == "8770/3":
        if "uveal" in tlow:
            sub = [c for c in ["C693","C694"] if c in ceil]
            ss = "Yes"
            rationale = ("A uveal melanoma is by definition an intraocular melanoma of the uveal tract (choroid, ciliary body, iris) of the eye; it does not arise on lip, skin or scrotum, so it is restricted to the intraocular (choroid C693 / ciliary body C694) subset of the ceiling.")
            source, sname = SRC_UVEAL
        else:
            ss = "No"
            rationale = ("Spitz melanoma (malignant Spitz tumour) is a cutaneous melanoma occurring across essentially all skin sites (lower extremities, trunk, upper extremities and head/neck); it is not restricted to a demonstrable proper subset of the ceiling.")

    elif code == "8780/3":
        ss = "No"
        rationale = ("Melanoma arising in blue nevus develops where blue nevi occur, which can be any anatomical/cutaneous area (scalp predilection but not exclusive); the literature does not establish restriction to a proper subset of the cutaneous ceiling.")

    elif code == "8813/3":
        ss = "No"
        rationale = ("Fascial fibrosarcoma is a deep soft-tissue fibrosarcoma without a literature-established restriction to a proper subset of the ceiling's soft-tissue/skin sites.")

    elif code == "8832/3":
        ss = "No"
        rationale = ("Dermatofibrosarcoma protuberans (fibrosarcomatous) arises in the dermis across the body - trunk (50-60%), limbs (~35%) and head/neck (10-15%); it spans essentially all cutaneous sites and is not restricted to a proper subset.")
        source = "https://dermnetnz.org/topics/dermatofibrosarcoma-protuberans"
        sname = "DermNet: Dermatofibrosarcoma protuberans - trunk 50-60%, limbs 35%, head/neck 10-15%"

    elif code in ("8853/3","8855/3"):
        ss = "No"
        rationale = ("This is a liposarcoma subtype occurring in deep soft tissue at multiple body sites (extremities and retroperitoneum); it is a generic soft-tissue sarcoma descriptor and is not restricted to a literature-established proper subset of the ceiling.")

    obj = {
        "code": code,
        "term": term,
        "site_specific": ss,
        "site_subset_codes": sub if ss == "Yes" else [],
        "site_subset_labels": lbl(sub) if ss == "Yes" else [],
        "rationale": rationale,
        "source": source if ss == "Yes" else source,  # keep source for No when we fetched one
        "source_name": sname,
    }
    # For non-Yes, brief schema allows source; keep fetched source where available else empty
    results.append(obj)

with open('/home/user/workspace/icdo32_execution/results/skin_03.json','w') as f:
    json.dump(results, f, indent=1, ensure_ascii=False)

from collections import Counter
c = Counter(r['site_specific'] for r in results)
print("len", len(results), dict(c))
urls = set(r['source'] for r in results if r['source'].startswith('http'))
print("http sources:", len(urls))
for u in urls: print(" ", u)
