from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import json
import os
import requests

# -----------------------------
# CARICAMENTO .env  (AGGIUNTO)
# -----------------------------
from dotenv import load_dotenv
load_dotenv()  # <-- Questa riga carica il file .env

app = FastAPI()

# -----------------------------
# CACHE IN RAM
# -----------------------------
cache = {}

def get_cached_answer(question: str):
    """Restituisce una risposta dalla cache se esiste."""
    return cache.get(question)

def save_to_cache(question: str, answer: dict):
    """Salva una risposta nella cache."""
    cache[question] = answer
    
# -----------------------------
# FUNZIONE LITURGIA DEL GIORNO
# -----------------------------
from datetime import datetime

def liturgia_del_giorno():
    # Giorno della settimana (0 = lunedì, 6 = domenica)
    giorno = datetime.now().weekday()

    # Mini-liturgia settimanale (puoi ampliarla quando vuoi)
    liturgia = [
        {
            "versetto_chiave": "Beati i poveri in spirito, perché di essi è il regno dei cieli",
            "riferimento": "Matteo 5,3",
            "prima_lettura": "Giacomo 1,1-11",
            "salmo_responsoriale": "Salmo 118",
            "vangelo": "Matteo 5,1-12",
            "antifona": "Il Signore è vicino a chi ha il cuore ferito",
            "colore_liturgico": "Verde"
        },
        {
            "versetto_chiave": "Il Signore è il mio pastore: non manco di nulla",
            "riferimento": "Salmo 23",
            "prima_lettura": "Isaia 55,6-11",
            "salmo_responsoriale": "Salmo 33",
            "vangelo": "Matteo 6,7-15",
            "antifona": "Il Signore guida i suoi fedeli",
            "colore_liturgico": "Verde"
        },
        {
            "versetto_chiave": "Io sono la via, la verità e la vita",
            "riferimento": "Giovanni 14,6",
            "prima_lettura": "Atti 4,1-12",
            "salmo_responsoriale": "Salmo 117",
            "vangelo": "Giovanni 14,1-6",
            "antifona": "Cristo è la nostra luce",
            "colore_liturgico": "Bianco"
        },
        {
            "versetto_chiave": "Signore, da chi andremo? Tu hai parole di vita eterna",
            "riferimento": "Giovanni 6,68",
            "prima_lettura": "Geremia 17,5-10",
            "salmo_responsoriale": "Salmo 1",
            "vangelo": "Luca 6,17-26",
            "antifona": "Beato chi confida nel Signore",
            "colore_liturgico": "Verde"
        },
        {
            "versetto_chiave": "Il Signore è vicino a chi lo invoca",
            "riferimento": "Salmo 145",
            "prima_lettura": "Isaia 58,1-9",
            "salmo_responsoriale": "Salmo 50",
            "vangelo": "Matteo 9,14-15",
            "antifona": "Ricordati di noi, Signore",
            "colore_liturgico": "Viola"
        },
        {
            "versetto_chiave": "Chi rimane in me e io in lui porta molto frutto",
            "riferimento": "Giovanni 15,5",
            "prima_lettura": "Atti 9,31-42",
            "salmo_responsoriale": "Salmo 115",
            "vangelo": "Giovanni 15,1-8",
            "antifona": "Rimanete nel mio amore",
            "colore_liturgico": "Bianco"
        },
        {
            "versetto_chiave": "Questo è il mio Figlio prediletto: ascoltatelo",
            "riferimento": "Marco 9,7",
            "prima_lettura": "Genesi 22,1-18",
            "salmo_responsoriale": "Salmo 115",
            "vangelo": "Marco 9,2-10",
            "antifona": "Cristo è la nostra gloria",
            "colore_liturgico": "Bianco"
        }
    ]

    return liturgia[giorno]

# -----------------------------
# MODELLI Pydantic (CORRETTI)
# -----------------------------

class AskRequest(BaseModel):
    question: str

class SpiritualAnswer(BaseModel):
    answer: str
    source: str
    explanation: str
    category: str
    sourceLiturgical: Optional[str] = None

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
GROQ_MODEL = "llama-3.3-70b-versatile"

# -----------------------------
# CARICAMENTO CORPUS SPIRITUALE
# -----------------------------

def load_corpus():
    corpus_path = os.path.join(os.path.dirname(__file__), "corpus.json")
    with open(corpus_path, "r", encoding="utf-8") as f:
        return json.load(f)

corpus = load_corpus()
print("🔥 CORPUS CARICATO:", corpus)

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
# COMMENTO LITURGICO (MODULO)
# -----------------------------

