import streamlit as st
import random
import os
import base64

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- ANIMASYON TOGGLE (A/B) ---
    # Tarayıcıyı her hatada animasyonu yeniden oynatmaya zorlar.
    e_count = st.session_state.get('error_count', 0)
    anim_toggle = "A" if e_count % 2 == 0 else "B"
    
    # --- 0. SİBER-GÖRSEL ZIRH ---
    st.markdown(f'''
        <style>
        header[data-testid="stHeader"], [data-testid="stDecoration"], footer {{ display: none !important; }}
        .stApp {{ background-color: #0e1117 !important; }}

        /* BAŞLIK GÖRÜNÜRLÜK GARANTİSİ */
        [data-testid="stMainViewContainer"] {{
            padding-top: 160px !important; 
        }}

        .cyber-hud {{
            position: fixed; top: 0; left: 0; right: 0;
            height: 100px; background-color: #0e1117 !important;
            border-bottom: 3px solid #00E5FF; z-index: 99999 !important;
            padding: 0 30px; display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 10px 30px #000000 !important;
        }}

        /* KOMPAKT PİTO GÖRSELİ (60px) */
        .hud-pito-gif img {{
            width: 60px; height: 60px; border-radius: 50%; border: 2px solid #00E5FF;
            object-fit: cover; background: #000; margin-right: 12px;
            box-shadow: 0 0 10px #00E5FF;
        }}

        /* DOUBLE PULSE ANIMATION */
        @keyframes cyberPulseA {{
            0% {{ transform: scale(1); color: #00E5FF; }}
            50% {{ transform: scale(1.6); color: #FF0000; text-shadow: 0 0 20px #FF0000; }}
            100% {{ transform: scale(1); color: #00E5FF; }}
        }}
        @keyframes cyberPulseB {{
            0% {{ transform: scale(1); color: #00E5FF; }}
            50% {{ transform: scale(1.6); color: #FF0000; text-shadow: 0 0 20px #FF0000; }}
            100% {{ transform: scale(1); color: #00E5FF; }}
        }}

        .pulse-active-A {{ display: inline-block; animation: cyberPulseA 0.6s ease-in-out; font-weight: 900 !important; }}
        .pulse-active-B {{ display: inline-block; animation: cyberPulseB 0.6s ease-in-out; font-weight: 900 !important; }}

        @media (max-width: 768px) {{
            .cyber-hud {{ height: 140px !important; flex-direction: column; justify-content: center; padding: 10px; }}
            .hud-pito-gif img {{ width: 45px !important; height: 45px !important; margin-right: 0; margin-bottom: 5px; }}
            [data-testid="stMainViewContainer"] {{ padding-top: 220px !important; }} 
        }}

        /* OKUNABİLİR BUTONLAR */
        div.stButton > button {{ background-color: #00E5FF !important; color: #000 !important; font-weight: 900 !important; border: none !important; }}
        div.stButton > button p {{ color: #000 !important; font-weight: 900 !important; }}

        .hud-item {{ color: #E0E0E0; font-family: 'Fira Code', monospace; font-size: 0.9rem; margin: 0 10px; }}
        .hud-v {{ color: #00E5FF; font-weight: bold; }}
        .console-box {{ background-color: #000; color: #ADFF2F; border-radius: 8px; padding: 15px; font-family: monospace; }}
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. HUD VE GIF MOTORU ---
    p_xp = max(0, 20 - (e_count * 5))
    p_mod = emotions_module.pito_durum_belirle(e_count, st.session_state.cevap_dogru)
    
    def get_gif_b64(mod):
        path = os.path.join(os.path.dirname(__file__), "assets", f"pito_{mod}.gif")
        if os.path.exists(path):
            return f"data:image/gif;base64,{base64.b64encode(open(path, 'rb').read()).decode()}"
        return ""

    pulse_class = f"pulse-active-{anim_toggle}" if e_count > 0 else ""
    err_html = f'<span class="{pulse_class}">{e_count}</span>'
    xp_html = f'<span class="{pulse_class}">{p_xp}</span>'

    st.markdown(f'''
        <div class="cyber-hud">
            <div style="display: flex; align-items: center; flex-direction: inherit;">
                <div class="hud-pito-gif"><img src="{get_gif_b64(p_mod)}"></div>
                <div class="hud-item">👤 <span class="hud-v">{u['ad_soyad']}</span></div>
            </div>
            <div style="display: flex; align-items: center; flex-wrap: wrap; justify-content: center;">
                <div class="hud-item">💎 Potansiyel: <span class="hud-v">{xp_html} XP</span></div>
                <div class="hud-item">⚠️ Hata: <span class="hud-v">{err_html}/4</span></div>
                <div class="hud-item">🏆 Toplam: <span class="hud-v">{int(u['toplam_puan'])} XP</span></div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    # --- 2. ANA BAŞLIK VE İLERLEME ---
    st.markdown("<h1 style='text-align:center; color:#00E5FF;'>🎓 PİTO PYTHON AKADEMİ</h1>", unsafe_allow_html=True)

    m_idx = int(u['mevcut_modul']) - 1
    total_m = 10 
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    
    c_i = modul['egzersizler'].index(egz) + 1
    overall_progress = (m_idx + (c_i / len(modul['egzersizler']))) / total_m

    st.markdown(f"<div style='color:#00E5FF; font-weight:bold;'>🚀 Akademi Yolculuğu | 📍 {m_idx + 1}. Modül, {c_i}. Görev</div>", unsafe_allow_html=True)
    st.progress(min(overall_progress, 1.0))

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns([7.5, 2.5])
    
    with cl:
        # Navigasyon
        cn1, cn2, cn3 = st.columns([0.4, 0.4, 0.2])
        with cn1: st.markdown(f"💬 *{msgs['welcome'].format(u['ad_soyad'].split()[0])}*")
        with cn2:
            if st.button("🔍 Geçmiş Egzersizler", use_container_width=True, key="rev"):
                st.session_state.in_review = True; st.rerun()
        with cn3:
            if st.button("🚪 Çıkış", use_container_width=True, key="exit"):
                st.session_state.user = None; st.rerun()

        with st.expander(f"📖 {modul['modul_adi']}", expanded=True):
            st.write(modul['pito_anlatimi'])
            st.info(f"🎯 **GÖREV {egz['id']}:** {egz['yonerge']}")

        # Editör ve Mantık
        if not st.session_state.cevap_dogru and e_count < 4:
            if e_count > 0:
                st.error(f"🚨 Pito: {random.choice(msgs['errors'][f'level_{min(e_count, 4)}']).format(u['ad_soyad'].split()[0])}")
            
            if "reset_trigger" not in st.session_state: st.session_state.reset_trigger = 0
            user_code = st.text_area("Siber-Editor", value=egz['sablon'], height=180, key=f"ed_{egz['id']}_{st.session_state.reset_trigger}", label_visibility="collapsed")
            
            b_btns = st.columns([4, 1.2])
            with b_btns[0]:
                if st.button("KODU KONTROL ET 🚀", type="primary", use_container_width=True):
                    st.session_state.current_code = user_code
                    if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru = True; st.balloons(); st.rerun()
                    else: st.session_state.error_count += 1; st.rerun()
            with b_btns[1]:
                if st.button("🔄 SIFIRLA", use_container_width=True):
                    st.session_state.reset_trigger += 1; st.rerun()

        elif st.session_state.cevap_dogru:
            st.success(f"✅ Harika iş! (+{p_xp} XP)")
            if st.button("SIRADAKİ GÖREVE GEÇ ➡️", type="primary", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)

        elif e_count >= 4:
            st.warning("🚨 Bu egzersizden puan alamadın çözümü incele ve devam et")
            st.code(egz['cozum'], language="python")
            if st.button("DEVAM ET ➡️", type="primary", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
