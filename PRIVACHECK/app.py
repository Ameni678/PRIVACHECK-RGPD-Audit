import os
import html
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from privacheck.config import APP_NAME
from privacheck.database import (
    init_db, get_dashboard_stats, list_audits, get_audit_payloads,
    delete_knowledge, get_knowledge
)
from privacheck.i18n import tr
from privacheck.document_processor import extract_text
from privacheck.audit_engine import run_audit
from privacheck.report_generator import generate_pdf
from privacheck.rag_engine import (
    answer_question, add_knowledge_file, list_knowledge_files, retrieve
)
from privacheck.llm_client import llm_status
from privacheck.ml.predictor import model_exists, predict_document
from privacheck.ml.train_model import train_model, DATASET_PATH
from privacheck.ml.evaluation import load_evaluation, feature_importance

load_dotenv()
st.set_page_config(
    page_title="PRIVACHECK AI | RGPD Audit Workspace",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_db()

# ---------- Design system ----------
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root{--ink:#15264a;--ink2:#42516d;--violet:#6658d3;--lav:#f0efff;--bg:#f4f6fb;--muted:#77839a;--line:#e3e8f1;--green:#16866a;--amber:#b7791f;--red:#bd465c}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;font-size:16px}
.stApp{background:var(--bg);color:var(--ink)}
[data-testid="stHeader"]{background:rgba(244,246,251,.96)}
[data-testid="stMainBlockContainer"]{max-width:1540px;padding:2.1rem 2.4rem 4rem}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line)}
[data-testid="stSidebar"]>div:first-child{padding:1.35rem 1.05rem}
h1,h2,h3{font-family:'Manrope',sans-serif!important;color:var(--ink)}
h1{font-size:2.4rem!important;font-weight:800!important;letter-spacing:-1.2px}
h2{font-size:1.65rem!important;font-weight:800!important;letter-spacing:-.6px}
h3{font-size:1.25rem!important;font-weight:750!important}
p,label,.stMarkdown{color:var(--ink2)}
p{font-size:1.06rem;line-height:1.7}
.pc-brand{display:flex;align-items:center;gap:12px;padding:7px 5px 22px}
.pc-brand img{width:48px;height:48px;object-fit:contain}
.pc-brand-name{font:800 19px Manrope;color:#15264a;letter-spacing:-.65px}
.pc-brand-sub{font-size:10px;color:#8792a8;font-weight:800;letter-spacing:1.35px;margin-top:3px}
.pc-eyebrow{font-size:12px;color:#6d61d6;font-weight:800;letter-spacing:1.7px;text-transform:uppercase;margin-bottom:10px}
.pc-title{font:800 34px/1.18 Manrope;color:#15264a;letter-spacing:-1.2px}
.pc-desc{font-size:16px;color:#738098;margin-top:10px;max-width:900px;line-height:1.6}
.pc-rule{height:1px;background:var(--line);margin:25px 0 28px}
.pc-hero{position:relative;overflow:hidden;border-radius:24px;padding:34px 38px;background:linear-gradient(112deg,#14264b 0%,#253b70 58%,#6257c9 100%);color:white;min-height:220px;box-shadow:0 18px 42px #1c2b501c}
.pc-hero:after{content:"";position:absolute;width:270px;height:270px;border:1px solid #ffffff2b;border-radius:50%;right:-45px;top:-105px;box-shadow:0 0 0 30px #ffffff09,0 0 0 65px #ffffff08}
.pc-hero-kicker{font-size:12px;letter-spacing:1.8px;color:#d2d0ff;font-weight:800}
.pc-hero-title{font:800 30px Manrope;color:white;margin-top:15px;letter-spacing:-.7px;max-width:820px}
.pc-hero-copy{font-size:16px;line-height:1.7;color:#e0e5f5;max-width:760px;margin-top:10px}
.pc-hero-chip{display:inline-block;margin-top:19px;border:1px solid #ffffff44;background:#ffffff13;padding:8px 13px;border-radius:30px;color:#f4f2ff;font-size:12px;font-weight:600}
.pc-card{background:#fff;border:1px solid var(--line);border-radius:18px;padding:22px 23px;box-shadow:0 6px 22px #17255408;min-height:132px}
.pc-card-label{font-size:12px;color:#77839a;text-transform:uppercase;letter-spacing:.8px;font-weight:800}
.pc-card-value{font:800 32px Manrope;color:#15264a;margin-top:10px;letter-spacing:-.8px}
.pc-card-foot{font-size:13px;color:#8994a8;margin-top:7px}
.pc-section{font:800 19px Manrope;color:#15264a;letter-spacing:-.35px;margin:29px 0 8px}
.pc-muted{font-size:15px;color:#7c879d;line-height:1.55}
.pc-panel{background:#fff;border:1px solid var(--line);border-radius:19px;padding:23px 24px;box-shadow:0 6px 22px #17255407}
.pc-panel-title{font:800 17px Manrope;color:#15264a}
.pc-panel-sub{font-size:15px;color:#7c879d;margin-top:5px}
.pc-tag{display:inline-block;border-radius:30px;padding:6px 11px;font-size:12px;font-weight:800}
.pc-tag-good{background:#e7f6f1;color:#16866a}.pc-tag-warn{background:#fff4e3;color:#a86b18}.pc-tag-risk{background:#fcecef;color:#bd4d62}.pc-tag-violet{background:#f0eeff;color:#6655d8}
.pc-callout{border:1px solid #e3e0ff;background:#f7f6ff;border-radius:14px;padding:15px 17px;color:#505b7c;font-size:14px;line-height:1.7}
.pc-empty{padding:38px 24px;border:1px dashed #d4dbea;border-radius:16px;text-align:center;background:#fbfcff;color:#8994a8;font-size:15px}
.pc-evidence{border-left:4px solid #8175e4;background:#f8f7ff;padding:15px 17px;border-radius:0 12px 12px 0;font-size:14px;color:#465071;line-height:1.7}
/* Clear, accessible controls */
.stButton>button,.stDownloadButton>button{min-height:44px;border-radius:11px!important;padding:9px 17px!important;font-size:15px!important;font-weight:700!important;border:1px solid #d9dff0!important;color:#273858!important;background:#fff!important;transition:all .18s ease!important}
.stButton>button[kind="primary"],.stDownloadButton>button[kind="primary"]{background:linear-gradient(110deg,#5146bd,#7569df)!important;color:#fff!important;border:0!important;box-shadow:0 7px 17px #6d5ce733}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-1px);box-shadow:0 8px 20px #17255418;border-color:#aaa3e9!important}
.stButton>button:focus-visible,.stDownloadButton>button:focus-visible{outline:3px solid #aaa3e9!important;outline-offset:2px}
[data-testid="stFileUploader"] section{background:#fbfcff;border:1.5px dashed #c5cce0;border-radius:15px;padding:14px}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);padding:18px 20px;border-radius:16px;box-shadow:0 5px 18px #17255408}
[data-testid="stMetricLabel"] p{font-size:13px!important;text-transform:uppercase;letter-spacing:.65px;font-weight:800;color:#77839a!important}
[data-testid="stMetricValue"]{font:800 29px Manrope!important;color:#15264a!important}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:13px;overflow:hidden}
[data-testid="stExpander"]{border:1px solid var(--line);border-radius:13px;background:white}
[data-baseweb="input"] input,[data-baseweb="textarea"] textarea{border-radius:10px!important;font-size:15px!important}
[data-baseweb="select"]{font-size:15px!important}
[data-testid="stSidebar"] [role="radiogroup"]{gap:7px}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:11px 12px;border-radius:11px;border:1px solid transparent;font-size:15px!important}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#f6f5ff;border-color:#e8e3ff}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:#f0eeff;border-color:#dfdaff;color:#5146bd;font-weight:750}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p{font-size:13px}
[data-testid="stChatMessage"]{border:1px solid var(--line);border-radius:15px;padding:14px 17px;background:#fff}
[data-testid="stChatInput"] textarea{font-size:15px!important}
hr{border-color:var(--line)!important}
small{color:#8994a8}
@media(max-width:900px){[data-testid="stMainBlockContainer"]{padding:1.3rem 1rem 3rem}.pc-title{font-size:27px}.pc-hero{padding:25px;min-height:unset}.pc-hero-title{font-size:24px}}
[data-testid=\"stAppViewContainer\"]:has(option:checked[value=\"ar\"]){direction:rtl}
</style>
""", unsafe_allow_html=True)

# ---------- Language and state ----------
if "lang" not in st.session_state:
    st.session_state.lang = "fr"
if "document_text" not in st.session_state:
    st.session_state.document_text = ""
if "document_name" not in st.session_state:
    st.session_state.document_name = ""
if "audit_result" not in st.session_state:
    st.session_state.audit_result = None
if "chat" not in st.session_state:
    st.session_state.chat = []

LANG = st.session_state.lang
FR = LANG == "fr"
# Interface translations for the main navigation and frequent actions.
# Unmapped specialist descriptions fall back to English rather than being mistranslated.
LOCALES = {
    "de": {
        "Vue d’ensemble":"Übersicht", "Nouvel audit":"Neue Prüfung", "Assistant IA":"KI-Assistent",
        "Base documentaire":"Wissensdatenbank", "Historique":"Verlauf", "À propos":"Über PRIVACHECK",
        "Langue":"Sprache", "Espace d’analyse sécurisé":"Sicherer Analysebereich",
        "Audits réalisés":"Durchgeführte Prüfungen", "Documents analysés":"Analysierte Dokumente",
        "Indicateur moyen":"Durchschnittlicher Indikator", "Points à examiner":"Zu prüfende Punkte",
        "Importer un document":"Dokument importieren", "Choisir un fichier PDF, DOCX ou TXT":"PDF-, DOCX- oder TXT-Datei auswählen",
        "Ou coller directement le texte":"Oder Text direkt einfügen", "Extraire le texte":"Text extrahieren",
        "Texte extrait avec succès.":"Text erfolgreich extrahiert.", "Aperçu du document":"Dokumentvorschau",
        "Nom du document":"Dokumentname", "Lancer l’audit RGPD":"DSGVO-Prüfung starten",
        "Analyse terminée.":"Analyse abgeschlossen.", "Résultats de l’audit":"Prüfergebnisse",
        "Synthèse exécutive":"Zusammenfassung", "Preuves et recommandations":"Nachweise und Empfehlungen",
        "Télécharger le rapport PDF":"PDF-Bericht herunterladen", "Effacer la conversation":"Unterhaltung löschen",
        "Ajouter une source (PDF, DOCX, TXT)":"Quelle hinzufügen (PDF, DOCX, TXT)",
        "Indexer la source":"Quelle indexieren", "Supprimer":"Löschen", "Exporter l’historique CSV":"Verlauf als CSV exportieren",
        "Traitement local par défaut":"Lokale Verarbeitung standardmäßig", "À vérifier":"Zu prüfen",
    },
    "ar": {
        "Vue d’ensemble":"نظرة عامة", "Nouvel audit":"تدقيق جديد", "Assistant IA":"المساعد الذكي",
        "Base documentaire":"قاعدة المعرفة", "Historique":"السجل", "À propos":"حول التطبيق",
        "Langue":"اللغة", "Espace d’analyse sécurisé":"مساحة تحليل آمنة",
        "Audits réalisés":"عمليات التدقيق", "Documents analysés":"المستندات المحللة",
        "Indicateur moyen":"المؤشر المتوسط", "Points à examiner":"نقاط للمراجعة",
        "Importer un document":"استيراد مستند", "Choisir un fichier PDF, DOCX ou TXT":"اختر ملف PDF أو DOCX أو TXT",
        "Ou coller directement le texte":"أو ألصق النص مباشرة", "Extraire le texte":"استخراج النص",
        "Texte extrait avec succès.":"تم استخراج النص بنجاح.", "Aperçu du document":"معاينة المستند",
        "Nom du document":"اسم المستند", "Lancer l’audit RGPD":"بدء تدقيق GDPR",
        "Analyse terminée.":"اكتمل التحليل.", "Résultats de l’audit":"نتائج التدقيق",
        "Synthèse exécutive":"الملخص التنفيذي", "Preuves et recommandations":"الأدلة والتوصيات",
        "Télécharger le rapport PDF":"تحميل تقرير PDF", "Effacer la conversation":"مسح المحادثة",
        "Ajouter une source (PDF, DOCX, TXT)":"إضافة مصدر (PDF أو DOCX أو TXT)",
        "Indexer la source":"فهرسة المصدر", "Supprimer":"حذف", "Exporter l’historique CSV":"تصدير السجل CSV",
        "Traitement local par défaut":"المعالجة محلياً بشكل افتراضي", "À vérifier":"قيد المراجعة",
    }
}
def tx(fr, en):
    if LANG == "fr": return fr
    if LANG == "en": return en
    return LOCALES.get(LANG, {}).get(fr, en)

def header(kicker, title, desc):
    st.markdown(
        f'<div class="pc-eyebrow">{kicker}</div><div class="pc-title">{title}</div>'
        f'<div class="pc-desc">{desc}</div><div class="pc-rule"></div>',
        unsafe_allow_html=True
    )

def empty(msg):
    st.markdown(f'<div class="pc-empty">{msg}</div>', unsafe_allow_html=True)

def tag(text, kind="violet"):
    st.markdown(f'<span class="pc-tag pc-tag-{kind}">{text}</span>', unsafe_allow_html=True)

def card(label, value, foot):
    st.markdown(
        f'<div class="pc-card"><div class="pc-card-label">{label}</div>'
        f'<div class="pc-card-value">{value}</div><div class="pc-card-foot">{foot}</div></div>',
        unsafe_allow_html=True
    )

def safe_chart(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#59647f", size=11),
        margin=dict(l=8,r=8,t=18,b=8), legend_title_text="",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ---------- Sidebar ----------
with st.sidebar:
    brand_col, name_col = st.columns([1, 3], vertical_alignment="center")
    with brand_col:
        st.image(str(Path(__file__).parent / "assets" / "privacheck_logo.png"), width=54)
    with name_col:
        st.markdown('<div class="pc-brand-name">PRIVACHECK</div><div class="pc-brand-sub">ANALYSE · CONFORMITÉ · CONFIANCE</div>', unsafe_allow_html=True)
    st.selectbox(
        "🌐  " + tx("Langue", "Language"), ["fr", "en", "de", "ar"],
        format_func=lambda x: {"fr":"🇫🇷 Français", "en":"🇬🇧 English", "de":"🇩🇪 Deutsch", "ar":"🇸🇦 العربية"}[x],
        key="lang"
    )
    if st.session_state.lang == "ar":
        st.markdown("<style>[data-testid='stAppViewContainer']{direction:rtl}[data-testid='stSidebar']{direction:rtl}.stMarkdown{text-align:right}</style>", unsafe_allow_html=True)
    st.markdown('<div class="pc-muted" style="font-weight:800;letter-spacing:1px;margin:18px 0 7px">WORKSPACE</div>', unsafe_allow_html=True)
    pages = {
        "dashboard": tx("Vue d’ensemble", "Overview"),
        "audit": tx("Nouvel audit", "New audit"),
        "assistant": tx("Assistant IA", "AI assistant"),
        "knowledge": tx("Base documentaire", "Knowledge base"),
        "ml": "ML Analytics",
        "history": tx("Historique", "Audit history"),
        "about": tx("À propos", "About"),
    }
    page_key = st.radio(
        "Navigation", list(pages.keys()),
        format_func=lambda k: {
            "dashboard":"◫  "+pages[k], "audit":"＋  "+pages[k],
            "assistant":"✧  "+pages[k], "knowledge":"▤  "+pages[k],
            "ml":"⌁  "+pages[k], "history":"◷  "+pages[k], "about":"ⓘ  "+pages[k]
        }[k],
        label_visibility="collapsed"
    )
    st.divider()
    if llm_status()["configured"]:
        tag(tx("IA connectée", "AI connected"), "good")
    else:
        tag(tx("IA non configurée", "AI not configured"), "warn")
    st.caption(tx("Traitement local par défaut", "Local processing by default"))
    st.caption("PRIVACHECK AI · v2.0")

# ---------- Dashboard ----------
if page_key == "dashboard":
    st.markdown(
        f'<div class="pc-hero"><div class="pc-hero-kicker">PRIVACY GOVERNANCE · INTELLIGENCE</div>'
        f'<div class="pc-hero-title">{tx("La confidentialité, avec une vision plus claire.", "Privacy, with a clearer point of view.")}</div>'
        f'<div class="pc-hero-copy">{tx("Analysez les politiques de confidentialité, identifiez les éléments à examiner et appuyez vos décisions sur des sources documentaires.", "Review privacy policies, identify areas that need attention and support decisions with documentary evidence.")}</div>'
        f'<div class="pc-hero-chip">●  {tx("Espace d’analyse sécurisé", "Privacy review workspace")}</div></div>',
        unsafe_allow_html=True
    )
    st.markdown(f'<div class="pc-section">{tx("Vue d’ensemble", "Workspace overview")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pc-muted">{tx("Suivez l’activité et les indicateurs de vos analyses documentaires.", "Monitor activity and indicators from your document reviews.")}</div>', unsafe_allow_html=True)
    stats = get_dashboard_stats()
    c1,c2,c3,c4 = st.columns(4)
    with c1: card(tx("Audits réalisés","Audits performed"), stats["audits"], tx("Analyses enregistrées","Saved analyses"))
    with c2: card(tx("Documents analysés","Documents reviewed"), stats["documents"], tx("Un document par audit","One document per audit"))
    with c3: card(tx("Indicateur moyen","Average indicator"), f'{stats["average_score"]:.1f}%' if stats["average_score"] is not None else "—", tx("Repérage documentaire","Documentary screening"))
    with c4: card(tx("Points à examiner","Items to review"), stats["risk_items"], tx("Sur les audits enregistrés","Across saved audits"))
    audits = get_audit_payloads(limit=250)
    left,right = st.columns([1.35,1])
    with left:
        st.markdown(f'<div class="pc-section">{tx("Activité récente","Recent activity")}</div>',unsafe_allow_html=True)
        if audits:
            rows = [{"Document":x["title"],"Date":x["created_at"][:10],"Indicateur":round(x["score"],1)} for x in audits[:8]]
            df = pd.DataFrame(rows)
            fig = px.bar(df, x="Date", y="Indicateur", color_discrete_sequence=["#7868e8"], hover_data=["Document"])
            fig.update_traces(marker_line_width=0)
            fig.update_yaxes(range=[0,100],ticksuffix="%",gridcolor="#edf0f6",zeroline=False)
            fig.update_xaxes(showgrid=False)
            safe_chart(fig)
        else:
            empty(tx("Les activités apparaîtront ici après votre premier audit.", "Activity will appear here after your first audit."))
    with right:
        st.markdown(f'<div class="pc-section">{tx("État des critères","Criteria overview")}</div>',unsafe_allow_html=True)
        if audits:
            counts={"Mention repérée":0,"À vérifier":0}
            for a in audits:
                for item in a.get("details",[]):
                    if item.get("evidence"): counts["Mention repérée"]+=1
                    else: counts["À vérifier"]+=1
            dff=pd.DataFrame({"Statut":list(counts.keys()),"Nombre":list(counts.values())})
            fig=px.pie(dff,names="Statut",values="Nombre",hole=.72,color="Statut",
                       color_discrete_map={"Mention repérée":"#6d5ce7","À vérifier":"#e9a64b"})
            fig.update_traces(textinfo="none",marker=dict(line=dict(color="#fff",width=4)))
            safe_chart(fig)
            st.caption(tx("Les mentions détectées ne constituent pas une validation juridique.", "Detected mentions are not a legal compliance confirmation."))
        else:
            empty(tx("Aucune donnée disponible pour le moment.", "No data available yet."))
    st.markdown(f'<div class="pc-section">{tx("Derniers audits","Latest audits")}</div>',unsafe_allow_html=True)
    recent=list_audits(limit=7)
    if recent:
        st.dataframe(pd.DataFrame(recent),use_container_width=True,hide_index=True)
    else:
        st.info(tx("Commencez par importer une politique de confidentialité dans Nouvel audit.","Start by uploading a privacy policy under New audit."))

# ---------- New audit ----------
elif page_key == "audit":
    header("DOCUMENT REVIEW",tx("Nouvel audit documentaire","New document review"),
           tx("Importez une politique de confidentialité et obtenez un repérage structuré des critères RGPD.","Upload a privacy policy to receive a structured screening of GDPR-related criteria."))
    st.markdown('<div class="pc-panel">',unsafe_allow_html=True)
    st.markdown(f"**{tx('Importer un document','Upload a document')}**")
    uploaded=st.file_uploader(tx("Choisir un fichier PDF, DOCX ou TXT","Choose a PDF, DOCX or TXT file"),type=["pdf","docx","txt"])
    pasted=st.text_area(tx("Ou coller directement le texte","Or paste the text directly"),height=170,
                        placeholder=tx("Collez ici le contenu de la politique de confidentialité…","Paste the privacy policy text here…"))
    col_a,col_b=st.columns([1,3])
    with col_a:
        if st.button(tx("Extraire le texte","Extract text"),use_container_width=True):
            try:
                if uploaded:
                    extracted=extract_text(uploaded.name,uploaded.getvalue())
                    st.session_state.document_name=uploaded.name
                elif pasted.strip():
                    extracted=pasted.strip()
                    st.session_state.document_name=tx("Texte saisi manuellement","Pasted text")
                else:
                    extracted=""
                if extracted:
                    st.session_state.document_text=extracted
                    st.success(tx("Texte extrait avec succès.","Text extracted successfully."))
                else:
                    st.warning(tx("Importez un fichier ou collez un texte.","Upload a file or paste text."))
            except Exception as exc:
                st.error(f"{tx('Erreur d’extraction','Extraction error')}: {exc}")
    with col_b:
        if st.session_state.document_text:
            st.caption(f"{len(st.session_state.document_text):,} {tx('caractères extraits','characters extracted')}")
    st.markdown('</div>',unsafe_allow_html=True)

    if st.session_state.document_text:
        with st.expander(tx("Aperçu du document","Document preview"),expanded=False):
            st.text_area(" ",st.session_state.document_text[:24000],height=230,disabled=True)
        title=st.text_input(tx("Nom du document","Document title"),value=st.session_state.document_name or "Privacy Policy")
        if st.button(tx("Lancer l’audit RGPD","Run GDPR screening"),type="primary"):
            try:
                st.session_state.audit_result=run_audit(st.session_state.document_text,title,st.session_state.lang)
                st.success(tx("Analyse terminée.","Screening completed."))
            except Exception as exc:
                st.error(str(exc))

    result=st.session_state.audit_result
    if result:
        st.markdown(f'<div class="pc-section">{tx("Résultats de l’audit","Review results")}</div>',unsafe_allow_html=True)
        score=result["score"]
        a,b,c=st.columns([1,1,1])
        with a: st.metric(tx("Indicateur documentaire","Documentary indicator"),f"{score:.1f}%")
        with b: st.metric(tx("Mentions repérées","Mentions detected"),result["counts"]["partial"])
        with c: st.metric(tx("Non identifiés","Not identified"),result["counts"]["risk"])
        st.markdown(f'<div class="pc-callout">ⓘ {tx("Cet indicateur mesure uniquement la présence de mentions textuelles. Il ne constitue ni une certification ni une conclusion juridique.","This indicator only measures the presence of textual mentions. It is not a certification or legal conclusion.")}</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="pc-section">{tx("Synthèse exécutive","Executive summary")}</div>',unsafe_allow_html=True)
        st.write(result["summary"])
        table=pd.DataFrame([{"Critère":x["criterion"],"Repérage":x["status"],"Référence":x["reference"]} for x in result["details"]])
        st.dataframe(table,use_container_width=True,hide_index=True)
        st.markdown(f'<div class="pc-section">{tx("Preuves et recommandations","Evidence and recommendations")}</div>',unsafe_allow_html=True)
        for item in result["details"]:
            with st.expander(f"{item['criterion']} · {item['status']}"):
                st.markdown(f'<div class="pc-evidence">{html.escape(item["evidence"] or tx("Aucun passage explicite identifié.","No explicit passage identified."))}</div>',unsafe_allow_html=True)
                st.caption(item["reference"])
                st.write(item["note"])
        with st.expander(tx("Recommandations générales","General recommendations"),expanded=True):
            for rec in result["recommendations"]:
                st.markdown(f"- {rec}")
        pdf=generate_pdf(result,st.session_state.lang)
        st.download_button(tx("Télécharger le rapport PDF","Download PDF report"),pdf,
                           file_name="privacheck_audit_report.pdf",mime="application/pdf",type="primary")

# ---------- RAG Assistant ----------
elif page_key == "assistant":
    header("RAG INTELLIGENCE",tx("Assistant confidentialité","Privacy assistant"),
           tx("Posez vos questions sur le RGPD et obtenez des réponses appuyées par les sources de la base documentaire.","Ask questions about GDPR and receive answers grounded in your knowledge base."))
    st.markdown(f'<div class="pc-callout">{tx("Les réponses sont générées à partir des passages retrouvés. Vérifiez toujours les références officielles et le contexte juridique.","Answers are generated from retrieved passages. Always verify official references and legal context.")}</div>',unsafe_allow_html=True)
    if not st.session_state.chat:
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown(f'<div class="pc-panel"><div class="pc-panel-title">✧ PRIVACHECK AI</div><div class="pc-panel-sub">{tx("Assistant documentaire basé sur le RAG","RAG-powered document assistant")}</div><br>{tx("Vous pouvez commencer par demander :","You can start by asking:")}<br><br>• {tx("Quelles sont les informations à fournir selon l’article 13 ?","What information must be provided under Article 13?")}<br>• {tx("Quels droits sont mentionnés dans le document analysé ?","Which rights are mentioned in the reviewed document?")}<br>• {tx("Comment fonctionne la durée de conservation ?","How do retention periods work?")}</div>',unsafe_allow_html=True)
    for msg in st.session_state.chat:
       with st.chat_message(
    msg["role"],
    avatar="assistant" if msg["role"] == "assistant" else "user"
):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(tx("Sources retrouvées","Retrieved sources")):
                    for source in msg["sources"]:
                        st.markdown(f"**{source['source']}** · score TF-IDF {source['score']:.3f}")
                        st.caption(source["text"][:900])
    prompt=st.chat_input(tx("Posez une question sur le RGPD…","Ask a GDPR question…"))
    if prompt:
        st.session_state.chat.append({"role":"user","content":prompt})
        hits=retrieve(prompt,top_k=4)
        with st.spinner(tx("Recherche dans la base documentaire…","Searching the knowledge base…")):
            answer=answer_question(prompt,st.session_state.lang,st.session_state.document_text)
        st.session_state.chat.append({"role":"assistant","content":answer,"sources":hits})
        st.rerun()
    if st.button(tx("Effacer la conversation","Clear conversation")):
        st.session_state.chat=[]
        st.rerun()

# ---------- Knowledge base ----------
elif page_key == "knowledge":
    header("KNOWLEDGE CENTER",tx("Base documentaire","Knowledge base"),
           tx("Centralisez les textes de référence utilisés par le moteur de recherche RAG.","Manage the reference documents used by the RAG retrieval engine."))
    st.markdown(f'<div class="pc-callout">{tx("Privilégiez les textes officiels et les guides institutionnels à jour. Les documents importés sont enregistrés dans la base SQLite locale.","Prefer current official legal texts and institutional guidance. Uploaded files are stored in the local SQLite database.")}</div>',unsafe_allow_html=True)
    uploaded=st.file_uploader(tx("Ajouter une source (PDF, DOCX, TXT)","Add a source (PDF, DOCX, TXT)"),type=["pdf","docx","txt"],key="knowledge_upload")
    if uploaded and st.button(tx("Indexer la source","Index source"),type="primary"):
        try:
            content=extract_text(uploaded.name,uploaded.getvalue())
            add_knowledge_file(uploaded.name,content)
            st.success(tx("Source ajoutée à la base documentaire.","Source added to the knowledge base."))
            st.rerun()
        except Exception as exc:
            st.error(str(exc))
    sources=get_knowledge()
    st.markdown(f'<div class="pc-section">{tx("Sources disponibles","Available sources")} · {len(sources)}</div>',unsafe_allow_html=True)
    if sources:
        for source in sources:
            col1,col2=st.columns([5,1])
            with col1:
                st.markdown(f"**▤ {source['filename']}**")
                st.caption(f"{source['added_at']} · {len(source['content']):,} {tx('caractères','characters')}")
            with col2:
                if st.button(tx("Supprimer","Delete"),key=f"del_{source['id']}"):
                    delete_knowledge(source["id"])
                    st.rerun()
            st.divider()
    else:
        empty(tx("Aucune source ajoutée. Ajoutez le RGPD et des guides CNIL pour enrichir le RAG.","No sources added. Add GDPR and supervisory authority guidance to enrich RAG."))
    st.markdown("**Official references**")
    st.markdown("- [Texte officiel du RGPD — EUR-Lex](https://eur-lex.europa.eu/eli/reg/2016/679/oj)")
    st.markdown("- [Guide RGPD — CNIL](https://www.cnil.fr/fr/rgpd-guide)")

# ---------- ML Analytics ----------
elif page_key == "ml":
    header("MACHINE LEARNING LAB","ML Analytics",
           tx("Classification NLP des paragraphes de politiques de confidentialité. Le modèle est entraîné et évalué sur un jeu de données annoté.","NLP classification of privacy-policy paragraphs. The model is trained and evaluated on a labeled dataset."))
    st.markdown(f'<div class="pc-callout">ⓘ {tx("Le dataset inclus est un jeu de démonstration construit pour tester le pipeline. Les performances ne prouvent pas une capacité de décision juridique et ne doivent pas être présentées comme une validation RGPD.","The included dataset is an illustrative demo set for testing the pipeline. Its metrics do not establish legal decision-making capability or GDPR compliance validation.")}</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="pc-section">{tx("1. Entraîner le classificateur","1. Train the classifier")}</div>',unsafe_allow_html=True)
    st.write(tx("Algorithme : TF-IDF + Linear Support Vector Machine (LinearSVC).","Algorithm: TF-IDF + Linear Support Vector Machine (LinearSVC)."))
    custom=st.file_uploader(tx("Dataset annoté personnalisé (CSV facultatif)","Custom labeled dataset (optional CSV)"),type=["csv"],key="ml_dataset")
    st.caption(tx("Format requis : deux colonnes text et label, avec au moins 4 exemples par classe.","Required format: two columns text and label, with at least 4 examples per class."))
    if st.button(tx("Entraîner le modèle","Train model"),type="primary"):
        temp_path=None
        try:
            if custom:
                temp_path=Path("data")/"custom_ml_dataset.csv"
                temp_path.parent.mkdir(exist_ok=True)
                temp_path.write_bytes(custom.getvalue())
            with st.spinner(tx("Entraînement et évaluation…","Training and evaluation…")):
                metrics=train_model(temp_path)
            st.success(tx("Modèle entraîné et sauvegardé.","Model trained and saved."))
        except Exception as exc:
            st.error(f"{tx('Entraînement impossible','Training failed')}: {exc}")
    metrics=load_evaluation()
    if metrics:
        st.markdown(f'<div class="pc-section">{tx("2. Évaluation du modèle","2. Model evaluation")}</div>',unsafe_allow_html=True)
        m1,m2,m3,m4=st.columns(4)
        m1.metric("Accuracy",f"{metrics['accuracy']*100:.1f}%")
        m2.metric("Train samples",metrics["train_size"])
        m3.metric("Test samples",metrics["test_size"])
        m4.metric(tx("Classes","Classes"),len(metrics["labels"]))
        st.caption(f"Dataset: {metrics['source']} · {metrics['dataset_size']} {tx('exemples','samples')}")
        st.markdown(f'<div class="pc-section">{tx("Rapport par classe","Per-class report")}</div>',unsafe_allow_html=True)
        report=[]
        for label in metrics["labels"]:
            r=metrics["report"].get(label,{})
            report.append({"Classe":label,"Precision":round(r.get("precision",0),3),"Recall":round(r.get("recall",0),3),"F1-score":round(r.get("f1-score",0),3),"Support":int(r.get("support",0))})
        st.dataframe(pd.DataFrame(report),use_container_width=True,hide_index=True)
        cm=pd.DataFrame(metrics["confusion_matrix"],index=metrics["labels"],columns=metrics["labels"])
        fig=px.imshow(cm,text_auto=True,aspect="auto",color_continuous_scale=["#f4f2ff","#6d5ce7"],labels=dict(x="Predicted",y="Actual",color="Samples"))
        fig.update_layout(height=480)
        st.markdown(f'<div class="pc-section">{tx("Matrice de confusion","Confusion matrix")}</div>',unsafe_allow_html=True)
        safe_chart(fig)
        st.markdown(f'<div class="pc-section">{tx("Importance des caractéristiques","Feature importance")}</div>',unsafe_allow_html=True)
        importance = feature_importance(top_n=6)
        if importance:
            imp_df = pd.DataFrame(importance)
            selected_class = st.selectbox(tx("Catégorie","Category"), sorted(imp_df["category"].unique()))
            class_df = imp_df[imp_df["category"] == selected_class].sort_values("weight", ascending=True)
            fig_imp = px.bar(class_df, x="weight", y="term", orientation="h", color_discrete_sequence=["#7868e8"])
            fig_imp.update_layout(height=270)
            fig_imp.update_xaxes(showgrid=True, gridcolor="#edf0f6", zeroline=False)
            fig_imp.update_yaxes(title="")
            safe_chart(fig_imp)
        st.markdown(f'<div class="pc-callout">{metrics["warning"]}</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="pc-section">{tx("3. Classifier le document courant","3. Classify the current document")}</div>',unsafe_allow_html=True)
        if st.session_state.document_text:
            if st.button(tx("Classifier les paragraphes du document chargé","Classify paragraphs from loaded document")):
                try:
                    st.session_state.ml_predictions=predict_document(st.session_state.document_text)
                except Exception as exc:
                    st.error(str(exc))
            predictions=st.session_state.get("ml_predictions",[])
            if predictions:
                pred_df=pd.DataFrame([{"Paragraph":p["text"][:180]+"…" if len(p["text"])>180 else p["text"],"Predicted category":p["category"],"Decision margin":round(p["decision_margin"],3)} for p in predictions])
                st.dataframe(pred_df,use_container_width=True,hide_index=True)
                st.caption(tx("Decision margin = écart des scores internes du classificateur, pas une probabilité ni un niveau de confiance calibré.","Decision margin = gap between internal classifier scores, not a probability or calibrated confidence level."))
        else:
            st.info(tx("Chargez d’abord un document dans Nouvel audit pour activer la classification.","Load a document under New audit to enable classification."))
    else:
        empty(tx("Aucun modèle entraîné. Lancez l’entraînement pour créer votre premier classificateur.","No trained model yet. Run training to create your first classifier."))

# ---------- History ----------
elif page_key == "history":
    header("AUDIT ARCHIVE",tx("Historique des audits","Audit history"),
           tx("Consultez les analyses enregistrées dans la base locale.","Browse analyses saved in the local database."))
    history=list_audits(limit=250)
    if history:
        df=pd.DataFrame(history)
        st.dataframe(df,use_container_width=True,hide_index=True)
        csv=df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(tx("Exporter l’historique CSV","Export history CSV"),csv,"privacheck_history.csv","text/csv")
    else:
        empty(tx("Aucun audit enregistré pour le moment.","No audits have been saved yet."))

# ---------- About ----------
elif page_key == "about":
    header("ABOUT PRIVACHECK",tx("Une plateforme d’aide à l’analyse documentaire","A platform for documentary privacy review"),
           tx("PRIVACHECK AI combine des méthodes NLP, un moteur de recherche documentaire et une assistance IA pour faciliter le repérage des informations relatives à la confidentialité.","PRIVACHECK AI combines NLP methods, document retrieval and AI assistance to support the review of privacy-related information."))
    st.image(str(Path(__file__).parent / "assets" / "privacheck_logo.png"), width=360)
    a,b=st.columns(2)
    with a:
        st.markdown('<div class="pc-panel"><div class="pc-panel-title">Technology stack</div><br>• Python & Streamlit<br>• NLP · TF-IDF · LinearSVC<br>• RAG · TF-IDF retrieval<br>• LLM API integration<br>• SQLite · PDF reporting</div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="pc-panel"><div class="pc-panel-title">Core modules</div><br>• Document processing<br>• Explainable rule-based screening<br>• Retrieval-augmented assistant<br>• Supervised text classification<br>• Audit history and reporting</div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    st.warning(tx("PRIVACHECK AI est un prototype pédagogique. Il ne remplace pas un DPO, un conseil juridique, une analyse d’impact ou un audit complet de conformité. L’absence d’une mention dans une politique ne prouve pas une violation du RGPD.","PRIVACHECK AI is an educational prototype. It does not replace a DPO, legal advice, a data protection impact assessment or a full compliance audit. Missing wording in a policy does not prove a GDPR violation."))
