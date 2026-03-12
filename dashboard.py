import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(page_title="IMDb Movies Dashboard", layout="wide")
st.title("🎬 IMDb Top 1000 Movies Dashboard")

# ── Încărcare date ────────────────────────────────────────────────
fisier = st.file_uploader("Încarcă fișierul CSV", type=["csv"])

if fisier is None:
    st.info("Încarcă un fișier CSV pentru a continua.")
    st.stop()

df = pd.read_csv(fisier)

# ── Curățare date ─────────────────────────────────────────────────
df["Released_Year"] = pd.to_numeric(df["Released_Year"], errors="coerce")

# separăm genurile (ex: "Action, Drama" → ["Action","Drama"])
df["Genre"] = df["Genre"].str.split(", ")

# listă cu toate genurile unice
all_genres = sorted(set(g for sublist in df["Genre"] for g in sublist))

# ── Statistici generale ───────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total filme", len(df))
col2.metric("Rating mediu", round(df["IMDB_Rating"].mean(), 2))
col3.metric("Rating maxim", df["IMDB_Rating"].max())
col4.metric("Ani diferiți", df["Released_Year"].nunique())

st.dataframe(
    df[["Series_Title","Released_Year","Genre","IMDB_Rating"]].head(10),
    use_container_width=True
)

# ── Filtre în sidebar ─────────────────────────────────────────────
st.sidebar.header("Filtre")

gen_selectat = st.sidebar.multiselect(
    "Selectează gen",
    all_genres,
    default=all_genres
)

# filtrare după gen
df_filtrat = df[df["Genre"].apply(lambda x: any(g in x for g in gen_selectat))]

# ── Grafic 1 — Plotly ─────────────────────────────────────────────
st.subheader("⭐ Rating mediu pe gen")

# transformăm genurile pentru analiză
df_exploded = df_filtrat.explode("Genre")

rating_gen = df_exploded.groupby("Genre")["IMDB_Rating"].mean().reset_index()

fig = px.bar(
    rating_gen,
    x="Genre",
    y="IMDB_Rating",
    color="Genre",
    title="Rating mediu IMDb pe gen"
)

st.plotly_chart(fig, use_container_width=True)

# ── Grafic 2 — Scatter Plot ───────────────────────────────────────
st.subheader("📊 Rating vs Număr de voturi")

fig2 = px.scatter(
    df_filtrat,
    x="No_of_Votes",
    y="IMDB_Rating",
    color=df_filtrat["Genre"].astype(str),
    hover_data=["Series_Title"]
)

st.plotly_chart(fig2, use_container_width=True)

# ── Grafic 3 — Matplotlib ─────────────────────────────────────────
st.subheader("📈 Distribuția ratingurilor")

fig3, ax = plt.subplots(figsize=(9,4))

ax.hist(
    df_filtrat["IMDB_Rating"].dropna(),
    bins=20,
    color="#ff5c00",
    edgecolor="white"
)

ax.set_title("Distribuția ratingurilor IMDb")
ax.set_xlabel("Rating")
ax.set_ylabel("Număr filme")

st.pyplot(fig3)
plt.close(fig3)

# ── Top 10 filme ──────────────────────────────────────────────────
st.subheader("🏆 Top 10 filme după rating")

top_filme = df_filtrat.sort_values("IMDB_Rating", ascending=False).head(10)

st.dataframe(
    top_filme[["Series_Title","Released_Year","Genre","IMDB_Rating"]],
    use_container_width=True
)