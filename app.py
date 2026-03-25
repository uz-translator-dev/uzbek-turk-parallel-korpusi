import streamlit as st
import pandas as pd
import re
import os

# Sahifa sozlamalari
st.set_page_config(page_title="TR-UZ Korpus", layout="wide")
st.title("🇹🇷🇺🇿 Parallel Korpus Qidiruv Tizimi")

# Ma'lumotlarni yuklash
@st.cache_data
def load_data():
    # DIQQAT: Fayl nomi GitHub-dagi bilan bir xil bo'lishi shart!
    file_name = "coliqushi.tr_uz.xlsx" 
    if os.path.exists(file_name):
        return pd.read_excel(file_name).fillna('')
    else:
        st.error(f"Xatolik: {file_name} fayli topilmadi! Iltimos, GitHub-ga yuklanganini tekshiring.")
        return pd.DataFrame()

df = load_data()

# Qidiruv paneli
st.sidebar.header("Qidiruv paneli")
uz_word = st.sidebar.text_input("O'zbekcha o'zak:", placeholder="Masalan: gul")
tr_word = st.sidebar.text_input("Turkcha o'zak:", placeholder="Masalan: çiçek")

if st.sidebar.button("🔍 IZLASH"):
    if not uz_word and not tr_word:
        st.warning("Iltimos, so'z kiriting!")
    else:
        # So'z o'zagi bo'yicha regex (word boundary \b bilan)
        uz_pat = rf'\b{re.escape(uz_word)}\w*' if uz_word else ""
        tr_pat = rf'\b{re.escape(tr_word)}\w*' if tr_word else ""

        results = []
        for _, row in df.iterrows():
            try:
                # 1-ustun TR, 2-ustun UZ (Sizning Excelingiz bo'yicha)
                txt_tr = str(row.iloc[1])
                txt_uz = str(row.iloc[2])

                m_uz = re.search(uz_pat, txt_uz, re.I) if uz_pat else True
                m_tr = re.search(tr_pat, txt_tr, re.I) if tr_pat else True

                if m_uz and m_tr:
                    def mark(text, word):
                        if not word: return text
                        return re.sub(rf'(\b{re.escape(word)}\w*)', r'<mark style="background:yellow; font-weight:bold">\1</mark>', text, flags=re.I)
                    
                    res_tr = mark(txt_tr, tr_word if tr_word else None)
                    res_uz = mark(txt_uz, uz_word if uz_word else None)
                    results.append((res_tr, res_uz))
            except: continue

        if results:
            st.success(f"{len(results)} ta natija topildi.")
            for r_tr, r_uz in results:
                st.markdown(f"**TR:** {r_tr}", unsafe_allow_html=True)
                st.markdown(f"**UZ:** {r_uz}", unsafe_allow_html=True)
                st.divider()
        else:
            st.info("Hech narsa topilmadi.")
else:
    st.info("Chap tomondan so'z kiriting.")