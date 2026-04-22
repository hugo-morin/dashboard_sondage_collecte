# app.py
# Dashboard Streamlit – Sondage collecte des matières résiduelles
# Version v1 – comité environnemental

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


from collections import Counter
import math


import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import FrenchStemmer
from unidecode import unidecode
import re


nltk.download("stopwords")

french_stopwords = set(stopwords.words("french"))
stemmer = FrenchStemmer()

domain_stopwords = {
    "rien", "aucun", "aucune", "ok", "correct",
    "inform", "information", "informe",
    "fait", "faire", "deja", "déjà",
    "merci"
}

concept_map = {
    "recycl": "recyclage",
    "recyclag": "recyclage",
    "recycler": "recyclage",

    "collect": "collecte",
    "ramass": "collecte",
    "cueil": "collecte",

    "compost": "compost",
    "odeur": "odeurs",
    "puant": "odeurs",

    "horaire": "horaire",
    "semaine": "horaire",
    "frequenc": "frequence"
}

INTENT_RULES = {
    "information": {
        "keywords": ["info", "inform", "clar", "savoir", "connaitr", "expliqu"],
        "label": "Manque d’information claire"
    },
    "horaire": {
        "keywords": ["jour", "lundi", "jeudi", "semaine", "horaire", "frequenc"],
        "label": "Horaire ou fréquence de collecte"
    },
    "bac": {
        "keywords": ["bac", "volume", "plein", "capac"],
        "label": "Capacité ou gestion des bacs"
    },
    "compost": {
        "keywords": ["compost", "odeur", "ete", "faune", "sac"],
        "label": "Gestion du compost et des odeurs"
    }
}

def detect_intent(cleaned_text):
    for intent in INTENT_RULES.values():
        if any(k in cleaned_text for k in intent["keywords"]):
            return intent["label"]
    return "Autre / non classé"


def clean_text(text):
    text = str(text).lower()
    text = unidecode(text)
    text = re.sub(r"[^a-z ]", " ", text)

    normalized_tokens = []

    for t in text.split():
        if (
            t in french_stopwords
            or t in domain_stopwords
            or len(t) <= 2
        ):
            continue

        # 1. stemming
        stem = stemmer.stem(t)

        # 2. normalisation conceptuelle
        token = concept_map.get(stem, stem)

        normalized_tokens.append(token)

    return " ".join(normalized_tokens)



# -------------------------------------------------------------------
# CONFIG GÉNÉRALE
# -------------------------------------------------------------------

st.set_page_config(
    page_title="Sondage – Matières résiduelles",
    page_icon="♻️",
    layout="wide"
)

st.title("🌱 Sondage – Collecte des matières résiduelles")
st.markdown(
    """
    **Comité environnemental – Vue exploratoire des résultats**  
    Cette application vise à offrir une lecture rapide, claire et constructive
    des réponses au sondage.
    """
)

# -------------------------------------------------------------------
# CHARGEMENT DES DONNÉES
# -------------------------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_excel("sondage_collecte_anonymized.xlsx", engine="openpyxl")
    df.columns = [c.strip() for c in df.columns]
    return df

df = load_data()

# -------------------------------------------------------------------
# FILTRE PRINCIPAL
# -------------------------------------------------------------------

st.sidebar.header("🎛️ Filtres")

role_col = df.columns[0]  # "Êtes-vous..."

roles = ["Tous"] + sorted(df[role_col].dropna().unique().tolist())
selected_role = st.sidebar.selectbox("Êtes-vous…", roles)

if selected_role != "Tous":
    df_f = df[df[role_col] == selected_role].copy()
else:
    df_f = df.copy()

n_total = len(df_f)

st.sidebar.markdown(f"**Nombre de répondant·es : {n_total}**")

# -------------------------------------------------------------------
# IDENTIFICATION DES TYPES DE QUESTIONS
# -------------------------------------------------------------------

# Heuristique simple :
# - peu de modalités -> fermée
# - beaucoup de valeurs uniques ou texte libre -> ouverte

def is_open_text(series, threshold=15):
    return series.dropna().nunique() > threshold

question_cols = df.columns[1:]

