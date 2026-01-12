import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. DOSYA YOLLARI VE VERİTABANI HAZIRLIĞI ---
ASSETS_DIR = "assets"
MÜFREDAT_DOSYASI = "mufredat.json"
VERİTABANI_DOSYASI = "skorlar.csv"

# Veritabanını (CSV) tablo yapısına göre oluştur veya yükle
def veritabani_yukle():
    if os.path.exists(VERİTABANI_DOSYASI):
        return pd.read_csv(VERİTABANI_DOSYASI)
    else:
        # Görseldeki sütun başlıklarını esas alan boş tablo
        return pd.DataFrame(columns=[
            "Okul No", "Öğrencinin Adı", "Sınıf", "Puan", 
            "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", 
            "Mevcut Egzersiz", "Tarih"
        ])

def veritabani_kaydet(df):
    df.to_csv(VERİTABANI_DOSYASI, index=False)

# --- 2. OTURUM YÖNETİMİ ---
if "initialized" not in st.session_state:
    st.session_state.update({
        "modul_idx": 0, "adim_idx": 0, "hata_sayisi": 0,
        "mevcut_puan": 20, "toplam_puan": 0, "kilitli": False,
        "giris_yapildi": False, "ogrenci_no": "", "adim_tamamlandi": False,
        "pito_mesaj": "", "pito_mesaj_turu": "", "ogrenci_adi": "", "sinif": ""
    })

df_skorlar = veritabani_yukle()

# --- 3. GİRİŞ VE KAYIT SİSTEMİ ---
def giris_ekrani():
    st.title("🎓 Pito Akademi Giriş")
    st.image(os.path.join(ASSETS_DIR, "pito_merhaba.gif"), width=200)
    
    no = st.text_input("Okul Numaranızı Girin (Sadece Sayı):")
    
    if st.button("Sisteme Giriş Yap"):
        if no.isdigit():
            no_int = int(no)
            # Veritabanında öğrenciyi ara
            ogrenci_verisi = df_skorlar[df_skorlar["Okul No"] == no_int]
            
            if not ogrenci_verisi.empty:
                # KAYITLI ÖĞRENCİ: Verileri Session State'e yükle
                satir = ogrenci_verisi.iloc[0]
                st.session_state.update({
                    "ogrenci_no": no_int,
                    "ogrenci_adi": satir["Öğrencinin Adı"],
                    "sinif": satir["Sınıf"],
                    "toplam_puan": satir["Puan"],
                    "modul_idx": satir["Mevcut Modül"],
                    "adim_idx": satir["Mevcut Egzersiz"],
                    "giris_yapildi": True
                })
                st.success(f"Tekrar hoş geldin {st.session_state.ogrenci_adi}! Kaldığın yerden devam ediyoruz.")
                st.rerun() # Macbook uyumu için rerun
            else:
                # YENİ KAYIT FORMU
                st.session_state.ogrenci_no = no_int
                st.session_state.yeni_kayit_modu = True
        else:
            st.error("Lütfen geçerli bir numara girin.")

    if st.session_state.get("yeni_kayit_modu"):
        st.divider()
        st.subheader("Yeni Öğrenci Kaydı")
        ad = st.text_input("Adınız ve Soyadınız:")
        sinif = st.selectbox("Sınıfınız:", ["9-A", "9-B", "10-A", "10-B", "11-A", "12-A"])
        
        if st.button("Kaydı Tamamla ve Başla"):
            yeni_satir = {
                "Okul No": st.session_state.ogrenci_no,
                "Öğrencinin Adı": ad,
                "Sınıf": sinif,
                "Puan": 0,
                "Rütbe": "Egg 🥚",
                "Tamamlanan Modüller": 0,
                "Mevcut Modül": 0,
                "Mevcut Egzersiz": 0,
                "Tarih": datetime.now().strftime("%d-%m-%Y")
            }
            # Veritabanını güncelle
            yeni_df = pd.concat([df_skorlar, pd.DataFrame([yeni_satir])], ignore_index=True)
            veritabani_kaydet(yeni_df)
            
            st.session_state.update({
                "ogrenci_adi": ad, "sinif": sinif, "giris_yapildi": True
            })
            st.rerun()

# --- 4. VERİ GÜNCELLEME (İLERLEME KAYDI) ---
def ilerlemeyi_kaydet():
    # Veritabanını yükle ve ilgili satırı güncelle
    df = veritabani_yukle()
    idx = df[df["Okul No"] == st.session_state.ogrenci_no].index
    
    if not idx.empty:
        df.at[idx[0], "Puan"] = st.session_state.toplam_puan
        df.at[idx[0], "Mevcut Modül"] = st.session_state.modul_idx
        df.at[idx[0], "Mevcut Egzersiz"] = st.session_state.adim_idx
        df.at[idx[0], "Tarih"] = datetime.now().strftime("%d-%m-%Y")
        
        # Rütbe hesaplama
        ilerleme = (st.session_state.modul_idx * 5) + st.session_state.adim_idx
        if ilerleme > 35: r = "Python Hero 👑"
        elif ilerleme > 20: r = "Developer 🚀"
        else: r = "Egg 🥚"
        df.at[idx[0], "Rütbe"] = r
        
        veritabani_kaydet(df)

# --- ANA DÖNGÜ VE UI ---
if not st.session_state.giris_yapildi:
    giris_ekrani()
else:
    # (Önceki kodlardaki mufredat, kontrol_et ve sidebar fonksiyonları burada yer alır)
    # Egzersiz tamamlandığında 'ilerlemeyi_kaydet()' fonksiyonu çağrılır.
    pass
