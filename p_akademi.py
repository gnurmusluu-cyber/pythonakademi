import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
import time

# --- PİTO PROTOKOLÜ VE BAĞLANTI ---
def init_connection():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        # Tabloyu aç
        return client.open_by_url("https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit").get_worksheet(0)
    except Exception as e:
        return None

sheet = init_connection()

# Müfredat yükleme
with open('mufredat.json', 'r', encoding='utf-8') as f:
    mufredat = json.load(f)

# --- VERİ KONTROLÜ VE LİDERLİK ---
def get_safe_data():
    if sheet is None: return pd.DataFrame()
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def show_leaderboard():
    df = get_safe_data()
    st.sidebar.title("🏆 Liderlik Panosu")
    
    if df.empty:
        st.sidebar.info("Henüz kayıtlı öğrenci bulunmuyor. İlk sen ol!")
        return

    # Okul Top 5
    st.sidebar.subheader("🏫 Okul Geneli")
    if "Puan" in df.columns:
        top_school = df.sort_values(by="Puan", ascending=False).head(5)
        st.sidebar.table(top_school[["Öğrencinin Adı", "Puan"]])
    
    # Şampiyon Sınıf
    if "Sınıf" in df.columns and "Puan" in df.columns:
        st.sidebar.subheader("⭐ Şampiyon Sınıf")
        class_scores = df.groupby("Sınıf")["Puan"].sum()
        if not class_scores.empty:
            st.sidebar.success(f"Lider: {class_scores.idxmax()}")

# --- ANA UYGULAMA MANTIĞI ---
if sheet is None:
    st.error("Veritabanı bağlantısı kurulamadı. Lütfen teknik yöneticiye danışın.")
else:
    show_leaderboard()
    
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        st.title("🐍 Pito Python Akademi")
        tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
        
        with tab1:
            okul_no = st.text_input("Okul Numaran:")
            if st.button("Eğitime Başla"):
                df = get_safe_data()
                if not df.empty and str(okul_no) in df["Okul No"].astype(str).values:
                    user_data = df[df["Okul No"].astype(str) == str(okul_no)].iloc[0].to_dict()
                    st.session_state.user = user_data
                    st.rerun()
                else:
                    st.warning("Seni tanımıyorum, lütfen önce kayıt ol!")
        
        with tab2:
            st.subheader("Yeni Öğrenci Kaydı")
            # Kayıt formu işlemleri...
            # (Yeni kayıt olduğunda sheet.append_row ile veritabanına eklenir)
    else:
        # Eğitim ekranı ve Pito pedagojik geri bildirimleri
        user = st.session_state.user
        # ... (Önceki başarılı eğitim kodları buraya gelecek)
        
        # Syntax hatasına sebep olan kısmın düzeltilmiş hali:
        # Çıktıyı önce temizleyip sonra gösteriyoruz
        raw_solution = mufredat["Modül 1: Merhaba Python"][0]["cozum"] # Örnek erişim
        clean_output = raw_solution.replace('print(', '').replace(')', '').replace("'", "").replace('"', "")
        st.code(f"Kod Çalıştırıldı...\nÇıktı: {clean_output}")
