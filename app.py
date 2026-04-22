# app.py
# Dashboard Streamlit – Sondage collecte des matières résiduelles
# Version v1 – comité environnemental

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


COLOR_MAP = {
    "Toujours": "#2E7D32",           # vert foncé
    "Souvent": "#81C784",            # vert pâle
    "Rarement": "#FDD835",           # jaune
    "Jamais": "#E57373",             # rouge doux
    "C'est dur de s'y retrouver...": "#BDBDBD", #gris
    
    "Oui": "#2E7D32",   # même vert foncé
    "Non": "#E57373"    # même rouge doux
    
    
}




def wrap_title(text, max_len=40, max_lines=2):
    words = text.split()
    lines, current = [], ""

    for w in words:
        if len(current) + len(w) <= max_len:
            current += " " + w
        else:
            lines.append(current.strip())
            current = w
        if len(lines) == max_lines:
            break

    if current and len(lines) < max_lines:
        lines.append(current.strip())

    return "<br>".join(lines)


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
                <div style="font-size:1rem; font-weight:500; color:#444; margin-bottom:0.25rem;">
                    {label}
                </div>
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

cols = st.columns(2)
col_idx = 0

for col in question_cols:
    if col in open_questions:
        continue

    counts = (
        df_f[col]
        .value_counts(dropna=True, normalize=True)
        .mul(100)
        .round(1)
        .to_frame(name="Pourcentage")
        .reset_index()
        .rename(columns={col: "Réponse"})
    )
    
    counts["Couleur"] = counts["Réponse"].map(COLOR_MAP)

    
    
    fig = px.pie(
        counts,
        names="Réponse",
        values="Pourcentage",
        hole=0.4,
        color="Réponse",
        color_discrete_map=COLOR_MAP
    )

    
    fig.update_traces(
        textinfo="label+percent",
        textposition="inside",
        insidetextorientation="horizontal",
        textfont=dict(size=13, color="white"),
        marker=dict(line=dict(color="white", width=1))
    )

    fig.update_layout(
        title=dict(
            text=wrap_title(col, max_len=45, max_lines=3),
            x=0.5,
            y=0.95,
            xanchor="center",
            yanchor="top",
            font=dict(size=17)
        ),
        showlegend=False,
        margin=dict(t=110, l=40, r=40, b=20)
    )




    with cols[col_idx]:
        st.plotly_chart(fig, width="stretch")

    col_idx = (col_idx + 1) % 2


# -------------------------------------------------------------------
# ANALYSE DES RÉPONSES OUVERTES – THÈMES
# -------------------------------------------------------------------


st.header("🧠 Ce qui ressort des réponses ouvertes (synthèse)")

st.caption(
    "Analyse exploratoire – à des fins de discussion interne. \n \n"
    "Les réponses ouvertes ont été regroupées automatiquement"
    "pour dégager des tendances."
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


