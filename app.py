import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Sondage - Matières résiduelles",
    page_icon="♻️",
    layout="wide",
)


COLOR_MAP = {
    "Toujours": "#6D4CC2",
    "Souvent": "#9D7AE0",
    "Rarement": "#D6B85A",
    "Jamais": "#D96C9A",
    "C'est dur de s'y retrouver...": "#A7A0C9",
    "Oui": "#6D4CC2",
    "Non": "#D96C9A",
}

ACCENT = "#8E63D9"
SURFACE = "#F7F1FF"
PANEL = "#FFFFFF"
TEXT = "#2D2340"
MUTED = "#6B6282"
GRID = "#DED5F0"
OPEN_QUESTION_COLOR = "#A14FCB"
RESIDENT_LABEL = "Résident(e) d'Entrelacs"

OPEN_QUESTIONS = [
    "Qu'est-ce qui vous aiderait ou motiverait à recycler davantage?",
    "Qu'est-ce qui vous aiderait ou motiverait à composter davantage?",
]


def inject_styles() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
                radial-gradient(circle at top left, rgba(142,99,217,0.20), transparent 28%),
                radial-gradient(circle at top right, rgba(208,122,200,0.18), transparent 30%),
                linear-gradient(180deg, #F3ECFF 0%, #FBF7FF 38%, #F6F0FC 100%);
            color: {TEXT};
        }}

        [data-testid="stHeader"] {{
            background: rgba(0, 0, 0, 0);
        }}

        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #4A347A 0%, #32214F 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }}

        section[data-testid="stSidebar"] * {{
            color: #F7F3EA !important;
        }}

        .block-container {{
            padding-top: 2.2rem;
            padding-bottom: 3rem;
        }}

        h1, h2, h3 {{
            font-family: Georgia, "Times New Roman", serif;
            color: {TEXT};
            letter-spacing: -0.02em;
        }}

        p, li, label, div[data-testid="stMarkdownContainer"] {{
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
        }}

        .hero-card {{
            padding: 2.2rem 2.4rem;
            border-radius: 28px;
            background:
                linear-gradient(125deg, rgba(247,241,255,0.96), rgba(255,255,255,0.84)),
                linear-gradient(135deg, rgba(109,76,194,0.12), rgba(209,110,186,0.10));
            border: 1px solid rgba(34, 49, 39, 0.08);
            box-shadow: 0 24px 60px rgba(34, 49, 39, 0.08);
            margin-bottom: 1.25rem;
        }}

        .eyebrow {{
            display: inline-block;
            padding: 0.35rem 0.8rem;
            border-radius: 999px;
            background: rgba(109, 76, 194, 0.12);
            color: #6D4CC2;
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}

        .hero-title {{
            font-size: clamp(2rem, 4vw, 3.5rem);
            line-height: 1.04;
            margin: 0.8rem 0 0.55rem 0;
        }}

        .hero-copy {{
            max-width: 52rem;
            font-size: 1.05rem;
            color: {MUTED};
            line-height: 1.7;
            margin-bottom: 1.3rem;
        }}

        .hero-stats {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.9rem;
        }}

        .hero-pill {{
            background: rgba(255, 255, 255, 0.84);
            border: 1px solid rgba(34, 49, 39, 0.08);
            padding: 0.9rem 1rem;
            border-radius: 18px;
            min-width: 170px;
        }}

        .hero-pill-label {{
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: {MUTED};
        }}

        .hero-pill-value {{
            font-size: 1.55rem;
            font-weight: 700;
            color: {TEXT};
            margin-top: 0.15rem;
        }}

        .section-intro {{
            color: {MUTED};
            max-width: 56rem;
            margin-top: -0.3rem;
            margin-bottom: 1rem;
        }}

        .metric-card {{
            background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(247,241,255,0.92));
            border: 1px solid rgba(34, 49, 39, 0.08);
            border-radius: 24px;
            padding: 1.15rem 1.2rem 1.25rem;
            box-shadow: 0 16px 40px rgba(34, 49, 39, 0.06);
            min-height: 190px;
        }}

        .metric-label {{
            color: {MUTED};
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 700;
        }}

        .metric-value {{
            font-family: Georgia, "Times New Roman", serif;
            font-size: 3rem;
            line-height: 1;
            margin: 0.7rem 0 0.4rem;
            color: {TEXT};
        }}

        .metric-copy {{
            font-size: 1rem;
            color: {MUTED};
            line-height: 1.5;
        }}

        .panel-card {{
            background: rgba(255, 255, 255, 0.86);
            border: 1px solid rgba(34, 49, 39, 0.08);
            border-radius: 26px;
            padding: 1rem 1rem 0.35rem;
            box-shadow: 0 18px 44px rgba(34, 49, 39, 0.06);
            margin-bottom: 1rem;
        }}

        .open-question-card {{
            background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(245,239,255,0.94));
            border: 1px solid rgba(34, 49, 39, 0.08);
            border-radius: 26px;
            padding: 1.2rem 1.2rem 0.5rem;
            box-shadow: 0 18px 44px rgba(34, 49, 39, 0.06);
            margin-bottom: 1rem;
        }}

        .open-kicker {{
            color: {OPEN_QUESTION_COLOR};
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.35rem;
        }}

        .open-help {{
            color: {MUTED};
            font-size: 0.95rem;
            margin-top: -0.25rem;
        }}

        .footnote {{
            color: {MUTED};
            font-size: 0.92rem;
            margin-top: -0.15rem;
            padding-bottom: 0.6rem;
        }}

        div[data-testid="stMetric"] {{
            background: transparent;
            border: none;
        }}

        div[data-testid="stSidebar"] .stSelectbox label {{
            color: #F8F1FF !important;
            font-weight: 700;
        }}

        div[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div {{
            background: #FFFDFE !important;
            border: 1px solid #D9CFEA !important;
            color: #2D2340 !important;
            box-shadow: 0 8px 22px rgba(17, 12, 32, 0.18) !important;
        }}

        div[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span {{
            color: #2D2340 !important;
            font-weight: 600 !important;
        }}

        div[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div > div {{
            color: #2D2340 !important;
            opacity: 1 !important;
        }}

        div[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div > div:first-child {{
            color: #2D2340 !important;
            opacity: 1 !important;
            font-weight: 600 !important;
        }}

        div[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] input {{
            color: #2D2340 !important;
            -webkit-text-fill-color: #2D2340 !important;
            caret-color: #2D2340 !important;
        }}

        div[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] input::placeholder {{
            color: #6B6282 !important;
            -webkit-text-fill-color: #6B6282 !important;
        }}

        div[data-testid="stSidebar"] .stSelectbox svg {{
            fill: #4A347A !important;
        }}

        div[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div:hover {{
            border-color: #B8A5D8 !important;
            background: #FFFFFF !important;
        }}

        div[data-testid="stSidebar"] .stSelectbox [data-baseweb="popover"] {{
            color: #2D2340 !important;
        }}

        div[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div:focus-within {{
            border-color: #8E63D9 !important;
            box-shadow: 0 0 0 3px rgba(142, 99, 217, 0.22), 0 8px 22px rgba(17, 12, 32, 0.18) !important;
        }}

        div[data-testid="stSidebar"] div[role="listbox"] {{
            background: #FFFDFE !important;
            border: 1px solid #D9CFEA !important;
            box-shadow: 0 16px 36px rgba(17, 12, 32, 0.18) !important;
        }}

        div[data-testid="stSidebar"] div[role="option"] {{
            color: #2D2340 !important;
            background: transparent !important;
        }}

        div[data-testid="stSidebar"] div[role="option"]:hover {{
            background: #F2EAFE !important;
        }}

        div[data-testid="stSidebar"] div[role="option"][aria-selected="true"] {{
            background: #E9DDFB !important;
            color: #2D2340 !important;
            font-weight: 700 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def wrap_title(text: str, max_len: int = 36, max_lines: int = 3) -> str:
    words = text.split()
    lines = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_len or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
        if len(lines) == max_lines:
            break

    if current and len(lines) < max_lines:
        lines.append(current)

    return "<br>".join(lines)


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_excel("sondage_collecte_anonymized.xlsx", engine="openpyxl")
    df.columns = [col.strip() for col in df.columns]
    return df


def rate_for_values(frame: pd.DataFrame, column: str, accepted_values: list[str]) -> float:
    if column not in frame.columns:
        return np.nan
    valid = frame[column].dropna()
    if valid.empty:
        return np.nan
    return valid.isin(accepted_values).mean() * 100


def render_metric_card(column, label: str, value: float, suffix: str) -> None:
    if np.isnan(value):
        value_markup = "—"
        copy = "Aucune réponse exploitable pour ce filtre."
    else:
        value_markup = f"{value:.0f} %"
        copy = f"des répondant·es ont indiqué <strong>{suffix}</strong>."

    column.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value_markup}</div>
            <div class="metric-copy">{copy}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_pie_figure(counts: pd.DataFrame, title: str):
    fig = px.pie(
        counts,
        names="Reponse",
        values="Pourcentage",
        hole=0.62,
        color="Reponse",
        color_discrete_map=COLOR_MAP,
    )

    fig.update_traces(
        textinfo="percent",
        textposition="inside",
        insidetextorientation="horizontal",
        textfont=dict(size=14, color="white"),
        marker=dict(line=dict(color="#FFFFFF", width=3)),
        hovertemplate="%{label}<br>%{value:.1f}%<extra></extra>",
        sort=False,
    )

    fig.update_layout(
        title=dict(
            text=wrap_title(title),
            x=0.5,
            y=0.94,
            xanchor="center",
            yanchor="top",
            font=dict(size=18, family="Georgia, serif", color=TEXT),
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            title="",
            font=dict(size=12, color=TEXT),
        ),
        margin=dict(t=110, l=20, r=20, b=70),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def build_open_question_figure(plot_df: pd.DataFrame, title: str):
    fig = px.bar(
        plot_df,
        x="% excl. vides",
        y="Intent",
        orientation="h",
        text="% excl. vides",
    )

    fig.update_traces(
        texttemplate="%{text:.1f} %",
        textposition="outside",
        marker=dict(color=OPEN_QUESTION_COLOR, line=dict(color="#7E33A8", width=1.2)),
        hovertemplate="%{y}<br>%{x:.1f}%<extra></extra>",
    )

    fig.update_layout(
        title=dict(
            text=title,
            x=0.01,
            xanchor="left",
            font=dict(size=20, family="Georgia, serif", color=TEXT),
        ),
        xaxis_title="Part des répondant·es ayant mentionné ce thème",
        yaxis_title="",
        xaxis=dict(
            range=[0, plot_df["% excl. vides"].max() * 1.18 if not plot_df.empty else 100],
            gridcolor=GRID,
            zeroline=False,
            tickfont=dict(color=TEXT),
            title_font=dict(color=MUTED),
        ),
        yaxis=dict(
            categoryorder="total ascending",
            tickfont=dict(color=TEXT),
        ),
        margin=dict(t=70, l=30, r=40, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


inject_styles()
df = load_data()

role_col = df.columns[0]
question_cols = df.columns[1:]

st.sidebar.markdown("## Filtres")
st.sidebar.caption("Affinez la lecture des résultats selon le profil de réponse.")

roles = ["Tous"] + sorted(df[role_col].dropna().unique().tolist())
selected_role = st.sidebar.radio("Profil répondant", roles)

if selected_role != "Tous":
    df_f = df[df[role_col] == selected_role].copy()
else:
    df_f = df.copy()

n_total = len(df_f)
n_questions = len(question_cols)
n_residents = int(df_f[role_col].eq(RESIDENT_LABEL).sum())
resident_share = (n_residents / n_total * 100) if n_total else np.nan

st.markdown(
    f"""
    <div class="hero-card">
        <span class="eyebrow">Tableau de bord environnemental</span>
        <h1 class="hero-title">Collecte des matières résiduelles.</h1>
        <p class="hero-copy">
            Ce tableau de bord offre une analyse du sondage réalisé au printemps 2025 auprès de la population 
            et fait ressortir les thèmes qui méritent d'être clarifiés ou encouragés.
        </p>
        <div class="hero-stats">
            <div class="hero-pill">
                <div class="hero-pill-label">Filtre actif</div>
                <div class="hero-pill-value">{selected_role}</div>
            </div>
            <div class="hero-pill">
                <div class="hero-pill-label">Répondant·es</div>
                <div class="hero-pill-value">{n_total}</div>
            </div>
            <div class="hero-pill">
                <div class="hero-pill-label">Questions analysées</div>
                <div class="hero-pill-value">{n_questions}</div>
            </div>
            <div class="hero-pill">
                <div class="hero-pill-label">Part de résident·es</div>
                <div class="hero-pill-value">{resident_share:.0f} %</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown("## Vue d'ensemble")
st.markdown(
    """
    <div class="section-intro">
        Une lecture rapide des indicateurs qui donnent le ton : habitudes de tri, compréhension des
        consignes et appétit pour un service complémentaire.
    </div>
    """,
    unsafe_allow_html=True,
)

metrics_config = [
    (
        "Recyclage",
        "Selon vous, est-ce que vous mettez au bac bleu toutes les matières qui sont recyclables?",
        ["Toujours"],
        "toujours",
    ),
    (
        "Compost",
        "Selon vous, est-ce que vous mettez au bac brun toutes les matières qui sont compostables?",
        ["Toujours"],
        "toujours",
    ),
    (
        "Nouvelle façon de trier",
        "Saviez-vous qu'il y a une nouvelle façon, plus simple, de trier vos matières résiduelles pour la récupération?",
        ["Oui"],
        "oui",
    ),
    (
        "Dépôt communautaire",
        "Est-ce que vous utiliseriez ce service de dépôt communautaire à la mairie?",
        ["Toujours", "Souvent"],
        "toujours ou souvent",
    ),
]

metric_columns = st.columns(len(metrics_config))
for column, (label, col_name, accepted_values, suffix) in zip(metric_columns, metrics_config):
    render_metric_card(column, label, rate_for_values(df_f, col_name, accepted_values), suffix)

st.markdown("## Réponses collectées")
st.markdown(
    """
    <div class="section-intro">
        Chaque question fermée est présentée comme une petite fiche de lecture.
    </div>
    """,
    unsafe_allow_html=True,
)

closed_question_columns = st.columns(2)
col_idx = 0

for question in question_cols:
    if question in OPEN_QUESTIONS:
        continue

    counts = (
        df_f[question]
        .value_counts(dropna=True, normalize=True)
        .mul(100)
        .round(1)
        .rename_axis("Reponse")
        .reset_index(name="Pourcentage")
    )

    if counts.empty:
        continue

    with closed_question_columns[col_idx]:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.plotly_chart(build_pie_figure(counts, question), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    col_idx = (col_idx + 1) % 2

st.markdown("## Ce qui ressort des réponses ouvertes")
st.markdown(
    """
    <div class="section-intro">
        Les réponses libres ont été regroupées par thèmes pour alimenter la discussion interne.
        Ce n'est pas une lecture définitive, mais un bon point de départ pour prioriser les suites.
    </div>
    """,
    unsafe_allow_html=True,
)

for question in OPEN_QUESTIONS:
    st.markdown('<div class="open-question-card">', unsafe_allow_html=True)
    st.markdown('<div class="open-kicker">Synthèse thématique</div>', unsafe_allow_html=True)
    st.markdown(f"### {question}")
    st.markdown(
        """
        <div class="open-help">
            Les pourcentages ci-dessous sont calculés parmi les personnes ayant donné une réponse à cette question.
        </div>
        """,
        unsafe_allow_html=True,
    )

    non_empty = df_f[question].dropna()
    if non_empty.empty:
        st.info("Aucune réponse pour ce filtre.")
        st.markdown("</div>", unsafe_allow_html=True)
        continue

    summary = non_empty.value_counts().rename_axis("Intent").reset_index(name="n")
    summary = summary[summary["Intent"] != "Autre / non classé"]
    summary["% excl. vides"] = (summary["n"] / len(non_empty) * 100).round(1)
    summary = summary.sort_values("% excl. vides", ascending=False)

    if summary.empty:
        st.info("Les réponses n'ont pas pu être regroupées en thèmes interprétables ici.")
        st.markdown("</div>", unsafe_allow_html=True)
        continue

    plot_df = summary[["Intent", "% excl. vides"]].copy()
    st.plotly_chart(build_open_question_figure(plot_df, "Thèmes mentionnés"), use_container_width=True)
    st.markdown(
        """
        <div class="footnote">
            Lecture suggérée : plus une barre est longue, plus ce thème revient souvent dans les commentaires.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
