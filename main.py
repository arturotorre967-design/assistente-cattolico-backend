from fastapi import FastAPI
from pydantic import BaseModel
import json
import os
import requests

app = FastAPI()

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

    if intensita_alta:
        accoglienza = (
            "🌿 **Accoglienza**\n"
            "Sento la profondità del tuo dolore. È come una nube pesante che ti avvolge, "
            "ma anche nelle nubi più scure una luce sottile continua a filtrare.\n\n"
        )
    elif prima_persona:
        accoglienza = (
            "🌿 **Accoglienza**\n"
            "Tu stai attraversando un tratto di strada impegnativo. Non sei solo: "
            "Dio cammina accanto a te, anche quando i passi si fanno incerti.\n\n"
        )
    else:
        accoglienza = (
            "🌿 **Accoglienza**\n"
            f"Nel tuo cuore affiora il tema della **{m['tema']}**. Fermati un istante, respira, "
            "lascia che una luce gentile ti raggiunga.\n\n"
        )

    illuminazione = (
        "✨ **Illuminazione dal corpus**\n"
        f"{m['messaggio']} {m['nota']}\n"
        "Lascia che queste parole scendano lentamente nel cuore, come una goccia di pace.\n\n"
    )

    scrittura = (
        "📖 **Luce della Scrittura**\n"
        f"*{m['fonte']}*\n"
        "La Parola è come un raggio che attraversa la notte e apre un varco di speranza.\n\n"
    )

    preghiera = ""
    if tema in temi_delicati:
        preghiera = (
            "🙏 **Preghiera breve**\n"
            f"{preghiere[tema]}\n"
            "Ripeti queste parole lentamente, come un respiro dell’anima.\n\n"
        )

    passo_concreto = ""
    if domanda_diretta:
        passo_concreto = (
            "🌱 **Un passo concreto**\n"
            "Oggi prova a fermarti un minuto in silenzio. Metti una mano sul petto, "
            "chiudi gli occhi e ripeti: *“Signore, guidami Tu.”*\n\n"
        )

    benedizione = (
        "🕊️ **Benedizione finale**\n"
        "Che una pace sottile, come un filo di luce, attraversi ciò che stai vivendo. "
        "Cammina con fiducia: ogni passo, anche il più piccolo, è custodito da Dio."
    )

    risposta = accoglienza + illuminazione + scrittura + preghiera + passo_concreto + benedizione

    return {
        "answer": risposta,
        "source": m["fonte"],
        "explanation": m["nota"],
        "category": m["tema"]
    }

# -----------------------------
# MOTORE AI (FASE B - GROQ + LLAMA 3.1)
# -----------------------------

