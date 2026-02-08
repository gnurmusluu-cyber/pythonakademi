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
    # --- 1. VERİ YAPISI VE GÜVENLİK ---
    if isinstance(mufredat, dict) and "pito_akademi_mufredat" in mufredat:
        m_list = mufredat["pito_akademi_mufredat"] [cite: 2026-02-07]
    else:
        m_list = mufredat

    try:
        m_idx = int(u['mevcut_modul']) - 1
        modul = m_list[m_idx]
        egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0]) [cite: 2026-02-07]
    except Exception:
        st.error("🚨 Veri Okuma Hatası! Sistem kilitlendi.")
        return

    e_count = st.session_state.get('error_count', 0) [cite: 2026-02-07]
    if "anim_nonce" not in st.session_state: st.session_state.anim_nonce = 0

    # --- KOD ÇIKTISINI YAKALAMA MOTORU (BOŞ ÇIKTI DENETİMLİ) ---
    def kod_calistir_cikti_al(kod, giris_verisi=''):
        safe_input = str(giris_verisi) if (giris_verisi and str(giris_verisi).strip() != "") else "0"
        buffer = io.StringIO()
        old_stdout = system_sys.stdout
        system_sys.stdout = buffer
        def mock_input(prompt=''): return safe_input
        exec_scope = {'__builtins__': __builtins__, 'input': mock_input}
        try:
            exec(kod, exec_scope)
            res = buffer.getvalue().strip()
            # 🚨 ÇIKTI DENETİMİ: Çıktı boşsa öğrenciyi bilgilendir
            if not res:
                return "ℹ️ Bu kod herhangi bir çıktı üretmedi." [cite: 2026-02-07]
            return res 
        except Exception as e:
            return f'⚠️ SİSTEM HATASI: {str(e)}'
        finally:
            system_sys.stdout = old_stdout

    # --- 0. SİBER-GÖRSEL TASARIM (STATİK HUD) ---
    st.markdown(f'''
        <style>
        header[data-testid="stHeader"], [data-testid="stDecoration"], footer {{ display: none !important; }}
        .stApp {{ background-color: #0e1117 !important; }}
        
        .cyber-hud {{
            width: 100%; min-height: 125px;
            background-color: #0e1117 !important; border-bottom: 3px solid #00E5FF;
            padding: 20px 40px; display: flex;
            justify-content: space-between; align-items: center; 
            box-shadow: 0 10px 40px #000; margin-bottom: 30px;
        }}
        
        .input-warning-box {{
            padding: 12px; border-radius: 8px; border: 2px solid #FF4B4B;
            background-color: rgba(255, 75, 75, 0.15); color: #FF4B4B;
            font-weight: bold; text-align: center; margin-bottom: 10px;
            animation: shake 0.5s infinite;
        }}
        @keyframes shake {{
            0% {{ transform: translate(1px, 1px) rotate(0deg); }}
            25% {{ transform: translate(-2px, -1px) rotate(-1deg); }}
            50% {{ transform: translate(2px, 1px) rotate(1deg); }}
            100% {{ transform: translate(0, 0) rotate(0deg); }}
        }}
        
        .cyber-terminal {{ background-color: #000; color: #ADFF2F; padding: 15px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 20px; font-family: monospace; }}
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. RUH HALİ (EMOTIONS.PY) VE HUD ---
    cevap_durumu = st.session_state.get('cevap_dogru', False) [cite: 2026-02-07]
    p_mod = emotions_module.pito_durum_belirle(e_count, cevap_durumu)
    rn, rc = ranks_module.rütbe_ata(u['toplam_puan']) [cite: 2026-02-07]
    
    def get_gif_b64(mod):
        path = os.path.join(os.path.dirname(__file__), 'assets', f'pito_{mod}.gif')
        if os.path.exists(path):
            with open(path, "rb") as f:
                return f'data:image/gif;base64,{base64.b64encode(f.read()).decode()}'
        return ""

    st.markdown(f'''
        <div class="cyber-hud">
            <div style="display: flex; align-items: center;">
                <div class="hud-pito-gif"><img src="{get_gif_b64(p_mod)}" style="width:70px; border-radius:50%; border:2px solid #ADFF2F;"></div>
                <div style="color: #E0E0E0; font-family: monospace; margin-left:15px; font-size: 0.9rem;">👤 <b>{u['ad_soyad'][:15]}</b><br><span style="color:#ADFF2F;">🎖️ {rn}</span></div>
            </div>
            <div style="color:#00E5FF; font-family:monospace; font-size:1.1rem;">💎 XP: {max(0, 20-(e_count*5))} | ⚠️ HATA: {e_count}/4 | 🏆 TOPLAM: {u['toplam_puan']}</div>
        </div>
    ''', unsafe_allow_html=True)

    # --- 2. ANA PANEL ---
    cl, cr = st.columns([7.2, 2.8])
    with cl:
        n1, n2, n3 = st.columns([0.4, 0.4, 0.2])
        with n1: st.markdown(f"💬 *{msgs['welcome'].format(u['ad_soyad'].split()[0])}*") [cite: 2026-02-07]
        with n2: 
            if st.button("🔍 Geçmiş Egzersizler", key="btn_review"):
                st.session_state.in_review = True; st.rerun()
        with n3:
            if st.button("🚪 Çıkış", key="btn_exit"):
                st.session_state.user = None; st.rerun()

        # 🚨 AKILLI INPUT DENETİMİ (Sadece Gerekliyse)
        has_input = "input(" in egz['dogru_cevap_kodu'] or "input(" in egz['sablon'] [cite: 2026-02-07]
        user_input_val = st.session_state.get('user_input_val', '').strip()

        if has_input:
            if not user_input_val:
                st.markdown('<div class="input-warning-box">🚨 SİBER-BARİKAT: Kodun bir veri bekliyor! Lütfen aşağıdaki kutuyu doldur.</div>', unsafe_allow_html=True)
            with st.popover("⌨️ VERİ GİRİŞİ YAP (Mecburi)", use_container_width=True):
                st.session_state.user_input_val = st.text_input("Giriş yapın:", key=f"inp_{egz['id']}")
        else:
            st.session_state.user_input_val = ""

        with st.expander(f"📖 {modul['modul_adi']}", expanded=True):
            st.markdown(f"**Yönerge:** {egz['yonerge']}")

        u_code = st.text_area('Editor', value=egz['sablon'], height=200, key=f"ed_{egz['id']}", label_visibility='collapsed') [cite: 2026-02-07]
        
        if st.button("KODU KONTROL ET 🚀", type="primary", use_container_width=True):
            if has_input and not st.session_state.get('user_input_val', '').strip():
                st.error("🚨 HATA: Veri girişi yapmadan kontrol edilemez!") [cite: 2026-02-07]
            elif u_code.strip() == egz['sablon'].strip():
                st.warning("🚨 HATA: Önce kodu tamamlamalısın!")
            else:
                if normalize_fonksiyonu(u_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                    yeni_xp = int(u['toplam_puan']) + max(0, 20-(e_count*5)) [cite: 2026-02-07]
                    supabase.table("kullanicilar").update({"toplam_puan": yeni_xp}).eq("ogrenci_no", int(u['ogrenci_no'])).execute()
                    st.session_state.user['toplam_puan'] = yeni_xp
                    st.session_state.cevap_dogru = True
                    st.balloons(); st.rerun()
                else:
                    st.session_state.error_count = st.session_state.get('error_count', 0) + 1 [cite: 2026-02-07]
                    st.rerun()

        if st.session_state.get('cevap_dogru'):
            out = kod_calistir_cikti_al(u_code, st.session_state.get('user_input_val', '0'))
            st.markdown(f'<div class="cyber-terminal"><b>SİBER-ÇIKTI:</b><br>{out}</div>', unsafe_allow_html=True)
            
            # 🚨 VALUEERROR KESİN ÇÖZÜMÜ
            if st.button("SIRADAKİ GÖREVE GEÇ ➡️"):
                st.session_state.cevap_dogru = False
                st.session_state.error_count = 0
                st.session_state.user_input_val = ""
                
                curr_idx = modul['egzersizler'].index(egz)
                if curr_idx + 1 < len(modul['egzersizler']):
                    n_id = str(modul['egzersizler'][curr_idx + 1]['id'])
                    n_m = int(u['mevcut_modul'])
                else:
                    n_m = int(u['mevcut_modul']) + 1
                    n_id = f"{n_m}.1"
                
                ilerleme_fonksiyonu(0, u_code, egz['id'], n_id, n_m) [cite: 2026-02-07]

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u) [cite: 2026-02-07]
