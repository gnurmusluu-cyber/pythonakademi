import streamlit as st
import random
import os
import base64

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- 0. SİBER-HUD VE RESPONSIVE CSS MÜHRÜ ---
    st.markdown('''
        <style>
        .stApp { background-color: #0e1117; }
        
        /* Sayfa Genel Boşluklarını Minimize Etme */
        .block-container {
            padding-top: 0rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }

        /* SABİT ÜST HUD BAR (GIF DESTEKLİ) */
        .cyber-hud {
            position: fixed; top: 0; left: 0; width: 100%;
            background: rgba(14, 17, 23, 0.98);
            border-bottom: 2px solid #00E5FF;
            z-index: 999999; padding: 10px 25px;
            display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 4px 20px rgba(0, 229, 255, 0.3);
            backdrop-filter: blur(15px);
            flex-wrap: wrap;
        }

        /* PITO GIF ÇERÇEVESİ (KOKPİT) */
        .hud-pito-gif img {
            width: 45px;
            height: 45px;
            border-radius: 50%;
            border: 2px solid #00E5FF;
            object-fit: cover;
            background: #000;
            margin-right: 12px;
        }

        .hud-item { color: #E0E0E0; font-family: 'Fira Code', monospace; font-size: 0.85rem; margin: 2px 8px; }
        .hud-v { color: #00E5FF; font-weight: bold; text-shadow: 0 0 5px #00E5FF; }

        /* HUD Altında Kalmaması İçin İçerik Kaydırma */
        .main-container { margin-top: 75px; }

        /* MOBİL UYUMLULUK ZIRHI */
        @media (max-width: 768px) {
            .cyber-hud { padding: 8px 10px; justify-content: center; }
            .hud-item { font-size: 0.75rem; margin: 2px 5px; }
            .main-container { margin-top: 115px; }
            .hud-pito-gif img { width: 35px; height: 35px; margin-right: 8px; }
            .academy-header { font-size: 1.5rem !important; }
        }

        .console-box {
            background-color: #000000 !important; color: #00E5FF !important;
            border: 1px solid #333; border-radius: 8px;
            padding: 15px; font-family: 'Courier New', monospace; margin: 10px 0;
            box-shadow: 0 0 10px rgba(0, 229, 255, 0.2);
        }
        .academy-header {
            text-align: center; color: #00E5FF; font-size: 2rem; font-weight: bold;
            text-shadow: 0 0 15px rgba(0, 229, 255, 0.4); margin-bottom: 20px;
        }
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. HUD VERİLERİ VE PİTO GIF HAZIRLIĞI ---
    p_xp = max(0, 20 - (st.session_state.error_count * 5))
    
    # emotions.py'den duygu durumunu ve Base64 GIF'i alıyoruz
    p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
    
    # Base64 dönüşümü (GIF'in HUD içinde görünmesi için kritik)
    def get_base64_gif(mod):
        path = os.path.join(os.path.dirname(__file__), "assets", f"pito_{mod}.gif")
        if os.path.exists(path):
            with open(path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            return f"data:image/gif;base64,{encoded}"
        return ""

    pito_gif = get_base64_gif(p_mod)

    # KOKPİT (HUD) HTML ÇIKTISI
    st.markdown(f'''
        <div class="cyber-hud">
            <div style="display: flex; align-items: center;">
                <div class="hud-pito-gif"><img src="{pito_gif}" alt="Pito"></div>
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
    total_m = len(mufredat)
    ad_k = u['ad_soyad'].split()[0]
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    c_i, t_i = modul['egzersizler'].index(egz) + 1, len(modul['egzersizler'])

    # İlerleme Barları
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown(f"<div style='color:#00E5FF; font-weight:bold; font-size:0.8rem;'>🚀 AKADEMİ: %{int((m_idx/total_m)*100)}</div>", unsafe_allow_html=True)
        st.progress(min((m_idx) / total_m, 1.0))
    with col_p2:
        st.markdown(f"<div style='color:#00E5FF; font-weight:bold; font-size:0.8rem;'>📍 MODÜL {m_idx+1} - GÖREV {c_i}/{t_i}</div>", unsafe_allow_html=True)
        st.progress(c_i / t_i)

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns([7.5, 2.5])
    
    with cl:
        # Pito Mesajı ve İnceleme Düğmesi Yan Yana
        c_msg, c_rev = st.columns([0.65, 0.35])
        with c_msg:
            st.markdown(f"<div style='color:#00E5FF; font-style:italic; font-size:1.1rem;'>💬 {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)
        with c_rev:
            if st.button("🔍 Önceki egzersizleri incele", help="Geçmiş görev çözümlerini gör", key="btn_review_main", use_container_width=True):
                st.session_state.in_review = True
                st.rerun()

        with st.expander(f"📖 {modul['modul_adi']}", expanded=True):
            st.markdown(f"<div style='background:rgba(0,229,255,0.03); padding:15px; border-radius:10px;'>{modul['pito_anlatimi']}</div>", unsafe_allow_html=True)
            st.markdown(f"### 🎯 GÖREV {egz['id']}")
            st.info(egz['yonerge'])

        # --- EDİTÖR VE KONTROL AKIŞI ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            if st.session_state.error_count > 0:
                st.error(f"🚨 **Pito:** {random.choice(msgs['errors'][f'level_{min(st.session_state.error_count, 4)}']).format(ad_k)}")
                if st.session_state.error_count == 3: st.warning(f"💡 **İPUCU:** {egz.get('ipucu', 'Kodu tekrar kontrol et!')}")

            if "reset_trigger" not in st.session_state: st.session_state.reset_trigger = 0
            user_code = st.text_area("Siber-Editor", value=egz['sablon'], height=180, key=f"v_hud_{egz['id']}_{st.session_state.reset_trigger}", label_visibility="collapsed")

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
            st.warning("🚨 Limit doldu! Çözümü ve çıktıyı incele:")
            st.code(egz['cozum'], language="python")
            st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', '...')}</div>", unsafe_allow_html=True)
            if st.button("DEVAM ET ➡️", type="primary", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr:
        # Onur Kürsüsü sağ kolona geri mühürlendi
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)

    st.markdown('</div>', unsafe_allow_html=True)