def generate_ai_answer(question: str):
    """
    Usa la logica della Fase A (tema + corpus + struttura spirituale)
    e chiede al modello Groq di generare un testo armonico, contemplativo e fedele.
    """
    tema = classify_tema(question)
    messaggi = get_messages_by_tema(tema)

    if not messaggi:
        # fallback: usa comunque la v5 supervisionata
        return generate_supervised_answer_v5(question)

    m = messaggi[0]

    # Prompt di sistema: identità e confini dell'assistente
    system_prompt = (
        "Sei un assistente spirituale cattolico. "
        "Parli con tono contemplativo, mite, rispettoso, mai invadente, "
        "mai psicologico, sempre radicato nella Scrittura e nella Tradizione. "
        "Non inventi dottrina, non inventi citazioni, non dai consigli morali complessi. "
        "Non nomini mai il Catechismo o documenti se non vengono già forniti. "
        "Usa uno stile semplice, luminoso, accogliente."
    )

    # Prompt di contesto: corpus + struttura
    context_prompt = f"""
Utente:
{question}

Tema principale (classificato): {m['tema']}

Messaggio dal corpus:
{m['messaggio']}

Nota spirituale/teologica:
{m['nota']}

Fonte biblica/spirituale:
{m['fonte']}

Scrivi una risposta che:
- accolga il vissuto dell'utente con delicatezza
- riprenda il contenuto del messaggio e della nota
- faccia riferimento alla fonte in modo semplice (senza tecnicismi)
- mantenga un tono contemplativo, lento, luminoso
- resti breve ma denso (8–12 frasi)
- NON inserisca nuove citazioni o dottrina non presenti sopra
- NON dia consigli psicologici, ma solo spirituali (fiducia, preghiera, speranza, abbandono in Dio)
- non usi elenco puntato, ma un unico testo continuo

Non ripetere letteralmente tutto il testo del corpus, ma rielaboralo con delicatezza.
Non cambiare il senso della nota o della fonte.
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context_prompt}
        ],
        "temperature": 0.6,
        "max_tokens": 600
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=body, timeout=20)
        response.raise_for_status()
        data = response.json()

        ai_text = data["choices"][0]["message"]["content"].strip()

        return {
            "answer": ai_text,
            "source": m["fonte"],
            "explanation": m["nota"],
            "category": m["tema"]
        }
    except Exception:
        # in caso di errore con Groq, fallback sicuro al motore v5
        return generate_supervised_answer_v5(question)

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
# REGOLE DI RISPOSTA (RAPIDE)
# -----------------------------

rules = [
    {
        "keywords": ["tarocchi", "oroscopo", "magia", "cartomanzia", "medium", "divinazione"],
        "answer": "La Chiesa invita a evitare ogni forma di divinazione.",
        "source": "Catechismo della Chiesa Cattolica, 2116",
        "explanation": "La divinazione contraddice l'affidamento fiducioso a Dio.",
        "category": "Dottrina"
    },
    {
        "keywords": ["sofferenza", "dolore", "malattia", "croce", "patire"],
        "answer": "Unisci la tua sofferenza a quella di Cristo.",
        "source": "Colossesi 1,24",
        "explanation": "La sofferenza, vissuta con Cristo, diventa partecipazione alla sua opera redentrice.",
        "category": "Sofferenza e Croce"
    },
    {
        "keywords": ["paura", "ansia", "angoscia", "preoccupazione", "timore"],
        "answer": "Non temere, Dio è con te.",
        "source": "Isaia 41,10",
        "explanation": "La presenza di Dio dona forza e pace nei momenti difficili.",
        "category": "Consolazione"
    },
    {
        "keywords": ["perdono", "colpa", "peccato", "confessione", "misericordia"],
        "answer": "Dio è misericordioso e sempre pronto a perdonare.",
        "source": "Luca 15,11-32",
        "explanation": "Come il Padre del figliol prodigo, Dio accoglie chi torna a Lui.",
        "category": "Misericordia"
    },
    {
        "keywords": ["vocazione", "chiamata", "discernimento", "volontà di dio"],
        "answer": "Ascolta la voce di Dio nel silenzio e nella preghiera.",
        "source": "1 Samuele 3,10",
        "explanation": "Il discernimento nasce dall'ascolto profondo della volontà di Dio.",
        "category": "Discernimento"
    },
    {
        "keywords": ["speranza", "fiducia", "scoraggiamento", "disperazione"],
        "answer": "La speranza cristiana non delude.",
        "source": "Romani 5,5",
        "explanation": "Lo Spirito Santo infonde nei cuori la speranza che sostiene nelle prove.",
        "category": "Speranza"
    },
    {
        "keywords": ["preghiera", "pregare", "rosario", "adorazione"],
        "answer": "La preghiera è respiro dell'anima.",
        "source": "Catechismo della Chiesa Cattolica, 2559",
        "explanation": "La preghiera è l'umile incontro tra la sete di Dio e la sete dell'uomo.",
        "category": "Preghiera"
    },
    {
        "keywords": ["amore", "carità", "prossimo", "aiutare"],
        "answer": "Ama il prossimo tuo come te stesso.",
        "source": "Marco 12,31",
        "explanation": "La carità è il cuore della vita cristiana.",
        "category": "Carità"
    },
    {
        "keywords": ["fede", "credere", "dubbio", "incredulità"],
        "answer": "La fede cresce chiedendola a Dio.",
        "source": "Marco 9,24",
        "explanation": "Anche chi dubita può dire: 'Credo, aiutami nella mia incredulità'.",
        "category": "Fede"
    },
    {
        "keywords": ["spirito santo", "consolatore", "dono", "carismi"],
        "answer": "Lo Spirito Santo ti guida nella verità.",
        "source": "Giovanni 16,13",
        "explanation": "È lo Spirito che illumina il cuore e dona pace.",
        "category": "Spirito Santo"
    },
    {
        "keywords": ["matrimonio", "famiglia", "relazione", "fidanzamento", "conflitto"],
        "answer": "L’amore vero è paziente e misericordioso.",
        "source": "1 Corinzi 13,4-7",
        "explanation": "La carità è il fondamento di ogni relazione cristiana.",
        "category": "Relazioni"
    },
    {
        "keywords": ["tentazione", "peccato", "demonio", "lotta", "caduta"],
        "answer": "Dio ti dà la forza per resistere alla tentazione.",
        "source": "1 Corinzi 10,13",
        "explanation": "Nessuna prova supera le tue forze se ti affidi a Dio.",
        "category": "Lotta spirituale"
    },
    {
        "keywords": ["crescita", "migliorare", "conversione", "cammino", "santità"],
        "answer": "La santità cresce un passo alla volta.",
        "source": "Gaudete et Exsultate",
        "explanation": "Dio ti guida nel cammino quotidiano verso la santità.",
        "category": "Crescita spirituale"
    },
    {
        "keywords": ["guerra", "pace", "ingiustizia", "violenza", "male"],
        "answer": "Beati gli operatori di pace.",
        "source": "Matteo 5,9",
        "explanation": "La pace nasce da cuori riconciliati con Dio.",
        "category": "Pace e Giustizia"
    },
    {
        "keywords": ["maria", "madonna", "santi", "intercessione"],
        "answer": "Maria ti accompagna come Madre.",
        "source": "Giovanni 19,27",
        "explanation": "La devozione mariana conduce sempre a Cristo.",
        "category": "Devozione"
    },
    {
        "keywords": ["sacramenti", "eucaristia", "comunione", "battesimo"],
        "answer": "I sacramenti sono incontri reali con Cristo.",
        "source": "Catechismo della Chiesa Cattolica, 1116",
        "explanation": "Attraverso i sacramenti, Cristo agisce nella tua vita.",
        "category": "Sacramenti"
    },
    {
        "keywords": ["senso", "scopo", "vita", "esistenza", "vuoto"],
        "answer": "La tua vita ha un valore infinito agli occhi di Dio.",
        "source": "Salmo 139,14",
        "explanation": "Dio ti ha creato per amore e per un fine unico.",
        "category": "Senso della vita"
    }
]

# -----------------------------
# ENDPOINT PRINCIPALE (REGOLE RAPIDE)
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

# -----------------------------
# ENDPOINT DI TEST MOTORE SUPERVISIONATO (v5)
# -----------------------------

@app.post("/test-supervised-v5")
def test_supervised_v5(request: AskRequest):
    return generate_supervised_answer_v5(request.question)

# -----------------------------
# ENDPOINT MOTORE AI (FASE B - GROQ)
# -----------------------------

@app.post("/api/ask-ai", response_model=SpiritualAnswer)
async def ask_ai(request: AskRequest):
    result = generate_ai_answer(request.question)
    return SpiritualAnswer(
        answer=result["answer"],
        source=result["source"],
        explanation=result["explanation"],
        category=result["category"]
    )
