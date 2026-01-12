import streamlit as st
import json

# --- 1. VERİ YÜKLEME ---
def verileri_yukle():
    try:
        with open('mufredat.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Hata: 'mufredat.json' bulunamadı!")
        return None

# --- 2. SESSION STATE ---
if "initialized" not in st.session_state:
    st.session_state.update({
        "modul_idx": 0, "adim_idx": 0, "hata_sayisi": 0,
        "mevcut_puan": 20, "toplam_puan": 0, "kilitli": False,
        "giris_yapildi": False, "ogrenci_no": "", "adim_tamamlandi": False,
        "aktif_gif": "pito_merhaba.gif" # Başlangıç GIF'i
    })

mufredat = verileri_yukle()

# --- 3. SİDEBAR VE LİDERLİK ---
def sidebar_goster():
    with st.sidebar:
        st.title("🐍 Pito Panel")
        if st.session_state.giris_yapildi:
            st.image(st.session_state.aktif_gif, use_container_width=True) # Pito Sidebar'da!
            st.subheader(f"No: {st.session_state.ogrenci_no}")
            
            ilerleme = (st.session_state.modul_idx * 5) + (st.session_state.adim_idx + 1)
            st.progress(ilerleme / 45)
            st.write(f"🏆 Puan: **{st.session_state.toplam_puan}**")
            st.divider()
            st.table({"Sıra": [1, 2, 3], "Öğrenci": ["Mehmet", "Ayşe", "Siz"], "Puan": [920, 850, st.session_state.toplam_puan]})

# --- 4. HATA VE GIF MANTIĞI ---
def kontrol_et(girilen_kod, dogru_kod, ipucu):
    # Boşlukları ve tırnak farklarını yok say
    t_giris = girilen_kod.strip().replace('"', "'").replace(" ", "")
    t_cozum = dogru_kod.strip().replace('"', "'").replace(" ", "")
    
    if t_giris == t_cozum:
        st.session_state.adim_tamamlandi = True
        st.session_state.aktif_gif = "pito_basari.gif" # Başarı GIF'i
    else:
        st.session_state.hata_sayisi += 1
        st.session_state.mevcut_puan = max(0, st.session_state.mevcut_puan - 5)
        
        if st.session_state.hata_sayisi < 3:
            st.session_state.aktif_gif = "pito_dusunuyor.gif" # Düşünme GIF'i
        else:
            st.session_state.aktif_gif = "pito_hata.gif" # Hata/İpucu GIF'i
            if st.session_state.hata_sayisi >= 4:
                st.session_state.kilitli = True

# --- 5. ANA EKRAN ---
sidebar_goster()

if mufredat:
    if not st.session_state.giris_yapildi:
        st.title("🎓 Pito Akademi Giriş")
        st.image("pito_merhaba.gif", width=200)
        no = st.text_input("Okul Numaran:")
        if st.button("Başla") and no.isdigit():
            st.session_state.ogrenci_no, st.session_state.giris_yapildi = no, True
            st.rerun()
    else:
        modul_adlari = list(mufredat.keys())
        if st.session_state.modul_idx < len(modul_adlari):
            aktif_modul = modul_adlari[st.session_state.modul_idx]
            adim = mufredat[aktif_modul][st.session_state.adim_idx]
            
            st.header(f"📍 {aktif_modul}")
            st.subheader(adim['baslik'])
            
            with st.chat_message("assistant", avatar="🐍"):
                st.markdown(f"**Pito:** {adim['pito_notu']}")
            
            st.info(f"📝 **GÖREV:** {adim['egzersiz']}")
            user_code = st.text_area("Kod Paneli:", value=adim['taslak'], key=f"e_{st.session_state.modul_idx}_{st.session_state.adim_idx}", disabled=st.session_state.kilitli)
            
            if not st.session_state.adim_tamamlandi and not st.session_state.kilitli:
                if st.button("Çalıştır", type="primary"):
                    kontrol_et(user_code, adim['cozum'], adim['ipucu'])
                    st.rerun()

            if st.session_state.kilitli:
                st.error(f"🛑 Çözüm: {adim['cozum']}")
                if st.button("Anladım, Geç"):
                    st.session_state.adim_tamamlandi, st.session_state.mevcut_puan = True, 0
                    st.rerun()

            if st.session_state.adim_tamamlandi:
                st.success(f"🎉 Harika! +{st.session_state.mevcut_puan} Puan.")
                if st.button("Sonraki Adım ➡️"):
                    st.session_state.toplam_puan += st.session_state.mevcut_puan
                    if st.session_state.adim_idx < 4: st.session_state.adim_idx += 1
                    else: st.session_state.adim_idx, st.session_state.modul_idx = 0, st.session_state.modul_idx + 1
                    
                    st.session_state.update({"adim_tamamlandi": False, "hata_sayisi": 0, "mevcut_puan": 20, "kilitli": False, "aktif_gif": "pito_merhaba.gif"})
                    st.rerun()
        else:
            st.title("🏆 MEZUN OLDUN!")
            st.image("pito_mezun.gif", use_container_width=True)
            st.balloons()
