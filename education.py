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
    
    # 🚨 ANİMASYON SENSÖRÜ: Her hatada state'i zorla günceller
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

    # --- 0. SİBER-GÖRSEL TASARIM (ANİMASYON VE HUD MÜHÜRLERİ) ---
    st.markdown(f'''
        <style>
        header[data-testid="stHeader"], [data-testid="stDecoration"], footer {{ display: none !important; }}
        .stApp {{ background-color: #0e1117 !important; }}
        [data-testid="stMainViewContainer"] {{ padding-top: 185px !important; }}
        
        /* HUD TASARIMI */
        .cyber-hud {{
            position: fixed; top: 0; left: 0; right: 0; height: 120px;
            background-color: #0e1117 !important; border-bottom: 3px solid #00E5FF;
            z-index: 99999 !important; padding: 0 40px; display: flex;
            justify-content: space-between; align-items: center; box-shadow: 0 10px 40px #000;
        }}

        @keyframes cyber-shake {{
            0% {{ transform: translate(1px, 1px); }}
            25% {{ transform: translate(-3px, -1px); }}
            50% {{ transform: translate(3px, 1px); }}
            75% {{ transform: translate(-1px, 2px); }}
            100% {{ transform: translate(0, 0); }}
        }}
        .hud-shake {{ animation: cyber-shake 0.3s ease-in-out; }}
        .success-pulse {{ animation: cyber-shake 0.5s infinite; color: #ADFF2F !important; }}

        .hud-capsule {{
            background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(0, 229, 255, 0.3);
            padding: 6px 14px; border-radius: 50px; display: flex; align-items: center; gap: 8px; font-family: monospace;
        }}
        
        .input-alert {{
            border: 2px solid #FF4B4B; background: rgba(255, 75, 75, 0.1);
            padding: 10px; border-radius: 8px; margin-bottom: 10px;
            color: #FF4B4B; font-weight: bold; text-align: center;
            animation: cyber-shake 0.4s infinite;
        }}
        .cyber-terminal {{ background-color: #000; color: #ADFF2F; padding: 15px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 20px; font-family: monospace; }}
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. HUD HESAPLAMA ---
    rn, rc = ranks_module.rütbe_ata(u['toplam_puan'])
    p_xp = max(0, 20 - (e_count * 5))
    p_mod = emotions_module.pito_durum_belirle(e_count, st.session_state.cevap_dogru)
    
    # Animasyon ve Renk Durumu
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
                <div style="color: #E0E0E0; font-family: monospace; margin-left:15px;">👤 <b>{u['ad_soyad']}</b> <span class="rank-badge">🎖️ {rn}</span></div>
            </div>
            <div class="hud-stats-container" style="display:flex; gap:15px;">
                <div class="hud-capsule">💎 <span class="{shake_class}" style="color:#00E5FF; font-weight:900;">{p_xp} XP</span></div>
                <div class="hud-capsule">⚠️ <span class="{shake_class}" style="color:{error_color}; font-weight:900;">{e_count}/4</span></div>
                <div class="hud-capsule" style="border-color:#ADFF2F;">🏆 <span class="{'success-pulse' if st.session_state.cevap_dogru else ''}" style="color:#ADFF2F; font-weight:900;">{u['toplam_puan']} XP</span></div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    # --- 2. ANA İÇERİK VE DENETİMLER ---
    m_idx = int(u['mevcut_modul']) - 1
    modul = m_list[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    
    cl, cr = st.columns([7.5, 2.5])
    with cl:
        # 🚨 GİRDİ (INPUT) DENETİMİ
        has_input = "input(" in egz['dogru_cevap_kodu'] or "input(" in egz['sablon']
        user_input = st.session_state.get('user_input_val', '').strip()
        
        if has_input:
            if not user_input:
                st.markdown('<div class="input-alert">🚨 VERİ GİRİŞİ YAPILMADI! Lütfen aşağıdaki kutuyu kullan.</div>', unsafe_allow_html=True)
            with st.popover("⌨️ VERİ GİRİŞİ YAP", use_container_width=True):
                st.session_state.user_input_val = st.text_input("Değer Gir:", key=f"inp_{egz['id']}")

        u_code = st.text_area('Editor', value=egz['sablon'], height=180, key=f"ed_{egz['id']}", label_visibility='collapsed')
        
        if st.button("KODU KONTROL ET 🚀", type="primary", use_container_width=True):
            # 🚨 SİBER-DENETİMLER
            if has_input and not user_input:
                st.error("🚨 HATA: Kodun veri bekliyor! Popover alanından giriş yapmalısın.")
            elif u_code.strip() == egz['sablon'].strip():
                st.warning("🚨 HATA: Egzersize henüz dokunmadın! Boşlukları doldur veya kodu değiştir.")
            else:
                # Başarı ve Hata Senkronizasyonu
                st.session_state.anim_nonce += 1 # Animasyonu zorla oynat
                if normalize_fonksiyonu(u_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                    yeni_xp = int(u['toplam_puan']) + p_xp
                    supabase.table("kullanicilar").update({"toplam_puan": yeni_xp, "tarih": "now()"}).eq("ogrenci_no", int(u['ogrenci_no'])).execute()
                    st.session_state.user['toplam_puan'] = yeni_xp
                    st.session_state.cevap_dogru = True
                    st.balloons(); st.rerun()
                else:
                    st.session_state.error_count += 1; st.rerun()

        # Çıktı ve Sıradaki Görev Akışı
        if st.session_state.cevap_dogru:
            out = kod_calistir_cikti_al(u_code, user_input)
            st.markdown(f'<div class="cyber-terminal">{out if out else egz.get("beklenen_cikti", "Başarılı!")}</div>', unsafe_allow_html=True)
            if st.button("SIRADAKİ GÖREVE GEÇ ➡️", key="btn_next"):
                st.session_state.anim_nonce = 0 # Sıfırla
                s_i = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_i]['id'], u['mevcut_modul']) if s_i < len(modul['egzersizler']) else (f"{int(u['mevcut_modul'])+1}.1", int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, u_code, egz['id'], n_id, n_m)

    with cr:
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
