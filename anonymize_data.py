import pandas as pd
import numpy as np
import re
from unidecode import unidecode
from nltk.corpus import stopwords
from nltk.stem.snowball import FrenchStemmer
import nltk

# -------------------------
# NLP setup
# -------------------------
nltk.download("stopwords")

french_stopwords = set(stopwords.words("french"))
domain_stopwords = {
    "rien", "aucun", "aucune", "ok", "correct",
    "deja", "déjà", "merci", "tout"
}

stemmer = FrenchStemmer()

concept_map = {
    "recycl": "recyclage",
    "recyclag": "recyclage",
    "collect": "collecte",
    "ramass": "collecte",
    "horaire": "horaire",
    "frequenc": "frequence",
    "compost": "compost",
    "odeur": "odeurs",
    "bac": "bacs"
}

INTENT_RULES = {
    "Manque d’information claire": ["info", "clar", "savoir", "expliqu", "clair"],
    "Horaire ou fréquence de collecte": ["horaire", "frequence", "jour", "semaine"],
    "Capacité ou gestion des bacs": ["bac", "plein", "capac"],
    "Gestion du compost et des odeurs": ["compost", "odeur", "ete", "faune"]
}

# -------------------------
# Functions
# -------------------------
def clean_text(text):
    text = str(text).lower()
    text = unidecode(text)
    text = re.sub(r"[^a-z ]", " ", text)

    tokens = []
    for t in text.split():
        if (
            t in french_stopwords
            or t in domain_stopwords
            or len(t) <= 2
        ):
            continue

        stem = stemmer.stem(t)
        tokens.append(concept_map.get(stem, stem))

    return " ".join(tokens)


def detect_intent(cleaned_text):
    for label, keywords in INTENT_RULES.items():
        if any(k in cleaned_text for k in keywords):
            return label
    return "Autre / non classé"


# -------------------------
# Main processing
# -------------------------
INPUT_FILE = "sondage_collecte_clean.xlsx"
OUTPUT_FILE = "sondage_collecte_anonymized.xlsx"

OPEN_COLUMNS = [
    "Qu'est-ce qui vous aiderait ou motiverait à recycler davantage?",
    "Qu'est-ce qui vous aiderait ou motiverait à composter davantage?",
    "Avez-vous d'autres questions ou commentaires à nous dire, par rapport à la collecte de matières résiduelles?"
]

df = pd.read_excel(INPUT_FILE)

for col in OPEN_COLUMNS:
    new_values = []

    for val in df[col]:
        if pd.isna(val) or str(val).strip() == "":
            new_values.append(np.nan)
        else:
            cleaned = clean_text(val)
            intent = detect_intent(cleaned)
            new_values.append(intent)

    df[col] = new_values

df.to_excel(OUTPUT_FILE, index=False)

print(f"✅ Fichier anonymisé créé : {OUTPUT_FILE}")
