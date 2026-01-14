from fastapi import FastAPI
from pydantic import BaseModel
import json
import os

app = FastAPI()

# -----------------------------
# CARICAMENTO CORPUS SPIRITUALE
# -----------------------------

def load_corpus():
    corpus_path = os.path.join(os.path.dirname(__file__), "corpus.json")
    with open(corpus_path, "r", encoding="utf-8") as f:
        return json.load(f)

corpus = load_corpus()

def get_messages_by_tema(tema: str):
    risultati = [item for item in corpus if item["tema"] == tema]
    return risultati

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
# MODELLI
# -----------------------------

class AskRequest(BaseModel):
    question: str

class SpiritualAnswer(BaseModel):
    answer: str
    source: str
    explanation: str
    category: str

# -----------------------------
# REGOLE DI RISPOSTA
# -----------------------------

rules = [
    # DOTTRINA / DIVINAZIONE
    {
        "keywords": ["tarocchi", "oroscopo", "magia", "cartomanzia", "medium", "divinazione"],
        "answer": "La Chiesa invita a evitare ogni forma di divinazione.",
        "source": "Catechismo della Chiesa Cattolica, 2116",
        "explanation": "La divinazione contraddice l'affidamento fiducioso a Dio.",
        "category": "Dottrina"
    },

    # SOFFERENZA
    {
        "keywords": ["sofferenza", "dolore", "malattia", "croce", "patire"],
        "answer": "Unisci la tua sofferenza a quella di Cristo.",
        "source": "Colossesi 1,24",
        "explanation": "La sofferenza, vissuta con Cristo, diventa partecipazione alla sua opera redentrice.",
        "category": "Sofferenza e Croce"
    },

    # PAURA / ANSIA
    {
        "keywords": ["paura", "ansia", "angoscia", "preoccupazione", "timore"],
        "answer": "Non temere, Dio è con te.",
        "source": "Isaia 41,10",
        "explanation": "La presenza di Dio dona forza e pace nei momenti difficili.",
        "category": "Consolazione"
    },

    # PERDONO / PECCATO
    {
        "keywords": ["perdono", "colpa", "peccato", "confessione", "misericordia"],
        "answer": "Dio è misericordioso e sempre pronto a perdonare.",
        "source": "Luca 15,11-32",
        "explanation": "Come il Padre del figliol prodigo, Dio accoglie chi torna a Lui.",
        "category": "Misericordia"
    },

    # VOCAZIONE / DISCERNIMENTO
    {
        "keywords": ["vocazione", "chiamata", "discernimento", "volontà di dio"],
        "answer": "Ascolta la voce di Dio nel silenzio e nella preghiera.",
        "source": "1 Samuele 3,10",
        "explanation": "Il discernimento nasce dall'ascolto profondo della volontà di Dio.",
        "category": "Discernimento"
    },

    # SPERANZA
    {
        "keywords": ["speranza", "fiducia", "scoraggiamento", "disperazione"],
        "answer": "La speranza cristiana non delude.",
        "source": "Romani 5,5",
        "explanation": "Lo Spirito Santo infonde nei cuori la speranza che sostiene nelle prove.",
        "category": "Speranza"
    },

    # PREGHIERA
    {
        "keywords": ["preghiera", "pregare", "rosario", "adorazione"],
        "answer": "La preghiera è respiro dell'anima.",
        "source": "Catechismo della Chiesa Cattolica, 2559",
        "explanation": "La preghiera è l'umile incontro tra la sete di Dio e la sete dell'uomo.",
        "category": "Preghiera"
    },

    # CARITÀ / AMORE
    {
        "keywords": ["amore", "carità", "prossimo", "aiutare"],
        "answer": "Ama il prossimo tuo come te stesso.",
        "source": "Marco 12,31",
        "explanation": "La carità è il cuore della vita cristiana.",
        "category": "Carità"
    },

    # FEDE / DUBBI
    {
        "keywords": ["fede", "credere", "dubbio", "incredulità"],
        "answer": "La fede cresce chiedendola a Dio.",
        "source": "Marco 9,24",
        "explanation": "Anche chi dubita può dire: 'Credo, aiutami nella mia incredulità'.",
        "category": "Fede"
    },

    # SPIRITO SANTO
    {
        "keywords": ["spirito santo", "consolatore", "dono", "carismi"],
        "answer": "Lo Spirito Santo ti guida nella verità.",
        "source": "Giovanni 16,13",
        "explanation": "È lo Spirito che illumina il cuore e dona pace.",
        "category": "Spirito Santo"
    },

    # RELAZIONI / FAMIGLIA
    {
        "keywords": ["matrimonio", "famiglia", "relazione", "fidanzamento", "conflitto"],
        "answer": "L’amore vero è paziente e misericordioso.",
        "source": "1 Corinzi 13,4-7",
        "explanation": "La carità è il fondamento di ogni relazione cristiana.",
        "category": "Relazioni"
    },

    # LOTTA SPIRITUALE
    {
        "keywords": ["tentazione", "peccato", "demonio", "lotta", "caduta"],
        "answer": "Dio ti dà la forza per resistere alla tentazione.",
        "source": "1 Corinzi 10,13",
        "explanation": "Nessuna prova supera le tue forze se ti affidi a Dio.",
        "category": "Lotta spirituale"
    },

    # CRESCITA SPIRITUALE
    {
        "keywords": ["crescita", "migliorare", "conversione", "cammino", "santità"],
        "answer": "La santità cresce un passo alla volta.",
        "source": "Gaudete et Exsultate",
        "explanation": "Dio ti guida nel cammino quotidiano verso la santità.",
        "category": "Crescita spirituale"
    },

    # PACE E GIUSTIZIA
    {
        "keywords": ["guerra", "pace", "ingiustizia", "violenza", "male"],
        "answer": "Beati gli operatori di pace.",
        "source": "Matteo 5,9",
        "explanation": "La pace nasce da cuori riconciliati con Dio.",
        "category": "Pace e Giustizia"
    },

    # MARIA E I SANTI
    {
        "keywords": ["maria", "madonna", "santi", "intercessione"],
        "answer": "Maria ti accompagna come Madre.",
        "source": "Giovanni 19,27",
        "explanation": "La devozione mariana conduce sempre a Cristo.",
        "category": "Devozione"
    },

    # SACRAMENTI
    {
        "keywords": ["sacramenti", "eucaristia", "comunione", "battesimo"],
        "answer": "I sacramenti sono incontri reali con Cristo.",
        "source": "Catechismo della Chiesa Cattolica, 1116",
        "explanation": "Attraverso i sacramenti, Cristo agisce nella tua vita.",
        "category": "Sacramenti"
    },

    # SENSO DELLA VITA
    {
        "keywords": ["senso", "scopo", "vita", "esistenza", "vuoto"],
        "answer": "La tua vita ha un valore infinito agli occhi di Dio.",
        "source": "Salmo 139,14",
        "explanation": "Dio ti ha creato per amore e per un fine unico.",
        "category": "Senso della vita"
    }
]

# -----------------------------
# ENDPOINT PRINCIPALE
# -----------------------------

@app.post("/api/ask", response_model=SpiritualAnswer)
async def ask_question(request: AskRequest):
    question = request.question.lower()

    for rule in rules:
        if any(keyword in question for keyword in rule["keywords"]):
            return SpiritualAnswer(
                answer=rule["answer"],
                source=rule["source"],
                explanation=rule["explanation"],
                category=rule["category"]
            )

    return SpiritualAnswer(
        answer="Cerca prima il Regno di Dio.",
        source="Matteo 6,33",
        explanation="Dio guida chi si affida a Lui.",
        category="Generale"
    )

# -----------------------------
# ENDPOINT DI TEST CORPUS
# -----------------------------

@app.get("/test-corpus")
def test_corpus():
    return {
        "corpus_size": len(corpus),
        "first_item": corpus[0] if corpus else None
    }

# -----------------------------
# ENDPOINT DI TEST CLASSIFICATORE
# -----------------------------

@app.get("/test-classify")
def test_classify(q: str):
    tema = classify_tema(q)
    return {
        "tema": tema,
        "messaggi": get_messages_by_tema(tema)
    }
