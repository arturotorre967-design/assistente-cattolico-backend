from fastapi import FastAPI
from pydantic import BaseModel
import json
import os
import requests

app = FastAPI()

# -----------------------------
# TEST LETTURA CHIAVE GROQ
# -----------------------------
@app.get("/test-key")
def test_key():
    return {"groq_key": os.getenv("GROQ_API_KEY")}

# -----------------------------
# CONFIGURAZIONE GROQ
# -----------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

# -----------------------------
# CARICAMENTO CORPUS SPIRITUALE
# -----------------------------

def load_corpus():
    corpus_path = os.path.join(os.path.dirname(__file__), "corpus.json")
    with open(corpus_path, "r", encoding="utf-8") as f:
        return json.load(f)

corpus = load_corpus()

def get_messages_by_tema(tema: str):
    return [item for item in corpus if item["tema"] == tema]

# -----------------------------
# CLASSIFICATORE DI TEMA
# -----------------------------

tema_keywords = {
    "paura": ["paura", "ansia", "angoscia", "timore", "preoccupazione"],
    "solitudine": ["solo", "solitudine", "abbandonato"],
    "colpa": ["colpa", "peccato", "sbagliato", "vergogna"],
    "tristezza": ["triste", "tristezza", "piangere", "lacrime"],
    "gioia": ["gioia", "felice", "ringraziare"],
    "amore": ["amore", "amare", "voler bene"],
    "fedeltà": ["fedeltà", "tradimento", "costanza"],
    "coraggio": ["coraggio", "forza", "affrontare"],
    "discernimento": ["discernere", "discernimento", "decisione", "volontà di dio"],
    "pazienza": ["pazienza", "attendere", "sopportare"],
    "silenzio": ["silenzio", "tacere", "interiorità"],
    "speranza": ["speranza", "disperazione", "scoraggiamento"],
    "prova_sofferenza": ["sofferenza", "dolore", "prova", "croce"],
    "perdono": ["perdonare", "perdono", "misericordia"],
    "umiltà": ["umile", "umiltà", "orgoglio"],
    "gratitudine": ["grazie", "gratitudine", "riconoscenza"],
    "tentazione": ["tentazione", "tentato", "cadere"],
    "vocazione": ["vocazione", "chiamata", "volontà di dio"]
}

def classify_tema(question: str):
    q = question.lower()
    for tema, keywords in tema_keywords.items():
        if any(k in q for k in keywords):
            return tema
    return "generale"

# -----------------------------
# MOTORE SPIRITUALE SUPERVISIONATO (VERSIONE v5)
# -----------------------------

def generate_supervised_answer_v5(question: str):
    tema = classify_tema(question)
    messaggi = get_messages_by_tema(tema)

    temi_delicati = ["paura", "solitudine", "colpa", "tristezza", "prova_sofferenza", "tentazione"]

    preghiere = {
        "paura": "Signore, posa la Tua mano su questo cuore inquieto e donagli respiro.",
        "solitudine": "Signore, avvolgi con la Tua presenza chi si sente smarrito e solo.",
        "colpa": "Signore, riversa la Tua misericordia e sciogli ogni nodo del cuore.",
        "tristezza": "Signore, asciuga le lacrime e accendi una piccola luce nella notte.",
        "prova_sofferenza": "Signore, sostieni chi porta una croce pesante e dona forza nel cammino.",
        "tentazione": "Signore, rafforza questo cuore e guidalo nella fedeltà e nella pace."
    }

    intensita_alta = any(
        word in question.lower()
        for word in ["tantissimo", "molto", "troppo", "non ce la faccio", "distrutto", "a pezzi"]
    )

    prima_persona = any(
        word in question.lower()
        for word in ["io", "mi sento", "sto vivendo", "non riesco", "ho paura", "mi sembra"]
    )

    domanda_diretta = any(
        word in question.lower()
        for word in ["cosa devo fare", "come faccio", "perché succede", "come andare avanti"]
    )

    if not messaggi:
        risposta = (
            "🌿 **Accoglienza**\n"
            "In questo momento il tuo cuore cerca luce. Respira lentamente: Dio è vicino.\n\n"
            "✨ **Illuminazione**\n"
            "Anche quando tutto sembra fermo, una piccola scintilla di speranza continua a brillare.\n\n"
            "📖 **Luce della Scrittura**\n"
            "*Proverbi 3,5*\n\n"
            "🕊️ **Benedizione finale**\n"
            "Che una pace silenziosa scenda su di te e ti accompagni."
        )
        return {
            "answer": risposta,
            "source": "Proverbi 3,5",
            "explanation": "La fiducia in Dio sostiene nei momenti di oscurità.",
            "category": "Generale"
        }

    m = messaggi[0]

    # (continua con la tua Parte 2 identica…)