def genera_commento_liturgico(lettura, tema_liturgico, versetto_liturgico):
    """
    Genera un commento liturgico più lungo e contemplativo,
    basato sulla liturgia del giorno.
    """

    prompt_commento = f"""
Sei un accompagnatore spirituale cattolico.
Genera un commento liturgico lungo, contemplativo e pastorale.

LITURGIA DEL GIORNO
- Lettura: {lettura}
- Tema liturgico: {tema_liturgico}
- Versetto chiave: {versetto_liturgico}

ISTRUZIONI
- Non fare esegesi tecnica.
- Non essere accademico.
- Non usare linguaggio complesso.
- Non moralizzare.
- Offri una meditazione che aiuti a pregare.
- Collega la liturgia alla vita quotidiana.
- Sii dolce, profondo, paterno e fraterno.
- Lunghezza: 2–3 paragrafi brevi.

OBIETTIVO
Offrire una meditazione che possa essere letta lentamente,
come un piccolo momento di lectio divina.
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": prompt_commento}
        ]
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=body)

    try:
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except:
        return "Oggi la liturgia ci invita a fermarci, ad ascoltare la Parola e a lasciarci toccare dal suo silenzioso abbraccio."
        
# -----------------------------
# COMMENTO LITURGICO (VERSIONE AVANZATA)
# -----------------------------

def genera_commento_liturgico_avanzato(lettura, tema_liturgico, versetto_liturgico,
                                       tema_utente, emozione, bisogno, intensita):
    """
    Genera un commento liturgico lungo, contemplativo e personalizzato,
    integrando liturgia del giorno e vissuto dell'utente.
    """

    prompt_commento = f"""
Sei un accompagnatore spirituale cattolico.
Genera un commento liturgico lungo, profondo e contemplativo,
che unisca la liturgia del giorno al vissuto dell'utente.

LITURGIA DEL GIORNO
- Lettura: {lettura}
- Tema liturgico: {tema_liturgico}
- Versetto chiave: {versetto_liturgico}

VISSUTO DELL'UTENTE
- Tema spirituale: {tema_utente}
- Emozione dominante: {emozione}
- Bisogno spirituale: {bisogno}
- Intensità del vissuto: {intensita}

STRUTTURA RICHIESTA (LECTIO DIVINA)
1. LECTIO — Cosa dice la Parola oggi? Spiega con semplicità.
2. MEDITATIO — Cosa dice questa Parola alla vita dell’utente?
   Collega la liturgia al suo vissuto, con delicatezza.
3. ORATIO — Offri una breve preghiera ispirata alla liturgia.
4. CONTEMPLATIO — Una frase finale che rimanga nel cuore.

STILE
- Non fare esegesi tecnica.
- Non essere accademico.
- Non moralizzare.
- Sii paterno, fraterno, contemplativo.
- Sii dolce, profondo, semplice.
- Lunghezza: 3–4 paragrafi brevi.

OBIETTIVO
Offrire una meditazione che aiuti a pregare e a sentire la vicinanza di Dio.
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": prompt_commento}
        ]
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=body)

    try:
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except:
        return (
            "Oggi la liturgia ci invita a fermarci, ad ascoltare la Parola e a lasciarci "
            "toccare dal suo silenzioso abbraccio. Anche nel tuo vissuto, Dio desidera "
            "parlarti con delicatezza e luce."
        )

# -----------------------------
# CITAZIONI BIBLICHE E SANTI
# -----------------------------

versetti_biblici = {
    "paura": "«Non temere, perché io sono con te» (Isaia 41,10)",
    "solitudine": "«Il Signore è vicino a chi ha il cuore ferito» (Salmo 34,19)",
    "colpa": "«Dove abbondò il peccato, sovrabbondò la grazia» (Romani 5,20)",
    "tristezza": "«Il Signore asciugherà ogni lacrima» (Apocalisse 21,4)",
    "speranza": "«Io conosco i progetti che ho fatto per voi» (Geremia 29,11)",
    "vocazione": "«Parla, Signore, il tuo servo ascolta» (1 Samuele 3,10)",
    "prova_sofferenza": "«Ti basta la mia grazia» (2 Corinzi 12,9)",
    "perdono": "«Rimetti a noi i nostri debiti» (Matteo 6,12)",
    "amore": "«Dio è amore» (1 Giovanni 4,8)",
    "discernimento": "«Mostrami, Signore, la tua via» (Salmo 86,11)",
    "generale": "«Il Signore è il mio pastore: non manco di nulla» (Salmo 23,1)"
}

frasi_santi = {
    "paura": "«La paura è un nemico della fede» – San Pio da Pietrelcina",
    "solitudine": "«Dio è più intimo a noi di quanto noi lo siamo a noi stessi» – Sant’Agostino",
    "colpa": "«Dio non si stanca mai di perdonarci» – Papa Francesco",
    "tristezza": "«La tristezza non viene da Dio» – San Francesco d’Assisi",
    "speranza": "«La speranza è la virtù dei cuori forti» – Santa Teresa d’Avila",
    "vocazione": "«Fai ciò che puoi, e Dio farà il resto» – San Giovanni Bosco",
    "prova_sofferenza": "«Nulla ti turbi, nulla ti spaventi: solo Dio basta» – Santa Teresa d’Avila",
    "perdono": "«È nella misericordia che si vede il volto di Dio» – San Giovanni Paolo II",
    "amore": "«Dove non c’è amore, metti amore» – San Giovanni della Croce",
    "discernimento": "«La volontà di Dio è la nostra pace» – Santa Chiara",
    "generale": "«Tutto posso in Colui che mi dà forza» – San Paolo"
}

