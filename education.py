import streamlit as st
import random

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- 0. ELEKTRİK MAVİSİ & FERAH CSS ---
    st.markdown("""
        <style>
        /* Ana Renkler ve Fontlar */
        .stApp { background-color: #0e1117; color: #E0E0E0; }
        .stTextArea textarea {
            background-color: #161b22 !important;
            color: #00E5FF !important;
            border: 1px solid #00E5FF !important;
            border-radius: 12px !important;
            font-family: 'Fira Code', 'Courier New', monospace !important;
        }
        
        /* Görev Kutusu Modern Kart */
        .gorev-card {
            background: rgba(0, 229, 255, 0.05);
            border-left: 5px solid #00E5FF;
            padding: 15px;
            border-radius: 0 12px 12px 0;
            margin-bottom: 20px;
        }
        
        /* Rozetler ve Başlıklar */
        .blue-title { color: #00E5FF; font-weight: bold; font-size: 1.2rem; }
        .xp-badge { background: #00E5FF; color: #000; padding: 2px 8px; border-radius: 5px; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    m_idx = int(u['mevcut_modul']) - 1
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    ad_k = u['ad_soyad'].split()[0]

    # --- 1. YAN PANEL (Kılavuz ve Liderlik) ---
    with st.sidebar:
        st.markdown(f"<div class='blue-title'>🚀 {modul['modul_adi']}</div>", unsafe_allow_html=True)
        st.info(modul.get('pito_anlatimi', 'Konu anlatımı yükleniyor...'))
        st.divider()
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)

    # --- 2. ÜST BİLGİ SATIRI ---
    col_p, col_s = st.columns([3, 1])
    with col_p:
        p_xp = max(0, 20 - (st.session_state.error_count * 5))
        st.markdown(f"📍 **Görev {egz['id']}** | <span class='xp-badge'>{p_xp} XP Potansiyel</span>", unsafe_allow_html=True)
    with col_s:
        st.markdown(f"⚠️ Hata: **{st.session_state.error_count}/4**")

    # --- 3. PİTO ETKİLEŞİM ---
    p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
    c_pito, c_msg = st.columns([1, 4])
    with c_pito: emotions_module.pito_goster(p_mod)
    with c_msg:
        if st.session_state.error_count > 0:
            st.error(f"**Pito:** {random.choice(msgs['errors'][f'level_{min(st.session_state.error_count, 4)}']).format(ad_k)}")
        else:
            st.markdown(f"<div style='background:#161b22; padding:10px; border-radius:10px;'>💬 <b>Pito:</b> {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)

    st.divider()

    # --- 4. GÖREV VE EDİTÖR ---
    if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
        st.markdown(f"<div class='gorev-card'><b>GÖREV:</b> {egz['yonerge']}</div>", unsafe_allow_html=True)
        
        if "reset_trig" not in st.session_state: st.session_state.reset_trig = 0

        user_code = st.text_area("Yazılım Alanı", value=egz['sablon'], height=160, 
                                 key=f"edit_v2_{egz['id']}_{st.session_state.reset_trig}", label_visibility="collapsed")

        btn_run, btn_res = st.columns([4, 1])
        with btn_run:
            if st.button("Kodu Gönder 🚀", use_container_width=True):
                st.session_state.current_code = user_code
                if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                    st.session_state.cevap_dogru = True
                else:
                    st.session_state.error_count += 1
                st.rerun()
        with btn_res:
            if st.button("🔄", help="Kod Şablonuna Dön"):
                st.session_state.reset_trig += 1
                st.rerun()

    # BAŞARI / HATA AKIŞI
    elif st.session_state.cevap_dogru:
        st.balloons()
        st.success(f"✅ Müthişsin {ad_k}! Bir sonraki göreve hazır mısın?")
        if st.button("Devam Et ➡️", use_container_width=True):
            s_idx = modul['egzersizler'].index(egz) + 1
            n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
            ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)
