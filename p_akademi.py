import streamlit as st  # Hata 1 Çözümü: Kütüphane tanımı en üstte
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. AYARLAR VE VERİ KONTROLÜ ---
ASSETS_DIR = "assets"
MÜFREDAT_DOSYASI = "mufredat.json"

def get_asset_path(filename):
    """Assets klasörü yolunu güvenli şekilde döndürür."""
    return os.path.join(ASSETS_DIR, filename)

def mufredat_yukle():
    if not os.path.exists(MÜFREDAT_DOSYASI):
        st.error(f"⚠️ '{MÜFREDAT_DOSYASI}' dosyası bulunamadı!")
        return None
    with open(MÜFREDAT_DOSYASI, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- 2. DOĞRUDAN GOOGLE SHEETS BAĞLANTISI ---
# .streamlit/secrets.toml içindeki linki kullanır
conn = st.connection("gsheets", type=GSheetsConnection)

def veritabani_islem(islem_tipi="oku", yeni_df=None):
    """CSV kullanmadan doğrudan Google Sheets ile konuşur."""
    try:
        if islem_tipi == "oku":
            # ttl=0 verinin her seferinde online tablodan taze gelmesini sağlar
            return conn.read(worksheet="Pito_Akademi_Skorlar", ttl=0)
        elif islem_tipi == "kaydet":
            conn.update(worksheet="Pito_Akademi_Skorlar", data=yeni_df)
            st.cache_data.clear() # Yeni verinin hemen görünmesi için önbelleği temizler
    except Exception as e:
        st.error(f"⚠️ Veritabanı Bağlantı Hatası: {e}")
        # Hata anında sistemin çökmemesi için boş bir şablon döner
        return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Mevcut Modül", "Mevcut Egzersiz"])

# --- 3. SESSION STATE BAŞLATMA ---
if "initialized" not in st.session_state:
    st.session_state.update({
        "initialized": True,
        "modul_idx": 0, "adim_idx": 0, "hata_sayisi": 0,
        "mevcut_puan": 20, "toplam_puan": 0, "kilitli": False,
        "giris_yapildi": False, "ogrenci_no": "", "adim_tamamlandi": False,
        "pito_mesaj": "", "pito_mesaj_turu": "", "aktif_gif": "pito_merhaba.gif"
    })

mufredat = mufredat_yukle()

# --- 4. KONTROL MEKANİZMASI ---
def kontrol_et(girilen_kod, dogru_kod, ipucu):
    t_giris = girilen_kod.strip().replace('"', "'").replace(" ", "")
    t_cozum = dogru_kod.strip().replace('"', "'").replace(" ", "")
    
    if t_giris == t_cozum:
        st.session_state.adim_tamamlandi = True
        st.session_state.aktif_gif = "pito_basari.gif"
        st.session_state.pito_mesaj = f"🎉 Harika! Nusaybin SBAL'in gururusun. +{st.session_state.mevcut_puan} Puan!"
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

# --- 5. ANA EKRAN AKIŞI ---
if not st.session_state.giris_yapildi:
    st.title("🎓 Pito Akademi Giriş")
    # Hata 2 Çözümü: GIF yolu assets/ klasörüyle düzeltildi
    gif_yolu = get_asset_path("pito_merhaba.gif")
    if os.path.exists(gif_yolu): st.image(gif_yolu, width=200)
    
    no = st.text_input("Okul Numaranızı Girin (Sadece Sayı):")
    if st.button("Eğitime Başla"):
        if no.isdigit():
            df = veritabani_islem("oku")
            if not df.empty and "Okul No" in df.columns:
                df["Okul No"] = df["Okul No"].astype(str)
                ogrenci = df[df["Okul No"] == str(no)]
                
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
            else:
                st.error("⚠️ Veritabanı tablosu okunamadı veya 'Okul No' sütunu eksik.")
        else: st.error("Lütfen sayı giriniz.")

    if st.session_state.get("yeni_kayit_modu"):
        ad = st.text_input("Ad Soyad:")
        sinif = st.selectbox("Sınıf:", ["9-A", "9-B", "10-A", "11-A", "12-A"])
        if st.button("Kaydı Tamamla"):
            df = veritabani_islem("oku")
            yeni_veri = pd.DataFrame([{
                "Okul No": st.session_state.ogrenci_no, "Öğrencinin Adı": ad, "Sınıf": sinif, 
                "Puan": 0, "Rütbe": "Yeni Başlayan", "Mevcut Modül": 0, "Mevcut Egzersiz": 0,
                "Tarih": datetime.now().strftime("%d-%m-%Y")
            }])
            veritabani_islem("kaydet", pd.concat([df, yeni_veri], ignore_index=True))
            st.session_state.update({"giris_yapildi": True, "yeni_kayit_modu": False})
            st.rerun()

else:
    # --- DERS EKRANI (BOŞ EKRAN SORUNU ÇÖZÜLDÜ) ---
    with st.sidebar:
        st.title("🐍 Pito Panel")
        gif_yolu = get_asset_path(st.session_state.aktif_gif)
        if os.path.exists(gif_yolu): st.image(gif_yolu)
        st.write(f"🏆 Puan: **{st.session_state.toplam_puan}**")
        if st.button("Güvenli Çıkış"):
            st.session_state.clear()
            st.rerun()

    if mufredat:
        moduller = list(mufredat.keys())
        if st.session_state.modul_idx < len(moduller):
            modul_adi = moduller[st.session_state.modul_idx]
            adim = mufredat[modul_adi][st.session_state.adim_idx]

            st.header(f"📍 {modul_adi}")
            st.subheader(adim['baslik'])
            with st.chat_message("assistant", avatar="🐍"):
                st.markdown(f"**Pito:** {adim['pito_notu']}")

            st.divider()
            if st.session_state.pito_mesaj:
                if st.session_state.pito_mesaj_turu == "success": st.success(st.session_state.pito_mesaj)
                elif st.session_state.pito_mesaj_turu == "warning": st.warning(st.session_state.pito_mesaj)
                else: st.error(st.session_state.pito_mesaj)

            ed_key = f"ed_{st.session_state.modul_idx}_{st.session_state.adim_idx}"
            user_code = st.text_area("Boşlukları Doldur:", value=adim['taslak'], key=ed_key, disabled=st.session_state.kilitli)
            
            if not st.session_state.adim_tamamlandi and not st.session_state.kilitli:
                if st.button("Kodu Çalıştır", type="primary"):
                    kontrol_et(user_code, adim['cozum'], adim['ipucu'])
                    st.rerun()

            if st.session_state.kilitli:
                st.error(f"🛑 Doğru Çözüm: {adim['cozum']}")
                if st.button("Anladım, Geç"):
                    st.session_state.update({"adim_tamamlandi": True, "mevcut_puan": 0, "pito_mesaj": ""})
                    st.rerun()

            if st.session_state.adim_tamamlandi:
                if st.button("Sonraki Adım ➡️"):
                    st.session_state.toplam_puan += st.session_state.mevcut_puan
                    if st.session_state.adim_idx < 4: st.session_state.adim_idx += 1
                    else: st.session_state.adim_idx, st.session_state.modul_idx = 0, st.session_state.modul_idx + 1
                    
                    # --- GOOGLE SHEETS CANLI GÜNCELLEME ---
                    df = veritabani_islem("oku")
                    df["Okul No"] = df["Okul No"].astype(str)
                    idx = df[df["Okul No"] == str(st.session_state.ogrenci_no)].index
                    if not idx.empty:
                        df.at[idx[0], "Puan"] = st.session_state.toplam_puan
                        df.at[idx[0], "Mevcut Modül"] = st.session_state.modul_idx
                        df.at[idx[0], "Mevcut Egzersiz"] = st.session_state.adim_idx
                        veritabani_islem("kaydet", df)
                    
                    st.session_state.update({"adim_tamamlandi": False, "hata_sayisi": 0, "mevcut_puan": 20, "kilitli": False, "pito_mesaj": ""})
                    st.rerun()
        else:
            st.title("🏆 MEZUN OLDUN!")
            gif_mezun = get_asset_path("pito_mezun.gif")
            if os.path.exists(gif_mezun): st.image(gif_mezun)
            st.balloons()