def recupera_citazioni(tema):
    tema = tema.lower()
    versetto = versetti_biblici.get(tema, versetti_biblici["generale"])
    santo = frasi_santi.get(tema, frasi_santi["generale"])
    return versetto, santo

# -----------------------------
# PROMPT MAESTRO (VERSIONE COMPLETA)
# -----------------------------

def genera_prompt(testo_utente, tema, versetto, frase_santo, blend_toni,
                  lettura, tema_liturgico, versetto_liturgico,
                  commento_liturgico):
    return f"""
IDENTITÀ
Tu sei un accompagnatore spirituale cattolico.
Parli con dolcezza, profondità e rispetto.
Non giudichi, non imponi, non moralizzi.
Ascolti il cuore della persona e la accompagni verso Dio con misericordia.

INTENZIONE
Il tuo compito è offrire una risposta che consoli, illumini e orienti verso la presenza di Dio.
Non dai consigli pratici rischiosi.
Non fai diagnosi psicologiche.
Non sostituisci un sacerdote.
Offri luce, pace e speranza.

TONO
La tua voce è una sintesi armoniosa di:
- paternità (protezione, fermezza)
- fraternità (vicinanza, empatia)
- contemplazione (silenzio, profondità)
- pastorale (equilibrio, misericordia)
Blend dei toni da applicare: {blend_toni}

INPUT UTENTE
{testo_utente}

TEMA SPIRITUALE
{tema}

CITAZIONI
Versetto biblico: {versetto}
Frase di un santo: {frase_santo}

LITURGIA DEL GIORNO
Lettura: {lettura}
Tema liturgico: {tema_liturgico}
Versetto chiave: {versetto_liturgico}
Integra la liturgia solo se è naturale e utile alla persona.

COMMENTO LITURGICO APPROFONDITO
{commento_liturgico}

PRUDENZA PASTORALE
- Non dare consigli medici, psicologici o legali.
- Non fare diagnosi.
- Non promettere miracoli specifici.
- Non usare toni colpevolizzanti.
- Non contraddire la dottrina cattolica.
- Non citare testi non verificati.
- Non usare linguaggio manipolativo.

STRUTTURA DELLA RISPOSTA
1. Accoglienza empatica.
2. Luce dalla Parola e dai Santi.
3. Collegamento con la liturgia del giorno (solo se naturale).
4. Riflessione spirituale personalizzata.
5. Invito alla pace e alla fiducia.
6. Breve preghiera finale (opzionale).

OBIETTIVO FINALE
Genera una risposta spirituale profonda, consolante e teologicamente solida,
che aiuti la persona a percepire la vicinanza di Dio.
"""

# -----------------------------
# ENDPOINT UNICO /risposta
# -----------------------------

