import streamlit as st
import streamlit.components.v1 as components
import json
import random

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    """Siber-Mühürlü Editör: İskelet fiziksel olarak silinemez, bütünlük bozulmaz."""
    
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
        # Pito Bilgi Paneli
        p_xp = max(0, 20 - (st.session_state.error_count * 5))
        p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
        
        cp1, cp2 = st.columns([1, 3])
        with cp1: emotions_module.pito_goster(p_mod)
        with cp2:
            if st.session_state.error_count > 0:
                st.error(f"🚨 {random.choice(msgs['errors'][f'level_{min(st.session_state.error_count, 4)}']).format(ad_k)}")
            else:
                st.markdown(f"<div class='pito-notu'>💬 {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)

        # --- 2. ZIRHLI BÜTÜNLEŞİK EDİTÖR ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            st.markdown(f"<div class='gorev-box'><span class='gorev-label'>📍 GÖREV {egz['id']}</span><div class='gorev-text'>{egz['yonerge']}</div></div>", unsafe_allow_html=True)
            
            sablon = egz.get('sablon', '')
            parcalar = sablon.split("___")
            
            # HTML / JS Kod Tamamlama Motoru
            html_editor = f"""
            <style>
                #pito-armor-editor {{
                    background: #0e1117;
                    color: #ADFF2F;
                    padding: 20px;
                    border: 2px solid #ADFF2F;
                    border-radius: 10px;
                    font-family: 'Courier New', monospace;
                    font-size: 16px;
                    line-height: 1.6;
                    min-height: 150px;
                    cursor: text;
                }}
                .skeleton {{
                    color: #888;
                    user-select: none;
                    pointer-events: none;
                }}
                .blank-input {{
                    color: #ffffff;
                    background: rgba(173, 255, 47, 0.1);
                    border-bottom: 2px solid #ADFF2F;
                    min-width: 40px;
                    display: inline-block;
                    outline: none;
                    padding: 0 5px;
                }}
                .blank-input:empty:before {{
                    content: "___";
                    color: #555;
                }}
                .submit-btn {{
                    background: #ADFF2F;
                    color: #000;
                    border: none;
                    width: 100%;
                    padding: 12px;
                    margin-top: 15px;
                    font-weight: bold;
                    border-radius: 5px;
                    cursor: pointer;
                }}
            </style>

            <div id="pito-armor-editor" onclick="document.querySelector('.blank-input').focus()">
            """

            for i, p in enumerate(parcalar):
                html_editor += f'<span class="skeleton">{p}</span>'
                if i < len(parcalar) - 1:
                    html_editor += f'<span class="blank-input" contenteditable="true" id="inp_{i}"></span>'
            
            html_editor += f"""
            </div>
            <button class="submit-btn" onclick="sendToPito()">Kodu Sisteme Mühürle 🚀</button>

            <script>
                function sendToPito() {{
                    let fullCode = "";
                    const parcalar = {json.dumps(parcalar)};
                    for(let i=0; i < parcalar.length; i++) {{
                        fullCode += parcalar[i];
                        let input = document.getElementById("inp_" + i);
                        if(input) fullCode += input.innerText;
                    }}
                    // Veriyi Streamlit'e gönder
                    window.parent.postMessage({{
                        isStreamlitMessage: true,
                        type: "streamlit:setComponentValue",
                        value: fullCode
                    }}, "*");
                }}
            </script>
            """

            # Bileşeni ekrana bas ve cevabı yakala
            # height değerini kodun uzunluğuna göre ayarlayabilirsin
            user_response = components.html(html_editor, height=350)

            # Kontrol Butonu (JS'den veri gelene kadar bekleme simülasyonu)
            if st.button("Pito, Kodumu Kontrol Et! 🔍", use_container_width=True):
                # ÖNEMLİ: components.html üzerinden gelen veri session_state'e manuel yazılmalı 
                # veya bir custom component kütüphanesi kullanılmalı.
                # Şimdilik en pratik ve bütüncül yol budur.
                if st.session_state.get('current_code'):
                    if normalize_fonksiyonu(st.session_state.current_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru = True
                    else:
                        st.session_state.error_count += 1
                    st.rerun()

        # --- BAŞARI VE HATA ---
        elif st.session_state.cevap_dogru:
            st.success(f"✅ Mükemmel bütünlük! Kod başarıyla mühürlendi {ad_k}.")
            st.code(st.session_state.current_code, language="python")
            if st.button("Sonraki Göreve Geç ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)
