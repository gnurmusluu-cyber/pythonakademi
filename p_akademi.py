import streamlit as st
import json
import time

# --- 1. VERİ YÜKLEME VE YAPILANDIRMA ---
def verileri_yukle():
    try:
        with open('mufredat.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        st.error("mufredat.json dosyası bulunamadı! Lütfen dosyayı ana dizine ekle.")
        return {}

# --- 2. SESSION STATE (OTURUM YÖNETİMİ) ---
if "initialized" not in st.session_state:
    st.session_state.update({
        "initialized": True,
        "modul_idx": 0,
        "adim_idx": 0,
        "hata_sayisi": 0,
        "mevcut_puan": 20,
        "toplam_puan": 0,
        "kilitli": False,
        "ogrenci_no": "",
        "giris_yapildi": False
    })

mufredat = verileri_yukle()
modul_listesi = list(mufredat.keys())

# --- 3. SİDEBAR (SABİT LİDERLİK VE İLERLEME) ---
def sidebar_goster():
    with st.sidebar:
        st.title("🐍 Pito Panel")
        if st.session_state.giris_yapildi:
            st.success(f"Öğrenci: {st.session_state.ogrenci_no}")
            
            # Rütbe Sistemi
            toplam_adim = (st.session_state.modul_idx * 5) + (st.session_state.adim_idx + 1)
            rutbeler = ["Egg 🥚", "Hatchling 🐣", "Coder 💻", "Developer 🚀", "Engineer 🛠️", "Master 🧙", "Hero 👑"]
            mevcut_rutbe = rutbeler[min(toplam_adim // 7, 6)]
            
            st.metric("Rütbe", mevcut_rutbe)
            st.progress(toplam_adim / 45)
            st.write(f"📊 Toplam Puan: **{st.session_state.toplam_puan}**")
            
            st.divider()
            st.subheader("🏆 SBAL Liderlik Tablosu")
            # Sabit Liste Girişi
            st.table({
                "Sıra": [1, 2, 3],
                "Öğrenci": ["Ahmet 12/A", "Zeynep 11/C", "Siz"],
                "Puan": [840, 790, st.session_state.toplam_puan]
            })
            
            if st.button("Eğitimi Sıfırla", use_container_width=True):
                st.session_state.clear()
                st.rerun()

# --- 4. HATA VE PUAN MANTIĞI ---
def kontrol_et(girilen_kod, dogru_kod, ipucu):
    # Boşlukları ve tırnak farklarını yok sayarak kontrol et
    if girilen_kod.strip().replace('"', "'") == dogru_kod.strip().replace('"', "'"):
        st.success(f"🎉 Harika! Nusaybin'in gururusun. +{st.session_state.mevcut_puan} Puan!")
        st.session_state.toplam_puan += st.session_state.mevcut_puan
        st.session_state.hata_sayisi = 0
        st.session_state.mevcut_puan = 20
        st.session_state.kilitli = False
        
        if st.button("Sonraki Adıma Geç ➡️"):
            if st.session_state.adim_idx < 4:
                st.session_state.adim_idx += 1
            else:
                st.session_state.adim_idx = 0
                st.session_state.modul_idx += 1
            st.rerun()
    else:
        st.session_state.hata_sayisi += 1
        st.session_state.mevcut_puan = max(0, st.session_state.mevcut_puan - 5)
        st.error(f"Pito: 'Küçük bir hata ama pes etmek yok! Kalan Puan: {st.session_state.mevcut_puan}'")
        
        if st.session_state.hata_sayisi == 3:
            st.warning(f"💡 Pito'dan İpucu: {ipucu}")
        
        if st.session_state.hata_sayisi >= 4:
            st.session_state.kilitli = True
            st.error(f"🛑 4. Hata! Editör kilitlendi. Doğru Çözüm:\n\n{dogru_kod}")
            if st.button("Çözümü İnceledim, Devam Et"):
                if st.session_state.adim_idx < 4:
                    st.session_state.adim_idx += 1
                else:
                    st.session_state.adim_idx = 0
                    st.session_state.modul_idx += 1
                st.session_state.hata_sayisi = 0
                st.session_state.mevcut_puan = 20
                st.session_state.kilitli = False
                st.rerun()

# --- 5. ANA EKRAN AKIŞI ---
sidebar_goster()

if not st.session_state.giris_yapildi:
    st.title("🎓 Pito Python Akademi")
    st.subheader("Nusaybin Süleyman Bölünmez Anadolu Lisesi")
    no = st.text_input("Okul Numaranı Gir (Sadece Sayı):")
    if st.button("Eğitime Başla"):
        if no.isdigit():
            st.session_state.ogrenci_no = no
            st.session_state.giris_yapildi = True
            st.rerun()
        else:
            st.warning("Lütfen geçerli bir numara gir.")
else:
    # Modül ve Adım Verisini Al
    try:
        aktif_modul_adi = modul_listesi[st.session_state.modul_idx]
        adim_verisi = mufredat[aktif_modul_adi][st.session_state.adim_idx]
    except IndexError:
        st.balloons()
        st.title("🏆 TEBRİKLER PYTHON HERO!")
        st.write("Tüm modülleri başarıyla tamamladın.")
        st.stop()

    st.header(f"📍 {aktif_modul_adi}")
    st.subheader(adim_verisi['baslik'])

    # Pito'nun Notu
    with st.chat_message("assistant", avatar="🐍"):
        st.markdown(f"**Pito Der ki:** {adim_verisi['pito_notu']}")

    st.divider()
    st.markdown(f"📝 **GÖREV:** {adim_verisi['egzersiz']}")

    # KOD EDİTÖRÜ (TASLAK İLE)
    # Key değişimi, her yeni adımda editörün sıfırlanmasını sağlar
    editor_key = f"editor_{st.session_state.modul_idx}_{st.session_state.adim_idx}"
    
    user_code = st.text_area(
        "Kod Paneli (Boşlukları Doldur):",
        value=adim_verisi['taslak'],
        height=150,
        key=editor_key,
        disabled=st.session_state.kilitli
    )

    if st.button("Kodu Çalıştır", type="primary"):
        kontrol_et(user_code, adim_verisi['cozum'], adim_verisi['ipucu'])
