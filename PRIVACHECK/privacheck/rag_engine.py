from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .database import add_knowledge, get_knowledge
from .llm_client import generate_answer
from .config import DATA_DIR
import re

SEED_SOURCES = [
("GDPR Articles 12-14", """GDPR Article 12 requires transparent, intelligible and easily accessible information and communication. Article 13 applies when personal data are collected from the data subject and lists information to provide, including controller identity, purposes, legal basis, recipients, retention, rights and the right to lodge a complaint. Article 14 concerns information when personal data have not been obtained from the data subject."""),
("GDPR Articles 15-22", """GDPR Articles 15 to 22 address data subject rights: access, rectification, erasure, restriction, data portability, objection and safeguards related to automated individual decision-making, including profiling. The conditions and exceptions in the Regulation must be checked."""),
("GDPR Articles 32 and 44-49", """GDPR Article 32 concerns security of processing and appropriate technical and organisational measures. Articles 44 to 49 govern transfers of personal data to third countries or international organisations. The applicable transfer mechanism and circumstances must be assessed."""),
("CNIL guidance reminder", """CNIL guidance explains practical approaches to transparency, data minimisation, retention, security and the exercise of data subject rights. Guidance should be checked in its current official version before making a compliance conclusion.""")
]

def _ensure_seed():
    existing = get_knowledge()
    names = {x["filename"] for x in existing}
    for name, content in SEED_SOURCES:
        if name not in names:
            add_knowledge(name, content, datetime.now().isoformat(timespec="seconds"))

def add_knowledge_file(filename, content):
    add_knowledge(filename, content, datetime.now().isoformat(timespec="seconds"))

def list_knowledge_files():
    _ensure_seed()
    rows = get_knowledge()
    return [{"ID":r["id"],"Source":r["filename"],"Ajouté le":r["added_at"]} for r in rows]

def retrieve(query, top_k=4):
    _ensure_seed()
    rows = get_knowledge()
    chunks, metadata = [], []
    for row in rows:
        # Basic paragraph chunking; suitable as a starter RAG corpus.
        for chunk in re.split(r"\n{2,}", row["content"]):
            if chunk.strip():
                chunks.append(chunk.strip())
                metadata.append(row["filename"])
    if not chunks:
        return []
    vectorizer = TfidfVectorizer(ngram_range=(1,2), stop_words=None)
    matrix = vectorizer.fit_transform(chunks + [query])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    best = scores.argsort()[::-1][:top_k]
    return [{"text":chunks[i],"source":metadata[i],"score":float(scores[i])} for i in best if scores[i] > 0]

def answer_question(question, lang="fr", document_text=""):
    hits = retrieve(question)
    context = "\n\n".join(f"[Source: {h['source']}]\n{h['text']}" for h in hits)
    if document_text:
        context += "\n\n[Document currently analyzed]\n" + document_text[:7000]
    if not context:
        context = "No relevant reference passage was retrieved."
    answer = generate_answer(question, context, lang)
    if answer:
        return answer
    if hits:
        excerpts = "\n\n".join(f"**{h['source']}**\n{h['text']}" for h in hits)
        return (("Je n'ai pas pu interroger le modèle IA. Voici les passages retrouvés :\n\n" if lang=="fr" else
                 "The AI model could not be reached. Retrieved passages:\n\n") + excerpts)
    return ("Aucune source pertinente n'a été retrouvée. Ajoutez le texte officiel du RGPD ou un guide CNIL dans la base documentaire."
            if lang=="fr" else "No relevant source was retrieved. Add the official GDPR text or CNIL guidance to the knowledge base.")
