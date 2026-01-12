import streamlit as st
import pandas as pd
import time
from streamlit_gsheets import GSheetsConnection

# --- AYARLAR ---
KULLANICILAR_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- SİSTEM HAFIZASI ---
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "cevap_dogru" not in st.session_state: st.session_state.cevap_dogru = False
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"

# --- VERİTABANI GÜNCELLEME (KRİTİK FONKSİYON) ---
def ilerleme_kaydet(kazanilan_puan, n_id, n_m):
    # Google Sheets'ten güncel veriyi çek
    df = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
    idx = df[df['ogrenci_no'] == st.session_state.user['ogrenci_no']].index[0]
    
    # Verileri işle [cite: 2026-01-12]
    df.at[idx, 'toplam_puan'] = int(float(df.at[idx, 'toplam_puan'])) + kazanilan_puan
    df.at[idx, 'mevcut_egzersiz'] = str(n_id)
    df.at[idx, 'mevcut_modul'] = int(n_m)
    
    # Sheets'e geri yaz
    conn.update(spreadsheet=KULLANICILAR_URL, data=df)
    
    # Yerel hafızayı güncelle ve resetle
    st.session_state.user = df.iloc[idx].to_dict()
    st.session_state.error_count = 0
    st.session_state.cevap_dogru = False
    st.session_state.pito_mod = "merhaba"
    st.rerun()

# --- EĞİTİM PANELİ ---
if st.session_state.user:
    u = st.session_state.user
    mufredat = load_mufredat() # JSON yükleme fonksiyonun
    
    # Mevcut Modül ve Egzersizi Belirle
    m_idx = int(float(u['mevcut_modul'])) - 1
    modul = mufredat['pito_akademi_mufredat'][m_idx]
    egz_listesi = modul['egzersizler']
    egz = next((e for e in egz_listesi if e['id'] == str(u['mevcut_egzersiz'])), egz_listesi[0])
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(f"assets/pito_{st.session_state.pito_mod}.gif")
        st.info(f"**GÖREV {egz['id']}:** {egz['yonerge']}")

    with col2:
        st.subheader("💻 Komut Paneli")
        puan_potansiyeli = max(0, 20 - (st.session_state.error_count * 5))
        
        # DURUM 1: HENÜZ DOĞRU YAPILMADI VE HATA SINIRI AŞILMADI
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            kod_input = st.text_area("Kodunu Yaz:", value=egz['sablon'], height=200)
            if st.button("Kontrol Et"):
                if kod_input.strip() == egz['dogru_cevap_kodu'].strip():
                    st.session_state.cevap_dogru = True
                    st.session_state.pito_mod = "tebrik"
                    st.rerun()
                else:
                    st.session_state.error_count += 1
                    st.session_state.pito_mod = "hata"
                    st.rerun()

        # DURUM 2: CEVAP DOĞRU (İLERLEME BUTONU)
        elif st.session_state.cevap_dogru:
            st.success(f"🌟 Harika! {puan_potansiyeli} XP Kazandın.")
            
            # Sonraki ID Hesaplama
            curr_idx = egz_listesi.index(egz)
            if curr_idx + 1 < len(egz_listesi):
                next_id, next_m = egz_listesi[curr_idx + 1]['id'], u['mevcut_modul']
            else:
                next_id, next_m = f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1

            if st.button("Sonraki Göreve Geç ➡️"):
                ilerleme_kaydet(puan_potansiyeli, next_id, next_m)

        # DURUM 3: 4 HATA (KİLİT VE ÇÖZÜM)
        elif st.session_state.error_count >= 4:
            st.error("🚫 Panel Kilitlendi. Çözümü incele.")
            with st.expander("📖 Çözümü Gör"):
                st.code(egz['cozum'])
            
            # Kilitli ilerleme hesaplama
            curr_idx = egz_listesi.index(egz)
            n_id = egz_listesi[curr_idx + 1]['id'] if curr_idx+1 < len(egz_listesi) else f"{int(u['mevcut_modul'])+1}.1"
            n_m = u['mevcut_modul'] if curr_idx+1 < len(egz_listesi) else int(u['mevcut_modul']) + 1
            
            if st.button("Çözümü Anladım, Sıradaki Göreve Geç ➡️"):
                ilerleme_kaydet(0, n_id, n_m)
