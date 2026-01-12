import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
import time

# --- 1. AYARLAR VE BAĞLANTI ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide")

def init_connection():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        # Streamlit Secrets üzerinden yetkilendirme
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        url = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit"
        return client.open_by_url(url).get_worksheet(0)
    except Exception as e:
        st.error(f"⚠️ Bağlantı Hatası: {e}")
        return None

sheet = init_connection()

# Müfredat Yükleme
try:
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        mufredat = json.load(f)
except FileNotFoundError:
    st.error("mufredat.json dosyası bulunamadı!")
    st.stop()

# --- 2. VERİ YÖNETİMİ ---
def get_clean_data():
    if sheet is None: return pd.DataFrame()
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def update_progress(user_no, updates):
    df = get_clean_data()
    if df.empty: return
    try:
        row_idx = df[df['Okul No'].astype(str) == str(user_no)].index[0] + 2
        for col, val in updates.items():
            col_idx = df.columns.get_loc(col) + 1
            sheet.update_cell(row_idx, col_idx, val)
    except Exception as e:
        st.error(f"Güncelleme Hatası: {e}")

# --- 3. GİRİŞ VE KAYIT ---
if "user" not in st.session_state:
    st.session_state.user = None
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

def login_screen():
    st.title("🐍 Pito Python Akademi")
    st.info("Süleyman Bölünmez Anadolu Lisesi Programlama Portalı")
    
    tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])
    
    df = get_clean_data()
    
    with tab1:
        okul_no = st.text_input("Okul Numaranı Gir:", key="login_input")
        if st.button("Akademiye Gir"):
            if not df.empty and str(okul_no) in df['Okul No'].astype(str).values:
                st.session_state.user = df[df['Okul No'].astype(str) == str(okul_no)].iloc[0].to_dict()
                st.rerun()
            else:
                st.warning("Numara bulunamadı. Lütfen önce kayıt ol.")
                
    with tab2:
        with st.form("register_form"):
            new_ad = st.text_input("Ad Soyad:")
            new_no = st.text_input("Okul No:")
            new_sinif = st.selectbox("Sınıf:", ["9-A", "9-B", "10-A", "10-B", "11-A", "12-A"])
            if st.form_submit_button("Kaydı Tamamla"):
                if new_ad and new_no.isdigit():
                    # Yeni öğrenci verisi (Görseldeki sütun yapısına uygun)
                    new_row = [int(new_no), new_ad, new_sinif, 0, "Egg", 0, 1, 1, time.strftime("%Y-%m-%d")]
                    sheet.append_row(new_row)
                    st.success("Kaydın oluşturuldu! Şimdi giriş yapabilirsin.")
                else:
                    st.error("Lütfen tüm alanları doğru doldur.")

# --- 4. EĞİTİM PANELİ ---
def main_academy():
    user = st.session_state.user
    moduller = list(mufredat.keys())
    m_idx = int(user["Mevcut Modül"]) - 1
    e_idx = int(user["Mevcut Egzersiz"]) - 1
    
    # Liderlik Tablosu (Sidebar)
    df = get_clean_data()
    if not df.empty:
        st.sidebar.title("🏆 Liderlik Tablosu")
        top_5 = df.sort_values(by="Puan", ascending=False).head(5)
        st.sidebar.table(top_5[["Öğrencinin Adı", "Puan"]])

    # Modül Sonu Kontrolü
    if m_idx >= len(moduller):
        st.balloons()
        st.success("🎓 Tüm modülleri tamamladın! Tebrikler!")
        return

    curr_mod = moduller[m_idx]
    ex = mufredat[curr_mod][e_idx]
    
    st.header(f"📍 {curr_mod}")
    st.subheader(ex["baslik"])
    st.markdown(f"> **Pito Notu:** {ex['pito_notu']}")
    
    # Hata Kontrolü
    is_locked = st.session_state.attempts >= 4
    u_input = st.text_input(ex["egzersiz"], value=ex["taslak"], disabled=is_locked)
    
    if not is_locked:
        if st.button("Kodu Çalıştır"):
            if u_input.strip() == ex["cozum"].strip():
                st.success("🎉 Harika! Doğru cevap.")
                # Çıktı işleme (SyntaxError korumalı)
                cikti = ex["cozum"].replace("print(", "").replace(")", "").replace("'", "").replace('"', "")
                st.code(f"Çıktı: {cikti}")
                
                # İlerleme Mantığı
                new_ex = e_idx + 2
                new_mod = m_idx + 1
                if new_ex > 5:
                    new_ex = 1
                    new_mod += 1
                
                update_progress(user["Okul No"], {
                    "Puan": int(user["Puan"]) + 20,
                    "Mevcut Modül": new_mod,
                    "Mevcut Egzersiz": new_ex
                })
                st.session_state.attempts = 0
                if st.button("Sonraki Adım"): st.rerun()
            else:
                st.session_state.attempts += 1
                if st.session_state.attempts == 3:
                    st.warning(f"💡 Pito'dan İpucu: {ex['ipucu']}")
                elif st.session_state.attempts >= 4:
                    st.error("❌ 4. hatayı yaptın. Bu adımdan puan alamadın.")
                    st.rerun()
                    
    if is_locked:
        st.info("🔓 Çözüm Bloğu")
        st.code(ex["cozum"], language="python")
        if st.button("Anladım, Sonraki Egzersize Geç"):
            new_ex = e_idx + 2
            new_mod = m_idx + 1
            if new_ex > 5:
                new_ex = 1
                new_mod += 1
            update_progress(user["Okul No"], {"Mevcut Modül": new_mod, "Mevcut Egzersiz": new_ex})
            st.session_state.attempts = 0
            st.rerun()

# --- 5. ÇALIŞTIR ---
if sheet is not None:
    if st.session_state.user is None:
        login_screen()
    else:
        main_academy()