open_questions = [
    "Qu'est-ce qui vous aiderait ou motiverait à recycler davantage?",
    "Qu'est-ce qui vous aiderait ou motiverait à composter davantage?",
    "Avez-vous d'autres questions ou commentaires à nous dire, par rapport à la collecte de matières résiduelles?"
]

# -------------------------------------------------------------------
# VUE D’ENSEMBLE – QUESTIONS FERMÉES CLÉS
# -------------------------------------------------------------------

st.header("🔎 Vue d’ensemble")

def rate_for_values(col, accepted_values):
    if col not in df_f.columns:
        return np.nan
    valid = df_f[col].dropna()
    if len(valid) == 0:
        return np.nan
    return (valid.isin(accepted_values).mean()) * 100


metrics_config = [
    (
        "Recyclage",
        "Selon vous, est-ce que vous mettez au bac bleu toutes les matières qui sont recyclables?",
        ["Toujours"],
        "toujours"
    ),
    (
        "Compost",
        "Selon vous, est-ce que vous mettez au bac brun toutes les matières qui sont compostables?",
        ["Toujours"],
        "toujours"
    ),
    (
        "Nouvelle façon de trier",
        "Saviez-vous qu'il y a une nouvelle façon, plus simple, de trier vos matières résiduelles pour la récupération?",
        ["Oui"],
        "oui"
    ),
    (
        "Utilisation dépôt communautaire",
        "Est-ce que vous utiliseriez ce service de dépôt communautaire à la mairie?",
        ["Toujours", "Souvent"],
        "toujours ou souvent"
    )
]

cols = st.columns(len(metrics_config))

for c, (label, col_name, accepted, text_suffix) in zip(cols, metrics_config):
    rate = rate_for_values(col_name, accepted)
    
    if not np.isnan(rate):
        c.markdown(
            f"""
            <div style="text-align:center;">
                <div style="font-size:2.2rem; font-weight:600;">
                    {rate:.0f} %
                </div>
                <div style="font-size:1.1rem; color:#555;">
                    ont dit <em>{text_suffix}</em>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        c.markdown("–")


# -------------------------------------------------------------------
# QUESTIONS FERMÉES – VISUALISATION
# -------------------------------------------------------------------

st.header("📊 Réponses collectées")

for col in question_cols:
    if col in open_questions : 
        continue
    
    st.subheader(col)

    counts = (
        df_f[col]
        .value_counts(dropna=True, normalize=True)
        .mul(100)
        .round(1)
        .to_frame(name="Pourcentage")
        .reset_index()
        .rename(columns={col: "Réponse"})
    )


    
    fig = px.bar(
        counts,
        x="Pourcentage",
        y="Réponse",
        orientation="h",
        text="Pourcentage"
    )

    fig.update_traces(texttemplate="%{text} %")


    fig.update_layout(
        yaxis=dict(categoryorder="total ascending"),
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10)
    )

    st.plotly_chart(fig, width="stretch")

    st.divider()

# -------------------------------------------------------------------
# ANALYSE DES RÉPONSES OUVERTES – THÈMES
# -------------------------------------------------------------------


st.header("🧠 Ce qui ressort des réponses ouvertes (synthèse)")

# -------------------------------------------------------------------
# NOTE DE FIN
# -------------------------------------------------------------------

st.caption(
    "Analyse exploratoire – à des fins de discussion interne. "
    "Les réponses ouvertes sont regroupées automatiquement "
    "pour dégager des tendances, sans jugement de valeur."
)

for col in open_questions:
    st.subheader(col)

    total_n = len(df_f)
    non_empty = df_f[col].dropna()

    if len(non_empty) == 0:
        st.info("Aucune réponse.")
        continue

    summary = (
        non_empty
        .value_counts()
        .to_frame(name="n")
        .reset_index()
    )

    summary = summary.rename(columns={col: "Intent"})

    summary["% incl. vides"] = (summary["n"] / total_n * 100).round(1)
    summary["% excl. vides"] = (summary["n"] / len(non_empty) * 100).round(1)

    summary = summary[summary["Intent"] != "Autre / non classé"]

    summary = summary.sort_values("% excl. vides", ascending=False)

    st.dataframe(
        summary[["Intent", "% incl. vides", "% excl. vides"]],
        width="stretch"
    )

    st.divider()


