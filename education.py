import streamlit as st
import random

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase, inceleme_modu=False):
    # --- 0. SİBER-HUD VE DARALTILMIŞ YERLEŞİM CSS ---
    st.markdown('''
        <style>
        /* Sayfa Genel Boşluklarını Sıfırlama */
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        .stApp { background-color: #0e1117; }
        
        /* SABİT ÜST HUD BAR (Daha İnce) */
        .cyber-hud {
            position: fixed; top: 0; left: 0; width: 100%;
            background: rgba(14, 17, 23, 0.98);
            border-bottom: 2px solid #00E5FF;
            z-index: 99999; padding: 8px 25px; /* Padding azaltıldı */
            display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 4px 15px rgba(0, 229, 255, 0.2);
            backdrop-filter: blur(10px);
        }
        .hud-item { color: #E0E0E0; font-family: 'Fira Code', monospace; font-size: 0.85rem; }
        .hud-v { color: #00E5FF; font-weight: bold; }

        /* İçeriği HUD Barına İyice Yaklaştırma */
        .main-container { margin-top: 45px; } /* 60/80'den 45'e çekildi */

        .academy-header {
            text-align: center; color: #00E5FF; font-family: 'Fira Code', monospace;
            font-size: 1.8rem; font-weight: bold; letter-spacing: 1px;
            text-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
            margin-top: 0px !important; margin-bottom: 5px !important;
        }

        .kokpit-label { color: #00E5FF; font-family: 'Fira Code', monospace; font-size: 0.8rem; font-weight: bold; }
        
        .console-box {
            background-color: #000 !important; color: #00E5FF !important;
            border: 1px solid #333; border-radius: 8px;
            padding: 12px; font-family: 'Courier New', monospace; margin: 8px 0;
        }
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. HUD (SABİT ÜST BAR) ---
    p_xp = max(0, 20 - (st.session_state.error_count * 5))
    st.markdown(f'''
        <div class="cyber-hud">
            <div class="hud-item">👤 <span class="hud-v">{u['ad_soyad']}</span></div>
            <div class="hud-item">💎 Kazanılacak: <span class="hud-v">{p_xp} XP</span></div>
            <div class="hud-item">⚠️ Hata: <span class="hud-v">{st.session_state.error_count}/4</span></div>
            <div class="hud-item">🏆 Toplam: <span class="hud-v">{int(u['toplam_puan'])} XP</span></div>
        </div>
    ''', unsafe_allow_html=True)

    # --- 2. YAN PANEL (SIDEBAR) ---
    with st.sidebar:
        # Liderlik tablosu burada gösterilir, yan panel çakılı kalır.
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)

    # --- 3. ANA İÇERİK (YUKARI ÇEKİLDİ) ---
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("<div class='academy-header'>🎓 PİTO PYTHON AKADEMİ</div>", unsafe_allow_html=True)

    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    ad_k = u['ad_soyad'].split()[0]
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    c_i, t_i = modul['egzersizler'].index(egz) + 1, len(modul['egzersizler'])

    # İlerleme Çubukları (Daha Kompakt)
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown(f"<div class='kokpit-label'>🚀 AKADEMİ: %{int((m_idx/total_m)*100)}</div>", unsafe_allow_html=True)
        st.progress(min((m_idx) / total_m, 1.0))
    with col_p2:
        st.markdown(f"<div class='kokpit-label'>📍 MODÜL {m_idx + 1} - GÖREV {c_i}/{t_i}</div>", unsafe_allow_html=True)
        st.progress(c_i / t_i)

    st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
    
    # Ana Çalışma Alanı
    p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
    cp1, cp2 = st.columns([1, 5])
    with cp1: emotions_module.pito_goster(p_mod)
    with cp2: st.markdown(f"<div style='color:#00E5FF; font-style:italic;'>💬 {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)

    with st.expander(f"📖 {modul['modul_adi']}", expanded=True):
        st.markdown(f"<div style='background:rgba(0,229,255,0.03); padding:12px; border-radius:10px;'>{modul['pito_anlatimi']}</div>", unsafe_allow_html=True)
        st.markdown(f"### 🎯 GÖREV {egz['id']}")
        st.info(egz['yonerge'])

    # --- AKIŞ KONTROLÜ (İnceleme ve Eğitim) ---
    if inceleme_modu:
        st.markdown("📖 **Pito'nun İdeal Çözümü:**")
        st.code(egz['cozum'], language="python")
        st.markdown("💻 **Beklenen Çıktı:**")
        st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', 'Çıktı bilgisi yok.')}</div>", unsafe_allow_html=True)

    elif not st.session_state.cevap_dogru and st.session_state.error_count < 4:
        if st.session_state.error_count > 0:
            st.error(f"🚨 **Pito:** {random.choice(msgs['errors'][f'level_{min(st.session_state.error_count, 4)}']).format(ad_k)}")
            if st.session_state.error_count == 3: st.warning(f"💡 **İPUCU:** {egz.get('ipucu', 'Kodu tekrar kontrol et!')}")

        if "reset_trigger" not in st.session_state: st.session_state.reset_trigger = 0
        user_code = st.text_area("Siber-Editor", value=egz['sablon'], height=180, key=f"fix_v2_{egz['id']}_{st.session_state.reset_trigger}", label_visibility="collapsed")

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
        st.markdown("💻 **Konsol Çıktısı:**")
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

    st.markdown('</div>', unsafe_allow_html=True)
