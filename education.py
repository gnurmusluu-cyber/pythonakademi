import streamlit as st
import random

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- 0. SİBER-BUZ (ICE-BLUE) KOKPİT CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; }
        
        /* İlerleme Göstergeleri */
        .kokpit-label { color: #00E5FF; font-family: 'Fira Code', monospace; font-size: 0.8rem; font-weight: bold; margin-bottom: 2px; }
        .stProgress > div > div > div > div { background-image: linear-gradient(to right, #00B8D4, #00E5FF) !important; }
        
        /* Görev Kartı Tasarımı */
        .cyber-card {
            background: rgba(0, 229, 255, 0.03);
            border: 1px solid rgba(0, 229, 255, 0.15);
            border-radius: 12px;
            padding: 18px; margin-bottom: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        /* Neon Editör */
        .stTextArea textarea {
            background-color: #161b22 !important;
            color: #00E5FF !important;
            border: 1px solid #00E5FF !important;
            border-radius: 10px !important;
            font-family: 'Fira Code', monospace !important;
            font-size: 1rem !important;
            line-height: 1.6 !important;
        }

        /* Modern Butonlar */
        .stButton > button[kind="primary"] {
            background: #00E5FF !important;
            color: #000 !important;
            border: none !important;
            font-weight: bold !important;
        }
        
        .stButton > button[kind="secondary"] {
            border: 2px solid #00E5FF !important;
            color: #00E5FF !important;
            background: rgba(0, 229, 255, 0.05) !important;
            font-weight: bold !important;
        }
        .stButton > button:hover {
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.4) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- VERİ VE KONUM KONTROLÜ ---
    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    ad_k = u['ad_soyad'].split()[0]
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    c_i, t_i = modul['egzersizler'].index(egz) + 1, len(modul['egzersizler'])

    # --- 1. YAN PANEL (KILAVUZ & REKABET) ---
    with st.sidebar:
        st.markdown(f"### 🚀 {modul['modul_adi']}")
        st.info(modul.get('pito_anlatimi', 'Konu içeriği yükleniyor...'))
        st.divider()
        st.markdown("<div style='text-align:center; color:#00E5FF; font-weight:bold;'>🏆 ONUR KÜRSÜSÜ</div>", unsafe_allow_html=True)
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)

    # --- 2. ÜST PANEL (İLERLEME GÖSTERGELERİ) ---
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"<div class='kokpit-label'>🎓 AKADEMİ YOLCULUĞU (%{int((m_idx/total_m)*100)})</div>", unsafe_allow_html=True)
        st.progress(min((m_idx) / total_m, 1.0))
    with col_b:
        st.markdown(f"<div class='kokpit-label'>📍 MODÜL GÖREVİ ({c_i} / {t_i})</div>", unsafe_allow_html=True)
        st.progress(c_i / t_i)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 3. ANA ÇALIŞMA ALANI ---
    p_xp = max(0, 20 - (st.session_state.error_count * 5))
    p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
    
    cl, cr = st.columns([1, 4])
    with cl:
        emotions_module.pito_goster(p_mod)
    with cr:
        st.markdown(f"💎 **{p_xp} XP** | ⚠️ **Hata: {st.session_state.error_count}/4**")
        st.markdown(f"<div style='color:#00E5FF; font-style:italic;'>💬 {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)

    # Görev ve Editör Akışı
    if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
        st.markdown(f"### 🎯 GÖREV {egz['id']}")
        st.markdown(f"<div class='cyber-card'>{egz['yonerge']}</div>", unsafe_allow_html=True)

        # --- KRİTİK ALAN: HATA VE İPUCU PANELİ (EDİTÖR ÜZERİNDE) ---
        if st.session_state.error_count > 0:
            err_msg = random.choice(msgs['errors'][f'level_{min(st.session_state.error_count, 4)}']).format(ad_k)
            st.error(f"🚨 **Pito:** {err_msg}")
            
            if st.session_state.error_count == 3:
                st.warning(f"💡 **İPUCU:** {egz.get('ipucu', 'Kodu tekrar gözden geçir arkadaşım!')}")

        # Editör Alanı
        if "reset_trigger" not in st.session_state: st.session_state.reset_trigger = 0
        user_code = st.text_area("Siber-Editor", value=egz['sablon'], height=180, 
                                 key=f"final_ux_{egz['id']}_{st.session_state.reset_trigger}", label_visibility="collapsed")

        # Butonlar
        b_check, b_reset = st.columns([4, 1.5])
        with b_check:
            if st.button("KODU MÜHÜRLE 🚀", type="primary", use_container_width=True):
                st.session_state.current_code = user_code
                if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                    st.session_state.cevap_dogru = True
                else:
                    st.session_state.error_count += 1
                st.rerun()
        with b_reset:
            if st.button("🔄 SIFIRLA", type="secondary", use_container_width=True):
                st.session_state.reset_trigger += 1
                st.rerun()

    # --- 4. SONUÇ AKIŞLARI ---
    elif st.session_state.cevap_dogru:
        st.balloons()
        st.success(f"✅ Harika iş çıkardın {ad_k}! Bir sonraki göreve hazır mısın?")
        if st.button("DEVAM ET ➡️", type="primary", use_container_width=True):
            s_idx = modul['egzersizler'].index(egz) + 1
            n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
            ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)

    elif st.session_state.error_count >= 4:
        st.warning("🚨 Limit doldu! Pito'nun ideal çözümünü incele ve mantığını kavra:")
        st.code(egz['cozum'], language="python")
        if st.button("ÇÖZÜMÜ ANLADIM, DEVAM ET ➡️", type="primary", use_container_width=True):
            s_idx = modul['egzersizler'].index(egz) + 1
            n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
            ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)
