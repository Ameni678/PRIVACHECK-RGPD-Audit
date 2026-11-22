import re
from datetime import datetime
from .database import save_audit

# Keyword patterns are screening signals, not legal determinations.
CRITERIA = [
 {"id":"purpose","fr":"Finalités du traitement","en":"Processing purposes","article":"Article 5(1)(b) et 13(1)(c)","patterns":[r"\bfinalit[ée]s?\b",r"\bpurpose(s)?\b",r"\bobjectif(s)? du traitement\b"],"weight":1},
 {"id":"legal_basis","fr":"Base légale","en":"Legal basis","article":"Article 6","patterns":[r"\bbase(s)? légale(s)?\b",r"\bconsentement\b",r"\bcontrat\b",r"\bint[ée]r[êe]t[s]? l[ée]gitime[s]?\b",r"\blegal basis\b",r"\bconsent\b"],"weight":1},
 {"id":"data_categories","fr":"Catégories de données","en":"Data categories","article":"Article 13(1)(c)","patterns":[r"\bdonn[ée]es personnelles\b",r"\bcategor(y|ies) of personal data\b",r"\bpersonal data\b"],"weight":1},
 {"id":"recipients","fr":"Destinataires","en":"Recipients","article":"Article 13(1)(e)","patterns":[r"\bdestinataires\b",r"\bprestataires\b",r"\brecipients\b",r"\bservice providers\b"],"weight":1},
 {"id":"retention","fr":"Durée de conservation","en":"Retention period","article":"Article 13(2)(a)","patterns":[r"\bdur[ée]e de conservation\b",r"\bconserv[ée]es? pendant\b",r"\bretention period\b",r"\bstored for\b"],"weight":1},
 {"id":"rights","fr":"Droits des personnes","en":"Data subject rights","article":"Articles 15 à 22","patterns":[r"\bdroit[s]? d['’]acc[èe]s\b",r"\brectification\b",r"\beffacement\b",r"\bportabilit[ée]\b",r"\bopposition\b",r"\bwithdraw.*consent\b",r"\bright to access\b",r"\bright to erasure\b"],"weight":1},
 {"id":"contact","fr":"Contact / responsable","en":"Controller contact","article":"Article 13(1)(a)","patterns":[r"\bresponsable du traitement\b",r"\bcontact\b.{0,50}@",r"\bdata controller\b",r"\bprivacy officer\b"],"weight":1},
 {"id":"complaint","fr":"Droit de réclamation","en":"Right to lodge a complaint","article":"Article 13(2)(d)","patterns":[r"\br[ée]clamation\b",r"\bautorit[ée] de contr[ôo]le\b",r"\bcnil\b",r"\bsupervisory authority\b",r"\bcomplaint\b"],"weight":1},
 {"id":"transfers","fr":"Transferts hors UE","en":"International transfers","article":"Articles 44 à 49","patterns":[r"\btransfert[s]? hors\b",r"\bpays tiers\b",r"\btransferts internationaux\b",r"\binternational transfers\b",r"\bthird countr(y|ies)\b"],"weight":1},
 {"id":"security","fr":"Sécurité des données","en":"Data security","article":"Article 32","patterns":[r"\bs[ée]curit[ée]\b",r"\bchiffrement\b",r"\bmesures techniques et organisationnelles\b",r"\bencryption\b",r"\bsecurity measures\b"],"weight":1},
 {"id":"automated","fr":"Décision automatisée / profilage","en":"Automated decision-making / profiling","article":"Article 22","patterns":[r"\bd[ée]cision[s]? automatis[ée]e[s]?\b",r"\bprofilage\b",r"\bautomated decision\b",r"\bprofiling\b"],"weight":1},
]

