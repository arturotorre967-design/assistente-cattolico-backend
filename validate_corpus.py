import json

REQUIRED_FIELDS = ["tema", "messaggio", "fonte", "nota"]

def validate_corpus(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Errore nel JSON: {e}")
        return False

    if not isinstance(data, list):
        print("❌ Il corpus deve essere una lista di oggetti JSON.")
        return False

    valid = True

    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            print(f"❌ L'elemento {i} non è un oggetto JSON.")
            valid = False
            continue

        for field in REQUIRED_FIELDS:
            if field not in entry:
                print(f"❌ Errore nell'elemento {i}: manca il campo '{field}'.")
                valid = False
            elif not entry[field]:
                print(f"❌ Errore nell'elemento {i}: il campo '{field}' è vuoto.")
                valid = False

    if valid:
        print("✅ Corpus valido! Nessun errore trovato.")
    else:
        print("⚠️ Validazione completata con errori.")

    return valid

if __name__ == "__main__":
    validate_corpus("corpus.json")
