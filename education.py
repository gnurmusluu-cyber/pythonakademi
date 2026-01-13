import streamlit as st
import streamlit.components.v1 as components
import random
import json

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    """Siber-Buz Akıllı Akış Editörü: Yazdıkça genişleyen inline girişler."""
    
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

        # --- 2. AKILLI AKIŞ EDİTÖRÜ (INLINE) ---
        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            st.markdown(f"<div class='gorev-box'><span class='gorev-label'>📍 GÖREV {egz['id']}</span><div class='gorev-text'>{egz['yonerge']}</div></div>", unsafe_allow_html=True)
            
            sablon = egz.get('sablon', '')
            parcalar = sablon.split("___")
            
            # HTML ve JavaScript ile Akıllı Editörü Oluşturuyoruz
            html_content = f"""
            <style>
                .editor-container {{
                    background: #0e1117;
                    color: #ADFF2F;
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid #ADFF2F;
                    font-family: 'Courier New', monospace;
                    font-size: 16px;
                    line-height: 2;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }}
                .inline-input {{
                    background: transparent;
                    border: none;
                    border-bottom: 2px dashed #ADFF2F;
                    color: #ffffff;
                    font-family: 'Courier New', monospace;
                    font-size: 16px;
                    padding: 0 5px;
                    min-width: 35px;
                    width: 35px;
                    outline: none;
                    transition: width 0.1s;
                }}
                .inline-input:focus {{
                    border-bottom: 2px solid #ffffff;
                }}
                .check-btn {{
                    background: #ADFF2F;
                    color: #000;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                    cursor: pointer;
                    margin-top: 20px;
                    width: 100%;
                }}
            </style>
            <div class="editor-container" id="editor">
            """

            for i, parca in enumerate(parcalar):
                html_content += f"<span>{parca}</span>"
                if i < len(parcalar) - 1:
                    html_content += f'<input type="text" class="inline-input" id="inp_{i}" placeholder="___" oninput="autoWidth(this)">'
            
            html_content += f"""
            </div>
            <button class="check-btn" onclick="submitCode()">Kodu Sisteme Gönder 🚀</button>

            <script>
                function autoWidth(el) {{
                    el.style.width = ((el.value.length + 3) * 10) + "px";
                }}
                
                function submitCode() {{
                    let finalCode = "";
                    const parcalar = {json.dumps(parcalar)};
                    for(let i=0; i < parcalar.length; i++) {{
                        finalCode += parcalar[i];
                        if(i < parcalar.length - 1) {{
                            finalCode += document.getElementById("inp_" + i).value;
                        }}
                    }}
                    // Streamlit'e veriyi gönder
                    const data = {{ "type": "pito_code", "code": finalCode }};
                    window.parent.postMessage({{ isStreamlitMessage: true, type: "streamlit:setComponentValue", value: data }}, "*");
                }}
            </script>
            """

            # HTML Bileşenini Render Et
            # components.html'den gelen veriyi yakalamak için st_js_connection benzeri bir mantık kullanılır.
            # Şimdilik en stabil yol: Bileşen değerini 'st.session_state' üzerinden kontrol etmek.
            response = components.html(html_content, height=400, scrolling=True)

            # Not: Veri yakalama için ana dosyada bir 'listener' olması gerekir.
            # Basitlik için manuel kontrol butonu (Streamlit native) ekleyelim:
            st.info("💡 Yukarıdaki 'Sisteme Gönder' butonuna bastıktan sonra aşağıdaki kontrolü onayla.")
            if st.button("Pito, Kodumu Kontrol Et! 🔍", use_container_width=True):
                # Bu kısım JS'den gelen 'finalCode'u session_state üzerinden okur
                # (Custom component geliştirme aşamasında olduğumuz için şimdilik text_area simülasyonu)
                if st.session_state.get('current_code'):
                    if normalize_fonksiyonu(st.session_state.current_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                        st.session_state.cevap_dogru = True
                    else:
                        st.session_state.error_count += 1
                    st.rerun()

        # --- BAŞARI VE HATA ---
        elif st.session_state.cevap_dogru:
            st.success(f"✅ Harika! Kod tam istediğim gibi akıyor {ad_k}.")
            st.code(st.session_state.current_code, language="python")
            if st.button("Sonraki Göreve Geç ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)
