import streamlit as st
from streamlit_gsheets import GSheetsConnection # GSheets kütüphanesi
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. AYARLAR VE VERİ KONTROLÜ ---
ASSETS_DIR = "assets"
MÜFREDAT_DOSYASI = "mufredat.json"

def get_asset_path(filename):
    return os.path.join(ASSETS_DIR, filename)

def mufredat_yukle():
    if not os.path.exists(MÜFREDAT_DOSYASI):
        st.error(f"⚠️ '{MÜFREDAT_DOSYASI}' bulunamadı!")
        return None
    with open(MÜFREDAT_DOSYASI, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- GOOGLE SHEETS BAĞLANTISI ---
conn = st.connection("gsheets", type=GSheetsConnection)

def veritabani_yukle():
    """Google Sheets tablosunu canlı olarak çeker."""
    try:
        # worksheet adı Pito_Akademi_Skorlar olmalı
        return conn.read(worksheet="Pito_Akademi_Skorlar", ttl="0")
    except:
        # Eğer tablo boşsa başlıkları oluşturur
        return pd.DataFrame(columns=[
            "Okul No", "Öğrencinin Adı", "Sınıf", "Puan", 
            "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", 
            "Mevcut Egzersiz", "Tarih"
        ])

def veritabani_kaydet(df):
    """Verileri Google Sheets üzerine yazar."""
    try:
        conn.update(worksheet="Pito_Akademi_Skorlar", data=df)
        st.cache_data.clear() # Önbelleği temizle ki yeni veri hemen görünsün
    except Exception as e:
        st.error(f"Google Sheets kayıt hatası: {e}")

# --- 2. SESSION STATE ---
if "initialized" not in st.session_state:
    st.session_state.update({
        "initialized": True, "modul_idx": 0, "adim_idx": 0, "hata_sayisi": 0,
        "mevcut_puan": 20, "toplam_puan": 0, "kilitli": False,
        "giris_yapildi": False, "ogrenci_no": "", "adim_tamamlandi": False,
        "pito_mesaj": "", "pito_mesaj_turu": "", "aktif_gif": "pito_merhaba.gif"
    })

mufredat = mufredat_yukle()
df_skorlar = veritabani_yukle()

# --- 3. KONTROL MEKANİZMASI ---
def kontrol_et(girilen_kod, dogru_kod, ipucu):
    t_giris = girilen_kod.strip().replace('"', "'").replace(" ", "")
    t_cozum = dogru_kod.strip().replace('"', "'").replace(" ", "")
    
    if t_giris == t_cozum:
        st.session_state.adim_tamamlandi = True
        st.session_state.aktif_gif = "pito_basari.gif"
        st.session_state.pito_mesaj = f"🎉 Harika! Nusaybin'in gururusun. +{st.session_state.mevcut_puan} Puan kazandın."
        st.session_state.pito_mesaj_turu = "success"
    else:
        st.session_state.hata_sayisi += 1
        st.session_state.mevcut_puan = max(0, st.session_state.mevcut_puan - 5)
        
        if st.session_state.hata_sayisi >= 4:
            st.session_state.kilitli = True
            st.session_state.aktif_gif = "pito_hata.gif"
            st.session_state.pito_mesaj = "4.kez hata yaptın. Bu egzersizden puan alamadın. Fakat çözümü inceleyebilirsin."
            st.session_state.pito_mesaj_turu = "error"
        elif st.session_state.hata_sayisi == 3:
            st.session_state.pito_mesaj = f"💡 Pito'dan İpucu: {ipucu}"
            st.session_state.pito_mesaj_turu = "warning"
        else:
            st.session_state.pito_mesaj = f"❌ Pito: Küçük bir hata ama pes etmek yok! Kalan Puan: {st.session_state.mevcut_puan}"
            st.session_state.pito_mesaj_turu = "error"

# --- 4. SİDEBAR ---
with st.sidebar:
    st.title("🐍 Pito Panel")
    if st.session_state.giris_yapildi:
        gif_yolu = get_asset_path(st.session_state.aktif_gif)
        if os.path.exists(gif_yolu): st.image(gif_yolu)
        st.subheader(f"No: {st.session_state.ogrenci_no}")
        st.write(f"🏆 Puan: **{st.session_state.toplam_puan}**")
        if st.button("Çıkış Yap"):
            st.session_state.clear()
            st.rerun()

# --- 5. ANA EKRAN ---
if not st.session_state.giris_yapildi:
    st.title("🎓 Pito Akademi Giriş")
    no = st.text_input("Okul Numaranızı Girin:")
    if st.button("Eğitime Başla"):
        if no.isdigit():
            # Tabloyu metin olarak kontrol et
            df_skorlar["Okul No"] = df_skorlar["Okul No"].astype(str)
            ogrenci = df_skorlar[df_skorlar["Okul No"] == str(no)]
            
            if not ogrenci.empty:
                satir = ogrenci.iloc[0]
                st.session_state.update({
                    "ogrenci_no": str(no), "toplam_puan": int(satir["Puan"]),
                    "modul_idx": int(satir["Mevcut Modül"]), "adim_idx": int(satir["Mevcut Egzersiz"]),
                    "giris_yapildi": True
                })
                st.rerun()
            else:
                st.session_state.ogrenci_no = str(no)
                st.session_state.yeni_kayit_modu = True
        else: st.error("Sadece sayı giriniz.")

    if st.session_state.get("yeni_kayit_modu"):
        ad = st.text_input("Adınız Soyadınız:")
        sinif = st.selectbox("Sınıfınız:", ["9-A", "9-B", "10-A", "11-A", "12-A"])
        if st.button("Kaydı Tamamla"):
            yeni_satir = pd.DataFrame([{
                "Okul No": str(st.session_state.ogrenci_no), "Öğrencinin Adı": ad, 
                "Sınıf": sinif, "Puan": 0, "Rütbe": "Egg 🥚", 
                "Mevcut Modül": 0, "Mevcut Egzersiz": 0,
                "Tarih": datetime.now().strftime("%d-%m-%Y")
            }])
            df_son = pd.concat([df_skorlar, yeni_satir], ignore_index=True)
            veritabani_kaydet(df_son) # Online Kayıt
            st.session_state.update({"giris_yapildi": True, "yeni_kayit_modu": False})
            st.rerun()
else:
    # Ders İçeriği (Mevcut mantık devam eder)
    if mufredat:
        modul_adlari = list(mufredat.keys())
        aktif_modul = modul_adlari[st.session_state.modul_idx]
        adim = mufredat[aktif_modul][st.session_state.adim_idx]

        st.header(f"📍 {aktif_modul}")
        st.subheader(adim['baslik'])
        
        # Pito Notu ve Kod Alanı...
        if st.session_state.pito_mesaj:
            if st.session_state.pito_mesaj_turu == "success": st.success(st.session_state.pito_mesaj)
            elif st.session_state.pito_mesaj_turu == "warning": st.warning(st.session_state.pito_mesaj)
            else: st.error(st.session_state.pito_mesaj)

        user_code = st.text_area("Boşlukları Doldur:", value=adim['taslak'], key=f"ed_{st.session_state.modul_idx}_{st.session_state.adim_idx}", disabled=st.session_state.kilitli)
        
        if not st.session_state.adim_tamamlandi and not st.session_state.kilitli:
            if st.button("Çalıştır", type="primary"):
                kontrol_et(user_code, adim['cozum'], adim['ipucu'])
                st.rerun()

        if st.session_state.adim_tamamlandi:
            if st.button("Sonraki Adım ➡️"):
                st.session_state.toplam_puan += st.session_state.mevcut_puan
                # İlerlemeyi güncelle
                if st.session_state.adim_idx < 4: st.session_state.adim_idx += 1
                else: st.session_state.adim_idx, st.session_state.modul_idx = 0, st.session_state.modul_idx + 1
                
                # Google Sheets Güncelleme
                df = veritabani_yukle()
                df["Okul No"] = df["Okul No"].astype(str)
                idx = df[df["Okul No"] == str(st.session_state.ogrenci_no)].index
                if not idx.empty:
                    df.at[idx[0], "Puan"] = st.session_state.toplam_puan
                    df.at[idx[0], "Mevcut Modül"] = st.session_state.modul_idx
                    df.at[idx[0], "Mevcut Egzersiz"] = st.session_state.adim_idx
                    veritabani_kaydet(df)
                
                st.session_state.update({"adim_tamamlandi": False, "hata_sayisi": 0, "mevcut_puan": 20, "kilitli": False, "pito_mesaj": ""})
                st.rerun()
