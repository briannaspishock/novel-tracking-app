import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# --- config ---
TARGET_WORDS = 15000

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

# --- google sheets connection ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(ttl="0s") # ttl=0 ensure live refresh
        if df is None or df.empty:
            return pd.DataFrame(columns=["writer", "date", "words"])
        return df
    except Exception:
        return pd.DataFrame(columns=["writer", "date", "words"])

df_logs = load_data()

# --- app header ---
st.title("💖 15k writing sprint")
st.caption("fill the bar to 15,000 words before the week ends!")

# --- totals ---
brie_total = int(df_logs[df_logs["writer"] == "Brie"]["words"].sum()) if not df_logs.empty else 0
kat_total = int(df_logs[df_logs["writer"] == "Kat"]["words"].sum()) if not df_logs.empty else 0

st.markdown("### 📊 Progress Leaderboard")

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
        new_row = pd.DataFrame([{
            "writer": author,
            "date": str(entry_date),
            "words": int(words_added)
        }])
        
        updated_df = pd.concat([df_logs, new_row], ignore_index=True)
        conn.update(data=updated_df)
        st.success(f"added {words_added:,} words for {author}!")
        st.rerun()

st.divider()

# --- history & breakdown ---
with st.expander("📜 writing logs & charts"):
    if not df_logs.empty:
        st.dataframe(df_logs.sort_values(by="date", ascending=False), use_container_width=True)
        st.bar_chart(df_logs, x="date", y="words", color="writer", stack=False)
    else:
        st.info("no words logged yet! fill in the form above to kick things off!")
