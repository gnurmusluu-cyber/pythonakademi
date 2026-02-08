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
    # --- 1. YAPI VE DURUM KONTROLÜ ---
    m_list = mufredat["pito_akademi_mufredat"] if isinstance(mufredat, dict) else mufredat
    e_count = st.session_state.get('error_count', 0)
    
    # --- KOD ÇIKTISINI YAKALAMA MOTORU (HTML VE INPUT DESTEKLİ) ---
    def kod_calistir_cikti_al(kod, giris_verisi=''):
        buffer = io.StringIO()
        old_stdout = system_sys.stdout
        system_sys.stdout = buffer
        
        # 🚨 SİBER-TAKİP: Standart input() yerine öğrencinin kutuya yazdığı veriyi enjekte et
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

    # --- 0. SİBER-GÖRSEL TASARIM (CSS) ---
    st.markdown(f'''
        <style>
        header[data-testid="stHeader"], [data-testid="stDecoration"], footer {{ display: none !important; }}
        .stApp {{ background-color: #0e1117 !important; }}
        [data-testid="stMainViewContainer"] {{ padding-top: 185px !important; }}
        .cyber-hud {{
            position: fixed; top: 0; left: 0; right: 0; height: 120px;
            background-color: #0e1117 !important; border-bottom: 3px solid #00E5FF;
            z-index: 99999 !important; padding: 0 40px; display: flex;
            justify-content: space-between; align-items: center; box-shadow: 0 10px 40px #000;
        }}
        .hud-pito-gif img {{ width: 75px !important; height: 75px !important; border-radius: 50%; border: 3px solid #00E5FF; object-fit: cover; }}
        .rank-badge {{ background: #ADFF2F; color: black; padding: 2px 8px; border-radius: 4px; font-weight: 900; font-size: 0.75rem; margin-left: 10px; text-transform: uppercase; }}
        .hud-stats-container {{ display: flex; gap: 12px; align-items: center; }}
        .hud-capsule {{
            background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(0, 229, 255, 0.3);
            padding: 6px 14px; border-radius: 50px; display: flex; align-items: center; gap: 8px; font-family: monospace; font-size: 0.85rem;
        }}
        .gorev-box-html {{ background: rgba(0, 229, 255, 0.05); border-left: 5px solid #00E5FF; padding: 15px; border-radius: 8px; color: #E0E0E0; margin-bottom: 20px; }}
        .terminal-label {{ color: #00E5FF; font-size: 0.7rem; font-weight: bold; margin-bottom: 5px; margin-top: 15px; }}
        .cyber-terminal {{ 
            background-color: #000; color: #ADFF2F; font-family: 'Courier New', monospace; 
            padding: 15px; border-radius: 8px; border: 1px solid #30363d; 
            margin-bottom: 20px; font-size: 0.9rem; min-height: 40px; overflow-x: auto;
        }}
        .sidebar-stats-card {{ background: rgba(0, 229, 255, 0.05); border: 1px solid rgba(0, 229, 255, 0.2); border-radius: 15px; padding: 15px; text-align: center; }}
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. HUD VE DUYGU MOTORU ---
    rn, rc = ranks_module.rütbe_ata(u['toplam_puan'])
    p_xp = max(0, 20 - (e_count * 5))
    p_mod = emotions_module.pito_durum_belirle(e_count, st.session_state.cevap_dogru)
    
    # Dinamik Renk Kontrolü
    if st.session_state.cevap_dogru:
        active_anim, error_color, success_c = "", "#ADFF2F", "success-pulse"
    elif e_count > 0:
        anim_toggle = 'A' if e_count % 2 == 0 else 'B'
        active_anim, error_color, success_c = f'anim-{anim_toggle}', "#FF4B4B", ""
    else:
        active_anim, error_color, success_c = "", "#00E5FF", ""

    def get_gif_b64(mod):
        path = os.path.join(os.path.dirname(__file__), 'assets', f'pito_{mod}.gif')
        return f'data:image/gif;base64,{base64.b64encode(open(path, "rb").read()).decode()}' if os.path.exists(path) else ''

    st.markdown(f'''
        <div class="cyber-hud">
            <div style="display: flex; align-items: center;">
                <div class="hud-pito-gif"><img src="{get_gif_b64(p_mod)}"></div>
                <div style="color: #E0E0E0; font-family: monospace;">👤 <b>{u['ad_soyad']}</b> <span class="rank-badge">🎖️ {rn}</span></div>
            </div>
            <div class="hud-stats-container">
                <div class="hud-capsule">💎 <span class="{active_anim}" style="color:#00E5FF; font-weight:900;">{p_xp} XP</span></div>
                <div class="hud-capsule">⚠️ <span class="{active_anim}" style="color:{error_color}; font-weight:900;">{e_count}/4</span></div>
                <div class="hud-capsule" style="border-color:#ADFF2F;">🏆 <span class="{success_c}" style="color:#ADFF2F; font-weight:900;">{u['toplam_puan']} XP</span></div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    # --- 2. ANA İÇERİK ---
    m_idx = int(u['mevcut_modul']) - 1
    modul = m_list[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    
    cl, cr = st.columns([7.5, 2.5])
    with cl:
        st.markdown(f"💬 *{msgs['welcome'].format(u['ad_soyad'].split()[0])}*")
        
        with st.expander(f"📖 {modul['modul_adi']}", expanded=True):
            st.markdown(f"<div class='gorev-box-html'>{modul['pito_anlatimi']}</div>", unsafe_allow_html=True)
            st.markdown(f"### 🎯 GÖREV {egz['id']}")
            st.markdown(f"<div class='gorev-box-html'>💡 <b>YÖNERGE:</b> {egz['yonerge']}</div>", unsafe_allow_html=True)

        # --- DURUM 1: ÇALIŞMA MODU ---
        if not st.session_state.cevap_dogru and e_count < 4:
            # 🚨 SİBER-GİRDİ ALANI
            has_input_call = "input(" in egz['dogru_cevap_kodu'] or "input(" in egz['sablon']
            if has_input_call:
                with st.popover("⌨️ VERİ GİRİŞİ YAP (Girdi Bekleniyor)", use_container_width=True):
                    st.session_state.user_input_val = st.text_input("Giriş Yap:", value="0", key=f"inp_{egz['id']}")
            
            u_code = st.text_area('Editor', value=egz['sablon'], height=180, key=f"ed_{egz['id']}", label_visibility='collapsed')
            
            col_b1, col_b2 = st.columns([4, 1.2])
            with col_b1:
                if st.button("KODU KONTROL ET 🚀", type="primary", use_container_width=True):
                    if has_input_call and not st.session_state.get('user_input_val', '').strip():
                        st.warning("🚨 Bu görev veri girişi bekliyor! Lütfen yukarıdaki butondan bir değer gir.")
                    elif normalize_fonksiyonu(u_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                        yeni_xp = int(u['toplam_puan']) + p_xp
                        supabase.table("kullanicilar").update({"toplam_puan": yeni_xp, "tarih": "now()"}).eq("ogrenci_no", int(u['ogrenci_no'])).execute()
                        st.session_state.user.update({"toplam_puan": yeni_xp})
                        st.session_state.current_code = u_code
                        st.session_state.cevap_dogru = True
                        st.balloons(); st.rerun()
                    else:
                        st.session_state.error_count += 1; st.rerun()
            with col_b2:
                if st.button("🔄 SIFIRLA", use_container_width=True): 
                    st.session_state.error_count = 0; st.rerun()

        # --- DURUM 2: BAŞARI MODU ---
        elif st.session_state.cevap_dogru:
            st.success(f"✅ Harika iş!")
            # 🚨 HİBRİT ÇIKTI SİSTEMİ
            live_out = kod_calistir_cikti_al(st.session_state.current_code, st.session_state.get('user_input_val', ''))
            final_out = live_out if (live_out and "SİSTEM HATASI" not in live_out) else egz.get('beklenen_cikti', 'Kod Başarıyla Mühürlendi.')
            
            st.markdown('<div class="terminal-label">🖥️ SİBER-ÇIKTI</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="cyber-terminal">{final_out}</div>', unsafe_allow_html=True)
            
            if st.button("SIRADAKİ GÖREVE GEÇ ➡️", type="primary", use_container_width=True):
                s_i = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_i]['id'], u['mevcut_modul']) if s_i < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, st.session_state.current_code, egz['id'], n_id, n_m)

        # --- DURUM 3: 4. HATA (KESİN ÇÖZÜM) ---
        elif e_count >= 4:
            st.warning("🚨 Çözümü incele ve siber-terminali kontrol et:")
            st.code(egz['cozum'], language="python")
            
            # 🚨 JSON'DAN GELEN İDEAL ÇIKTI
            sol_out = egz.get('beklenen_cikti', 'Çözüm kodu simüle edildi.')
            st.markdown('<div class="terminal-label">🖥️ SİBER-ÇIKTI (İDEAL ÇÖZÜM)</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="cyber-terminal">{sol_out}</div>', unsafe_allow_html=True)
            
            if st.button("ANLADIM, DEVAM ET ➡️", type="primary", use_container_width=True):
                s_i = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_i]['id'], u['mevcut_modul']) if s_i < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