def _find_evidence(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            start, end = max(0, match.start()-180), min(len(text), match.end()+260)
            return re.sub(r"\s+", " ", text[start:end]).strip()
    return ""

TRANSLATIONS = {
 "de": {"criteria": ["Verarbeitungszwecke", "Rechtsgrundlage", "Datenkategorien", "Empfänger", "Speicherdauer", "Rechte betroffener Personen", "Kontakt / Verantwortlicher", "Beschwerderecht", "Datenübermittlungen außerhalb der EU", "Datensicherheit", "Automatisierte Entscheidungen / Profiling"]},
 "ar": {"criteria": ["أغراض المعالجة", "الأساس القانوني", "فئات البيانات", "المستلمون", "مدة الاحتفاظ", "حقوق أصحاب البيانات", "جهة الاتصال / المسؤول", "حق تقديم شكوى", "نقل البيانات خارج الاتحاد الأوروبي", "أمن البيانات", "القرارات الآلية / التنميط"]}
}

def run_audit(text: str, title: str = "Untitled document", lang: str = "fr"):
    if not text or len(text.strip()) < 30:
        raise ValueError("Document text is too short to audit.")
    details = []
    localized = TRANSLATIONS.get(lang, {}).get("criteria", [])
    for idx, criterion in enumerate(CRITERIA):
        evidence = _find_evidence(text, criterion["patterns"])
        if evidence:
            status = ("Partiellement identifié" if lang == "fr" else "Partially identified")
            if lang == "de": status = "Teilweise erkannt"
            if lang == "ar": status = "تم العثور عليه جزئياً"
            note = ("Présence détectée ; vérifier la précision et l'exhaustivité." if lang=="fr"
                    else "A mention was detected; verify accuracy and completeness.")
        else:
            status = ("Non identifié" if lang == "fr" else "Not identified")
            if lang == "de": status = "Nicht erkannt"
            if lang == "ar": status = "لم يتم العثور عليه"
            note = ("Aucune mention explicite détectée. Cela ne prouve pas une non-conformité." if lang=="fr"
                    else "No explicit mention detected. This does not prove non-compliance.")
        details.append({
            "id":criterion["id"],
            "criterion": (criterion["fr"] if lang=="fr" else localized[idx] if localized else criterion["en"]),
            "status":status,
            "evidence":evidence,
            "reference":criterion["article"],
            "note":note
        })
    identified = sum(bool(x["evidence"]) for x in details)
    score = identified / len(details) * 100
    recs = []
    for item in details:
        if not item["evidence"]:
            recs.append(
                f"Vérifier et, si nécessaire, documenter : {item['criterion']} ({item['reference']})."
                if lang=="fr" else
                f"Check and, where applicable, document: {item['criterion']} ({item['reference']})."
            )
        else:
            recs.append(
                f"Faire valider la précision de « {item['criterion']} » au regard de {item['reference']}."
                if lang=="fr" else
                f"Validate the adequacy of “{item['criterion']}” against {item['reference']}."
            )
    if lang == "fr":
        summary = f"L'analyse documentaire a repéré {identified} critère(s) sur {len(details)} à partir de mentions textuelles. Les résultats nécessitent une vérification humaine."
    elif lang == "de":
        summary = f"Die Dokumentenanalyse hat textliche Hinweise zu {identified} von {len(details)} Kriterien gefunden. Die Ergebnisse müssen von einer Person überprüft werden."
    elif lang == "ar":
        summary = f"رصد التحليل النصي إشارات إلى {identified} من أصل {len(details)} معياراً. تتطلب النتائج مراجعة بشرية."
    else:
        summary = f"The document screening detected textual references for {identified} of {len(details)} criteria. Human review is required."
    result = {
        "title":title, "created_at":datetime.now().isoformat(timespec="seconds"),
        "score":score, "summary":summary, "details":details, "recommendations":recs,
        "counts":{"satisfactory":0,"partial":identified,"risk":len(details)-identified},
        "criteria":[{"Critère":x["criterion"],"Résultat":x["status"],"Référence":x["reference"]} for x in details],
        "language":lang
    }
    save_audit(result)
    return result
