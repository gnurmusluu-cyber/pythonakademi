import streamlit as st
import random

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase, inceleme_modu=False):
    # --- 0. SİBER-ESTETİK VE RESPONSİVE CSS ---
    st.markdown('''
        <style>
        .stApp { background-color: #0e1117; }
        
        /* Sayfa Boşluklarını Minimize Etme */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            max-width: 100% !important;
        }

        /* Sidebar İçeriği Ayarları */
        [data-testid="stSidebar"] {
            background-color: #161b22 !important;
            border-right: 1px solid #00E5FF;
        }

        .academy-header {
            text-align: center; color: #00E5FF; font-family: 'Fira Code', monospace;
            font-size: 2.2rem; font-weight: bold; letter-spacing: 2px;
            text-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
            margin-top: -10px !important; margin-bottom: 20px !important;
        }

        .status-card {
            background: rgba(0, 229, 255, 0.05);
            border: 1px solid #00E5FF;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }

        .console-box {
            background-color: #000 !important; color: #00E5FF !important;
            border: 1px solid #333; border-radius: 8px;
            padding: 12px; font-family: 'Courier New', monospace; margin: 10px 0;
            box-shadow: 0 0 10px rgba(0, 229, 255, 0.1);
        }

        .stTextArea textarea {
            background-color: #161b22 !important; color: #00E5FF !important;
            border: 1px solid #00E5FF !important; border-radius: 12px !important;
            font-family: 'Fira Code', monospace !important;
        }

        button[kind="primary"] {
            background-color: #00E5FF !important;
            color: #0e1117 !important;
            font-weight: bold !important;
        }
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. YAN PANEL (SIDEBAR) OPERASYONU ---
    with st.sidebar:
        st.markdown(f"### 🚀 YAZILIMCI KARTI")
        p_xp = max(0, 20 - (st.session_state.error_count * 5))
        
        # Öğrenci Durum Bilgileri Sidebar'da Sabit
        st.markdown(f'''
            <div class="status-card">
                <div style="color:#E0E0E0; font-size:0.9rem;">👤 <b>{u['ad_soyad']}</b></div>
                <div style="color:#00E5FF; font-size:0.85rem; margin-top:5px;">💎 Potansiyel: <b>{p_xp} XP</b></div>
                <div style="color:#FF4B4B; font-size:0.85rem;">⚠️ Hatalar: <b>{st.session_state.error_count}/4</b></div>
                <div style="color:#ADFF2F; font-size:0.85rem;">🏆 Toplam: <b>{int(u['toplam_puan'])} XP</b></div>
            </div>
        ''', unsafe_allow_html=True)
        
        st.divider()
        # Liderlik Tablosu sidebar'da devam ediyor
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)

    # --- 2. ANA İÇERİK ---
    st.markdown("<div class='academy-header'>🎓 PİTO PYTHON AKADEMİ</div>", unsafe_allow_html=True)

    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    ad_k = u['ad_soyad'].split()[0]
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    c_i, t_i = modul['egzersizler'].index(egz) + 1, len(modul['egzersizler'])

    # İlerleme Göstergeleri
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown(f"<div style='color:#00E5FF; font-weight:bold; font-size:0.8rem;'>🚀 AKADEMİ: %{int((m_idx/total_m)*100)}</div>", unsafe_allow_html=True)
        st.progress(min((m_idx) / total_m, 1.0))
    with col_p2:
        st.markdown(f"<div style='color:#00E5FF; font-weight:bold; font-size:0.8rem;'>📍 MODÜL {m_idx + 1} - GÖREV {c_i}/{t_i}</div>", unsafe_allow_html=True)
        st.progress(c_i / t_i)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Pito Durumu
    p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
    cp1, cp2 = st.columns([1, 5])
    with cp1: emotions_module.pito_goster(p_mod)
    with cp2:
        if inceleme_modu:
            st.markdown(f"<div style='color:#00E5FF; font-weight:bold; font-size:1.1rem;'>🔍 İNCELEME MODU AKTİF</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='color:#00E5FF; font-style:italic;'>💬 {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)

    with st.expander(f"📖 {modul['modul_adi']}", expanded=True):
        st.markdown(f"<div style='background:rgba(0,229,255,0.03); padding:15px; border-radius:10px;'>{modul['pito_anlatimi']}</div>", unsafe_allow_html=True)
        st.markdown(f"### 🎯 GÖREV {egz['id']}")
        st.info(egz['yonerge'])

    # --- 3. AKIŞ MANTIĞI ---
    if inceleme_modu:
        # İnceleme Modu Görünümü
        st.markdown("📖 **Pito'nun İdeal Çözümü:**")
        st.code(egz['cozum'], language="python")
        st.markdown("💻 **Beklenen Çıktı:**")
        st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', 'Çıktı verisi yok.')}</div>", unsafe_allow_html=True)

    elif not st.session_state.cevap_dogru and st.session_state.error_count < 4:
        # Hata ve İpucu
        if st.session_state.error_count > 0:
            st.error(f"🚨 **Pito:** {random.choice(msgs['errors'][f'level_{min(st.session_state.error_count, 4)}']).format(ad_k)}")
            if st.session_state.error_count == 3: st.warning(f"💡 **İPUCU:** {egz.get('ipucu', 'Kodu tekrar kontrol et!')}")

        if "reset_trigger" not in st.session_state: st.session_state.reset_trigger = 0
        user_code = st.text_area("Siber-Editor", value=egz['sablon'], height=180, key=f"v_final_s_{egz['id']}_{st.session_state.reset_trigger}", label_visibility="collapsed")

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
        # Başarı Ekranı ve Çıktı
        st.markdown("💻 **Konsol Çıktısı:**")
        st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', 'Kod çalıştırıldı.')}</div>", unsafe_allow_html=True)
        st.success(f"✅ Müthişsin {ad_k}!")
        if st.button("SIRADAKİ GÖREVE GEÇ ➡️", type="primary", use_container_width=True):
            s_idx = modul['egzersizler'].index(egz) + 1
            n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
            ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)

    elif st.session_state.error_count >= 4:
        # Hata Sınırı ve Çözüm
        st.warning("🚨 Limit doldu! Çözümü ve çıktıyı incele:")
        st.code(egz['cozum'], language="python")
        st.markdown(f"<div class='console-box'>{egz.get('beklenen_cikti', '...')}</div>", unsafe_allow_html=True)
        if st.button("ANLADIM, DEVAM ET ➡️", type="primary", use_container_width=True):
            s_idx = modul['egzersizler'].index(egz) + 1
            n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
            ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)
