import streamlit as st
import random
import os
import base64

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- ANIMASYON VE DURUM KONTROLÜ ---
    e_count = st.session_state.get('error_count', 0)
    # Hata animasyonu için toggle (A/B)
    err_anim_toggle = "A" if e_count % 2 == 0 else "B"
    
    # --- 0. SİBER-GÖRSEL ZIRH (SUCCESS PULSE EKLENDİ) ---
    st.markdown(f'''
        <style>
        header[data-testid="stHeader"], [data-testid="stDecoration"], footer {{ display: none !important; }}
        .stApp {{ background-color: #0e1117 !important; }}
        [data-testid="stMainViewContainer"] {{ padding-top: 185px !important; }}

        .cyber-hud {{
            position: fixed; top: 0; left: 0; right: 0;
            height: 120px; background-color: #0e1117 !important;
            border-bottom: 3px solid #00E5FF; z-index: 99999 !important;
            padding: 0 30px; display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 10px 30px #000000 !important;
        }}

        .hud-pito-gif img {{
            width: 75px; height: 75px; border-radius: 50%; border: 3px solid #00E5FF;
            object-fit: cover; background: #000; margin-right: 15px;
            box-shadow: 0 0 15px #00E5FF;
        }}

        /* --- SİBER-PULSE ANIMASYONLARI --- */
        @keyframes cyberPulseErrA {{
            0% {{ transform: scale(1); color: #00E5FF; }}
            50% {{ transform: scale(1.7); color: #FF0000; text-shadow: 0 0 20px #FF0000; }}
            100% {{ transform: scale(1); color: #00E5FF; }}
        }}
        @keyframes cyberPulseErrB {{
            0% {{ transform: scale(1); color: #00E5FF; }}
            50% {{ transform: scale(1.7); color: #FF0000; text-shadow: 0 0 20px #FF0000; }}
            100% {{ transform: scale(1); color: #00E5FF; }}
        }}
        @keyframes successPulse {{
            0% {{ transform: scale(1); color: #00E5FF; }}
            50% {{ transform: scale(1.8); color: #ADFF2F; text-shadow: 0 0 25px #ADFF2F; }}
            100% {{ transform: scale(1); color: #00E5FF; }}
        }}

        .err-pulse-A {{ display: inline-block; animation: cyberPulseErrA 0.7s ease-in-out; font-weight: 950 !important; }}
        .err-pulse-B {{ display: inline-block; animation: cyberPulseErrB 0.7s ease-in-out; font-weight: 950 !important; }}
        .success-pulse {{ display: inline-block; animation: successPulse 0.8s ease-in-out; font-weight: 950 !important; }}

        /* MOBİL DÜZENLEME */
        @media (max-width: 768px) {{
            .cyber-hud {{ height: 160px !important; flex-direction: column !important; justify-content: center !important; padding: 5px !important; }}
            .hud-user-info {{ flex-direction: row !important; margin-bottom: 8px !important; display: flex !important; align-items: center !important; }}
            .hud-pito-gif img {{ width: 60px !important; height: 60px !important; margin-right: 10px !important; }}
            .hud-stats {{ flex-direction: row !important; display: flex !important; gap: 10px !important; }}
            .hud-item {{ font-size: 0.8rem !important; margin: 0 5px !important; }}
            [data-testid="stMainViewContainer"] {{ padding-top: 250px !important; }} 
        }}

        div.stButton > button {{ background-color: #00E5FF !important; border: none !important; color: #000 !important; font-weight: 900 !important; }}
        .hud-item {{ color: #E0E0E0; font-family: 'Fira Code', monospace; font-size: 0.95rem; margin: 0 12px; }}
        .hud-v {{ color: #00E5FF; font-weight: bold; }}
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. HUD VERİLERİ VE MANTIK ---
    p_xp = max(0, 20 - (e_count * 5))
    p_mod = emotions_module.pito_durum_belirle(e_count, st.session_state.cevap_dogru)
    
    def get_gif_b64(mod):
        path = os.path.join(os.path.dirname(__file__), "assets", f"pito_{mod}.gif")
        if os.path.exists(path):
            return f"data:image/gif;base64,{base64.b64encode(open(path, 'rb').read()).decode()}"
        return ""

    # Animasyon Sınıfları
    err_class = f"err-pulse-{err_anim_toggle}" if e_count > 0 else ""
    success_class = "success-pulse" if st.session_state.cevap_dogru else ""
    
    # Toplam Puanın Anlık Artışı (Görsel Olarak)
    current_total = int(u['toplam_puan'])
    display_total = current_total + p_xp if st.session_state.cevap_dogru else current_total

    st.markdown(f'''
        <div class="cyber-hud">
            <div class="hud-user-info" style="display: flex; align-items: center;">
                <div class="hud-pito-gif"><img src="{get_gif_b64(p_mod)}"></div>
                <div class="hud-item">👤 <span class="hud-v">{u['ad_soyad']}</span></div>
            </div>
            <div class="hud-stats" style="display: flex; align-items: center; flex-wrap: wrap; justify-content: center;">
                <div class="hud-item">💎 Potansiyel: <span class="hud-v"><span class="{err_class}">{p_xp}</span> XP</span></div>
                <div class="hud-item">⚠️ Hata: <span class="hud-v"><span class="{err_class}">{e_count}</span>/4</span></div>
                <div class="hud-item">🏆 Toplam: <span class="hud-v"><span class="{success_class}">{display_total}</span> XP</span></div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    # --- 2. ANA İÇERİK ---
    st.markdown(f"<h1 style='text-align:center; color:#00E5FF; text-shadow: 0 0 15px #00E5FF; margin-bottom:30px;'>🎓 PİTO PYTHON AKADEMİ</h1>", unsafe_allow_html=True)

    m_idx = int(u['mevcut_modul']) - 1
    total_m = 10 
    ad_k = u['ad_soyad'].split()[0]
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    
    c_i = modul['egzersizler'].index(egz) + 1
    overall_progress = (m_idx + (c_i / len(modul['egzersizler']))) / total_m

    st.markdown(f'''
        <div style="display: flex; justify-content: space-between; color: #00E5FF; font-weight: bold; font-size: 0.9rem; margin-bottom: 5px;">
            <span>🚀 Akademi Yolculuğu (10 Modül Ölçekli)</span>
            <span>📍 {m_idx + 1}. Modül | {c_i}. Görev</span>
        </div>
    ''', unsafe_allow_html=True)
    st.progress(min(overall_progress, 1.0))

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns([7.5, 2.5])
    
    with cl:
        # Navigasyon
        cn1, cn2, cn3 = st.columns([0.4, 0.4, 0.2])
        with cn1: st.markdown(f"💬 *{msgs['welcome'].format(ad_k)}*")
        with cn2:
            if st.button("🔍 Geçmiş Egzersizler", use_container_width=True, key="rev"):
                st.session_state.in_review = True; st.rerun()
        with cn3:
            if st.button("🚪 Çıkış", use_container_width=True, key="exit"):
                st.session_state.user = None; st.rerun()

        with st.expander(f"📖 {modul['modul_adi']}", expanded=True):
            st.markdown(f"<div style='background:rgba(0,229,255,0.03); padding:15px; border-radius:10px;'>{modul['pito_anlatimi']}</div>", unsafe_allow_html=True)
            st.markdown(f"### 🎯 GÖREV {egz['id']}")
            st.info(egz['yonerge'])

        # --- EDİTÖR VE MANTIK ---
        if not st.session_state.cevap_dogru and e_count < 4:
            if e_count > 0:
                lvl = f"level_{min(e_count, 4)}"
                st.error(f"🚨 Pito: {random.choice(msgs['errors'][lvl]).format(ad_k)}")
            
            if "reset_trigger" not in st.session_state: st.session_state.reset_trigger = 0
            user_code = st.text_area("Siber-Editor", value=egz['sablon'], height=180, key=f"ed_{egz['id']}_{st.session_state.reset_trigger}", label_visibility="collapsed")
            
            b_btns = st.columns([4, 1.2])
            with b_btns[0]:
                if st.button("KODU KONTROL ET 🚀", type="primary", use_container_width=True):
                    st.session_state.current_code = user_code
                    if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru = True; st.balloons(); st.rerun()
                    else:
                        st.session_state.error_count += 1; st.rerun()
            with b_btns[1]:
                if st.button("🔄 SIFIRLA", use_container_width=True):
                    st.session_state.reset_trigger += 1; st.rerun()

        elif st.session_state.cevap_dogru:
            st.success(f"✅ Harika iş {ad_k}! (+{p_xp} XP)")
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
