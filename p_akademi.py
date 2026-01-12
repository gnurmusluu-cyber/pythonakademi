import streamlit as st # Hata 1 Çözümü: Kütüphane en üstte
import json
import os

# --- 1. AYARLAR VE VARLIK YOLLARI ---
ASSETS_DIR = "assets" # Hata 2 Çözümü: Assets klasörü kullanımı
DATABASE_FILE = "mufredat.json"

def get_asset_path(filename):
    return os.path.join(ASSETS_DIR, filename)

def mufredat_yukle():
    if not os.path.exists(DATABASE_FILE):
        st.error(f"⚠️ '{DATABASE_FILE}' bulunamadı!")
        return None
    with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def gif_goster(gif_name, width=None):
    path = get_asset_path(gif_name)
    if os.path.exists(path):
        if width: st.image(path, width=width)
        else: st.image(path, use_container_width=True)

# --- 2. SESSION STATE (PİTO PROTOKOLÜ) ---
if "initialized" not in st.session_state:
    st.session_state.update({
        "initialized": True,
        "modul_idx": 0, "adim_idx": 0, "hata_sayisi": 0,
        "mevcut_puan": 20, "toplam_puan": 0, "kilitli": False,
        "giris_yapildi": False, "ogrenci_no": "", "adim_tamamlandi": False,
        "aktif_gif": "pito_merhaba.gif",
        "pito_mesaj": "", "pito_mesaj_turu": ""
    })

mufredat = mufredat_yukle()

# --- 3. KONTROL MEKANİZMASI (ÖZEL MESAJ HIYERARŞİSİ) ---
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
        
        # 4. HATA: ÖZEL MESAJ VE KİLİT
        if st.session_state.hata_sayisi >= 4:
            st.session_state.kilitli = True
            st.session_state.aktif_gif = "pito_hata.gif"
            st.session_state.pito_mesaj = "4.kez hata yaptın. Bu egzersizden puan alamadın. Fakat çözümü inceleyebilirsin."
            st.session_state.pito_mesaj_turu = "error"
            
        # 3. HATA: İPUCU MESAJI
        elif st.session_state.hata_sayisi == 3:
            st.session_state.aktif_gif = "pito_hata.gif"
            st.session_state.pito_mesaj = f"💡 Pito'dan İpucu: {ipucu}"
            st.session_state.pito_mesaj_turu = "warning"
            
        # 1. VE 2. HATA: MOTİVASYON MESAJI
        else:
            st.session_state.aktif_gif = "pito_dusunuyor.gif"
            st.session_state.pito_mesaj = f"❌ Pito: Küçük bir hata ama pes etmek yok! Kalan Puan: {st.session_state.mevcut_puan}"
            st.session_state.pito_mesaj_turu = "error"

# --- 4. SİDEBAR (SABİT PANEL) ---
with st.sidebar:
    st.title("🐍 Pito Panel")
    if st.session_state.giris_yapildi:
        gif_goster(st.session_state.aktif_gif)
        st.subheader(f"No: {st.session_state.ogrenci_no}")
        toplam_adim = (st.session_state.modul_idx * 5) + (st.session_state.adim_idx + 1)
        st.progress(min(toplam_adim / 45, 1.0))
        st.write(f"🏆 Toplam Puan: **{st.session_state.toplam_puan}**")
        st.divider()
        st.table({"Öğrenci": ["Ali 12/A", "Merve 11/B", "Siz"], "Puan": [880, 820, st.session_state.toplam_puan]})
        if st.button("Sıfırla"):
            st.session_state.clear()
            st.rerun()

# --- 5. ANA EKRAN AKIŞI ---
if mufredat:
    if not st.session_state.giris_yapildi:
        st.title("🎓 Pito Akademi Giriş")
        gif_goster("pito_merhaba.gif", width=200)
        no = st.text_input("Okul Numaranızı Girin:")
        if st.button("Eğitime Başla") and no.isdigit():
            st.session_state.ogrenci_no, st.session_state.giris_yapildi = no, True
            st.rerun()
    else:
        modul_adi = list(mufredat.keys())[st.session_state.modul_idx]
        adim = mufredat[modul_adi][st.session_state.adim_idx]
        
        st.header(f"📍 {modul_adi}")
        st.subheader(adim['baslik'])
        
        # Pito terimleri derinlemesine açıklar
        with st.chat_message("assistant", avatar="🐍"):
            st.markdown(f"**Pito:** {adim['pito_notu']}")
        
        st.divider()
        st.info(f"📝 **GÖREV:** {adim['egzersiz']}")
        
        # Geri Bildirim Alanı (Kod Panelinin Hemen Üzeri)
        if st.session_state.pito_mesaj:
            if st.session_state.pito_mesaj_turu == "success": st.success(st.session_state.pito_mesaj)
            elif st.session_state.pito_mesaj_turu == "warning": st.warning(st.session_state.pito_mesaj)
            elif st.session_state.pito_mesaj_turu == "error": st.error(st.session_state.pito_mesaj)

        ed_key = f"ed_{st.session_state.modul_idx}_{st.session_state.adim_idx}"
        user_code = st.text_area("Boşlukları Doldur:", value=adim['taslak'], key=ed_key, disabled=st.session_state.kilitli)
        
        if not st.session_state.adim_tamamlandi and not st.session_state.kilitli:
            if st.button("Kodu Çalıştır", type="primary"):
                kontrol_et(user_code, adim['cozum'], adim['ipucu'])
                st.rerun()

        # 4. HATA: ÇÖZÜM GÖSTERİMİ
        if st.session_state.kilitli:
            st.error(f"🛑 Doğru Çözüm: {adim['cozum']}")
            if st.button("Anladım, Geç"):
                st.session_state.update({"adim_tamamlandi": True, "mevcut_puan": 0, "pito_mesaj": ""})
                st.rerun()

        # BAŞARI DURUMU VE GEÇİŞ
        if st.session_state.adim_tamamlandi:
            if st.button("Sonraki Adım ➡️"):
                st.session_state.toplam_puan += st.session_state.mevcut_puan
                if st.session_state.adim_idx < 4: st.session_state.adim_idx += 1
                else: st.session_state.adim_idx, st.session_state.modul_idx = 0, st.session_state.modul_idx + 1
                
                # Değerleri resetle
                st.session_state.update({"adim_tamamlandi": False, "hata_sayisi": 0, "mevcut_puan": 20, "kilitli": False, "aktif_gif": "pito_merhaba.gif", "pito_mesaj": ""})
                st.rerun()
