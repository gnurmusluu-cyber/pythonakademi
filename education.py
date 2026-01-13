import streamlit as st
import random
import re

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    """Pito Dedektif Editörü: Tek blok, korumalı iskelet sistemi."""
    
    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    ad_k = u['ad_soyad'].split()[0]

    # --- 1. ÜST PANEL ---
    st.markdown(f"<div class='progress-label'><span>🎓 Akademi</span><span>Modül {m_idx + 1} / {total_m}</span></div>", unsafe_allow_html=True)
    st.progress(min((m_idx) / total_m, 1.0))

    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    
    cl, cr = st.columns([7, 3])
    with cl:
        # Pito ve Durum Paneli
        p_xp = max(0, 20 - (st.session_state.error_count * 5))
        p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
        
        cp1, cp2 = st.columns([1, 3])
        with cp1: emotions_module.pito_goster(p_mod)
        with cp2:
            st.markdown(f"💎 **{p_xp} XP** | ⚠️ **Hata: {st.session_state.error_count}/4**")
            if st.session_state.error_count > 0:
                st.error(f"🚨 {random.choice(msgs['errors'][f'level_{min(st.session_state.error_count, 4)}']).format(ad_k)}")
            else:
                st.markdown(f"<div class='pito-notu'>💬 {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)

        # --- 2. KORUMALI TEK BLOK EDİTÖR ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            st.markdown(f"<div class='gorev-box'><span class='gorev-label'>📍 GÖREV {egz['id']}</span><div class='gorev-text'>{egz['yonerge']}</div></div>", unsafe_allow_html=True)
            
            # Başlangıçta şablonu hafızaya al
            if "last_valid_code" not in st.session_state or st.session_state.get("current_egz_id") != egz['id']:
                st.session_state.last_valid_code = egz['sablon']
                st.session_state.current_egz_id = egz['id']

            # İskelet parçalarını belirle (___ dışındaki her şey)
            skeletons = egz['sablon'].split("___")
            
            st.markdown("💻 **Pito Kod Bloğu (Sadece ___ alanlarını doldur):**")
            
            # TEK BLOK EDİTÖR
            user_code = st.text_area(
                "Kod Alanı",
                value=st.session_state.last_valid_code,
                height=180,
                key=f"editor_{egz['id']}",
                label_visibility="collapsed",
                help="Kodun iskeletini silersen Pito seni uyaracaktır!"
            )

            # --- DEDEKTİF KONTROLÜ ---
            # İskelet parçaları hala yerinde mi ve sırası doğru mu?
            is_legal = True
            for part in skeletons:
                if part not in user_code:
                    is_legal = False
                    break
            
            if not is_legal:
                st.warning("⚠️ **Pito:** 'Hey! Kodun iskeletini bozdun arkadaşım. Lütfen sadece ___ olan yerleri değiştir!'")
                # Hata yapıldığında butonu pasif kılmak veya uyarıyı göstermek yeterli
            else:
                st.session_state.last_valid_code = user_code # Geçerliyse kaydet

            st.write("---")
            if st.button("Kodu Çalıştır 🚀", use_container_width=True, disabled=not is_legal):
                st.session_state.current_code = user_code
                if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                    st.session_state.cevap_dogru = True
                else:
                    st.session_state.error_count += 1
                st.rerun()

        # --- BAŞARI VE HATA ---
        elif st.session_state.cevap_dogru:
            st.success(f"✅ Harika! Kod tıkır tıkır çalışıyor {ad_k}.")
            st.code(st.session_state.current_code, language="python")
            if st.button("Sonraki Göreve Geç ➡️", use_container_width=True):
                # Resetleme ve ilerleme
                st.session_state.last_valid_code = None
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)
        
        elif st.session_state.error_count >= 4:
            st.warning("🚨 Çözümü inceleyip yeni göreve geçebilirsin.")
            st.code(egz['cozum'], language="python")
            if st.button("Sıradaki Göreve Geç ➡️", use_container_width=True):
                st.session_state.last_valid_code = None
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