@app.post("/risposta", response_model=SpiritualAnswer)
def risposta_unica(payload: AskRequest):
    # AskRequest ha il campo "question"
    domanda = payload.question

    # 1️⃣ Classificazione del tema
    tema = classify_tema(domanda)

    # 2️⃣ Citazioni vere (Bibbia + Santi)
    versetto, frase_santo = recupera_citazioni(tema)

    # 3️⃣ Analisi emotiva (placeholder)
    emozione = "non_specificata"
    bisogno = "non_specificato"
    intensita = "media"

    # 4️⃣ Blend dei toni
    blend_toni = "40% fraterno, 40% paterno, 20% contemplativo"

    # 5️⃣ Liturgia del giorno
    lit = liturgia_del_giorno()
    lettura = lit["lettura"]
    tema_liturgico = lit["tema"]
    versetto_liturgico = lit["versetto_chiave"]

    # 6️⃣ Commento liturgico avanzato
    commento_liturgico = genera_commento_liturgico_avanzato(
        lettura=lettura,
        tema_liturgico=tema_liturgico,
        versetto_liturgico=versetto_liturgico,
        tema_utente=tema,
        emozione=emozione,
        bisogno=bisogno,
        intensita=intensita
    )

    # 7️⃣ SYSTEM MESSAGE (istruzioni fisse)
    system_message = """
Sei un assistente spirituale cattolico. Rispondi con tono caldo, fraterno, paterno e contemplativo.
La tua risposta deve SEMPRE contenere:
- una citazione biblica centrale
- un riferimento liturgico del giorno
- un pensiero di un Santo
- un invito concreto alla preghiera o a un gesto spirituale
- una breve preghiera finale
- zero errori grammaticali
- Non usare mai “cara fratello” o altre combinazioni grammaticalmente errate.
Usa sempre “caro fratello” oppure “cara sorella” in base al genere percepito dal testo dell’utente.
Se il genere non è chiaro, usa “caro amico”.
Puoi usare immagini poetiche, metafore bibliche e simboli spirituali. La struttura può variare liberamente.
Puoi variare liberamente stile, immagini, metafore e struttura.
Usa un linguaggio poetico, simbolico e meditativo, ricco di immagini spirituali e contemplative.
"""

    # 8️⃣ USER MESSAGE (prompt maestro)
    user_message = f"""
Sei un assistente spirituale cattolico. Rispondi con tono caldo, fraterno, paterno e contemplativo.
La tua risposta deve SEMPRE contenere:
- una citazione biblica centrale
- un riferimento liturgico del giorno (se rilevante)
- un pensiero di un Santo (se disponibile)
- un invito concreto alla preghiera o a un gesto spirituale
- una breve preghiera finale
- zero errori grammaticali
- Non usare mai “cara fratello” o altre combinazioni grammaticalmente errate. Usa sempre “caro fratello” oppure “cara sorella” in base al genere percepito dal testo dell’utente. Se il genere non è chiaro, usa “caro amico”. Puoi variare liberamente stile, immagini, metafore e struttura.

Informazioni per costruire la risposta:
- Tema utente: {tema}
- Versetto biblico principale: {versetto}
- Frase di un Santo: {frase_santo}
- Lettura liturgica del giorno: {lettura}
- Tema liturgico: {tema_liturgico}
- Versetto liturgico chiave: {versetto_liturgico}
- Commento liturgico avanzato: {commento_liturgico}
- Emozione percepita: {emozione}
- Bisogno spirituale: {bisogno}
- Intensità emotiva: {intensita}
- Blend dei toni: {blend_toni}

Domanda dell’utente:
{domanda}

Genera una risposta spirituale profonda, coerente, cattolica, creativa, varia, non ripetitiva, senza ripetizioni inutili e piena di immagini spirituali.
"""

    # 9️⃣ Chiamata a Groq
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": GROQ_MODEL,
        "temperature": 1.3,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    }

    groq_response = requests.post(GROQ_API_URL, headers=headers, json=body)

    # 🔍 LOG COMPLETO DELLA RISPOSTA
    print("📨 RISPOSTA GREZZA GROQ:", groq_response.text)

    # 🔟 Parsing JSON
    try:
        groq_json = groq_response.json()
    except Exception as e:
        print("❌ Errore nel parsing JSON:", e)
        return SpiritualAnswer(
            answer="Errore nella generazione della risposta spirituale.",
            source="Errore interno",
            explanation=frase_santo,
            category=tema
        )

    if "choices" not in groq_json:
        print("❌ Nessun campo 'choices' nella risposta Groq:", groq_json)
        return SpiritualAnswer(
            answer="Errore nella generazione della risposta spirituale.",
            source="Errore interno",
            explanation=frase_santo,
            category=tema
        )

    risposta_groq = groq_json["choices"][0]["message"]["content"]

    # 1️⃣1️⃣ Fonte completa (Bibbia + Liturgia + Santo)
    fonte_completa = f"Bibbia: {versetto}; Liturgia del giorno: {versetto_liturgico}; Santo: {frase_santo}"

    # 1️⃣2️⃣ Risposta finale nel nuovo modello
    return SpiritualAnswer(
        answer=risposta_groq.strip(),
        source=fonte_completa,
        explanation=frase_santo,
        category=tema
    )

# -----------------------------
# ENDPOINT: Tutti i messaggi di un tema
# -----------------------------
@app.get("/messaggi/{tema}")
def get_all_messages_by_tema(tema: str):
    messages = get_messages_by_tema(tema)

    if not messages:
        return {"errore": "Tema non trovato", "tema": tema}

    return {"tema": tema, "messaggi": messages}

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
# QUALITY FILTER (Controllo qualità AI)
# -----------------------------

def quality_filter(text: str, fonte: str):
    # 1. Rimuove citazioni inventate
    if any(book in text for book in ["Isaia", "Salmo", "Giovanni", "Marco", "Luca", "Corinzi"]):
        if fonte not in text:
            # Se l'AI ha inventato una citazione, la rimuoviamo
            text = text.split(".")[0] + ". Dio è vicino."

    # 2. Accorcia risposte troppo lunghe
    if len(text) > 900:
        text = text[:900].rsplit(".", 1)[0] + "."

    # 3. Rimuove toni psicologici
    psicologia = ["ansia", "trauma", "terapia", "psicologico", "stress", "depressione"]
    for p in psicologia:
        if p in text.lower():
            text = text.replace(p, "fatica interiore")

    # 4. Armonizza il tono
    sostituzioni = {
        "Dio ti aiuta": "Dio ti accompagna",
        "Dio ti sostiene": "Dio posa la Sua mano sul tuo cammino",
        "non sei solo": "non sei mai abbandonato",
        "paura": "timore che cerca luce"
    }
    for k, v in sostituzioni.items():
        text = text.replace(k, v)

    return text

