import streamlit as st
import pandas as pd
import re
import os

# ================== SAHIFA ==================
st.set_page_config(page_title="Parallel korpus", layout="wide")

# ================== STYLE ==================
st.markdown("""
    <style>
    .main { background-color: #f0f8ff; }
    .stats-container {
        background-color: #e3f2fd;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 25px;
        border: 1px solid #bbdefb;
    }
    .result-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #2196f3;
        margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    mark {
        background: yellow;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ================== DATA ==================
@st.cache_data
def load_data():
    file_name = "coliqushi.tr_uz.xlsx"
    if os.path.exists(file_name):
        df = pd.read_excel(file_name).fillna('')
        total_words = df.iloc[:, 1:3].astype(str).apply(lambda x: x.str.split().str.len()).sum().sum()
        return df, len(df), total_words
    return pd.DataFrame(), 0, 0

df, total_sentences, total_words_count = load_data()

# ================== METADATA ==================
metadata = {
    "Kitob": "Choliqushi",
    "Muallifi": "Rashod Nuri Guntekin",
    "Muallif jinsi": "Erkak",
    "Muallifning yashagan davri": "1892–1956 yil",
    "Manba nomi": "Choliqushi",
    "Yaratilgan vaqti": "1922",
    "Nashr yili (vaqti)": "1956",
    "Tarjimon": "Mirza kalon Ismoiliy",
    "Qo'llanish sohasi": "Adabiyotshunoslik",
    "Adabiy turi": "Nasr",
    "Janri": "Roman",
    "Uslubi": "Badiiy",
    "Auditoriya yoshi": "18+",
    "Auditoriyaning salohiyat darajasi": "Keng omma uchun",
    "Ichki korpus turi": "Parallel",
    "Sahifasi": "43",
    "Teglovchi": "Norbekova Bahora"
}
# ================== TITLE ==================
st.markdown(f"""
<div class="stats-container">
    <h1 style='color: #0d47a1;'>Turkcha o'zbekcha parallel korpus</h1>
    <p><b>{total_sentences:,}</b> gaplar | <b>{total_words_count:,}</b> so'zlar | <b>Parallel</b></p>
</div>
""", unsafe_allow_html=True)

# ================== SEARCH ==================
st.subheader("🔍 Qidiruv va filtrlash")

col1, col2, col3, col4 = st.columns([2,1,1,1])

with col1:
    search_query = st.text_input("Qidiruv so'zi:")

with col2:
    lang_filter = st.selectbox("Qidiruv turi:", 
        ["Ikkitildagi parallel gap", "Turk tilidan", "O'zbek tilidan"])

with col3:
    search_mode = st.selectbox("Qidiruv usuli:", 
        ["Aniq so'z", "Barcha shakllar"])

with col4:
    limit_filter = st.selectbox("Natijalar soni:", ["10", "20", "Barchasi"])

# ================== SEARCH ==================
def exact_match(text, word):
    return re.search(rf'\b{re.escape(word)}\b', text, re.I)

def stem_match(text, word):
    return re.search(rf'\b{re.escape(word)}\w*', text, re.I)

def highlight(text, word, mode):
    if mode == "Aniq so'z":
        pattern = rf'(\b{re.escape(word)}\b)'
    else:
        pattern = rf'(\b{re.escape(word)}\w*)'
    return re.sub(pattern, r'<mark>\1</mark>', text, flags=re.I)

if search_query:
    limit = 10 if limit_filter == "10" else 20 if limit_filter == "20" else 999999
    results = []

    for _, row in df.iterrows():
        tr = str(row.iloc[1])
        uz = str(row.iloc[2])

        if search_mode == "Aniq so'z":
            f_tr = exact_match(tr, search_query)
            f_uz = exact_match(uz, search_query)
        else:
            f_tr = stem_match(tr, search_query)
            f_uz = stem_match(uz, search_query)

        match = False
        if lang_filter == "Ikkitildagi parallel gap" and (f_tr or f_uz):
            match = True
        elif lang_filter == "Turk tilidan" and f_tr:
            match = True
        elif lang_filter == "O'zbek tilidan" and f_uz:
            match = True

        if match:
            results.append({
                "tr": highlight(tr, search_query, search_mode),
                "uz": highlight(uz, search_query, search_mode)
            })

        if len(results) >= limit:
            break

    # ================== OUTPUT ==================
    st.info(f"Jami topilgan gaplar: {len(results)} ta")

    for res in results:
        c1, c2 = st.columns(2)

        with c1:
            st.markdown(f"<div class='result-card'><b>TR:</b><br>{res['tr']}</div>", unsafe_allow_html=True)

        with c2:
            st.markdown(f"<div class='result-card'><b>UZ:</b><br>{res['uz']}</div>", unsafe_allow_html=True)

        # ===== METADATA =====
        with st.expander("Ekstralingvistik teg"):
            for k, v in metadata.items():
                st.write(f"**{k}:** {v}")

else:
    st.info("Qidiruv uchun so'z kiriting")
