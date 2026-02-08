import streamlit as st
import random
import os
import base64
import pandas as pd
import sys as system_sys
import io
import html
import datetime

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- 1. VERİ YAPISI ---
    if isinstance(mufredat, dict) and "pito_akademi_mufredat" in mufredat:
        m_list = mufredat["pito_akademi_mufredat"]
    else:
        m_list = mufredat

    try:
        m_idx = int(u['mevcut_modul']) - 1
        modul = m_list[m_idx]
        egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    except:
        st.error("🚨 Veri Okuma Hatası!")
        return

    e_count = st.session_state.get('error_count', 0)
    if "anim_nonce" not in st.session_state: st.session_state.anim_nonce = 0

    # --- KOD ÇIKTISINI YAKALAMA MOTORU ---
    def kod_calistir_cikti_al(kod, giris_verisi=''):
        buffer = io.StringIO()
        old_stdout = system_sys.stdout
        system_sys.stdout = buffer
        def mock_input(prompt=''): return str(giris_verisi)
        exec_scope = {'__builtins__': __builtins__, 'input': mock_input}
        try:
            exec(kod, exec_scope)
            res = buffer.getvalue().strip()
            return res 
        except Exception as e:
            return f'⚠️ SİSTEM HATASI: {str(e)}'
        finally:
            system_sys.stdout = old_stdout

    # --- 0. SİBER-GÖRSEL TASARIM (YERLEŞİM MÜHÜRLERİ) ---
    st.markdown(f'''
        <style>
        header[data-testid="stHeader"], [data-testid="stDecoration"], footer {{ display: none !important; }}
        .stApp {{ background-color: #0e1117 !important; }}
        
        /* 🚨 KRİTİK DÜZELTME: İçeriği HUD panelinin tamamen altına, görünür bölgeye iter */
        [data-testid="stMainViewContainer"] {{ 
            padding-top: 220px !important; 
        }}

        /* HUD PANELİ */
        .cyber-hud {{
            position: fixed; top: 0; left: 0; right: 0; height: 140px;
            background-color: #0e1117 !important; border-bottom: 3px solid #00E5FF;
            z-index: 1000 !important; padding: 0 40px; display: flex;
            justify-content: space-between; align-items: center; box-shadow: 0 10px 40px #000;
        }}

        .hud-pito-gif img {{ width: 70px !important; height: 70px !important; border-radius: 50%; border: 2px solid #00E5FF; object-fit: cover; }}
        .hud-progress-container {{ flex-grow: 1; margin: 0 40px; max-width: 400px; }}
        .progress-label {{ color: #00E5FF; font-size: 0.65rem; font-family: monospace; text-transform: uppercase; margin-bottom: 2px; display: block; }}
        
        @keyframes cyber-shake {{ 0% {{ transform: translate(1px, 1px); }} 50% {{ transform: translate(-2px, -1px); }} 100% {{ transform: translate(0, 0); }} }}
        .hud-shake {{ animation: cyber-shake 0.3s ease-in-out; }}
        
        .gorev-box-html {{ background: rgba(0, 229, 255, 0.05); border-left: 5px solid #00E5FF; padding: 15px; border-radius: 8px; color: #E0E0E0; margin-bottom: 10px; }}
        .cyber-terminal {{ background-color: #000; color: #ADFF2F; padding: 15px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 20px; font-family: monospace; }}
        
        /* 🚨 BUTONLARIN PANELİN ALTINDA KALMASINI ENGELLER */
        .stButton button {{ z-index: 10 !important; }}
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. HUD RENDER ---
    rn, rc = ranks_module.rütbe_ata(u['toplam_puan'])
    p_xp = max(0, 20 - (e_count * 5))
    p_mod = emotions_module.pito_durum_belirle(e_count, st.session_state.cevap_dogru)
    total_m = len(m_list)
    total_e = len(modul['egzersizler'])
    curr_e_idx = modul['egzersizler'].index(egz) + 1
    
    shake_class = "hud-shake" if st.session_state.anim_nonce > 0 else ""
    error_color = "#FF4B4B" if e_count > 0 else "#00E5FF"
    if st.session_state.cevap_dogru: error_color = "#ADFF2F"

    def get_gif_b64(mod):
        path = os.path.join(os.path.dirname(__file__), 'assets', f'pito_{mod}.gif')
        return f'data:image/gif;base64,{base64.b64encode(open(path, "rb").read()).decode()}' if os.path.exists(path) else ''

    st.markdown(f'''
        <div class="cyber-hud">
            <div style="display: flex; align-items: center;">
                <div class="hud-pito-gif"><img src="{get_gif_b64(p_mod)}"></div>
                <div style="color: #E0E0E0; font-family: monospace; margin-left:12px; font-size: 0.8rem;">👤 <b>{u['ad_soyad'][:10]}..</b><br><span style="color:#ADFF2F;">{rn}</span></div>
            </div>
            <div class="hud-progress-container">
                <span class="progress-label">AKADEMİ: {u['mevcut_modul']}/{total_m}</span>
                <div style="width:100%; background:rgba(255,255,255,0.1); height:4px; border-radius:2px; margin-bottom:8px;">
                    <div style="width:{(int(u['mevcut_modul'])/total_m)*100}%; background:#00E5FF; height:100%; border-radius:2px;"></div>
                </div>
                <span class="progress-label">GÖREV: {curr_e_idx}/{total_e}</span>
                <div style="width:100%; background:rgba(255,255,255,0.1); height:4px; border-radius:2px;">
                    <div style="width:{(curr_e_idx/total_e)*100}%; background:#ADFF2F; height:100%; border-radius:2px;"></div>
                </div>
            </div>
            <div class="hud-stats-container" style="display:flex; gap:10px;">
                <div class="hud-capsule" style="color:#00E5FF;">💎 <span class="{shake_class}">{p_xp}</span></div>
                <div class="hud-capsule" style="color:{error_color};">⚠️ <span class="{shake_class}">{e_count}/4</span></div>
                <div class="hud-capsule" style="color:#ADFF2F; border-color:#ADFF2F;">🏆 <span class="{'success-pulse' if st.session_state.cevap_dogru else ''}">{u['toplam_puan']}</span></div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    # --- 2. ANA PANEL (NAVİGASYON VE İÇERİK) ---
    cl, cr = st.columns([7.2, 2.8])
    with cl:
        # NAVİGASYON (Görünürlüğü mühürlendi!)
        nav1, nav2, nav3 = st.columns([0.4, 0.4, 0.2])
        with nav1: st.markdown(f"💬 *{msgs['welcome'].format(u['ad_soyad'].split()[0])}*")
        with nav2: 
            if st.button("🔍 Geçmiş Egzersizler", key="btn_review"): st.session_state.in_review = True; st.rerun()
        with nav3:
            if st.button("🚪 Çıkış", key="btn_exit"): st.session_state.user = None; st.rerun()

        # KONU VE GÖREV
        with st.expander(f"📖 {modul['modul_adi']}", expanded=True):
            st.markdown(f"<div class='gorev-box-html'>{modul['pito_anlatimi']}</div>", unsafe_allow_html=True)
            st.markdown(f"### 🎯 GÖREV {egz['id']}")
            st.markdown(f"<div class='gorev-box-html'>💡 <b>YÖNERGE:</b> {egz['yonerge']}</div>", unsafe_allow_html=True)

        # EDİTÖR
        has_input = "input(" in egz['dogru_cevap_kodu'] or "input(" in egz['sablon']
        if has_input:
            with st.popover("⌨️ VERİ GİRİŞİ YAP", use_container_width=True):
                st.session_state.user_input_val = st.text_input("Girdi:", key=f"inp_{egz['id']}")

        u_code = st.text_area('Editor', value=egz['sablon'], height=200, key=f"ed_{egz['id']}", label_visibility='collapsed')
        
        if st.button("KODU KONTROL ET 🚀", type="primary", use_container_width=True):
            if u_code.strip() == egz['sablon'].strip():
                st.warning("🚨 Egzersize henüz dokunmadın!")
            else:
                st.session_state.anim_nonce += 1
                if normalize_fonksiyonu(u_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                    yeni_xp = int(u['toplam_puan']) + p_xp
                    supabase.table("kullanicilar").update({"toplam_puan": yeni_xp, "tarih": "now()"}).eq("ogrenci_no", int(u['ogrenci_no'])).execute()
                    st.session_state.user['toplam_puan'] = yeni_xp
                    st.session_state.cevap_dogru = True
                    st.balloons(); st.rerun()
                else:
                    st.session_state.error_count += 1; st.rerun()

        if st.session_state.cevap_dogru:
            out = kod_calistir_cikti_al(u_code, st.session_state.get('user_input_val', ''))
            st.markdown(f'<div class="cyber-terminal">{out if out else egz.get("beklenen_cikti", "Başarılı!")}</div>', unsafe_allow_html=True)
            if st.button("SIRADAKİ GÖREVE GEÇ ➡️"):
                st.session_state.anim_nonce = 0
                s_i = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_i]['id'], u['mevcut_modul']) if s_i < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, u_code, egz['id'], n_id, n_m)

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