# -----------------------------
# MOTORE AI PURO (con recinto cattolico)
# -----------------------------

def generate_ai_answer(question: str):
    print("🧠 Generazione RISPOSTA AI (motore contemplativo controllato)")

    system_message = """
Sei un assistente spirituale cattolico fedele al Magistero.
Non inventare mai citazioni bibliche o dei santi.
Non contraddire mai il Catechismo.
Non dare consigli morali contrari alla Chiesa.
Non fare teologia creativa o speculativa.

Tono:
- contemplativo, poetico, caldo, paterno
- profondo ma semplice
- mai giudicante
- mai rigido
- mai ripetitivo

Struttura OBBLIGATORIA della risposta AI:

1) Una frase iniziale che riassume il cuore spirituale.
2) Una breve meditazione (6–10 righe) che:
   - parte dalla domanda dell’utente
   - usa immagini bibliche generiche (luce, cammino, acqua viva…)
   - NON cita versetti specifici
   - NON usa riferimenti numerati (niente “Giovanni 3,16”)
3) Un invito concreto alla preghiera o a un gesto spirituale.
4) Una preghiera finale breve, rivolta a Dio.

Regole:
- Non usare la stessa preghiera finale ogni volta.
- Non usare la stessa frase iniziale ogni volta.
- Non usare sezioni dell’ibrido (niente “Riferimento biblico”, “Altre luci”, ecc.).
- Zero errori grammaticali.
"""

    user_message = f"""
Domanda dell'utente:
{question}

Istruzioni:
- Rispondi con una meditazione cattolica profonda.
- Non citare versetti specifici.
- Non usare la struttura dell’ibrido.
- Mantieni la struttura obbligatoria indicata nel system message.
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": GROQ_MODEL,
        "temperature": 1.15,  # più creativa dell’ibrido
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    }

    groq_response = requests.post(GROQ_API_URL, headers=headers, json=body)
    print("📨 RISPOSTA GREZZA GROQ (AI):", groq_response.text)

    try:
        groq_json = groq_response.json()
        risposta = groq_json["choices"][0]["message"]["content"].strip()
    except:
        risposta = "Non riesco a generare una risposta in questo momento, ma Dio è vicino a te."

    # Il motore AI non usa fonti specifiche
    return {
        "answer": risposta,
        "source": "AI-contemplativa",
        "explanation": "",
        "category": "meditativa"
    }

# -----------------------------
# FUNZIONE DI FUSIONE IBRIDA
# -----------------------------

def fuse_answers(rule_answer: str, ai_answer: str, question: str):
    fusion_prompt = f"""
L'utente ha chiesto:
{question}

Risposta del motore a regole:
{rule_answer}

Risposta del motore AI:
{ai_answer}

Unisci le due risposte in un unico testo contemplativo, breve, mite, luminoso.
- Mantieni solo ciò che è coerente con la spiritualità cattolica.
- Evita ripetizioni.
- Non aggiungere dottrina nuova.
- Non introdurre citazioni non presenti.
- Usa frasi brevi, essenziali, come un soffio di luce.
- Tono: contemplativo, fraterno, silenzioso.
- Lunghezza: 8–12 frasi.
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "Sei un assistente spirituale cattolico."},
            {"role": "user", "content": fusion_prompt}
        ],
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 500
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=body)
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


# -----------------------------
# MOTORE IBRIDO COMPLETO (AI controllata)
# -----------------------------

