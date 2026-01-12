import streamlit as st # Hata 1: 'st' is not defined hatası için kütüphane en üstte olmalı
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. AYARLAR VE VARLIK KONTROLÜ ---
ASSETS_DIR = "assets"
MÜFREDAT_DOSYASI = "mufredat.json"
VERİTABANI_DOSYASI = "skorlar.csv"

def get_asset_path(filename):
    """Assets klasörü yolunu güvenli şekilde döner."""
    return os.path.join(ASSETS_DIR, filename)

def veritabani_yukle():
    """Görseldeki Pito_Akademi_Skorlar tablosuyla tam uyumlu yükleme."""
    if os.path.exists(VERİTABANI_DOSYASI):
        return pd.read_csv(VERİTABANI_DOSYASI)
    else:
        # Görseldeki sütun başlıklarını esas alan yapı
        return pd.DataFrame(columns=[
            "Okul No", "Öğrencinin Adı", "Sınıf", "Puan", 
            "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", 
            "Mevcut Egzersiz", "Tarih"
        ])

# --- 2. SESSION STATE BAŞLATMA ---
if "initialized" not in st.session_state:
    st.session_state.update({
        "initialized": True, "modul_idx": 0, "adim_idx": 0, 
        "hata_sayisi": 0, "mevcut_puan": 20, "toplam_puan": 0, 
        "kilitli": False, "giris_yapildi": False, "ogrenci_no": "", 
        "adim_tamamlandi": False, "aktif_gif": "pito_merhaba.gif",
        "pito_mesaj": "", "pito_mesaj_turu": "", "ogrenci_adi": "", "sinif": ""
    })

df_skorlar = veritabani_yukle()

# --- 3. VERİTABANI YAZMA (KORUMA MADDESİ) ---
def ilerlemeyi_kaydet():
    """Veri tabanı okuma hatası verirse üzerine yazma durdurulur."""
    try:
        df = veritabani_yukle()
        # Okul numarası eşleşen satırı bul
        no = int(st.session_state.ogrenci_no)
        idx = df[df["Okul No"] == no].index
        
        if not idx.empty:
            df.at[idx[0], "Puan"] = st.session_state.toplam_puan
            df.at[idx[0], "Mevcut Modül"] = st.session_state.modul_idx
            df.at[idx[0], "Mevcut Egzersiz"] = st.session_state.adim_idx
            df.at[idx[0], "Tarih"] = datetime.now().strftime("%d-%m-%Y")
            df.to_csv(VERİTABANI_DOSYASI, index=False)
    except Exception as e:
        st.error(f"Veri tabanı kayıt hatası: {e}")

# --- 4. GİRİŞ VE KAYIT SİSTEMİ ---
def giris_ekrani():
    st.title("🎓 Pito Akademi Giriş")
    # Hata 2: GIF yolu assets/ klasörüyle düzeltildi
    gif_yolu = get_asset_path("pito_merhaba.gif")
    if os.path.exists(gif_yolu):
        st.image(gif_yolu, width=200)
    
    no = st.text_input("Okul Numaranızı Girin (Sadece Sayı):")
    
    if st.button("Sisteme Giriş Yap"):
        if no.isdigit():
            no_int = int(no)
            ogrenci = df_skorlar[df_skorlar["Okul No"] == no_int]
            
            if not ogrenci.empty:
                # KAYITLI ÖĞRENCİ: Verileri yükle ve devam et
                satir = ogrenci.iloc[0]
                st.session_state.update({
                    "ogrenci_no": no_int, "ogrenci_adi": satir["Öğrencinin Adı"],
                    "sinif": satir["Sınıf"], "toplam_puan": satir["Puan"],
                    "modul_idx": int(satir["Mevcut Modül"]), "adim_idx": int(satir["Mevcut Egzersiz"]),
                    "giris_yapildi": True
                })
                st.rerun() # Macbook uyumu için rerun
            else:
                st.session_state.yeni_kayit_modu = True
                st.session_state.ogrenci_no = no_int
        else:
            st.error("Okul numarası sadece sayısal olmalı!")

    if st.session_state.get("yeni_kayit_modu"):
        st.divider()
        st.subheader("Yeni Öğrenci Kaydı")
        ad = st.text_input("Adınız ve Soyadınız:")
        sinif = st.selectbox("Sınıfınız:", ["9-A", "9-B", "10-A", "10-B", "11-A", "12-A"])
        
        if st.button("Kaydı Tamamla ve Başla"):
            yeni_satir = pd.DataFrame([{
                "Okul No": st.session_state.ogrenci_no,
                "Öğrencinin Adı": ad, "Sınıf": sinif, "Puan": 0,
                "Rütbe": "Egg 🥚", "Tamamlanan Modüller": 0,
                "Mevcut Modül": 0, "Mevcut Egzersiz": 0,
                "Tarih": datetime.now().strftime("%d-%m-%Y")
            }])
            df_yeni = pd.concat([df_skorlar, yeni_satir], ignore_index=True)
            df_yeni.to_csv(VERİTABANI_DOSYASI, index=False)
            st.session_state.update({"ogrenci_adi": ad, "sinif": sinif, "giris_yapildi": True})
            st.rerun()

# --- 5. ANA EKRAN AKIŞI ---
if not st.session_state.giris_yapildi:
    giris_ekrani()
else:
    # (Buraya daha önce hazırladığımız mufredat yükleme ve kontrol_et mantığı gelecek)
    st.write(f"Hoş geldin, {st.session_state.ogrenci_adi}!")
    # Her başarılı adımda: ilerlemeyi_kaydet() çağrılır.
