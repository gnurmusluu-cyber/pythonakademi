import streamlit as st
import random
import os
import base64

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- 0. SİBER-MOBİL ZIRH (GÖRSEL DÜZENLEME) ---
    st.markdown('''
        <style>
        header[data-testid="stHeader"], [data-testid="stDecoration"], footer { display: none !important; }
        .stApp { background-color: #0e1117 !important; }

        /* HUD: SABİT ÜST PANEL (SIZDIRMAZ ZIRH) */
        .cyber-hud {
            position: fixed; top: 0; left: 0; right: 0;
            height: 110px;
            background-color: #0e1117 !important;
            border-bottom: 3px solid #00E5FF;
            z-index: 10000;
            padding: 0 20px;
            display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 15px 35px rgba(0,0,0,0.8);
        }

        /* PİTO KOKPİT GÖRSELİ */
        .hud-pito-gif img {
            width: 75px; height: 75px;
            border-radius: 50%; border: 3px solid #00E5FF;
            object-fit: cover; background: #000;
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
        }

        .hud-item { color: #E0E0E0; font-family: 'Fira Code', monospace; font-size: 0.95rem; margin: 0 10px; }
        .hud-v { color: #00E5FF; font-weight: bold; text-shadow: 0 0 8px #00E5FF; }

        /* MOBİL OPTİMİZASYONU (SIKIŞIKLIĞI GİDEREN MÜHÜR) */
        @media (max-width: 768px) {
            .cyber-hud {
                height: 140px; /* Yüksekliği esnettik */
                flex-direction: column;
                justify-content: center;
                padding: 10px;
            }
            .hud-pito-gif img { width: 55px; height: 55px; margin-bottom: 5px; }
            .hud-item { font-size: 0.8rem; margin: 2px 5px; }
            [data-testid="stMainViewContainer"] { padding-top: 150px !important; }
        }

        /* BUTON STANDARTI (Siyah Metin & Okunabilirlik) */
        div.stButton > button {
            background-color: #00E5FF !important;
            border: none !important;
            color: #000000 !important;
            font-weight: 900 !important;
        }
        div.stButton > button p, div.stButton > button span {
            color: #000000 !important;
            font-weight: 900 !important;
        }

        /* KONSOL KUTUSU */
        .console-box {
            background-color: #000 !important; color: #ADFF2F !important;
            border: 1px solid #333; border-radius: 8px;
            padding: 15px; font-family: 'Courier New', monospace; margin: 10px 0;
        }
        
        /* ÇERÇEVE İMHASI */
        * :focus { outline: none !important; box-shadow: none !important; }
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. HUD VERİLERİ ---
    p_xp = max(0, 20 - (st.session_state.error_count * 5))
    p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
    
    def get_base64_gif(mod):
        path = os.path.join(os.path.dirname(__file__), "assets", f"pito_{mod}.gif")
        if os.path.exists(path):
            with open(path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            return f"data:image/gif;base64,{encoded}"
        return ""

    pito_gif_base64 = get_base64_gif(p_mod)

    # HUD HTML
    st.markdown(f'''
        <div class="cyber-hud">
            <div style="display: flex; align-items: center;">
                <div class="hud-pito-gif"><img src="{pito_gif_base64}"></div>
                <div class="hud-item">👤 <span class="hud-v">{u['ad_soyad']}</span></div>
            </div>
            <div style="display: flex; align-items: center; flex-wrap: wrap; justify-content: center;">
                <div class="hud-item">💎 Potansiyel: <span class="hud-v">{p_xp} XP</span></div>
                <div class="hud-item">⚠️ Hata: <span class="hud-v">{st.session_state.error_count}/4</span></div>
                <div class="hud-item">🏆 Toplam: <span class="hud-v">{int(u['toplam_puan'])} XP</span></div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    # --- 2. EĞİTİM AKIŞI ---
    st.markdown(f"<h1 style='text-align:center; color:#00E5FF; text-shadow: 0 0 15px #00E5FF;'>🎓 PİTO AKADEMİ</h1>", unsafe_allow_html=True)

    m_idx = int(u['mevcut_modul']) - 1
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    ad_k = u['ad_soyad'].split()[0]

    # Navigasyon Barı
    c_msg, c_rev, c_exit = st.columns([0.4, 0.4, 0.2])
    with c_msg: st.markdown(f"💬 *{msgs['welcome'].format(ad_k)}*")
    with c_rev:
        if st.button("🔍 Geçmiş egzersizler", use_container_width=True, key="rev_edu"):
            st.session_state.in_review = True; st.rerun()
    with c_exit:
        if st.button("🚪 Çıkış", use_container_width=True, key="exit_edu"):
            st.session_state.user = None; st.rerun()

    st.progress((m_idx + 1) / len(mufredat))

    cl, cr = st.columns([7.5, 2.5])
    with cl:
        with st.expander(f"📖 {modul['modul_adi']}", expanded=True):
            st.write(modul['pito_anlatimi'])
            st.info(f"🎯 **GÖREV {egz['id']}:** {egz['yonerge']}")

        # --- EDİTÖR MANTIĞI ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            if st.session_state.error_count > 0:
                st.error(f"🚨 **Pito:** {random.choice(msgs['errors'][f'level_{min(st.session_state.error_count, 4)}']).format(ad_k)}")
                if st.session_state.error_count == 3: st.warning(f"💡 **İpucu:** {egz['ipucu']}")

            user_code = st.text_area("Siber-Editor", value=egz['sablon'], height=150, key=f"ed_{egz['id']}")
            
            if st.button("KODU KONTROL ET 🔍", type="primary", use_container_width=True):
                st.session_state.current_code = user_code
                if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                    st.session_state.cevap_dogru = True; st.balloons(); st.rerun()
                else:
                    st.session_state.error_count += 1; st.rerun()

        elif st.session_state.cevap_dogru:
            st.markdown("💻 **Konsol Çıktısı:**")
            st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', '...')}</div>", unsafe_allow_html=True)
            st.success(f"✅ Harika iş {ad_k}! (+{p_xp} XP)")
            if st.button("SIRADAKİ GÖREVE GEÇ ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)

        elif st.session_state.error_count >= 4:
            st.warning("🚨 Çözümü incele ve devam et:")
            st.code(egz['cozum'], language="python")
            st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', '...')}</div>", unsafe_allow_html=True)
            if st.button("DEVAM ET ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
