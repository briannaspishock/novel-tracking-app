import os
import json
import pandas as pd
import streamlit as st

# --- config ---
TARGET_WORDS = 15000
DATA_FILE = "word_count_data.json"

st.set_page_config(page_title="15k Word Challenge", page_icon="💖", layout="centered")

# --- pink aesthetic ---
st.markdown("""
    <style>
    /* main background & font styling */
    .main {
        background-color: #FFF0F5;
    }
    
    /* Header Styling */
    h1 {
        color: #D81B60 !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
    }
    h2, h3 {
        color: #C2185B !important;
    }
    
    /* customizing progress bar colors to hot pink */
    .stProgress > div > div > div > div {
        background-color: #FF1493 !important;
    }
    
    /* button styling */
    .stButton>button {
        background-color: #FF69B4 !important;
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
        font-weight: bold !important;
        padding: 10px 24px !important;
    }
    .stButton>button:hover {
        background-color: #FF1493 !important;
        color: white !important;
        transform: scale(1.02);
    }
    
    /* input highlights */
    div[data-baseweb="select"] > div {
        border-color: #FF69B4 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- data helpers ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"Brie": [], "Kat": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

if "data" not in st.session_state:
    st.session_state.data = load_data()

# --- app header ---
st.title("💖 15k writing sprint")
st.caption("fill the bar to 15,000 words before the week ends!")

# --- totals ---
brie_total = sum(entry["words"] for entry in st.session_state.data.get("Brie", []))
kat_total = sum(entry["words"] for entry in st.session_state.data.get("Kat", []))

st.markdown("### 📊 Progress Leaderboard")

col1, col2 = st.columns(2)

with col1:
    st.subheader("✨ Brie")
    pct_b = min(float(brie_total) / TARGET_WORDS, 1.0)
    st.metric(label="Total Words", value=f"{brie_total:,}", delta=f"{TARGET_WORDS - brie_total:,} left")
    st.progress(pct_b, text=f"{pct_b * 100:.1f}% of {TARGET_WORDS:,}")

with col2:
    st.subheader("✨ Kat")
    pct_b = min(float(kat_total) / TARGET_WORDS, 1.0)
    st.metric(label="Total Words", value=f"{kat_total:,}", delta=f"{TARGET_WORDS - kat_total:,} left")
    st.progress(pct_b, text=f"{pct_b * 100:.1f}% of {TARGET_WORDS:,}")

st.divider()

# --- input form ---
st.markdown("### ✍️ log today's words")

with st.form("log_words_form", clear_on_submit=True):
    col_person, col_date, col_words = st.columns([1, 1, 1])
    
    with col_person:
        author = st.selectbox("writer", ["Brie", "Kat"])
    
    with col_date:
        entry_date = st.date_input("date")
        
    with col_words:
        words_added = st.number_input("words written", min_value=1, max_value=20000, step=100)
        
    submitted = st.form_submit_button("add words ✨", use_container_width=True)

    if submitted:
        entry = {"date": str(entry_date), "words": int(words_added)}
        st.session_state.data[author].append(entry)
        save_data(st.session_state.data)
        st.success(f"added {words_added:,} words for {author}!")
        st.rerun()

st.divider()

# --- history & breakdown ---
with st.expander("📜 writing logs & charts"):
    logs = []
    for person in ["Brie", "Kat"]:
        for entry in st.session_state.data.get(person, []):
            logs.append({"writer": person, "date": entry["date"], "words": entry["words"]})
    
    if logs:
        df = pd.DataFrame(logs)
        st.dataframe(df.sort_values(by="date", ascending=False), use_container_width=True)
        st.bar_chart(df, x="date", y="words", color="writer", stack=False)
    else:
        st.info("no words logged yet! fill in the form above to kick things off!")
