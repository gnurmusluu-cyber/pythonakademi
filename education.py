import streamlit as st
import random
import re

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    """Pito Mühürlü Editör: CSS enjekte edilmiş, korumalı iskelet sistemi."""
    
    # --- 0. SİBER-EDİTÖR CSS ZIRHI ---
    st.markdown("""
        <style>
        /* Textarea'yı gerçek bir siber-editör gibi göster */
        div[data-testid="stTextArea"] textarea {
            background-color: #0e1117 !important;
            color: #ADFF2F !important;
            font-family: 'Courier New', Courier, monospace !important;
            border: 1px solid #ADFF2F !important;
            border-radius: 10px !important;
            padding: 15px !important;
            line-height: 1.5 !important;
            selection-background-color: #ADFF2F !important;
        }
        /* Odaklandığında parlasın */
        div[data-testid="stTextArea"] textarea:focus {
            border-color: #ffffff !important;
            box-shadow: 0 0 10px #ADFF2F !important;
        }
        /* Widgetlar arası boşluğu daralt */
        [data-testid="stVerticalBlock"] > div {
            gap: 0.5rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    ad_k = u['ad_soyad'].split()[0]

    # --- 1. ÜST PANEL (İLERLEME) ---
    st.markdown(f"<div class='progress-label'><span>🎓 Akademi Yolculuğu</span><span>Modül {m_idx + 1} / {total_m}</span></div>", unsafe_allow_html=True)
    st.progress(min((m_idx) / total_m, 1.0))

    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    
    cl, cr = st.columns([7, 3])
    with cl:
        # Pito ve Durum Bilgisi
        p_xp = max(0, 20 - (st.session_state.error_count * 5))
        p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
        
        cp1, cp2 = st.columns([1, 3])
        with cp1: emotions_module.pito_goster(p_mod)
        with cp2:
            st.markdown(f"💎 **Bu Görev: {p_xp} XP** | ⚠️ **Hata: {st.session_state.error_count}/4**")
            if st.session_state.error_count > 0:
                lvl_key = f"level_{min(st.session_state.error_count, 4)}"
                st.error(f"🚨 Pito: {random.choice(msgs['errors'][lvl_key]).format(ad_k)}")
            else:
                st.markdown(f"<div class='pito-notu'>💬 <b>Pito:</b> {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)

        # --- 2. MUHAFIZ EDİTÖR ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            st.markdown(f"<div class='gorev-box'><span class='gorev-label'>📍 GÖREV {egz['id']}</span><div class='gorev-text'>{egz['yonerge']}</div></div>", unsafe_allow_html=True)
            
            # İskelet mühürlerini belirle
            skeletons = egz['sablon'].split("___")
            
            # Hafıza koruması
            if "guardian_code" not in st.session_state or st.session_state.get("last_egz_id") != egz['id']:
                st.session_state.guardian_code = egz['sablon']
                st.session_state.last_egz_id = egz['id']

            st.markdown("💻 **Mühürlü Kod Alanı:**")
            
            # CSS ile zırhlanmış tek blok editör
            user_input = st.text_area(
                "Pito Editor",
                value=st.session_state.guardian_code,
                height=220,
                key=f"pito_edit_{egz['id']}",
                label_visibility="collapsed"
            )

            # --- MÜHÜR KONTROLÜ ---
            is_broken = False
            for part in skeletons:
                if part not in user_input:
                    is_broken = True
                    break
            
            if is_broken:
                st.warning("⚠️ **Pito:** 'Dostum, mühürlü kısımları sildin! Kod iskeletini senin için hemen geri getirdim.'")
                st.session_state.guardian_code = egz['sablon'] 
                st.rerun()
            else:
                st.session_state.guardian_code = user_input

            st.write("---")
            if st.button("Sistemi Çalıştır ve Kontrol Et 🚀", use_container_width=True):
                st.session_state.current_code = user_input
                if normalize_fonksiyonu(user_input) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                    st.session_state.cevap_dogru = True
                else:
                    st.session_state.error_count += 1
                st.rerun()

        # --- 3. BAŞARI VE PES ETME ---
        elif st.session_state.cevap_dogru:
            st.success(f"✅ Harika iş çıkardın {ad_k}! XP'ler hanene yazıldı.")
            st.code(st.session_state.current_code, language="python")
            if st.button("Sonraki Göreve Geç ➡️", use_container_width=True):
                st.session_state.guardian_code = None
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)
        
        elif st.session_state.error_count >= 4:
            st.warning("🚨 Çok zorlandın ama sorun değil. Pito'nun çözümünü inceleyebilirsin!")
            st.code(egz['cozum'], language="python")
            if st.button("Sıradaki Göreve Geç ➡️", use_container_width=True):
                st.session_state.guardian_code = None
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