def generate_hybrid_answer(question: str):
    # 1️⃣ CACHE
    cached = get_cached_answer(question)
    if cached:
        print("⚡ CACHE HIT — risposta immediata")
        return cached

    print("🧠 CACHE MISS — generazione nuova risposta IBRIDA CONTROLLATA")

    # 2️⃣ PILASTRI CATTOLICI (deterministici)
    tema = classify_tema(question)
    versetto, frase_santo = recupera_citazioni(tema)

    lit = liturgia_del_giorno()
    lettura = lit["lettura"]
    tema_liturgico = lit["tema"]
    versetto_liturgico = lit["versetto_chiave"]

    emozione = "non_specificata"
    bisogno = "non_specificato"
    intensita = "media"
    blend_toni = "40% fraterno, 40% paterno, 20% contemplativo"

    # 3️⃣ SYSTEM MESSAGE — RECINTO DOTTRINALE
    system_message = """
Sei un assistente spirituale cattolico fedele al Magistero della Chiesa.
Devi:
- rimanere sempre entro la dottrina cattolica
- non inventare mai citazioni bibliche o dei santi
- non contraddire mai il Catechismo della Chiesa Cattolica
- non fare teologia creativa o speculativa
- non dare consigli morali contrari alla Chiesa

Tono:
- caldo, fraterno, paterno, contemplativo
- rispettoso, umile, mai giudicante
- linguaggio semplice ma profondo

Struttura OBBLIGATORIA della risposta (rispetta esattamente queste sezioni):

1) Una riga iniziale che riassume il cuore del messaggio.
2) Sezione: "📖 RIFERIMENTO BIBLICO / SPIRITUALE"
   - Usa il versetto principale fornito dal sistema.
   - Puoi aggiungere UNA sola breve frase di commento.
3) Sezione: "🏛️ ALTRE LUCI DELLA TRADIZIONE"
   - Puoi citare al massimo 1-2 altri riferimenti (Bibbia, Padri, Santi, Magistero).
   - Se non sei sicuro, resta sul generico senza inventare riferimenti precisi.
4) Sezione: "🧭 PASSO CONCRETO"
   - Un solo gesto concreto, semplice, realistico, fattibile oggi.
5) Sezione: "🙏 PREGHIERA FINALE"
   - Una breve preghiera rivolta a Dio, in seconda persona ("Signore...").
6) Una breve parte contemplativa finale (massimo 6-8 righe), poetica ma sobria.

Regole:
- Non ripetere le stesse frasi identiche in ogni risposta.
- Non usare formule stereotipate sempre uguali.
- Non usare mai “cara fratello”: usa “caro fratello”, “cara sorella” o “caro amico” se il genere non è chiaro.
- Zero errori grammaticali.
"""

    # 4️⃣ USER MESSAGE — CONTESTO COMPLETO
    user_message = f"""
Domanda dell'utente:
{question}

Informazioni per costruire la risposta:
- Tema classificato: {tema}
- Versetto biblico principale: {versetto}
- Frase di un Santo: {frase_santo}
- Lettura liturgica del giorno: {lettura}
- Tema liturgico: {tema_liturgico}
- Versetto liturgico chiave: {versetto_liturgico}
- Emozione percepita: {emozione}
- Bisogno spirituale: {bisogno}
- Intensità emotiva: {intensita}
- Blend dei toni: {blend_toni}

Istruzioni:
- Usa il versetto principale come asse portante.
- Se non sei sicuro di un riferimento, non inventarlo.
- Collega con delicatezza la domanda dell'utente al Vangelo e alla Tradizione.
- Mantieni la struttura obbligatoria indicata nel system message.
"""

    # 5️⃣ CHIAMATA A GROQ
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": GROQ_MODEL,
        "temperature": 1.0,  # controllata, non troppo alta
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    }

    groq_response = requests.post(GROQ_API_URL, headers=headers, json=body)
    print("📨 RISPOSTA GREZZA GROQ (IBRIDO):", groq_response.text)

    try:
        groq_json = groq_response.json()
    except Exception as e:
        print("❌ Errore nel parsing JSON (ibrido):", e)
        result = {
            "answer": "Si è verificato un errore nella generazione della risposta spirituale.",
            "source": "Errore interno",
            "explanation": frase_santo,
            "category": tema
        }
        save_to_cache(question, result)
        return result

    if "choices" not in groq_json:
        print("❌ Nessun campo 'choices' nella risposta Groq (ibrido):", groq_json)
        result = {
            "answer": "Si è verificato un errore nella generazione della risposta spirituale.",
            "source": "Errore interno",
            "explanation": frase_santo,
            "category": tema
        }
        save_to_cache(question, result)
        return result

    risposta_groq = groq_json["choices"][0]["message"]["content"]

    fonte_completa = f"Bibbia: {versetto}; Liturgia del giorno: {versetto_liturgico}; Santo: {frase_santo}"

    result = {
        "answer": risposta_groq.strip(),
        "source": fonte_completa,
        "explanation": frase_santo,
        "category": tema
    }

    # 6️⃣ SALVATAGGIO IN CACHE
    save_to_cache(question, result)
    return result

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
# ENDPOINT MOTORE IBRIDO (CRASH-SAFE)
# -----------------------------

@app.post("/api/ask-hybrid", response_model=SpiritualAnswer)
async def ask_hybrid(request: AskRequest):
    try:
        result = generate_hybrid_answer(request.question)
        return SpiritualAnswer(
            answer=result["answer"],
            source=result["source"],
            explanation=result["explanation"],
            category=result["category"],
            sourceLiturgical=liturgia_del_giorno()["versetto_chiave"]
        )
    except Exception as e:
        print("ERRORE NEL MOTORE IBRIDO:", e)
        return SpiritualAnswer(
            answer="In questo momento non riesco a generare una risposta ibrida.",
            source="Sistema",
            explanation="Errore interno nel motore ibrido",
            category="Errore",
            sourceLiturgical=liturgia_del_giorno()["versetto_chiave"]
        )

