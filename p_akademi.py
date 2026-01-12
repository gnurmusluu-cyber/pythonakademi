import streamlit as st # Hata 1 Çözümü: Kütüphane tanımı
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. AYARLAR ---
ASSETS_DIR = "assets"
DATABASE_FILE = "mufredat.json"
VERİTABANI_DOSYASI = "skorlar.csv"

def get_asset_path(filename):
    return os.path.join(ASSETS_DIR, filename)

def veritabani_yukle():
    """Veritabanını tazeleyerek yükler."""
    if os.path.exists(VERİTABANI_DOSYASI):
        # Okul No sütununu mutlaka metin (str) olarak oku
        df = pd.read_csv(VERİTABANI_DOSYASI, dtype={"Okul No": str})
        return df
    else:
        return pd.DataFrame(columns=[
            "Okul No", "Öğrencinin Adı", "Sınıf", "Puan", 
            "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", 
            "Mevcut Egzersiz", "Tarih"
        ])

# --- 2. SESSION STATE ---
if "initialized" not in st.session_state:
    st.session_state.update({
        "initialized": True, "modul_idx": 0, "adim_idx": 0, 
        "hata_sayisi": 0, "mevcut_puan": 20, "toplam_puan": 0, 
        "kilitli": False, "giris_yapildi": False, "ogrenci_no": "", 
        "adim_tamamlandi": False, "aktif_gif": "pito_merhaba.gif",
        "pito_mesaj": "", "pito_mesaj_turu": "", "ogrenci_adi": "", "sinif": "",
        "yeni_kayit_modu": False
    })

# --- 3. İLERLEME KAYDETME (KOD KORUMA MADDESİ) ---
def ilerlemeyi_kaydet():
    try:
        df = veritabani_yukle()
        no = str(st.session_state.ogrenci_no)
        idx = df[df["Okul No"] == no].index
        
        if not idx.empty:
            df.at[idx[0], "Puan"] = st.session_state.toplam_puan
            df.at[idx[0], "Mevcut Modül"] = int(st.session_state.modul_idx)
            df.at[idx[0], "Mevcut Egzersiz"] = int(st.session_state.adim_idx)
            df.at[idx[0], "Tarih"] = datetime.now().strftime("%d-%m-%Y")
            df.to_csv(VERİTABANI_DOSYASI, index=False)
    except Exception as e:
        st.error(f"Kayıt hatası: {e}")

# --- 4. GİRİŞ VE KAYIT EKRANI ---
def giris_ekrani():
    st.title("🎓 Pito Akademi Giriş")
    gif_yolu = get_asset_path("pito_merhaba.gif")
    if os.path.exists(gif_yolu):
        st.image(gif_yolu, width=200)
    
    no_input = st.text_input("Okul Numaranızı Girin (Sadece Sayı):", key="login_no")
    
    if st.button("Sisteme Giriş Yap"):
        if no_input.isdigit():
            df_guncel = veritabani_yukle()
            # Karşılaştırmayı metin olarak yapıyoruz
            ogrenci = df_guncel[df_guncel["Okul No"] == str(no_input)]
            
            if not ogrenci.empty:
                satir = ogrenci.iloc[0]
                st.session_state.update({
                    "ogrenci_no": str(no_input),
                    "ogrenci_adi": satir["Öğrencinin Adı"],
                    "sinif": satir["Sınıf"],
                    "toplam_puan": int(satir["Puan"]),
                    "modul_idx": int(satir["Mevcut Modül"]),
                    "adim_idx": int(satir["Mevcut Egzersiz"]),
                    "giris_yapildi": True,
                    "yeni_kayit_modu": False
                })
                st.rerun()
            else:
                st.session_state.ogrenci_no = str(no_input)
                st.session_state.yeni_kayit_modu = True
                st.warning("Numara bulunamadı, lütfen kayıt olun.")
        else:
            st.error("Lütfen sadece sayı giriniz.")

    # YENİ KAYIT FORMU
    if st.session_state.yeni_kayit_modu:
        st.divider()
        st.subheader("📝 Yeni Öğrenci Kaydı")
        yeni_ad = st.text_input("Adınız ve Soyadınız:")
        yeni_sinif = st.selectbox("Sınıfınız:", ["9-A", "9-B", "10-A", "10-B", "11-A", "12-A"])
        
        if st.button("Kaydı Tamamla ve Eğitime Başla"):
            if yeni_ad:
                df_yeni = veritabani_yukle()
                yeni_satir = pd.DataFrame([{
                    "Okul No": str(st.session_state.ogrenci_no),
                    "Öğrencinin Adı": yeni_ad,
                    "Sınıf": yeni_sinif,
                    "Puan": 0,
                    "Rütbe": "Egg 🥚",
                    "Tamamlanan Modüller": 0,
                    "Mevcut Modül": 0,
                    "Mevcut Egzersiz": 0,
                    "Tarih": datetime.now().strftime("%d-%m-%Y")
                }])
                df_son = pd.concat([df_yeni, yeni_satir], ignore_index=True)
                df_son.to_csv(VERİTABANI_DOSYASI, index=False)
                
                st.session_state.update({
                    "ogrenci_adi": yeni_ad,
                    "sinif": yeni_sinif,
                    "giris_yapildi": True,
                    "yeni_kayit_modu": False
                })
                st.success("Kaydınız başarıyla oluşturuldu!")
                st.rerun()
            else:
                st.error("Lütfen adınızı giriniz.")

# --- 5. ANA EKRAN AKIŞI ---
if not st.session_state.giris_yapildi:
    giris_ekrani()
else:
    # Sidebar ve Müfredat Kodları Buraya Gelecek
    st.sidebar.title(f"👤 {st.session_state.ogrenci_adi}")
    st.sidebar.write(f"Sınıf: {st.session_state.sinif}")
    st.write(f"Başarılar {st.session_state.ogrenci_adi}! {st.session_state.modul_idx + 1}. Modül, {st.session_state.adim_idx + 1}. Egzersizdeyiz.")
    
    if st.sidebar.button("Çıkış Yap"):
        st.session_state.clear()
        st.rerun()
