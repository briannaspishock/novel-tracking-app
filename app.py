import pandas as pd
import requests
import streamlit as st

# cobfig
TARGET_WORDS = 5000

# jsonbin
BIN_ID = st.secrets.get("JSONBIN_BIN_ID", "6a67ba0cf5f4af5e29c9b023")
API_KEY = st.secrets.get("JSONBIN_API_KEY", "$2a$10$EMTUkpfWbyxq52/XEcwpC.YII2yX8zDP9SjkRt7Ni4AefanCP.hW6")

headers = {
    "Content-Type": "application/json",
    "X-Master-Key": API_KEY
}

st.set_page_config(page_title="5k word challenge", page_icon="📓", layout="centered")

# pink aesthetic 
st.markdown("""
    <style>
    .main { background-color: #FFF0F5; }
    h1 { color: #D81B60 !important; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    h2, h3 { color: #C2185B !important; }
    .stProgress > div > div > div > div { background-color: #FF1493 !important; }
    .stButton>button { background-color: #FF69B4 !important; color: white !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; padding: 10px 24px !important; }
    .stButton>button:hover { background-color: #FF1493 !important; color: white !important; transform: scale(1.02); }
    div[data-baseweb="select"] > div { border-color: #FF69B4 !important; }
    </style>
""", unsafe_allow_html=True)

# helpers
def load_data():
    try:
        res = requests.get(f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest", headers=headers)
        if res.status_code == 200:
            return res.json()["record"]
    except Exception:
        pass
    return {"Brie": [], "Kat": []}

def save_data(data):
    requests.put(f"https://api.jsonbin.io/v3/b/{BIN_ID}", json=data, headers=headers)

if "data" not in st.session_state:
    st.session_state.data = load_data()

# header
st.title("💖 5k writing sprint")
st.caption("fill the bar to 5,000 words before the week ends!")

# overview of writer totals 
brie_total = sum(entry["words"] for entry in st.session_state.data.get("Brie", []))
kat_total = sum(entry["words"] for entry in st.session_state.data.get("Kat", []))

st.markdown("### 📊 progress leaderboard")

col1, col2 = st.columns(2)

with col1:
    st.subheader("✨ Brie")
    pct_b = min(float(brie_total) / TARGET_WORDS, 1.0)
    st.metric(label="Total Words", value=f"{brie_total:,}", delta=f"{TARGET_WORDS - brie_total:,} left")
    st.progress(pct_b, text=f"{pct_b * 100:.1f}% of {TARGET_WORDS:,}")

with col2:
    st.subheader("✨ Kat")
    pct_k = min(float(kat_total) / TARGET_WORDS, 1.0)
    st.metric(label="Total Words", value=f"{kat_total:,}", delta=f"{TARGET_WORDS - kat_total:,} left")
    st.progress(pct_k, text=f"{pct_k * 100:.1f}% of {TARGET_WORDS:,}")

st.divider()

# daily log input form
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

# history
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