# -----------------------------
# ENDPOINT PRINCIPALE (MOTORE INTERNO CON VARIETÀ MASSIMA)
# -----------------------------

import random

@app.post("/api/ask", response_model=SpiritualAnswer)
async def ask_question(request: AskRequest):
    question = request.question.lower()

    # ============================
    # 1) CONTENUTI PER TEMA
    # ============================

    contenuti = {
        "Consolazione": {
            "frasi": [
                "Non temere: Dio posa una luce silenziosa sul tuo cuore.",
                "Il Signore cammina accanto a te anche quando tutto trema.",
                "La paura non è più forte della presenza di Dio.",
                "Dio sostiene il tuo cuore quando si sente fragile.",
                "Il timore si placa quando lasci spazio alla fiducia.",
                "Dio è vicino, anche quando non lo senti.",
                "La tua paura è un’ombra, ma Dio è una luce che non si spegne.",
                "Il Signore ti accompagna passo dopo passo.",
                "Dio custodisce ciò che temi di perdere.",
                "La pace di Dio può raggiungerti anche ora."
            ],
            "immagini": [
                "come una lampada accesa nella notte",
                "come un filo di luce che attraversa il cuore",
                "come un vento leggero che porta pace",
                "come una mano che ti sostiene nel silenzio",
                "come un raggio che apre un varco nell’ombra"
            ],
            "promesse": [
                "Dio non ti lascia solo nel timore.",
                "La Sua presenza è più forte delle tue paure.",
                "Il Signore ti guida anche quando non vedi la strada.",
                "Dio è con te in ogni passo.",
                "La Sua pace può raggiungerti anche ora."
            ],
            "commenti": [
                "Lascia che questa parola ti dia respiro.",
                "Accogli questa luce nel cuore.",
                "Questa promessa è per te.",
                "Dio ti accompagna in ciò che vivi.",
                "Questa verità può portare pace."
            ],
            "versetti": ["Isaia 41,10", "Salmo 27,1", "Salmo 23,1-4"]
        },

        "Fede": {
            "frasi": [
                "La fede cresce nel silenzio e nella fiducia.",
                "Dio sostiene chi desidera credere.",
                "La fede illumina ciò che non comprendiamo.",
                "La fiducia apre strade che non vedevamo.",
                "La fede è un seme che Dio fa crescere.",
                "Credere è lasciare spazio alla luce.",
                "La fede nasce dall’ascolto del cuore.",
                "Dio rafforza chi si affida a Lui.",
                "La fede è un passo verso la pace.",
                "Dio accoglie anche la tua piccola fede."
            ],
            "immagini": [
                "come una lampada che rischiara il cammino",
                "come un seme che cresce nel silenzio",
                "come un ruscello che porta vita",
                "come un filo che ti unisce a Dio",
                "come un’alba che dissolve la notte"
            ],
            "promesse": [
                "Dio non abbandona chi lo cerca.",
                "La Sua fedeltà è più forte dei tuoi dubbi.",
                "Il Signore accoglie la tua fede, anche fragile.",
                "Dio cammina con chi desidera credere.",
                "La Sua luce non viene meno."
            ],
            "commenti": [
                "Accogli questa parola come un seme.",
                "Lascia che questa verità ti accompagni.",
                "Questa luce può guidarti oggi.",
                "Dio parla anche nel silenzio.",
                "Questa promessa è per te."
            ],
            "versetti": ["Marco 9,24", "Romani 10,17", "Ebrei 11,1"]
        },

        "Speranza": {
            "frasi": [
                "La speranza non delude.",
                "Dio apre strade anche dove non le vedi.",
                "La luce di Dio vince ogni oscurità.",
                "La speranza è un dono che rinnova il cuore.",
                "Dio è fedele anche quando tutto sembra fermo.",
                "La speranza è un respiro che rialza.",
                "Dio accende una luce anche nei giorni pesanti.",
                "La speranza nasce dalla fiducia.",
                "Dio non smette di operare nel silenzio.",
                "La speranza è più forte della stanchezza."
            ],
            "immagini": [
                "come un’alba che ritorna",
                "come un seme che rompe la terra",
                "come un raggio che attraversa le nuvole",
                "come una brezza che porta sollievo",
                "come una porta che si apre lentamente"
            ],
            "promesse": [
                "Dio prepara per te un cammino.",
                "La Sua fedeltà non viene meno.",
                "Il Signore opera anche quando non te ne accorgi.",
                "Dio rialza chi spera in Lui.",
                "La Sua luce ti precede."
            ],
            "commenti": [
                "Lascia che questa promessa ti rialzi.",
                "Questa parola può essere la tua forza.",
                "Accogli questa luce nel cuore.",
                "Dio è vicino a chi spera.",
                "Questa verità può guidarti."
            ],
            "versetti": ["Romani 5,5", "Geremia 29,11", "Salmo 37,5"]
        }
    }

    # ============================
    # 2) CERCA UNA REGOLA CHE MATCHA
    # ============================

    for rule in rules:
        if any(keyword in question for keyword in rule["keywords"]):

            categoria = rule["category"]

            if categoria in contenuti:
                blocco = contenuti[categoria]

                frase = random.choice(blocco["frasi"])
                immagine = random.choice(blocco["immagini"])
                promessa = random.choice(blocco["promesse"])
                commento = random.choice(blocco["commenti"])
                versetto = random.choice(blocco["versetti"])

                # ============================
                # 3) STRUTTURE ALTERNATIVE
                # ============================

                struttura = random.choice(["A", "B", "C"])

                if struttura == "A":
                    risposta = f"{frase}\n\n📖 {versetto}\n{commento}"

                elif struttura == "B":
                    risposta = f"{frase}\n{immagine}\n\n📖 {versetto}"

                else:  # Struttura C
                    risposta = f"{frase}\n\n📖 {versetto}\n{promessa}\n{commento}"

                return SpiritualAnswer(
                    answer=risposta,
                    source=versetto,
                    explanation=commento,
                    category=categoria,
                    sourceLiturgical=liturgia_del_giorno()["versetto_chiave"]
                )

            # fallback se non ci sono contenuti
            return SpiritualAnswer(
                answer=rule["answer"],
                source=rule["source"],
                explanation=rule["explanation"],
                category=rule["category"],
                sourceLiturgical=liturgia_del_giorno()["versetto_chiave"]
            )

    # ============================
    # 4) FALLBACK GENERALE
    # ============================

    fallback_frasi = [
        "Cerca prima il Regno di Dio.",
        "Dio guida chi si affida a Lui.",
        "Il Signore illumina il cammino di chi lo cerca.",
        "Dio parla nel silenzio del cuore.",
        "Chi confida nel Signore trova pace."
    ]

    fallback_versetti = ["Matteo 6,33", "Salmo 37,5", "Proverbi 3,5"]

    fallback_commenti = [
        "Lascia che questa parola ti accompagni oggi.",
        "Accogli questa luce nel cuore.",
        "Questa promessa è per te."
    ]

    risposta = (
        f"{random.choice(fallback_frasi)}\n\n"
        f"📖 {random.choice(fallback_versetti)}\n"
        f"{random.choice(fallback_commenti)}"
    )

    return SpiritualAnswer(
        answer=risposta,
        source="Motore interno",
        explanation="Varietà sintetica",
        category="Generale",
        sourceLiturgical=liturgia_del_giorno()["versetto_chiave"]
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
        category=result["category"],
        sourceLiturgical=liturgia_del_giorno()["versetto_chiave"]
    )

