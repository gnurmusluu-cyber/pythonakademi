import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
import time

# --- PİTO PROTOKOLÜ AYARLARI ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide")

# Google Sheets Bağlantısı (Secrets üzerinden)
def init_connection():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_url("https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit")

try:
    conn = init_connection()
    sheet = conn.get_worksheet(0)
except Exception as e:
    st.error("Veritabanı bağlantısı kurulamadı. Lütfen teknik yöneticiye danışın.")
    st.stop()

# Müfredat Verisi
with open('mufredat.json', 'r', encoding='utf-8') as f:
    mufredat = json.load(f)

# --- YARDIMCI FONKSİYONLAR ---
def get_rank(puan):
    if puan < 100: return "Egg"
    elif puan < 300: return "Chick"
    elif puan < 600: return "Python Apprentice"
    elif puan < 1000: return "Python Coder"
    else: return "Python Hero"

def update_db(user_no, updates):
    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        row_idx = df[df['Okul No'] == int(user_no)].index[0] + 2 # Header + 0-index adjustment
        
        for col_name, value in updates.items():
            col_idx = df.columns.get_loc(col_name) + 1
            sheet.update_cell(row_idx, col_idx, value)
    except Exception as e:
        st.error(f"Veri yazılırken bir hata oluştu: {e}")

# --- SESSION STATE BAŞLATMA ---
if "user" not in st.session_state:
    st.session_state.user = None
if "attempts" not in st.session_state:
    st.session_state.attempts = 0
if "current_puan" not in st.session_state:
    st.session_state.current_puan = 20

# --- LİDERLİK TABLOSU (SIDEBAR) ---
def show_leaderboard():
    data = pd.DataFrame(sheet.get_all_records())
    st.sidebar.title("🏆 Liderlik Panosu")
    
    # Okul Top 5
    st.sidebar.subheader("🏫 Okul Geneli")
    top_school = data.sort_values(by="Puan", ascending=False).head(5)
    st.sidebar.dataframe(top_school[["Öğrencinin Adı", "Puan", "Rütbe"]], hide_index=True)
    
    # Şampiyon Sınıf
    st.sidebar.subheader("⭐ Şampiyon Sınıf")
    class_scores = data.groupby("Sınıf")["Puan"].sum().reset_index()
    if not class_scores.empty:
        champion = class_scores.loc[class_scores["Puan"].idxmax()]
        st.sidebar.info(f"Lider Sınıf: **{champion['Sınıf']}** ({champion['Puan']} Puan)")

# --- GİRİŞ VE KAYIT EKRANI ---
def login_screen():
    st.title("🐍 Pito Python Akademi")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Giriş Yap")
        okul_no = st.text_input("Okul Numaranı Gir (Sadece Sayı):", key="log_no")
        if st.button("Eğitime Devam Et"):
            if okul_no.isdigit():
                data = sheet.get_all_records()
                user = next((item for item in data if str(item["Okul No"]) == okul_no), None)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.warning("Bu numara kayıtlı değil. Lütfen yan taraftan kayıt ol!")
            else:
                st.error("Lütfen geçerli bir sayısal numara gir.")

    with col2:
        st.subheader("Yeni Kayıt")
        with st.form("kayit_formu"):
            n_ad = st.text_input("Ad Soyad:")
            n_no = st.text_input("Okul No:")
            n_sinif = st.selectbox("Sınıf:", ["9-A", "9-B", "10-A", "10-B", "11-A", "12-A"])
            if st.form_submit_button("Akademiye Katıl"):
                if n_no.isdigit() and n_ad:
                    sheet.append_row([int(n_no), n_ad, n_sinif, 0, "Egg", 0, 1, 1, time.strftime("%Y-%m-%d")])
                    st.success("Kaydın başarıyla oluşturuldu! Şimdi giriş yapabilirsin.")
                else:
                    st.error("Lütfen bilgileri eksiksiz ve numarayı sayısal gir.")

# --- ANA EĞİTİM PANELİ ---
def academy_main():
    user = st.session_state.user
    show_leaderboard()
    
    module_names = list(mufredat.keys())
    m_idx = int(user["Mevcut Modül"]) - 1
    e_idx = int(user["Mevcut Egzersiz"]) - 1
    
    # Mezuniyet Kontrolü
    if m_idx >= len(module_names):
        st.success("🎓 TEBRİKLER! Pito Python Akademi'den başarıyla mezun oldun!")
        if st.button("Eğitimi Tekrar Al (Puanın Sıfırlanır)"):
            update_db(user["Okul No"], {"Puan": 0, "Mevcut Modül": 1, "Mevcut Egzersiz": 1, "Tamamlanan Modüller": 0})
            st.session_state.user = None
            st.rerun()
        return

    curr_mod = module_names[m_idx]
    ex = mufredat[curr_mod][e_idx]
    
    st.title(f"📍 {curr_mod}")
    st.markdown(f"### {ex['baslik']}")
    st.info(f"**Pito'nun Notu:** {ex['pito_notu']}")

    # --- EDİTÖR ---
    st.subheader("💻 Kod Paneli")
    locked = st.session_state.attempts >= 4
    user_code = st.text_input(ex['egzersiz'], value=ex['taslak'], disabled=locked)

    if not locked:
        if st.button("Kodu Gönder"):
            if user_code.strip() == ex['cozum'].strip():
                # BAŞARI DURUMU
                st.balloons()
                st.success(f"🎉 Pito: Harika! Bu adımdan {st.session_state.current_puan} puan kazandın.")
                st.code(f"Çıktı: {ex['cozum']}")
                
                # İlerleme Mantığı
                new_e = e_idx + 2
                new_m = m_idx + 1
                if new_e > 5: # Modül bitti
                    new_e = 1
                    new_m += 1
                
                new_total_puan = int(user["Puan"]) + st.session_state.current_puan
                update_db(user["Okul No"], {
                    "Puan": new_total_puan,
                    "Mevcut Modül": new_m,
                    "Mevcut Egzersiz": new_e,
                    "Rütbe": get_rank(new_total_puan)
                })
                
                # Session refresh
                st.session_state.attempts = 0
                st.session_state.current_puan = 20
                if st.button("Sonraki Adım"): st.rerun()
            else:
                # HATA DURUMU
                st.session_state.attempts += 1
                st.session_state.current_puan -= 5
                
                if st.session_state.attempts < 3:
                    st.warning(f"❌ Pito: Küçük bir hata ama pes etmek yok! Kalan Puan: {st.session_state.current_puan}")
                elif st.session_state.attempts == 3:
                    st.info(f"💡 Pito'dan Bir İpucu: {ex['ipucu']}")
                elif st.session_state.attempts >= 4:
                    st.error("❌ 4.kez hata yaptın. Bu egzersizden puan alamadın. Fakat çözümü inceleyebilirsin.")
                    st.rerun()

    if locked:
        st.subheader("🔑 Çözümü İncele")
        st.code(ex['cozum'], language="python")
        if st.button("Anladım, Sonraki Adıma Geç"):
            # Puan almadan ilerle
            new_e = e_idx + 2
            new_m = m_idx + 1
            if new_e > 5:
                new_e = 1
                new_m += 1
            update_db(user["Okul No"], {"Mevcut Modül": new_m, "Mevcut Egzersiz": new_e})
            st.session_state.attempts = 0
            st.session_state.current_puan = 20
            st.rerun()

# --- ÇALIŞTIR ---
if st.session_state.user is None:
    login_screen()
else:
    academy_main()
