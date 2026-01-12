import streamlit as st
import pandas as pd
import json
import time
from streamlit_gsheets import GSheetsConnection

# --- AYARLAR VE TASARIM ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide")
KULLANICILAR_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"

# --- VERİ YÜKLEME ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_mufredat():
    with open('mufredat.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# --- İLERLEME VE VERİTABANI GÜNCELLEME ---
def ilerleme_kaydet(yeni_puan, yeni_egz_id, yeni_modul_id):
    # Mevcut veriyi çek
    df = conn.read(spreadsheet=KULLANICILAR_URL, ttl=0)
    u_idx = df[df['ogrenci_no'] == st.session_state.user['ogrenci_no']].index[0]
    
    # Verileri güncelle [cite: 2026-01-12]
    df.at[u_idx, 'toplam_puan'] = int(df.at[u_idx, 'toplam_puan']) + yeni_puan
    df.at[u_idx, 'mevcut_egzersiz'] = yeni_egz_id
    df.at[u_idx, 'mevcut_modul'] = yeni_modul_id
    
    # Google Sheets'e yaz
    conn.update(spreadsheet=KULLANICILAR_URL, data=df)
    
    # Yerel hafızayı güncelle
    st.session_state.user = df.iloc[u_idx].to_dict()
    st.session_state.error_count = 0
    st.rerun()

# --- SİSTEM HAFIZASI ---
if "user" not in st.session_state: st.session_state.user = None
if "error_count" not in st.session_state: st.session_state.error_count = 0
if "pito_mod" not in st.session_state: st.session_state.pito_mod = "merhaba"

# --- EĞİTİM EKRANI ---
mufredat = load_mufredat()

if st.session_state.user:
    u = st.session_state.user
    # Modül ve Egzersiz verisini hatasız çekme [cite: 2026-01-12]
    m_idx = int(float(u['mevcut_modul'])) - 1
    modul = mufredat['pito_akademi_mufredat'][m_idx]
    
    # Mevcut egzersizi bul
    egzersiz_listesi = modul['egzersizler']
    mevcut_id = str(u['mevcut_egzersiz'])
    egz = next((e for e in egzersiz_listesi if e['id'] == mevcut_id), egzersiz_listesi[0])
    
    # Puanlama Hesabı [cite: 2026-01-12]
    puan_potansiyeli = max(0, 20 - (st.session_state.error_count * 5))

    st.title(f"🚀 Modül {u['mevcut_modul']}: {modul['modul_adi']}")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(f"assets/pito_{st.session_state.pito_mod}.gif", width=250)
        st.info(f"**GÖREV {egz['id']}:** {egz['yonerge']}")
        
        # 3. HATA DÖNÜTÜ [cite: 2026-01-12]
        if st.session_state.error_count == 3:
            st.warning(f"💡 Pito'nun İpucu: {egz['ipucu']}")
            st.session_state.pito_mod = "dusunen"

    with col2:
        st.subheader("💻 Komut Paneli")
        st.write(f"🎯 Kazanılacak Puan: **{puan_potansiyeli} XP**")
        
        # 4. HATA KİLİDİ [cite: 2026-01-12]
        if st.session_state.error_count < 4:
            kod_girisi = st.text_area("Kodunu Yaz:", value=egz['sablon'], height=200)
            
            if st.button("Kontrol Et"):
                if kod_girisi.strip() == egz['dogru_cevap_kodu'].strip():
                    st.session_state.pito_mod = "basari"
                    st.success(f"Tebrikler! {puan_potansiyeli} puan kazandın.")
                    
                    # Bir sonraki egzersiz ID'sini hesapla
                    curr_idx = egzersiz_listesi.index(egz)
                    if curr_idx + 1 < len(egzersiz_listesi):
                        next_id = egzersiz_listesi[curr_idx + 1]['id']
                        next_m = u['mevcut_modul']
                    else:
                        next_id = f"{int(u['mevcut_modul'])+1}.1"
                        next_m = int(u['mevcut_modul']) + 1
                    
                    if st.button("Harika! Sonraki Göreve Geç ➡️"):
                        ilerleme_kaydet(puan_potansiyeli, next_id, next_m)
                else:
                    st.session_state.error_count += 1
                    st.session_state.pito_mod = "hata"
                    st.error("Kodun hatalı görünüyor, Pito üzgün! Tekrar dene.")
                    time.sleep(1)
                    st.rerun()
        else:
            # ÇÖZÜM VE KİLİT BLOĞU [cite: 2026-01-12]
            st.session_state.pito_mod = "dusunuyor"
            st.error("🚫 Üzgünüm, 4 hata yaptın ve panel kilitlendi. Bu görevden puan alamadın.")
            with st.expander("📖 Çözümü İncele", expanded=True):
                st.code(egz['cozum'], language='python')
            
            # Kilitliyken ilerleme butonu
            curr_idx = egzersiz_listesi.index(egz)
            n_id = egzersiz_listesi[curr_idx + 1]['id'] if curr_idx+1 < len(egzersiz_listesi) else f"{int(u['mevcut_modul'])+1}.1"
            n_m = u['mevcut_modul'] if curr_idx+1 < len(egzersiz_listesi) else int(u['mevcut_modul']) + 1
            
            if st.button("Çözümü Anladım, Sıradaki Göreve Geç ➡️"):
                ilerleme_kaydet(0, n_id, n_m)
