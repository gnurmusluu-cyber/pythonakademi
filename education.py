import streamlit as st
import streamlit.components.v1 as components
import json
import random

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    """Siber-Mühürlü Akış Editörü: İskelet silinemez, boşluklar yazdıkça genişler."""
    
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

        # --- 2. SİBER-MÜHÜRLÜ AKIŞ EDİTÖRÜ ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            st.markdown(f"<div class='gorev-box'><span class='gorev-label'>📍 GÖREV {egz['id']}</span><div class='gorev-text'>{egz['yonerge']}</div></div>", unsafe_allow_html=True)
            
            sablon = egz.get('sablon', '')
            parcalar = sablon.split("___")
            
            # HTML/JS Zırhlı Editör
            # Yazdıkça genişleyen (auto-width) ve silinemeyen iskelet yapısı
            html_content = f"""
            <style>
                #pito-armor-box {{
                    background: #0e1117;
                    color: #ADFF2F;
                    padding: 25px;
                    border: 1px solid #ADFF2F;
                    border-radius: 12px;
                    font-family: 'Courier New', monospace;
                    font-size: 18px;
                    line-height: 1.8;
                    cursor: text;
                }}
                .fixed-code {{
                    color: #888;
                    user-select: none; /* Seçilemez */
                    -webkit-user-select: none;
                }}
                .editable-blank {{
                    background: rgba(173, 255, 47, 0.1);
                    border: none;
                    border-bottom: 2px dashed #ADFF2F;
                    color: #ffffff;
                    font-family: inherit;
                    font-size: inherit;
                    min-width: 40px;
                    width: 40px;
                    outline: none;
                    padding: 0 4px;
                    transition: width 0.1s ease;
                    text-align: center;
                }}
                .editable-blank:focus {{
                    border-bottom: 2px solid #ffffff;
                    background: rgba(255, 255, 255, 0.1);
                }}
            </style>

            <div id="pito-armor-box">
            """
            
            for i, p in enumerate(parcalar):
                html_content += f'<span class="fixed-code">{p}</span>'
                if i < len(parcalar) - 1:
                    html_content += f'<input type="text" class="editable-blank" id="blank_{i}" placeholder="..." oninput="resizer(this)">'
            
            html_content += f"""
            </div>
            <script>
                function resizer(el) {{
                    el.style.width = ((el.value.length + 1) * 11) + "px";
                    
                    // Veriyi gizli bir köprü üzerinden Streamlit'e gönder
                    const allInputs = document.querySelectorAll('.editable-blank');
                    let final = "";
                    const parts = {json.dumps(parcalar)};
                    for(let i=0; i<parts.length; i++) {{
                        final += parts[i];
                        if(i < allInputs.length) final += allInputs[i].value;
                    }}
                    // Streamlit Bridge
                    window.parent.postMessage({{
                        isStreamlitMessage: true,
                        type: "streamlit:setComponentValue",
                        value: final
                    }}, "*");
                }}
            </script>
            """

            # Bileşeni ekrana bas (Değeri 'user_code' değişkenine aktarır)
            st.markdown("💻 **Pito Akıllı Editör:**")
            user_code = components.html(html_content, height=300)

            # --- KONTROL MEKANİZMASI ---
            st.write("---")
            if st.button("Kodu Çalıştır ve Kontrol Et 🚀", use_container_width=True):
                # 'user_code' bileşenden gelen nihai mühürlü metindir
                if user_code:
                    st.session_state.current_code = user_code
                    if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru = True
                    else:
                        st.session_state.error_count += 1
                    st.rerun()
                else:
                    st.warning("Pito: 'Henüz bir şey yazmadın arkadaşım!'")

        # --- 3. BAŞARI / HATA DURUMLARI ---
        elif st.session_state.cevap_dogru:
            st.success(f"✅ Harika iş çıkardın {ad_k}! Kodun siber-onay aldı.")
            st.code(st.session_state.current_code, language="python")
            if st.button("Sonraki Göreve Geç ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)
        
        elif st.session_state.error_count >= 4:
            st.warning("🚨 Çok zorlandın, ama sorun değil. İşte Pito'nun ideal çözümü:")
            st.code(egz['cozum'], language="python")
            if st.button("Sıradaki Göreve Geç ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
