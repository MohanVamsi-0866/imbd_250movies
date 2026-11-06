import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="IMDb Movie Analytics", page_icon="🎬", layout="wide", initial_sidebar_state="expanded")

# ---------- Theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: Inter, sans-serif; }
.stApp { background: radial-gradient(circle at 75% 0%, #26334b 0, #111827 38%, #0b1120 100%); color: #f8fafc; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#111827,#192335); border-right:1px solid #344158; }
[data-testid="stSidebar"] * { color:#f8fafc !important; }
.block-container { padding-top: 1.3rem; padding-bottom: 2rem; max-width: 1600px; }
.hero { padding: 25px 28px; border-radius: 16px; text-align:center; background:linear-gradient(110deg,rgba(7,15,30,.92),rgba(35,22,39,.78)), url('https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1800&q=85'); background-size:cover; background-position:center; border:1px solid #43506a; box-shadow:0 10px 35px #0005; margin-bottom:16px; }
.hero h1 {font-size:clamp(1.6rem,3vw,2.6rem);font-weight:800;margin:0;color:#fff;}
.hero p {font-size:1.05rem;margin:5px 0 0;color:#e2e8f0;}
.kpi {padding:16px 18px;border-radius:14px;color:white;min-height:100px;box-shadow:0 8px 22px #0003;}
.kpi-label {font-size:.9rem;font-weight:600;opacity:.95}.kpi-value {font-size:1.8rem;font-weight:800;margin-top:5px;}
.kpi-blue{background:linear-gradient(120deg,#1674cf,#1762a9)} .kpi-green{background:linear-gradient(120deg,#16a36a,#148b5b)}
.kpi-purple{background:linear-gradient(120deg,#8744ce,#6933a7)} .kpi-orange{background:linear-gradient(120deg,#ff941b,#ed7900)}
.panel {background:rgba(30,41,59,.78);border:1px solid #3a4962;border-radius:14px;padding:16px 18px;margin-bottom:12px;}
.small-muted {color:#b8c4d6;font-size:.88rem}
div[data-testid="stMetric"] {background:rgba(30,41,59,.75);padding:12px 14px;border:1px solid #3b4a63;border-radius:12px;}
div[data-testid="stMetricLabel"] p {color:#cbd5e1 !important}
.stButton>button {border-radius:9px;border:1px solid #52627d;font-weight:600;}
.stTabs [data-baseweb="tab-list"] {gap:8px;background:#1a2639;padding:6px;border-radius:12px;}
.stTabs [data-baseweb="tab"] {border-radius:8px;color:#e5e7eb;}
.stTabs [aria-selected="true"] {background:#237bd1;color:white;}
[data-testid="stDataFrame"] {border:1px solid #43516a;border-radius:10px;overflow:hidden;}
hr {border-color:#40506a !important;}
</style>
""", unsafe_allow_html=True)

# ---------- Helpers ----------
def norm_col(name):
    return re.sub(r"[^a-z0-9]", "", str(name).lower())

def find_col(df, candidates):
    lookup = {norm_col(c): c for c in df.columns}
    for candidate in candidates:
        if norm_col(candidate) in lookup:
            return lookup[norm_col(candidate)]
    for c in df.columns:
        if any(norm_col(x) in norm_col(c) for x in candidates):
            return c
    return None

def to_number(series):
    return pd.to_numeric(series.astype(str).str.replace(r"[^0-9.\-]", "", regex=True), errors="coerce")

def split_values(value):
    if pd.isna(value):
        return []
    return [x.strip() for x in re.split(r"[,|]", str(value)) if x.strip()]

def money_label(value):
    if pd.isna(value): return "—"
    value = float(value)
    if abs(value) >= 1_000_000_000: return f"${value/1_000_000_000:.2f}B"
    if abs(value) >= 1_000_000: return f"${value/1_000_000:.1f}M"
    return f"${value:,.0f}"

@st.cache_data(show_spinner=False)
def load_csv(file_bytes, filename):
    from io import BytesIO
    return pd.read_csv(BytesIO(file_bytes))

# ---------- Sidebar / data loading ----------
st.sidebar.markdown("<div style='background:#f5c518;color:#111827;font-weight:900;font-size:30px;display:inline-block;padding:5px 12px;border-radius:9px'>IMDb</div>", unsafe_allow_html=True)
st.sidebar.title("Movie Analytics Dashboard")
st.sidebar.divider()

uploaded = st.sidebar.file_uploader("Upload IMDb CSV dataset", type=["csv"], help="Upload the Top 250 Movies on IMDb CSV file.")
default_path = Path(__file__).parent / "Top 250 movies on imdb in 2026.csv"
if uploaded is not None:
    try:
        df = load_csv(uploaded.getvalue(), uploaded.name)
        st.session_state["dataset_name"] = uploaded.name
    except Exception as exc:
        st.error(f"Could not read the uploaded CSV: {exc}")
        st.stop()
elif default_path.exists():
    df = pd.read_csv(default_path)
    st.session_state["dataset_name"] = default_path.name
else:
    st.markdown("<div class='hero'><h1>IMDb Movie Analytics Dashboard</h1><p>Explore. Analyze. Discover.</p></div>", unsafe_allow_html=True)
    st.info("Upload your **Top 250 Movies on IMDb** CSV using the uploader in the left sidebar to load the dashboard.")
    st.markdown("### Expected data fields")
    st.write("The app automatically detects common column names for movie title, genre, country, IMDb rating, votes and worldwide gross. It also displays the dataset preview and column information after upload.")
    st.stop()

if df.empty:
    st.warning("The CSV file is empty. Please upload a dataset containing movie records.")
    st.stop()

# Detect and standardize important fields without changing the original columns.
title_col = find_col(df, ["title", "movie", "movieTitle", "originalTitle", "primaryTitle"])
genre_col = find_col(df, ["genres", "genre"])
country_col = find_col(df, ["country", "countries", "origin", "countryOfOrigin"])
rating_col = find_col(df, ["averageRating", "imdbRating", "rating"])
votes_col = find_col(df, ["numVotes", "votes", "numberOfVotes"])
gross_col = find_col(df, ["grossWorldwide", "worldwideGross", "worldwideGrossCollection", "gross"])

if title_col is None:
    st.error("A movie title column was not found. Please check that your CSV contains a title/movie column.")
    st.write("Available columns:", list(df.columns))
    st.stop()
for col in [rating_col, votes_col, gross_col]:
    if col:
        df[col] = to_number(df[col])

# Sidebar navigation
page = st.sidebar.radio("Navigate", ["Dashboard", "Movie Explorer", "Movie Search (Form + Session State)"], label_visibility="visible")
with st.sidebar.expander("Dataset Information", expanded=True):
    st.write(f"**File:** {st.session_state.get('dataset_name', 'Uploaded CSV')}")
    st.write(f"**Rows:** {df.shape[0]:,}")
    st.write(f"**Columns:** {df.shape[1]}")
    st.caption("Movie titles, ratings, votes, genres, countries and gross collections (where available).")

# Common data prep
rating_series = df[rating_col].dropna() if rating_col else pd.Series(dtype=float)
votes_series = df[votes_col].fillna(0) if votes_col else pd.Series(dtype=float)
genre_values = sorted({g for value in df[genre_col].dropna() for g in split_values(value)}) if genre_col else []
country_values = sorted({c for value in df[country_col].dropna() for c in split_values(value)}) if country_col else []

# ---------- Dashboard ----------
if page == "Dashboard":
    st.markdown("<div class='hero'><h1>IMDb Movie Analytics Dashboard</h1><p>Explore. Analyze. Discover.</p></div>", unsafe_allow_html=True)
    total_movies = len(df)
    avg_rating = rating_series.mean() if not rating_series.empty else 0
    highest_rating = rating_series.max() if not rating_series.empty else 0
    total_votes = votes_series.sum() if not votes_series.empty else 0
    kpis = st.columns(4)
    values = [("🎬", "Total Movies", f"{total_movies:,}", "kpi-blue"), ("⭐", "Average IMDb Rating", f"{avg_rating:.1f}" if avg_rating else "N/A", "kpi-green"), ("🏆", "Highest Rating", f"{highest_rating:.1f}" if highest_rating else "N/A", "kpi-purple"), ("👥", "Total Votes", f"{total_votes:,.0f}", "kpi-orange")]
    for col, (emoji, label, value, color) in zip(kpis, values):
        with col:
            st.markdown(f"<div class='kpi {color}'><div class='kpi-label'>{emoji} &nbsp;{label}</div><div class='kpi-value'>{value}</div></div>", unsafe_allow_html=True)
    st.divider()
    tab_genre, tab_rating, tab_gross = st.tabs(["📊  Genre Analysis", "🥧  Rating Analysis", "🪙  Gross Collection"])
    with tab_genre:
        left, right = st.columns([1, 1])
        with left:
            st.subheader("Movies by Genre")
            if genre_col:
                genre_counts = df[genre_col].dropna().apply(split_values).explode().value_counts().head(15).rename_axis("Genre").reset_index(name="Movies")
                fig = px.bar(genre_counts, x="Genre", y="Movies", color="Genre", text="Movies", template="plotly_dark")
                fig.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=20,b=10), xaxis_title="Genre", yaxis_title="Movie Count")
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("Genre column not found in this CSV.")
        with right:
            st.subheader("IMDb Rating Distribution")
            if not rating_series.empty:
                fig = px.histogram(df, x=rating_col, nbins=14, template="plotly_dark", color_discrete_sequence=["#2f8cff"])
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=20,b=10), xaxis_title="IMDb Rating", yaxis_title="Number of Movies")
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("IMDb rating column not found in this CSV.")
    with tab_rating:
        st.subheader("Rating vs Number of Votes")
        if rating_col and votes_col:
            scatter_df = df[[rating_col, votes_col, title_col]].dropna()
            fig = px.scatter(scatter_df, x=rating_col, y=votes_col, hover_name=title_col, log_y=True, template="plotly_dark", opacity=.75, color_discrete_sequence=["#2694ff"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="IMDb Rating", yaxis_title="Number of Votes (log scale)")
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Rating and/or votes columns were not found.")
        if rating_col:
            st.subheader("Highest Rated Movies")
            st.dataframe(df.sort_values(rating_col, ascending=False)[[c for c in [title_col, genre_col, rating_col, votes_col] if c]].head(10), use_container_width=True, hide_index=True)
    with tab_gross:
        st.subheader("Top 10 Movies by Worldwide Gross")
        if gross_col:
            gross_df = df.dropna(subset=[gross_col]).sort_values(gross_col, ascending=False).head(10).copy()
            gross_df["Gross Label"] = gross_df[gross_col].apply(money_label)
            fig = px.bar(gross_df.sort_values(gross_col), x=gross_col, y=title_col, orientation="h", text="Gross Label", template="plotly_dark", color_discrete_sequence=["#ff941b"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Worldwide Gross", yaxis_title="Movie Title", margin=dict(l=10,r=20,t=20,b=10))
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(gross_df[[title_col, gross_col]].rename(columns={title_col:"Movie",gross_col:"Worldwide Gross"}), use_container_width=True, hide_index=True)
        else: st.info("Worldwide gross column was not found in this CSV.")
    st.success(f"Dashboard loaded successfully! Explore {len(df):,} movie records.")
    with st.expander("Dataset Preview and Data Quality"):
        st.write("**First 10 records**")
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Column data types**")
            st.dataframe(df.dtypes.astype(str).rename("Data Type"), use_container_width=True)
        with c2:
            st.write("**Missing values by column**")
            st.dataframe(df.isna().sum().rename("Missing Values"), use_container_width=True)
        st.caption(f"Dataset shape: {df.shape[0]} rows × {df.shape[1]} columns")

# ---------- Interactive Movie Explorer ----------
elif page == "Movie Explorer":
    st.title("🔎 Interactive Movie Explorer")
    st.caption("Filter, search and sort the movie collection. All filters work together.")
    with st.container(border=True):
        c1,c2,c3 = st.columns(3)
        with c1:
            selected_genre = st.selectbox("Genre", ["All"] + genre_values, key="explorer_genre") if genre_values else "All"
            selected_countries = st.multiselect("Countries", country_values, key="explorer_countries") if country_values else []
        with c2:
            if rating_col and not rating_series.empty:
                low, high = float(rating_series.min()), float(rating_series.max())
                rating_range = st.slider("IMDb Rating Range", min_value=low, max_value=high, value=(low, high), step=0.1, key="explorer_rating")
            else: rating_range = (0.0, 10.0)
            min_votes = st.number_input("Minimum Votes", min_value=0, value=0, step=1000, key="explorer_votes")
        with c3:
            title_query = st.text_input("Search Movie Title", placeholder="Enter a movie title...", key="explorer_title")
            sort_order = st.radio("Sort by IMDb Rating", ["Descending", "Ascending"], horizontal=True, key="explorer_sort")
    filtered = df.copy()
    if selected_genre != "All" and genre_col:
        filtered = filtered[filtered[genre_col].apply(lambda x: selected_genre in split_values(x))]
    if selected_countries and country_col:
        filtered = filtered[filtered[country_col].apply(lambda x: any(c in split_values(x) for c in selected_countries))]
    if rating_col:
        filtered = filtered[filtered[rating_col].between(rating_range[0], rating_range[1], inclusive="both")]
    if votes_col:
        filtered = filtered[filtered[votes_col].fillna(0) >= min_votes]
    if title_query.strip():
        filtered = filtered[filtered[title_col].astype(str).str.contains(title_query.strip(), case=False, na=False)]
    if rating_col:
        filtered = filtered.sort_values(rating_col, ascending=(sort_order == "Ascending"))
    a,b = st.columns([1,5])
    a.metric("Filtered Movies", f"{len(filtered):,}")
    if b.button("↺ Reset Filters", use_container_width=False):
        for key in ["explorer_genre","explorer_countries","explorer_rating","explorer_votes","explorer_title","explorer_sort"]:
            st.session_state.pop(key, None)
        st.rerun()
    st.dataframe(filtered, use_container_width=True, hide_index=True, height=430)
    st.caption(f"Showing {len(filtered):,} of {len(df):,} movies.")

# ---------- Form + Session State ----------
else:
    st.title("🔍 Movie Search")
    st.caption("Search using a form. Your selected result is saved in Streamlit session state.")
    if "selected_movie" not in st.session_state:
        st.session_state.selected_movie = None
    with st.form("movie_search_form", clear_on_submit=False):
        search_title = st.text_input("Movie Title", placeholder="e.g. Inception")
        preferred_genre = st.selectbox("Preferred Genre", ["Any"] + genre_values) if genre_values else "Any"
        min_rating = st.slider("Minimum IMDb Rating", 0.0, 10.0, 7.0, 0.1)
        submitted = st.form_submit_button("🔎 Search Movie", use_container_width=True)
    if submitted:
        matches = df.copy()
        matches = matches[matches[title_col].astype(str).str.contains(search_title.strip(), case=False, na=False)] if search_title.strip() else matches
        if preferred_genre != "Any" and genre_col:
            matches = matches[matches[genre_col].apply(lambda x: preferred_genre in split_values(x))]
        if rating_col:
            matches = matches[matches[rating_col] >= min_rating]
        if not matches.empty:
            st.session_state.selected_movie = matches.sort_values(rating_col, ascending=False).iloc[0].to_dict() if rating_col else matches.iloc[0].to_dict()
            st.success("Matching movie found!")
        else:
            st.session_state.selected_movie = None
            st.info("No movie matched those preferences. Try a different title, genre or rating.")
    if st.session_state.selected_movie:
        movie = st.session_state.selected_movie
        st.markdown("### Selected Movie")
        st.subheader(str(movie.get(title_col, "Movie")))
        c1,c2,c3 = st.columns(3)
        c1.metric("IMDb Rating", f"{movie.get(rating_col):.1f}" if rating_col and pd.notna(movie.get(rating_col)) else "N/A")
        c2.metric("Votes", f"{movie.get(votes_col):,.0f}" if votes_col and pd.notna(movie.get(votes_col)) else "N/A")
        c3.metric("Genre", str(movie.get(genre_col, "N/A")) if genre_col else "N/A")
        st.dataframe(pd.DataFrame([movie]), use_container_width=True, hide_index=True)

st.sidebar.divider()
st.sidebar.caption("IMDb Movie Analytics • Streamlit project")
