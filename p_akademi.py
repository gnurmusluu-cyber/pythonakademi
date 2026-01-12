import streamlit as st
import json

# JSON VERİSİNİ YÜKLE
def mufredat_yukle():
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# SESSION STATE BAŞLATMA
if "puan" not in st.session_state:
    st.session_state.update({
        "modul_idx": 0, "adim_idx": 0, "hata_sayisi": 0,
        "mevcut_egzersiz_puani": 20, "toplam_puan": 0, "kilitli": False
    })

mufredat = mufredat_yukle()
modul_listesi = list(mufredat.keys())
aktif_modul_adi = modul_listesi[st.session_state.modul_idx]
aktif_adim = mufredat[aktif_modul_adi][st.session_state.adim_idx]

# --- SİDEBAR (SABİT) ---
with st.sidebar:
    st.title("🏆 Pito Akademi")
    st.metric("Puanın", st.session_state.toplam_puan)
    st.progress(((st.session_state.modul_idx * 5) + (st.session_state.adim_idx)) / 40)
    st.write("📍 Nusaybin SBAL Laboratuvarı")

# --- ANA EKRAN ---
st.header(f"📘 {aktif_modul_adi}")
st.subheader(aktif_adim['baslik'])

with st.chat_message("assistant", avatar="🐍"):
    st.write(aktif_adim['pito_notu'])

st.divider()
st.info(f"**Görev:** {aktif_adim['egzersiz']}")

# KOD EDİTÖRÜ
user_code = st.text_area("Kodunu Yaz:", height=150, disabled=st.session_state.kilitli)

if st.button("Çalıştır"):
    # Temizleme ve Karşılaştırma
    if user_code.strip() == aktif_adim['cozum'].strip():
        st.success("Tebrikler! +{} Puan".format(st.session_state.mevcut_egzersiz_puani))
        st.session_state.toplam_puan += st.session_state.mevcut_egzersiz_puani
        # İlerletme Mantığı (Sonraki butonu da eklenebilir)
        st.session_state.adim_idx += 1
        st.session_state.hata_sayisi = 0
        st.session_state.mevcut_egzersiz_puani = 20
        st.rerun()
    else:
        st.session_state.hata_sayisi += 1
        st.session_state.mevcut_egzersiz_puani -= 5
        st.error("Hata! Pito: Tekrar dene.")
        
        if st.session_state.hata_sayisi == 3:
            st.warning(f"💡 İpucu: {aktif_adim['ipucu']}")
        
        if st.session_state.hata_sayisi >= 4:
            st.session_state.kilitli = True
            st.error(f"🛑 4. Hata! Çözüm: \n\n {aktif_adim['cozum']}")
            if st.button("Anladım, Geç"):
                st.session_state.adim_idx += 1
                st.session_state.kilitli = False
                st.session_state.hata_sayisi = 0
                st.rerun()
