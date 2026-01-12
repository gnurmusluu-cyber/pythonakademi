import streamlit as st
import json
import os

# --- 1. AYARLAR VE YOL TANIMLAMALARI ---
ASSETS_DIR = "assets"
DATABASE_FILE = "mufredat.json"

def get_asset_path(filename):
    """Assets klasörü içindeki dosya yolunu döndürür."""
    return os.path.join(ASSETS_DIR, filename)

# --- 2. VERİ YÜKLEME ---
def mufredat_yukle():
    if not os.path.exists(DATABASE_FILE):
        st.error(f"⚠️ '{DATABASE_FILE}' bulunamadı! Lütfen dosyayı ana dizine ekleyin.")
        return None
    with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def gif_goster(gif_name, width=None):
    """GIF dosyasını assets klasöründen güvenli bir şekilde yükler."""
    path = get_asset_path(gif_name)
    if os.path.exists(path):
        if width:
            st.image(path, width=width)
        else:
            st.image(path, use_container_width=True)
    else:
        st.warning(f"🖼️ {gif_name} bulunamadı! Konum: {path}")

# --- 3. OTURUM YÖNETİMİ (PİTO PROTOKOLÜ) ---
#
if "initialized" not in st.session_state:
    st.session_state.update({
        "initialized": True,
        "modul_idx": 0, 
        "adim_idx": 0, 
        "hata_sayisi": 0,
        "mevcut_puan": 20, 
        "toplam_puan": 0, 
        "kilitli": False,
        "giris_yapildi": False, 
        "ogrenci_no": "", 
        "adim_tamamlandi": False,
        "aktif_gif": "pito_merhaba.gif"
    })

mufredat = mufredat_yukle()

# --- 4. SİDEBAR (SABİT PANEL) ---
def sidebar_goster():
    with st.sidebar:
        st.title("🐍 Pito Panel")
        # Sidebar liderlik listesi giriş ekranı dahil her an sabittir
        if st.session_state.giris_yapildi:
            gif_goster(st.session_state.aktif_gif)
            st.subheader(f"Öğrenci No: {st.session_state.ogrenci_no}")
            
            # 9 Modül x 5 Adım = 45 Adım İlerlemesi
            toplam_adim = (st.session_state.modul_idx * 5) + (st.session_state.adim_idx + 1)
            # Rütbeler Egg'den Python Hero'ya kadardır
            rutbeler = ["Egg 🥚", "Hatchling 🐣", "Coder 💻", "Developer 🚀", "Engineer 🛠️", "Master 🧙", "Python Hero 👑"]
            rutbe_idx = min(len(rutbeler)-1, (toplam_adim - 1) // 7)
            
            st.metric("Mevcut Rütbe", rutbeler[rutbe_idx])
            st.progress(min(toplam_adim / 45, 1.0))
            st.write(f"🏆 Toplam Puan: **{st.session_state.toplam_puan}**")
            
            st.divider()
            st.subheader("📊 Liderlik Tablosu")
            st.table({"Öğrenci": ["Ali 12/A", "Merve 11/B", "Siz"], "Puan": [880, 820, st.session_state.toplam_puan]})
            
            if st.button("Eğitimi Sıfırla"):
                st.session_state.clear()
                st.rerun() # Her buton tetikleyicisi st.rerun() içermeli

# --- 5. KONTROL MEKANİZMASI ---
#
def kontrol_et(girilen_kod, dogru_kod, ipucu):
    t_giris = girilen_kod.strip().replace('"', "'").replace(" ", "")
    t_cozum = dogru_kod.strip().replace('"', "'").replace(" ", "")
    
    if t_giris == t_cozum:
        st.session_state.adim_tamamlandi = True
        st.session_state.aktif_gif = "pito_basari.gif"
    else:
        # Her hata 5 puan düşürür
        st.session_state.hata_sayisi += 1
        st.session_state.mevcut_puan = max(0, st.session_state.mevcut_puan - 5)
        
        if st.session_state.hata_sayisi < 3:
            st.session_state.aktif_gif = "pito_dusunuyor.gif"
        elif st.session_state.hata_sayisi == 3:
            st.session_state.aktif_gif = "pito_hata.gif"
            # 3. hatada sarı kutuda ipucu
            st.warning(f"💡 Pito'dan İpucu: {ipucu}")
        
        if st.session_state.hata_sayisi >= 4:
            # 4. hatada editör kilitlenip kırmızı kutuda doğru çözüm
            st.session_state.kilitli = True
            st.session_state.aktif_gif = "pito_hata.gif"

# --- 6. ANA EKRAN AKIŞI ---
sidebar_goster()

if mufredat:
    if not st.session_state.giris_yapildi:
        st.title("🎓 Pito Akademi Giriş")
        gif_goster("pito_merhaba.gif", width=200)
        # Okul numarası sadece sayısal olmalı
        no = st.text_input("Okul Numaranızı Girin:")
        if st.button("Eğitime Başla"):
            if no.isdigit():
                st.session_state.ogrenci_no = no
                st.session_state.giris_yapildi = True
                st.rerun()
            else:
                st.error("Lütfen sadece sayısal bir numara giriniz!")
    else:
        moduller = list(mufredat.keys())
        if st.session_state.modul_idx < len(moduller):
            modul_adi = moduller[st.session_state.modul_idx]
            adim = mufredat[modul_adi][st.session_state.adim_idx]
            
            st.header(f"📍 {modul_adi}")
            st.subheader(adim['baslik'])
            
            # Pito terimleri derinlemesine ve örneklerle açıklar
            with st.chat_message("assistant", avatar="🐍"):
                st.markdown(f"**Pito:** {adim['pito_notu']}")
            
            st.divider()
            st.info(f"📝 **GÖREV:** {adim['egzersiz']}")
            
            ed_key = f"ed_{st.session_state.modul_idx}_{st.session_state.adim_idx}"
            user_code = st.text_area("Boşlukları Doldur:", value=adim['taslak'], key=ed_key, disabled=st.session_state.kilitli)
            
            # Kod Paneli Üzerinde Geri Bildirim
            if not st.session_state.adim_tamamlandi and not st.session_state.kilitli:
                if st.button("Çalıştır", type="primary"):
                    kontrol_et(user_code, adim['cozum'], adim['ipucu'])
                    st.rerun()

            if st.session_state.kilitli:
                st.error(f"🛑 4. Hata! Doğru Çözüm: {adim['cozum']}")
                if st.button("Anladım, Geç"):
                    st.session_state.adim_tamamlandi, st.session_state.mevcut_puan = True, 0
                    st.rerun()

            if st.session_state.adim_tamamlandi:
                st.success(f"🎉 Harika! +{st.session_state.mevcut_puan} Puan kazandın.")
                if st.button("Sonraki Adım ➡️"):
                    st.session_state.toplam_puan += st.session_state.mevcut_puan
                    # Bir sonraki egzersize geçildiğinde puan 20'ye resetlenir
                    if st.session_state.adim_idx < 4:
                        st.session_state.adim_idx += 1
                    else:
                        st.session_state.adim_idx, st.session_state.modul_idx = 0, st.session_state.modul_idx + 1
                    
                    st.session_state.update({"adim_tamamlandi": False, "hata_sayisi": 0, "mevcut_puan": 20, "kilitli": False, "aktif_gif": "pito_merhaba.gif"})
                    st.rerun()
        else:
            st.title("🏆 MEZUN OLDUN!")
            gif_goster("pito_mezun.gif")
            st.balloons()