# -----------------------------
# ENDPOINT LITURGIA DEL GIORNO
# -----------------------------

import requests
import datetime

def fallback_liturgia():
    return {
        "versetto_chiave": "Il Signore è la mia luce e la mia salvezza",
        "riferimento": "Salmo 27",

        "prima_lettura": "Isaia 55,1-11",
        "prima_lettura_testo": "O voi tutti assetati, venite all’acqua...",

        "salmo_responsoriale": "Salmo 22",
        "salmo_responsoriale_testo": "Il Signore è il mio pastore: non manco di nulla.",

        "vangelo": "Marco 1,1-8",
        "vangelo_testo": "Inizio del vangelo di Gesù Cristo, Figlio di Dio...",

        "antifona": "Oggi la salvezza è venuta in questa casa.",
        "colore_liturgico": "Verde"
    }


def liturgia_del_giorno():
    try:
        today = datetime.date.today().strftime("%Y-%m-%d")
        url = f"https://www.chiesacattolica.it/wp-json/liturgia/v1/giorno?data={today}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "it-IT,it;q=0.9",
            "Referer": "https://www.chiesacattolica.it/liturgia-del-giorno/",
            "Origin": "https://www.chiesacattolica.it",
            "Connection": "keep-alive"
        }

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        print("DEBUG CEI:", data)

        if not isinstance(data, dict) or "vangelo" not in data:
            return fallback_liturgia()

        return {
            "versetto_chiave": data["vangelo"]["testo"].split("\n")[0],
            "riferimento": data["vangelo"]["riferimento"],

            "prima_lettura": data["prima_lettura"]["riferimento"],
            "prima_lettura_testo": data["prima_lettura"]["testo"],

            "salmo_responsoriale": data["salmo"]["riferimento"],
            "salmo_responsoriale_testo": data["salmo"]["testo"],

            "vangelo": data["vangelo"]["riferimento"],
            "vangelo_testo": data["vangelo"]["testo"],

            "antifona": data.get("antifona_ingresso"),
            "colore_liturgico": data.get("colore")
        }

    except Exception as e:
        print("Errore API CEI:", e)
        return fallback_liturgia()


@app.get("/liturgia-del-giorno")
async def get_liturgia_del_giorno():
    return liturgia_del_giorno()
