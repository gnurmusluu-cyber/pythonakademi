import streamlit as st
import random
import os
import base64

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- 0. SİBER-MOBİL ZIRH VE BUTON OKUNABİLİRLİĞİ ---
    st.markdown('''
        <style>
        /* Varsayılanları sil */
        header[data-testid="stHeader"], [data-testid="stDecoration"], footer { display: none !important; }
        .stApp { background-color: #0e1117 !important; }

        /* HUD: SABİT ÜST PANEL (SIZDIRMAZ ZIRH) */
        .cyber-hud {
            position: fixed; top: 0; left: 0; right: 0;
            height: 115px;
            background-color: #0e1117 !important;
            border-bottom: 3px solid #00E5FF;
            z-index: 10000;
            padding: 0 25px;
            display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 15px 35px rgba(0,0,0,0.9);
        }

        /* MOBİL SIKIŞIKLIK ÇÖZÜMÜ */
        @media (max-width: 768px) {
            .cyber-hud {
                height: 160px !important; /* Alanı esnettik */
                flex-direction: column;
                justify-content: center;
                padding: 10px;
            }
            .hud-pito-gif img { width: 55px !important; height: 55px !important; margin-bottom: 5px; }
            .hud-item { font-size: 0.8rem !important; margin: 3px 5px !important; }
            [data-testid="stMainViewContainer"] { padding-top: 170px !important; }
        }

        /* PİTO KOKPİT GÖRSELİ */
        .hud-pito-gif img {
            width: 75px; height: 75px;
            border-radius: 50%; border: 3px solid #00E5FF;
            object-fit: cover; background: #000;
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
        }

        /* BUTON OKUNABİLİRLİĞİ (SİYAH METİN MÜHRÜ) */
        div.stButton > button {
            background-color: #00E5FF !important;
            border: none !important;
            transition: 0.3s;
        }
        div.stButton > button p, div.stButton > button span {
            color: #000000 !important;
            font-weight: 900 !important;
            font-size: 1rem !important;
        }
        div.stButton > button:hover {
            background-color: #ADFF2F !important;
            transform: scale(1.02);
        }

        .hud-item { color: #E0E0E0; font-family: 'Fira Code', monospace; font-size: 0.95rem; margin: 0 12px; }
        .hud-v { color: #00E5FF; font-weight: bold; text-shadow: 0 0 8px #00E5FF; }

        .console-box {
            background-color: #000 !important; color: #ADFF2F !important;
            border: 1px solid #333; border-radius: 10px;
            padding: 18px; font-family: 'Courier New', monospace; margin: 15px 0;
            box-shadow: inset 0 0 10px rgba(173, 255, 47, 0.1);
        }

        [data-testid="stMainViewContainer"] { padding-top: 130px !important; }
        * :focus { outline: none !important; box-shadow: none !important; }
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. HUD VE PİTO GIF HAZIRLIĞI ---
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

    # HUD HTML ÇIKTISI
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

    # --- 2. ANA İÇERİK VE NAVİGASYON ---
    m_idx = int(u['mevcut_modul']) - 1
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    ad_k = u['ad_soyad'].split()[0]

    c_msg, c_rev, c_exit = st.columns([0.45, 0.35, 0.2])
    with c_msg: st.markdown(f"<div style='color:#00E5FF; font-style:italic;'>💬 {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)
    with c_rev:
        if st.button("🔍 Geçmiş egzersizler", use_container_width=True, key="rev_edu"):
            st.session_state.in_review = True; st.rerun()
    with c_exit:
        if st.button("🚪 Çıkış", help="Güvenli Çıkış", use_container_width=True, key="exit_edu"):
            st.session_state.user = None; st.rerun()

    st.progress((m_idx + 1) / len(mufredat))

    cl, cr = st.columns([7.5, 2.5])
    with cl:
        with st.expander(f"📦 {modul['modul_adi']}", expanded=True):
            st.markdown(f"<div style='background:rgba(0,229,255,0.03); padding:15px; border-radius:10px;'>{modul['pito_anlatimi']}</div>", unsafe_allow_html=True)
            st.markdown(f"### 🎯 GÖREV {egz['id']}")
            st.info(egz['yonerge'])

        # --- 3. EDİTÖR VE KONTROL MOTORU ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            if st.session_state.error_count > 0:
                lvl = f"level_{min(st.session_state.error_count, 4)}"
                st.error(f"🚨 **Pito:** {random.choice(msgs['errors'][lvl]).format(ad_k)}")
                if st.session_state.error_count == 3:
                    st.warning(f"💡 **Pito'nun İpucu:** {egz.get('ipucu', 'Kodu tekrar kontrol et!')}")

            if "reset_trigger" not in st.session_state: st.session_state.reset_trigger = 0
            
            user_code = st.text_area("Siber-Editor", value=egz['sablon'], height=180, 
                                     key=f"ed_{egz['id']}_{st.session_state.reset_trigger}", label_visibility="collapsed")
            
            b_chk, b_res = st.columns([4, 1.2])
            with b_chk:
                if st.button("KODU KONTROL ET 🚀", type="primary", use_container_width=True):
                    st.session_state.current_code = user_code
                    if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru = True; st.balloons(); st.rerun()
                    else:
                        st.session_state.error_count += 1; st.rerun()
            with b_res:
                if st.button("🔄 SIFIRLA", use_container_width=True):
                    st.session_state.reset_trigger += 1; st.rerun()

        elif st.session_state.cevap_dogru:
            st.markdown("💻 **Konsol Çıktısı:**")
            st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', '...')}</div>", unsafe_allow_html=True)
            st.success(f"✅ Harika iş {ad_k}! (+{p_xp} XP)")
            if st.button("SIRADAKİ GÖREVE GEÇ ➡️", type="primary", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)

        elif st.session_state.error_count >= 4:
            st.warning("🚨 Limit doldu genç yazılımcı! Çözümü incele:")
            st.code(egz['cozum'], language="python")
            st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', '...')}</div>", unsafe_allow_html=True)
            if st.button("DEVAM ET ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
