
import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Clé Gemini introuvable dans .env")

client = genai.Client(api_key=api_key)

for attempt in range(3):
    try:
        print("Connexion à Gemini...")

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="Explique le RGPD en trois phrases."
        )

        print("\nRéponse de Gemini :\n")
        print(response.text)
        break

    except Exception as e:
        print(f"Tentative {attempt + 1} échouée : {e}")

        if attempt < 2:
            time.sleep(10 * (attempt + 1))
        else:
            print("Le service Gemini est momentanément indisponible.")
