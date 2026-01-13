import streamlit as st
import random

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- 0. SİBER-BUZ (ICE-BLUE) UX CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; }
        .kokpit-label { color: #00E5FF; font-family: 'Fira Code', monospace; font-size: 0.85rem; font-weight: bold; }
        .stProgress > div > div > div > div { background-image: linear-gradient(to right, #00B8D4, #00E5FF) !important; }
        
        /* Modern Kart ve Vurgular */
        .cyber-card {
            background: rgba(0, 229, 255, 0.03);
            border: 1px solid rgba(0, 229, 255, 0.2);
            border-radius: 12px;
            padding: 15px; margin-bottom: 10px;
        }

        /* Sıfırla Butonu Tasarımı */
        .stButton > button[kind="secondary"] {
            border: 1px solid #00E5FF !important;
            color: #00E5FF !important;
            background: rgba(0, 229, 255, 0.05) !important;
            border-radius: 8px !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    ad_k = u['ad_soyad'].split()[0]
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    c_i, t_i = modul['egzersizler'].index(egz) + 1, len(modul['egzersizler'])

    # --- 1. YAN PANEL (BİLGİ & REKABET) ---
    with st.sidebar:
        st.markdown(f"### 🚀 {modul['modul_adi']}")
        st.info(modul.get('pito_anlatimi', '...'))
        st.divider()
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)

    # --- 2. ÜST GÖSTERGE PANELİ ---
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='kokpit-label'>🎓 AKADEMİ YOLCULUĞU (%{int((m_idx/total_m)*100)})</div>", unsafe_allow_html=True)
        st.progress(min((m_idx) / total_m, 1.0))
    with c2:
        st.markdown(f"<div class='kokpit-label'>🗺️ MODÜL GÖREVİ ({c_i} / {t_i})</div>", unsafe_allow_html=True)
        st.progress(c_i / t_i)

    st.markdown("---")

    # --- 3. ANA ÇALIŞMA ALANI ---
    p_xp = max(0, 20 - (st.session_state.error_count * 5))
    p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
    
    col_pito, col_main = st.columns([1, 4])
    with col_pito:
        emotions_module.pito_goster(p_mod)
    
    with col_main:
        st.markdown(f"💎 **{p_xp} XP** | ⚠️ **Hata: {st.session_state.error_count}/4**")
        
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            st.markdown(f"<div class='cyber-card'><b>GÖREV:</b> {egz['yonerge']}</div>", unsafe_allow_html=True)

            # --- KRİTİK UX: HATA VE İPUCU PANELİ (EDİTÖR ÜZERİNDE) ---
            if st.session_state.error_count > 0:
                err_lvl = f"level_{min(st.session_state.error_count, 4)}"
                st.error(f"🚨 **Pito:** {random.choice(msgs['errors'][err_lvl]).format(ad_k)}")
                
                # 3. Hata İpucu Garantisi
                if st.session_state.error_count == 3:
                    st.warning(f"💡 **İPUCU:** {egz.get('ipucu', 'Kodu tekrar gözden geçir!')}")

            # --- EDİTÖR ---
            if "reset_trigger" not in st.session_state: st.session_state.reset_trigger = 0
            
            user_code = st.text_area("Editor", value=egz['sablon'], height=180, 
                                     key=f"ux_ed_{egz['id']}_{st.session_state.reset_trigger}", label_visibility="collapsed")

            b_run, b_res = st.columns([4, 1.2])
            with b_run:
                if st.button("KODU KONTROL ET 🚀", use_container_width=True):
                    st.session_state.current_code = user_code
                    if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru = True
                    else:
                        st.session_state.error_count += 1
                    st.rerun()
            with b_res:
                if st.button("🔄 SIFIRLA", type="secondary", use_container_width=True, help="Kodu ilk haline döndür"):
                    st.session_state.reset_trigger += 1
                    st.rerun()

        # BAŞARI VE KESİN ÇÖZÜM AKIŞI
        elif st.session_state.cevap_dogru:
            st.success(f"✅ Harika! {p_xp} XP kazandın.")
            if st.button("SONRAKİ GÖREVE GEÇ ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)

        elif st.session_state.error_count >= 4:
            st.warning("🚨 Pito'nun Çözümü:")
            st.code(egz['cozum'], language="python")
            if st.button("ANLADIM, DEVAM ET ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)
