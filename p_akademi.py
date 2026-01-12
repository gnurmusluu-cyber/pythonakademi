import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
import time

# --- PİTO PROTOKOLÜ VE BAĞLANTI ---
def init_connection():
    try:
        # 1. Kontrol: Secrets var mı?
        if "gcp_service_account" not in st.secrets:
            st.error("❌ HATA: Streamlit Secrets içinde 'gcp_service_account' anahtarı bulunamadı!")
            return None
        
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        url = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit"
        return client.open_by_url(url).get_worksheet(0)
    except Exception as e:
        st.error(f"⚠️ Bağlantı Kurulamadı: {e}")
        return None

sheet = init_connection()

# Müfredat Yükleme
with open('mufredat.json', 'r', encoding='utf-8') as f:
    mufredat = json.load(f)

# --- VERİ YÖNETİMİ (BOŞ VERİTABANI KORUMASI) ---
def get_clean_df():
    if sheet is None: return pd.DataFrame()
    data = sheet.get_all_records()
    if not data:
        # Eğer tablo boşsa, standart sütunlarla boş bir DataFrame oluştur
        return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Mevcut Modül", "Mevcut Egzersiz"])
    return pd.DataFrame(data)

# --- GİRİŞ VE KAYIT SİSTEMİ ---
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None and sheet is not None:
    st.title("🐍 Pito Python Akademi")
    tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])
    
    df = get_clean_df()
    
    with tab1:
        okul_no = st.text_input("Okul Numaranı Gir:", key="log_input")
        if st.button("Devam Et"):
            # Numara kontrolü (Sayısal olmalı)
            if not df.empty and str(okul_no) in df["Okul No"].astype(str).values:
                st.session_state.user = df[df["Okul No"].astype(str) == str(okul_no)].iloc[0].to_dict()
                st.rerun() # Macbook uyumu için şart
            else:
                st.warning("Seni tanımıyorum! Lütfen önce kayıt ol.")
    
    with tab2:
        with st.form("kayit_formu"):
            ad = st.text_input("Adın Soyadın:")
            no = st.text_input("Okul Numaran (Sayı):")
            sinif = st.selectbox("Sınıfın:", ["9-A", "9-B", "10-A", "10-B"])
            if st.form_submit_button("Akademiye Katıl"):
                if ad and no.isdigit():
                    # Yeni kayıt satırı
                    new_row = [int(no), ad, sinif, 0, "Egg", 0, 1, 1, time.strftime("%Y-%m-%d")]
                    sheet.append_row(new_row)
                    st.success("Kaydın yapıldı! Şimdi giriş yapabilirsin.")
                else:
                    st.error("Lütfen bilgileri eksiksiz ve numarayı sayısal gir!")

# --- EĞİTİM EKRANI ---
elif st.session_state.user is not None:
    user = st.session_state.user
    st.sidebar.write(f"Hoş geldin, **{user['Öğrencinin Adı']}**!")
    # Eğitim kodları buraya devam eder...
