import streamlit as st
import random

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- 0. ELEKTRİK MAVİSİ & MİNİMALİST CSS ---
    st.markdown("""
        <style>
        .stTextArea textarea {
            background-color: #0e1117 !important;
            color: #00E5FF !important;
            border: 1px solid #00E5FF !important;
            border-radius: 8px !important;
        }
        .progress-label { color: #00E5FF !important; font-weight: bold; }
        .stProgress > div > div > div > div { background-color: #00E5FF !important; }
        .gorev-box {
            border-left: 4px solid #00E5FF !important;
            background-color: rgba(0, 229, 255, 0.05) !important;
            padding: 10px; border-radius: 0 10px 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    ad_k = u['ad_soyad'].split()[0]

    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])

    # --- 1. YAN PANEL (BİLGİ MERKEZİ) ---
    with st.sidebar:
        st.markdown(f"### 🚀 {modul['modul_adi']}")
        st.info(modul.get('pito_anlatimi', '...'))
        st.divider()
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)

    # --- 2. ANA PANEL (KOD ALANI) ---
    # İlerleme Çubuğu (Kompakt)
    st.markdown(f"<div class='progress-label'>📍 Görev {egz['id']} / Modül {m_idx+1}</div>", unsafe_allow_html=True)
    st.progress((m_idx + 1) / total_m)

    cl, cr = st.columns([1, 4])
    with cl:
        p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
        emotions_module.pito_goster(p_mod)
    with cr:
        p_xp = max(0, 20 - (st.session_state.error_count * 5))
        st.markdown(f"💎 **{p_xp} XP** | ⚠️ **Hata: {st.session_state.error_count}/4**")
        if st.session_state.error_count > 0:
            st.error(f"Pito: {random.choice(msgs['errors'][f'level_{min(st.session_state.error_count, 4)}']).format(ad_k)}")
        else:
            st.markdown(f"💬 {msgs['welcome'].format(ad_k)}")

    # Görev ve Editör
    if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
        st.markdown(f"<div class='gorev-box'>{egz['yonerge']}</div>", unsafe_allow_html=True)
        
        if "reset_trigger" not in st.session_state: st.session_state.reset_trigger = 0

        user_code = st.text_area("Kod Yaz", value=egz['sablon'], height=150, 
                                 key=f"ed_{egz['id']}_{st.session_state.reset_trigger}", label_visibility="collapsed")

        c1, c2 = st.columns([4, 1])
        with c1:
            if st.button("Çalıştır 🚀", use_container_width=True):
                st.session_state.current_code = user_code
                if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                    st.session_state.cevap_dogru = True
                else:
                    st.session_state.error_count += 1
                st.rerun()
        with c2:
            if st.button("🔄", help="Sıfırla", use_container_width=True):
                st.session_state.reset_trigger += 1
                st.rerun()

    # Başarı/Hata Akışı (Kompakt)
    elif st.session_state.cevap_dogru:
        st.success("✅ Harika!")
        if st.button("Sıradaki ➡️", use_container_width=True):
            s_idx = modul['egzersizler'].index(egz) + 1
            n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
            ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)
