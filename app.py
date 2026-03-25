import streamlit as st
import pandas as pd
import re
import os

# Sahifa sozlamalari
st.set_page_config(page_title="TR-UZ Parallel Korpus", layout="wide")

# Maxsus dizayn (Och havorang va uslublar)
st.markdown("""
    <style>
    .main {
        background-color: #f0f8ff;
    }
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

# Ma'lumotlarni yuklash
@st.cache_data
def load_data():
    file_name = "coliqushi.tr_uz.xlsx" 
    if os.path.exists(file_name):
        df = pd.read_excel(file_name).fillna('')
        # So'zlar sonini hisoblash (taxminiy)
        total_words = df.iloc[:, 1:3].astype(str).apply(lambda x: x.str.split().str.len()).sum().sum()
        return df, len(df), total_words
    else:
        return pd.DataFrame(), 0, 0

df, total_texts, total_words_count = load_data()

# 1. Sarlavha va Statistika (Och havorang blokda)
st.markdown(f"""
    <div class="stats-container">
        <h1 style='color: #0d47a1; margin-bottom: 0;'>Turkcha-O'zbekcha Parallel Korpus</h1>
        <p style='font-size: 1.2rem; color: #1565c0;'>
            <b>{total_texts:,}</b> matnlar | <b>{total_words_count:,}</b> so'zlar | <b>Paralel</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

# 2. Qidiruv paneli (Tepada)
st.subheader("🔍 Qidiruv va Filtrlash")
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search_query = st.text_input("Kalit so'zni kiriting:", placeholder="Masalan: kitob yoki kitap")

with col2:
    lang_filter = st.selectbox("Qidiruv tili:", 
                               ["Ikki tildan", "Faqat turk tilidan", "Faqat o'zbek tilidan"])

with col3:
    limit_filter = st.selectbox("Natijalar soni:", 
                                ["10 ta", "20 ta", "Barchasi"])

# Qidiruv logikasi
if search_query:
    limit = 10 if limit_filter == "10 ta" else 20 if limit_filter == "20 ta" else 1000000
    
    results = []
    search_pat = rf'\b{re.escape(search_query)}\w*'
    
    for _, row in df.iterrows():
        txt_tr = str(row.iloc[1])
        txt_uz = str(row.iloc[2])
        
        found_tr = re.search(search_pat, txt_tr, re.I)
        found_uz = re.search(search_pat, txt_uz, re.I)
        
        match = False
        if lang_filter == "Ikki tildan" and (found_tr or found_uz):
            match = True
        elif lang_filter == "Faqat turk tilidan" and found_tr:
            match = True
        elif lang_filter == "Faqat o'zbek tilidan" and found_uz:
            match = True
            
        if match:
            # Highlight funksiyasi
            def mark(text, word):
                return re.sub(rf'(\b{re.escape(word)}\w*)', r'<mark>\1</mark>', text, flags=re.I)
            
            results.append({
                "tr": mark(txt_tr, search_query),
                "uz": mark(txt_uz, search_query)
            })
            if len(results) >= limit:
                break

    # 3. Natijalarni chiqarish
    st.info(f"Jami topilgan natijalar: {len(results)} ta")
    
    # Ikki kalonkada chiqarish
    for res in results:
        with st.container():
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""<div class="result-card"><b>TR:</b><br>{res['tr']}</div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div class="result-card"><b>UZ:</b><br>{res['uz']}</div>""", unsafe_allow_html=True)

else:
    st.write("---")
    st.info("Tizimdan foydalanish uchun yuqoridagi maydonga so'z kiriting.")
