import streamlit as st
import streamlit.components.v1 as components
import json
import random

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    """Siber-Buz Entegre Editör: Fiziksel koruma, akışkan genişleme ve çalışan butonlar."""
    
    m_idx = int(u['mevcut_modul']) - 1
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    ad_k = u['ad_soyad'].split()[0]

    # --- ÜST PANEL ---
    st.markdown(f"<div class='progress-label'><span>🎓 Akademi Yolculuğu</span><span>Modül {m_idx + 1}</span></div>", unsafe_allow_html=True)
    st.progress(min((m_idx) / len(mufredat), 1.0))

    cl, cr = st.columns([7, 3])
    with cl:
        # Pito Bilgi Kartı
        p_xp = max(0, 20 - (st.session_state.error_count * 5))
        p_mod = emotions_module.pito_durum_belirle(st.session_state.error_count, st.session_state.cevap_dogru)
        
        cp1, cp2 = st.columns([1, 3])
        with cp1: emotions_module.pito_goster(p_mod)
        with cp2:
            st.markdown(f"💎 **{p_xp} XP** | ⚠️ **Hata: {st.session_state.error_count}/4**")
            if st.session_state.error_count > 0:
                st.error(f"🚨 Pito: {random.choice(msgs['errors'][f'level_{min(st.session_state.error_count, 4)}']).format(ad_k)}")
            else:
                st.markdown(f"<div class='pito-notu'>💬 {msgs['welcome'].format(ad_k)}</div>", unsafe_allow_html=True)

        if not st.session_state.cevap_dogru and st.session_state.error_count < 4:
            st.markdown(f"<div class='gorev-box'><span class='gorev-label'>📍 GÖREV {egz['id']}</span><div class='gorev-text'>{egz['yonerge']}</div></div>", unsafe_allow_html=True)

            # --- SİBER-BUZ ENTEGRE EDİTÖR (HTML/JS) ---
            sablon = egz.get('sablon', '')
            parcalar = sablon.split("___")
            dogru_kod = normalize_fonksiyonu(egz['dogru_cevap_kodu'])

            html_code = f"""
            <div id="editor-container" style="background:#0e1117; color:#ADFF2F; padding:20px; border:2px solid #ADFF2F; border-radius:10px; font-family:'Courier New', monospace; font-size:16px; line-height:1.8;">
                <div id="pito-logic-editor" style="white-space: pre-wrap; word-wrap: break-word;">
            """
            
            for i, p in enumerate(parcalar):
                html_code += f'<span style="color:#888; user-select:none;">{p}</span>'
                if i < len(parcalar) - 1:
                    html_code += f'<input type="text" id="inp_{i}" oninput="this.style.width = ((this.value.length + 1) * 10) + \'px\'" style="background:rgba(173,255,47,0.1); border:none; border-bottom:2px dashed #ADFF2F; color:#fff; font-family:inherit; font-size:inherit; width:35px; outline:none; text-align:center; transition: width 0.1s;">'
            
            html_code += f"""
                </div>
                <button id="check-btn" style="width:100%; margin-top:20px; background:#ADFF2F; color:#000; border:none; padding:12px; font-weight:bold; border-radius:5px; cursor:pointer; font-family:sans-serif;">KODU KONTROL ET 🔍</button>
            </div>

            <script>
                const btn = document.getElementById('check-btn');
                const parcalar = {json.dumps(parcalar)};
                const dogruNorm = "{dogru_kod}";

                btn.onclick = function() {{
                    let finalCode = "";
                    for(let i=0; i < parcalar.length; i++) {{
                        finalCode += parcalar[i];
                        let inp = document.getElementById("inp_" + i);
                        if(inp) finalCode += inp.value;
                    }}
                    
                    // Normalizasyon ve Karşılaştırma
                    let userNorm = finalCode.replace(/\s+/g, '').toLowerCase();
                    
                    // Streamlit'e sonucu gönder
                    window.parent.postMessage({{
                        isStreamlitMessage: true,
                        type: "streamlit:setComponentValue",
                        value: {{ "status": userNorm === dogruNorm, "code": finalCode }}
                    }}, "*");
                }};
            </script>
            """

            # Bileşeni göster ve sonucu yakala
            # Not: height değeri kodun satır sayısına göre dinamik ayarlanabilir
            result = components.html(html_code, height=300)

            # Streamlit butonuna gerek kalmadı, JS'den gelen veriyi st.session_state'e aktaracak bir köprü kurmalıyız.
            # Ancak standart components.html'de veri yakalamak için 'result' değişkeni kullanılır.
            # Eğer veri geldiyse (result boş değilse) işlemi yap:
            if result:
                # Bazı Streamlit sürümlerinde result doğrudan dict döner
                if result.get("status"):
                    st.session_state.cevap_dogru = True
                    st.session_state.current_code = result.get("code")
                    st.rerun()
                else:
                    st.session_state.error_count += 1
                    st.rerun()

        # --- BAŞARI VE HATA EKRANLARI ---
        elif st.session_state.cevap_dogru:
            st.success(f"✅ Harika iş çıkardın {ad_k}!")
            st.code(st.session_state.current_code, language="python")
            if st.button("Sonraki Göreve Geç ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)
        
        elif st.session_state.error_count >= 4:
            st.warning("🚨 Çözümü inceleyip bir sonraki göreve geçebilirsin.")
            st.code(egz['cozum'], language="python")
            if st.button("Sıradaki Göreve Geç ➡️", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
