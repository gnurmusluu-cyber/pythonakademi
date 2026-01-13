import streamlit as st
import random

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- 0. SİBER-HUD VE RESPONSIVE CSS ---
    st.markdown('''
        <style>
        .stApp { background-color: #0e1117; }
        .block-container { padding-top: 0rem !important; padding-left: 1rem !important; padding-right: 1rem !important; max-width: 100% !important; }

        /* SABİT ÜST HUD BAR (GIF DESTEKLİ) */
        .cyber-hud {
            position: fixed; top: 0; left: 0; width: 100%;
            background: rgba(14, 17, 23, 0.98); border-bottom: 2px solid #00E5FF;
            z-index: 999999; padding: 10px 25px;
            display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 4px 20px rgba(0, 229, 255, 0.3); backdrop-filter: blur(15px);
            flex-wrap: wrap;
        }
        .hud-pito-gif img {
            width: 45px; height: 45px; border-radius: 50%;
            border: 2px solid #00E5FF; object-fit: cover; background: #000;
        }
        .hud-item { color: #E0E0E0; font-family: 'Fira Code', monospace; font-size: 0.85rem; margin: 2px 8px; }
        .hud-v { color: #00E5FF; font-weight: bold; text-shadow: 0 0 5px #00E5FF; }
        .main-container { margin-top: 75px; }

        @media (max-width: 768px) {
            .cyber-hud { padding: 5px 10px; justify-content: center; }
            .main-container { margin-top: 115px; }
            .hud-pito-gif img { width: 35px; height: 35px; }
        }
        .console-box { background-color: #000 !important; color: #00E5FF !important; border: 1px solid #333; border-radius: 8px; padding: 15px; font-family: 'Courier New', monospace; margin: 10px 0; }
        .academy-header { text-align: center; color: #00E5FF; font-size: 1.8rem; font-weight: bold; text-shadow: 0 0 15px rgba(0, 229, 255, 0.4); margin-bottom: 15px; }
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. HUD VERİLERİ VE CANLI PİTO GIF ---
    p_xp = max(0, 20 - (st.session_state.error_count * 5))
    p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
    pito_gif_base64 = emotions_module.get_pito_base64(p_mod) # Base64 verisini alıyoruz
    
    st.markdown(f'''
        <div class="cyber-hud">
            <div style="display: flex; align-items: center;">
                <div class="hud-pito-gif"><img src="{pito_gif_base64}" alt="Pito"></div>
                <div class="hud-item">👤 <span class="hud-v">{u['ad_soyad']}</span></div>
            </div>
            <div style="display: flex; align-items: center;">
                <div class="hud-item">💎 Potansiyel: <span class="hud-v">{p_xp} XP</span></div>
                <div class="hud-item">⚠️ Hata: <span class="hud-v">{st.session_state.error_count}/4</span></div>
                <div class="hud-item">🏆 Toplam: <span class="hud-v">{int(u['toplam_puan'])} XP</span></div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    # --- 2. ANA İÇERİK ---
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("<div class='academy-header'>🎓 PİTO PYTHON AKADEMİ</div>", unsafe_allow_html=True)

    m_idx = int(u['mevcut_modul']) - 1
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    ad_k = u['ad_soyad'].split()[0]

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns([7.5, 2.5])
    
    with cl:
        # Pito Mesajı ve İnceleme Butonu Yan Yana
        c_msg, c_rev = st.columns([0.65, 0.35])
        with c_msg: st.markdown(f"<div style='color:#00E5FF; font-style:italic;'>💬 {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)
        with c_rev:
            if st.button("🔍 Önceki egzersizleri incele", help="Geçmiş çözümleri gör", key="btn_review_main", use_container_width=True):
                st.session_state.in_review = True; st.rerun()

        with st.expander(f"📖 {modul['modul_adi']}", expanded=True):
            st.markdown(f"<div style='background:rgba(0,229,255,0.03); padding:15px; border-radius:10px;'>{modul['pito_anlatimi']}</div>", unsafe_allow_html=True)
            st.markdown(f"### 🎯 GÖREV {egz['id']}")
            st.info(egz['yonerge'])

        # --- EDİTÖR AKIŞI ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            if st.session_state.error_count > 0:
                st.error(f"🚨 **Pito:** {random.choice(msgs['errors'][f'level_{min(st.session_state.error_count, 4)}']).format(ad_k)}")
                if st.session_state.error_count == 3: st.warning(f"💡 **İPUCU:** {egz.get('ipucu', 'Kodu tekrar kontrol et!')}")
            if "reset_trigger" not in st.session_state: st.session_state.reset_trigger = 0
            user_code = st.text_area("Editor", value=egz['sablon'], height=180, key=f"v_hud_{egz['id']}_{st.session_state.reset_trigger}", label_visibility="collapsed")
            b1, b2 = st.columns([4, 1.5])
            with b1:
                if st.button("KODU KONTROL ET 🚀", type="primary", use_container_width=True):
                    st.session_state.current_code = user_code
                    if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru = True; st.balloons()
                    else: st.session_state.error_count += 1
                    st.rerun()
            with b2:
                if st.button("🔄 SIFIRLA", type="secondary", use_container_width=True):
                    st.session_state.reset_trigger += 1; st.rerun()

        elif st.session_state.cevap_dogru:
            st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', '...')}</div>", unsafe_allow_html=True)
            st.success(f"✅ Harika iş çıkardın {ad_k}!")
            if st.button("SIRADAKİ GÖREVE GEÇ ➡️", type="primary", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)

        elif st.session_state.error_count >= 4:
            st.warning("🚨 Limit doldu! Çözümü incele:")
            st.code(egz['cozum'], language="python")
            st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', '...')}</div>", unsafe_allow_html=True)
            if st.button("DEVAM ET ➡️", type="primary", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr: ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
    st.markdown('</div>', unsafe_allow_html=True)
