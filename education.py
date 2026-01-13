import streamlit as st
import random

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu):
    """Platformun ana eğitim ve görev akışını yönetir."""
    
    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    ad_k = u['ad_soyad'].split()[0]

    # --- ÜST İLERLEME ÇUBUKLARI ---
    st.markdown(f"<div class='progress-label'><span>🎓 Akademi Yolculuğu</span><span>Modül {m_idx + 1} / {total_m}</span></div>", unsafe_allow_html=True)
    st.progress(min((m_idx) / total_m, 1.0))

    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    c_i, t_i = modul['egzersizler'].index(egz) + 1, len(modul['egzersizler'])
    
    st.markdown(f"<div class='progress-label'><span>🗺️ Modül Görevleri</span><span>{c_i} / {t_i} Görev</span></div>", unsafe_allow_html=True)
    st.progress(c_i / t_i)

    # --- EĞİTİM ALANI ---
    cl, cr = st.columns([7, 3])
    with cl:
        # Hero Panel (Üst Bilgi)
        rn, rc = ranks_module.rütbe_ata(u['toplam_puan'])
        st.markdown(f"<div class='hero-panel'><h3>🚀 {modul['modul_adi']}</h3><p>{u['ad_soyad']} | <span class='rank-badge' style='background:black; color:#ADFF2F;'>{rn}</span></p></div>", unsafe_allow_html=True)
        
        # Konu Anlatımı
        with st.expander("📖 KONU ANLATIMI", expanded=True):
            st.markdown(f"<div style='background:#000; padding:15px; border-radius:10px;'>{modul.get('pito_anlatimi', '...')}</div>", unsafe_allow_html=True)
        
        # Puan Durumu
        p_xp = max(0, 20 - (st.session_state.error_count * 5))
        st.markdown(f'<div style="background:#161b22; padding:12px; border-radius:12px; border:1px solid #ADFF2F; color:#ADFF2F; font-weight:bold;">💎 {p_xp} XP | ⚠️ Hata: {st.session_state.error_count}/4</div>', unsafe_allow_html=True)
        
        # Pito Etkileşim
        p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
        cp1, cp2 = st.columns([1, 2])
        with cp1:
            emotions_module.pito_goster(p_mod)
        with cp2:
            if st.session_state.error_count > 0:
                lvl = f"level_{min(st.session_state.error_count, 4)}"
                msg = random.choice(msgs['errors'][lvl]).format(ad_k)
                st.error(f"🚨 Pito: {msg}")
                if st.session_state.error_count == 3:
                    st.warning(f"💡 İpucu: {egz['ipucu']}")
            else:
                st.markdown(f"<div class='pito-notu'>💬 <b>Pito:</b> {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)

        # --- ETKİLEŞİM VE KOD ALANI ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            st.markdown(f"<div class='gorev-box'><span class='gorev-label'>📍 GÖREV {egz['id']}</span><div class='gorev-text'>{egz['yonerge']}</div></div>", unsafe_allow_html=True)
            k_i = st.text_area("Pito Kod Editörü:", value=egz['sablon'], height=150)
            if st.button("Kodu Kontrol Et 🔍"):
                st.session_state.current_code = k_i
                if normalize_fonksiyonu(k_i) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                    st.session_state.cevap_dogru = True
                else:
                    st.session_state.error_count += 1
                st.rerun()
        elif st.session_state.cevap_dogru:
            st.success(f"✅ {random.choice(msgs['success']).format(ad_k, p_xp)}")
            st.markdown(f"<div class='console-box'>💻 Senin Çıktın:<br>> {egz['beklenen_cikti']}</div>", unsafe_allow_html=True)
            if st.button("Sonraki Göreve Geç ➡️"):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{u['mevcut_modul']+1}.1", u['mevcut_modul'] + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)
        elif st.session_state.error_count >= 4:
            with st.expander("📖 PİTO'NUN KESİN ÇÖZÜMÜ", expanded=True):
                st.code(egz['cozum'], language="python")
                st.markdown(f"<div class='console-box'>💻 Beklenen Çıktı:<br>> {egz['beklenen_cikti']}</div>", unsafe_allow_html=True)
            if st.button("Sıradaki Göreve Geç ➡️"):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{u['mevcut_modul']+1}.1", u['mevcut_modul'] + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)
    
    with cr:
        ranks_module.liderlik_tablosu_goster(st.session_state.supabase_client, current_user=u)