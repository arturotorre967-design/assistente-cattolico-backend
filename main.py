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
# MODELLI Pydantic (NUOVI)
# -----------------------------

class RispostaRequest(BaseModel):
    domanda: str

class RispostaFinale(BaseModel):
    risposta: str
    tema: str
    messaggio: str
    fonte: Optional[str] = None
    nota: Optional[str] = None

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
# LITURGIA DEL GIORNO (MODULO)
# -----------------------------

liturgia = {
    "domenica": {
        "lettura": "Dal Vangelo secondo Marco (1,14-20)",
        "tema": "Chiamata, sequela, fiducia",
        "versetto_chiave": "«Venite dietro a me, vi farò diventare pescatori di uomini»"
    },
    "lunedi": {
        "lettura": "Dal Vangelo secondo Matteo (5,1-12)",
        "tema": "Beatitudini, speranza, consolazione",
        "versetto_chiave": "«Beati i poveri in spirito»"
    },
    "martedi": {
        "lettura": "Dal Vangelo secondo Marco (2,23-28)",
        "tema": "Libertà, misericordia, legge",
        "versetto_chiave": "«Il sabato è stato fatto per l’uomo»"
    },
    "mercoledi": {
        "lettura": "Dal Vangelo secondo Luca (11,1-4)",
        "tema": "Preghiera, fiducia, intimità con Dio",
        "versetto_chiave": "«Signore, insegnaci a pregare»"
    },
    "giovedi": {
        "lettura": "Dal Vangelo secondo Giovanni (6,35-40)",
        "tema": "Pane di vita, speranza, fedeltà",
        "versetto_chiave": "«Chi viene a me non avrà fame»"
    },
    "venerdi": {
        "lettura": "Dal Vangelo secondo Matteo (9,9-13)",
        "tema": "Misericordia, conversione, chiamata",
        "versetto_chiave": "«Misericordia io voglio e non sacrifici»"
    },
    "sabato": {
        "lettura": "Dal Vangelo secondo Luca (18,1-8)",
        "tema": "Perseveranza, preghiera, fiducia",
        "versetto_chiave": "«Pregare sempre, senza stancarsi»"
    }
}

import datetime

def liturgia_del_giorno():
    giorno = datetime.datetime.now().strftime("%A").lower()

    mapping = {
        "monday": "lunedi",
        "tuesday": "martedi",
        "wednesday": "mercoledi",
        "thursday": "giovedi",
        "friday": "venerdi",
        "saturday": "sabato",
        "sunday": "domenica"
    }

    giorno_it = mapping.get(giorno, "domenica")
    return liturgia.get(giorno_it, liturgia["domenica"])
    
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

@app.post("/risposta", response_model=RispostaFinale)
def risposta_unica(payload: RispostaRequest):
    domanda = payload.domanda

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

    # 8️⃣ USER MESSAGE (il tuo prompt maestro, IDENTICO)
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

    # 9️⃣ Chiamata a Groq (temperature 1.3 ATTIVA)
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
        return RispostaFinale(
            risposta="Errore nella generazione della risposta spirituale.",
            tema=tema,
            messaggio=versetto,
            fonte="Errore interno",
            nota=frase_santo
        )

    if "choices" not in groq_json:
        print("❌ Nessun campo 'choices' nella risposta Groq:", groq_json)
        return RispostaFinale(
            risposta="Errore nella generazione della risposta spirituale.",
            tema=tema,
            messaggio=versetto,
            fonte="Errore interno",
            nota=frase_santo
        )

    risposta_groq = groq_json["choices"][0]["message"]["content"]

    # 1️⃣1️⃣ Fonte completa (Bibbia + Liturgia + Santo)
    fonte_completa = f"Bibbia: {versetto}; Liturgia del giorno: {versetto_liturgico}; Santo: {frase_santo}"

    # 1️⃣2️⃣ Risposta finale
    return RispostaFinale(
        risposta=risposta_groq.strip(),
        tema=tema,
        messaggio=versetto,
        fonte=fonte_completa,
        nota=frase_santo
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
# MOTORE AI (FASE B - GROQ + LLAMA 3.1)
# -----------------------------

def generate_ai_answer(question: str):
    tema = classify_tema(question)
    messaggi = get_messages_by_tema(tema)

    print("TEMA CLASSIFICATO:", tema)
    print("MESSAGGI TROVATI:", messaggi)

    if not messaggi:
        print("NESSUN MESSAGGIO TROVATO — ENTRA NEL FALLBACK")
        return generate_supervised_answer_v5(question)

    # ... resto della funzione ...

    m = messaggi[0]

    system_prompt = (
        "Sei un assistente spirituale cattolico. "
        "Parli con tono contemplativo, lento, mite, luminoso, come chi accompagna un’anima nel silenzio. "
        "Non fai psicologia, non analizzi emozioni, non dai consigli tecnici o terapeutici. "
        "Non inventi dottrina, non aggiungi citazioni non fornite, non introduci nuovi testi biblici. "
        "Usi solo il messaggio, la nota e la fonte che ti vengono dati. "
        "La tua risposta deve essere una rielaborazione poetica e contemplativa del messaggio, della nota e della fonte, "
        "senza aggiungere contenuti nuovi né introdurre idee non presenti. "
        "Ogni frase deve essere breve, essenziale, come un soffio di luce. "
        "Evita moralismi, ammonizioni, giudizi, spiegazioni complesse. "
        "Parla come un fratello che siede accanto, non come un professore. "
        "Usa immagini semplici: luce, silenzio, respiro, cammino, mano di Dio. "
        "Ogni frase deve portare pace, non informazioni. "
        "Non ripetere il corpus parola per parola: rielaboralo con delicatezza. "
        "Scrivi 8–12 frasi, senza elenchi, senza sezioni, senza emoji."
    )

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
- NON dia consigli psicologici, ma solo spirituali
- non usi elenco puntato, ma un unico testo continuo
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
        "temperature": 0.9,
        "top-p": 0.95
        "max_tokens": 600
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=body, timeout=20)
        print("STATUS CODE:", response.status_code)
        print("RAW RESPONSE:", response.text)
        response.raise_for_status()
        data = response.json()

        ai_text = data["choices"][0]["message"]["content"].strip()
        ai_text = quality_filter(ai_text, m["fonte"])

        return {
            "answer": ai_text,
            "source": m["fonte"],
            "explanation": m["nota"],
            "category": m["tema"]
        }

    except Exception as e:
        print("ERRORE GROQ:", e)
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
