import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- VERİTABANI BAĞLANTISI ---
KULLANICILAR_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def kayit_ol(numara, ad_soyad, sinif):
    # Başlangıç verilerini hazırla [cite: 2026-01-12]
    yeni_veri = pd.DataFrame([{
        "ogrenci_no": int(numara),
        "ad_soyad": ad_soyad,
        "sinif": sinif,
        "toplam_puan": 0,
        "en_yuksek_puan": 0,
        "mevcut_modul": 1,
        "mevcut_egzersiz": "1.1",
        "rutbe": "🥚 Yeni Başlayan",
        "kayit_tarihi": datetime.now().strftime("%Y-%m-%d")
    }])
    
    # Mevcut veriyi çek ve yenisini ekle
    mevcut_df = conn.read(spreadsheet=KULLANICILAR_URL)
    güncel_df = pd.concat([mevcut_df, yeni_veri], ignore_index=True)
    
    # Google Sheets'e geri yaz
    conn.update(spreadsheet=KULLANICILAR_URL, data=güncel_df)
    return yeni_veri.iloc[0].to_dict()

# --- GİRİŞ EKRANI MANTIĞI ---
if st.session_state.user_data is None:
    st.title("🐍 Pito Python Akademi")
    st.image("assets/pito_merhaba.gif", width=200)
    
    numara = st.number_input("Öğrenci Numaranı Yaz:", step=1, value=0)
    
    # Giriş Denemesi
    if st.button("Giriş Yap"):
        df_users = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
        user = df_users[df_users['ogrenci_no'] == numara]
        
        if not user.empty:
            st.session_state.user_data = user.iloc[0].to_dict()
            st.rerun()
        else:
            st.session_state.show_reg_form = True # Kayıt formunu tetikle
            st.warning("Seni tanıyamadım! İlk kez mi geliyorsun? Haydi kayıt ol!")

    # KAYIT FORMU [cite: 2026-01-12]
    if st.session_state.get("show_reg_form", False):
        with st.form("kayit_formu"):
            st.write(f"📝 **Numara: {numara} için Kayıt Oluştur**")
            yeni_ad = st.text_input("Adın ve Soyadın:")
            yeni_sinif = st.selectbox("Sınıfın:", ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"])
            
            if st.form_submit_button("Kaydı Tamamla ve Başla"):
                if yeni_ad and yeni_sinif:
                    user_dict = kayit_ol(numara, yeni_ad, yeni_sinif)
                    st.session_state.user_data = user_dict
                    st.success("Kaydın başarıyla oluşturuldu, Pito seni bekliyor!")
                    st.rerun()
                else:
                    st.error("Lütfen tüm alanları doldur!")
