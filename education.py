import streamlit as st
import random

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    """Bütünlüğü korunmuş, satır içi gömülü editör motoru."""
    
    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    ad_k = u['ad_soyad'].split()[0]

    # --- ÜST PANEL ---
    st.markdown(f"<div class='progress-label'><span>🎓 Akademi</span><span>Modül {m_idx + 1} / {total_m}</span></div>", unsafe_allow_html=True)
    st.progress(min((m_idx) / total_m, 1.0))

    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    
    cl, cr = st.columns([7, 3])
    with cl:
        # Pito ve Bilgi Kartı
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

        # --- BÜTÜNLEŞİK SATIR İÇİ EDİTÖR ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            st.markdown(f"<div class='gorev-box'><span class='gorev-label'>📍 GÖREV {egz['id']}</span><div class='gorev-text'>{egz['yonerge']}</div></div>", unsafe_allow_html=True)
            
            st.markdown("💻 **Pito Bütünleşik Editör (Boşlukları Tamamla):**")
            
            sablon_satirlari = egz.get('sablon', '').split('\n')
            final_cevaplar = {}

            # Her satırı tek tek işliyoruz
            for s_idx, satir in enumerate(sablon_satirlari):
                if "___" in satir:
                    # Satırı boşluklardan parçala
                    parcalar = satir.split("___")
                    cols = st.columns([len(p) if len(p) > 0 else 5 for p in parcalar] + [10] * (len(parcalar)-1))
                    
                    satir_cevaplari = []
                    col_idx = 0
                    for p_idx, parca in enumerate(parcalar):
                        # Sabit parça
                        if parca:
                            cols[col_idx].markdown(f"```python\n{parca}\n```")
                        col_idx += 1
                        
                        # Giriş kutusu (Eğer son parça değilse)
                        if p_idx < len(parcalar) - 1:
                            ans = cols[col_idx].text_input(
                                f"L{s_idx}B{p_idx}", 
                                key=f"input_{egz['id']}_{s_idx}_{p_idx}",
                                label_visibility="collapsed",
                                placeholder="?"
                            )
                            satir_cevaplari.append(ans)
                            col_idx += 1
                    final_cevaplar[s_idx] = satir_cevaplari
                else:
                    # İçinde boşluk olmayan satırı olduğu gibi, bütün halde göster
                    st.code(satir if satir.strip() else " ", language="python")

            st.write("---")
            if st.button("Kodu Çalıştır ⚡", use_container_width=True):
                # Kod parçalarını öğrenci girdileriyle birleştir
                olusan_kod_satirlari = []
                for s_idx, satir in enumerate(sablon_satirlari):
                    if s_idx in final_cevaplar:
                        parcalar = satir.split("___")
                        yeni_satir = ""
                        for i in range(len(final_cevaplar[s_idx])):
                            yeni_satir += parcalar[i] + final_cevaplar[s_idx][i]
                        yeni_satir += parcalar[-1]
                        olusan_kod_satirlari.append(yeni_satir)
                    else:
                        olusan_kod_satirlari.append(satir)
                
                final_code = "\n".join(olusan_kod_satirlari)
                st.session_state.current_code = final_code
                
                if normalize_fonksiyonu(final_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                    st.session_state.cevap_dogru = True
                else:
                    st.session_state.error_count += 1
                st.rerun()

        # Başarı ve Hata durumları (Mevcut yapı korunur)
        elif st.session_state.cevap_dogru:
            st.success(f"✅ Harika! Kod başarıyla çalıştırıldı.")
            st.code(st.session_state.current_code, language="python")
            if st.button("Sonraki Göreve Geç ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)
        
        elif st.session_state.error_count >= 4:
            st.warning("🚨 Pito: 'Bu seferlik ben yardım edeyim, işte doğru çözüm!'")
            st.code(egz['cozum'], language="python")
            if st.button("Sıradaki Göreve Geç ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
