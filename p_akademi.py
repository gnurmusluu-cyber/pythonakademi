import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
import time

# --- PİTO PROTOKOLÜ VE AYARLAR ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide")

# Google Sheets Bağlantısı
def init_connection():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # secrets.json dosyanızı Streamlit secrets'a veya yerel dosya yoluna ekleyin
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_url("https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit")

sheet = init_connection().get_worksheet(0)

# Müfredatı Yükle
with open('mufredat.json', 'r', encoding='utf-8') as f:
    mufredat = json.load(f)

# Rütbe Hesaplama
def get_rank(puan):
    if puan < 100: return "🥚 Egg"
    elif puan < 300: return "🐥 Chick"
    elif puan < 600: return "🐍 Python Apprentice"
    elif puan < 1000: return "🔥 Python Coder"
    else: return "👑 Python Hero"

# --- OTURUM YÖNETİMİ ---
if "user" not in st.session_state:
    st.session_state.user = None
if "attempts" not in st.session_state:
    st.session_state.attempts = 0
if "current_puan" not in st.session_state:
    st.session_state.current_puan = 20

# --- GİRİŞ VE KAYIT SİSTEMİ ---
def login_section():
    st.title("🐍 Pito Python Akademi'ye Hoş Geldin!")
    col1, col2 = st.columns(2)
    
    with col1:
        okul_no = st.text_input("Okul Numaranı Gir:", key="login_no")
        if st.button("Giriş Yap"):
            data = sheet.get_all_records()
            user_data = next((item for item in data if str(item["Okul No"]) == okul_no), None)
            
            if user_data:
                st.session_state.user = user_data
                st.success(f"Tekrar hoş geldin, {user_data['Öğrencinin Adı']}!")
                st.rerun()
            else:
                st.warning("Numara kayıtlı değil. Lütfen yan taraftan kayıt ol!")

    with col2:
        with st.expander("Yeni Kayıt Oluştur"):
            yeni_ad = st.text_input("Adın Soyadın:")
            yeni_no = st.text_input("Okul Numaran (Sadece Sayı):")
            yeni_sinif = st.selectbox("Sınıfın:", ["9-A", "9-B", "10-A", "10-B", "11-A", "12-A"])
            if st.button("Akademiye Katıl"):
                # Veritabanına ekleme
                new_row = [yeni_no, yeni_ad, yeni_sinif, 0, "🥚 Egg", 0, 1, 1, time.strftime("%Y-%m-%d")]
                sheet.append_row(new_row)
                st.success("Kaydın başarıyla oluşturuldu! Şimdi giriş yapabilirsin.")
                st.rerun()

# --- LİDERLİK TABLOSU ---
def sidebar_leaderboard():
    data = pd.DataFrame(sheet.get_all_records())
    st.sidebar.header("🏆 Liderlik Tablosu")
    
    # Okul Geneli
    st.sidebar.subheader("🏫 Okul Top 5")
    top_school = data.sort_values(by="Puan", ascending=False).head(5)
    st.sidebar.table(top_school[["Öğrencinin Adı", "Puan"]])
    
    # Şampiyon Sınıf
    st.sidebar.subheader("⭐ Şampiyon Sınıf")
    class_puan = data.groupby("Sınıf")["Puan"].sum().idxmax()
    st.sidebar.info(f"Şu anki lider: **{class_puan}**")

# --- ANA EĞİTİM EKRANI ---
def main_app():
    user = st.session_state.user
    sidebar_leaderboard()
    
    # Modül ve Egzersiz İndeksleri
    module_list = list(mufredat.keys())
    current_mod_idx = int(user["Mevcut Modül"]) - 1
    current_ex_idx = int(user["Mevcut Egzersiz"]) - 1
    
    # Tüm modüller bitti mi?
    if current_mod_idx >= len(module_list):
        st.balloons()
        st.header("🎓 Mezuniyet Tebrikler!")
        st.write("Tüm modülleri başarıyla tamamladın. Artık bir Python Kahramanısın!")
        if st.button("Eğitimi Tekrar Al (Puanın Sıfırlanır)"):
            # Veritabanı sıfırlama kodu buraya gelecek
            pass
        return

    curr_mod_name = module_list[current_mod_idx]
    exercise = mufredat[curr_mod_name][current_ex_idx]

    st.title(f"{curr_mod_name} - {exercise['baslik']}")
    st.info(f"**Pito Notu:** {exercise['pito_notu']}")

    # --- EDİTÖR PANELİ ---
    st.subheader("💻 Kod Paneli")
    user_input = st.text_input(exercise['egzersiz'], value=exercise['taslak'], disabled=(st.session_state.attempts >= 4))

    # --- GERİ BİLDİRİM VE KONTROL ---
    if st.button("Kodu Çalıştır", disabled=(st.session_state.attempts >= 4)):
        if user_input.strip() == exercise['cozum']:
            st.success(f"✅ Harika! {st.session_state.current_puan} puan kazandın.")
            st.code(f"Çıktı: {exercise['cozum'].replace('print(', '').replace(')', '').replace(\"'\", \"\")}")
            
            # Veritabanı Güncelleme (Bir sonraki adıma geçiş)
            # ... (sheet.update_cell mantığı ile mevcut modül/egzersiz güncellenir)
            st.button("Sonraki Adıma Geç", on_click=lambda: st.rerun())
        else:
            st.session_state.attempts += 1
            st.session_state.current_puan -= 5
            
            if st.session_state.attempts < 3:
                st.warning(f"❌ Pito: Küçük bir hata ama pes etmek yok! (Hata: {st.session_state.attempts}/4)")
            elif st.session_state.attempts == 3:
                st.warning(f"💡 Pito İpucu: {exercise['ipucu']}")
            elif st.session_state.attempts == 4:
                st.error("❌ 4. kez hata yaptın. Bu egzersizden puan alamadın. Fakat çözümü inceleyebilirsin.")

    if st.session_state.attempts >= 4:
        st.subheader("🔑 Çözüm Bloğu")
        st.code(exercise['cozum'], language="python")
        if st.button("Anladım, Sonraki Adıma Geç"):
            st.session_state.attempts = 0
            st.session_state.current_puan = 20
            # Veritabanında bir sonraki egzersize geçişi kaydet
            st.rerun()

# Uygulamayı Başlat
if st.session_state.user is None:
    login_section()
else:
    main_app()
