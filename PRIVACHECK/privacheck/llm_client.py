import os, requests

def llm_status():
    return {"configured": bool(os.getenv("LLM_API_KEY")) and os.getenv("ENABLE_LLM","true").lower()=="true"}

def _chat(messages):
    key = os.getenv("LLM_API_KEY","").strip()
    if not key or os.getenv("ENABLE_LLM","true").lower() != "true":
        return None
    base = os.getenv("LLM_BASE_URL","https://api.openai.com/v1").rstrip("/")
    model = os.getenv("LLM_MODEL","gpt-4o-mini")
    timeout = int(os.getenv("LLM_TIMEOUT","60"))
    response = requests.post(
        base + "/chat/completions",
        headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
        json={"model":model,"messages":messages,"temperature":0.2},
        timeout=timeout
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()

def generate_answer(question, context, lang="fr"):
    language_name = {"fr": "French", "en": "English", "de": "German", "ar": "Arabic"}.get(lang, "English")
    system = (
        "You are PRIVACHECK AI, an educational GDPR document assistant. "
        "Answer only from the supplied context. Clearly distinguish GDPR legal text, guidance, and document evidence. "
        "Never claim that a company is compliant or non-compliant based only on a privacy notice. "
        "If evidence is missing, say so. Cite source names. Do not invent article wording. "
        f"This is not legal advice. Reply in {language_name}."
    )
    user = f"REFERENCE CONTEXT:\n{context}\n\nQUESTION:\n{question}"
    try:
        return _chat([{"role":"system","content":system},{"role":"user","content":user}])
    except Exception as exc:
        return None
