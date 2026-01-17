import streamlit as st
import random
import os
import base64
import pandas as pd
import sys as system_sys
import io
import html

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- DURUM KONTROLÜ ---
    e_count = st.session_state.get('error_count', 0)
    # Çift kanal toggle: Hata sayısı değiştikçe A ve B arasında geçiş yaparak animasyonu her seferinde zorlar.
    err_anim_toggle = 'A' if e_count % 2 == 0 else 'B'
    
    # --- KOD ÇIKTISINI YAKALAMA MOTORU (HİBRİT & GÜVENLİ) ---
    def kod_calistir_cikti_al(kod, giris_verisi=''):
        buffer = io.StringIO()
        old_stdout = system_sys.stdout
        system_sys.stdout = buffer
        # input() simülasyonu: Öğrencinin popover'a girdiği veriyi döndürür.
        def mock_input(prompt=''): return giris_verisi
        exec_scope = {'__builtins__': __builtins__, 'input': mock_input}
        try:
            exec(kod, exec_scope)
            result = buffer.getvalue().strip()
            return html.escape(result) if result else ''
        except Exception as e:
            return f'⚠️ SİSTEM HATASI: {html.escape(str(e))}'
        finally:
            system_sys.stdout = old_stdout

    # --- 0. SİBER-GÖRSEL ZIRH (TAM ENTEGRASYON) ---
    st.markdown(f'''
        <style>
        header[data-testid="stHeader"], [data-testid="stDecoration"], footer {{ display: none !important; }}
        .stApp {{ background-color: #0e1117 !important; }}
        [data-testid="stMainViewContainer"] {{ padding-top: 185px !important; }}

        /* HUD ANA PANEL */
        .cyber-hud {{
            position: fixed; top: 0; left: 0; right: 0;
            height: 120px; background-color: #0e1117 !important;
            border-bottom: 3px solid #00E5FF; z-index: 99999 !important;
            padding: 0 40px; display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 10px 40px rgba(0,0,0,0.8);
        }}

        /* PİTO 75PX MÜHRÜ */
        .hud-pito-gif img {{
            width: 75px !important; height: 75px !important;
            border-radius: 50%; border: 3px solid #00E5FF;
            object-fit: cover; background: #000; margin-right: 20px;
            box-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
        }}

        /* İSTATİSTİK KAPSÜLLERİ */
        .hud-stats-container {{ display: flex; gap: 15px; align-items: center; }}
        .hud-capsule {{
            background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(0, 229, 255, 0.3);
            padding: 8px 16px; border-radius: 50px; display: flex; align-items: center; gap: 10px;
            font-family: 'Fira Code', monospace; font-size: 0.9rem; color: #E0E0E0;
        }}
        .hud-v-glow {{ color: #00E5FF; font-weight: 900; }}

        /* POPOVER (GİRİŞ KUTUSU) TASARIMI */
        div[data-testid="stPopover"] > button {{
            background-color: rgba(255, 215, 0, 0.1) !important;
            border: 2px solid #FFD700 !important;
            color: #FFD700 !important;
            font-weight: 900 !important;
            border-radius: 8px !important;
        }}

        /* SİBER TERMİNAL */
        .cyber-terminal {{
            background-color: #000000; color: #ADFF2F; font-family: 'Courier New', monospace;
            padding: 15px; border-radius: 8px; border: 1px solid #30363d; margin: 10px 0;
            white-space: pre-wrap; box-shadow: inset 0 0 10px rgba(173, 255, 47, 0.2); font-size: 0.9rem;
        }}
        .terminal-label {{ font-size: 0.7rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }}

        /* ÇİFT KANALLI PULSE */
        @keyframes pulseErrA {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.4); color: #FF0000; }} }}
        @keyframes pulseErrB {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.4); color: #FF0000; }} }}
        @keyframes successPulse {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.6); color: #ADFF2F; }} }}

        .err-p-A {{ display: inline-block; animation: pulseErrA 0.7s ease-in-out; font-weight: 950 !important; }}
        .err-p-B {{ display: inline-block; animation: pulseErrB 0.7s ease-in-out; font-weight: 950 !important; }}
        .success-pulse {{ display: inline-block; animation: successPulse 0.8s ease-in-out; font-weight: 950 !important; }}

        /* ÖĞRENCİ STATS KARTI */
        .my-stats-card {{
            background: rgba(0, 229, 255, 0.05); border: 1px solid rgba(0, 229, 255, 0.2);
            border-radius: 12px; padding: 12px; margin-bottom: 15px; text-align: center;
        }}
        .my-stats-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 8px; }}
        .my-stat-box {{ background: rgba(0, 0, 0, 0.3); padding: 8px; border-radius: 8px; border: 1px solid rgba(0, 229, 255, 0.1); }}
        .my-stat-label {{ font-size: 0.65rem; color: #888; text-transform: uppercase; font-weight: bold; }}
        .my-stat-val {{ font-size: 1.1rem; color: #ADFF2F; font-weight: 950; font-family: monospace; }}
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. SIRALAMA VE HUD VERİLERİ ---
    p_xp = max(0, 20 - (e_count * 5))
    p_mod = emotions_module.pito_durum_belirle(e_count, st.session_state.cevap_dogru)
    
    try:
        res = supabase.table('kullanicilar').select('*').execute()
        df_all = pd.DataFrame(res.data)
        df_okul = df_all.sort_values(by='toplam_puan', ascending=False).reset_index(drop=True)
        okul_sira = df_okul[df_okul['ogrenci_no'] == u['ogrenci_no']].index[0] + 1
        df_sinif = df_okul[df_okul['sinif'] == u['sinif']].reset_index(drop=True)
        sinif_sira = df_sinif[df_sinif['ogrenci_no'] == u['ogrenci_no']].index[0] + 1
    except:
        okul_sira, sinif_sira = '?', '?'

    def get_gif_b64(mod):
        path = os.path.join(os.path.dirname(__file__), 'assets', f'pito_{mod}.gif')
        if os.path.exists(path):
            return f'data:image/gif;base64,{base64.b64encode(open(path, "rb").read()).decode()}'
        return ''

    err_class = f'err-p-{err_anim_toggle}' if e_count > 0 else ''
    success_class = 'success-pulse' if st.session_state.cevap_dogru else ''
    display_total = int(u['toplam_puan']) + (p_xp if st.session_state.cevap_dogru else 0)

    # HUD RENDER
    st.markdown(f'''
        <div class="cyber-hud">
            <div style="display: flex; align-items: center;">
                <div class="hud-pito-gif"><img src="{get_gif_b64(p_mod)}"></div>
                <div style="color: #E0E0E0; font-family: monospace; font-size: 1.1rem;">
                    👤 <span style="color: #00E5FF; font-weight: bold;">{u['ad_soyad']}</span>
                </div>
            </div>
            <div class="hud-stats-container">
                <div class="hud-capsule"><span>💎</span> <span class="hud-v-glow {err_class}">{p_xp} XP</span></div>
                <div class="hud-capsule"><span>⚠️</span> <span class="hud-v-glow {err_class}">{e_count}/4</span></div>
                <div class="hud-capsule" style="border-color: #ADFF2F;"><span>🏆</span> <span class="hud-v-glow {success_class}" style="color: #ADFF2F;">{display_total} XP</span></div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    # --- 2. ANA İÇERİK ---
    st.markdown('<h1 style="text-align:center; color:#00E5FF; margin-bottom:30px;">🎓 PİTO PYTHON AKADEMİ</h1>', unsafe_allow_html=True)
    m_idx = int(u['mevcut_modul']) - 1
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    
    cl, cr = st.columns([7.5, 2.5])
    
    with cl:
        # NAVİGASYON
        cn1, cn2, cn3 = st.columns([0.4, 0.4, 0.2])
        with cn1: st.markdown(f'💬 *{msgs["welcome"].format(u["ad_soyad"].split()[0])}*')
        with cn2: 
            if st.button('🔍 Geçmiş Egzersizler', use_container_width=True): st.session_state.in_review = True; st.rerun()
        with cn3:
            if st.button('🚪 Çıkış', use_container_width=True): st.session_state.user = None; st.rerun()

        with st.expander(f'📖 {modul["modul_adi"]}', expanded=True):
            st.markdown(f'<div style="background:rgba(0,229,255,0.03); padding:15px; border-radius:10px;\">{modul["pito_anlatimi"]}</div>', unsafe_allow_html=True)
            st.markdown(f'### 🎯 GÖREV {egz["id"]}')
            st.info(egz['yonerge'])

        # --- EDİTÖR VE GİRİŞ KONTROLÜ ---
        if not st.session_state.cevap_dogru and e_count < 4:
            # GÖREV INPUT GEREKTİRİYOR MU?
            needs_input = 'input' in egz['dogru_cevap_kodu'] or 'input' in egz['sablon']
            
            s_input = ''
            if needs_input:
                # SARI PARLAYAN AÇILIR BOX (POPOVER)
                with st.popover('⌨️ VERİ GİRİŞİ YAP (GEREKLİ)', use_container_width=True):
                    st.markdown('<p style="color:#FFD700; font-weight:bold;">Programın beklediği veriyi buraya yaz:</p>', unsafe_allow_html=True)
                    s_input = st.text_input('GirisVerisi', placeholder='Örn: 5', label_visibility='collapsed')

            if "reset_trigger" not in st.session_state: st.session_state.reset_trigger = 0
            user_code = st.text_area('Editor', value=egz['sablon'], height=180, key=f'ed_{egz["id"]}_{st.session_state.reset_trigger}', label_visibility='collapsed')
            
            b1, b2 = st.columns([4, 1.2])
            with b1:
                if st.button('KODU KONTROL ET 🚀', type='primary', use_container_width=True):
                    # SİBER-BARİYER: GİRİŞ YAPILMAMIŞSA ENGELLE
                    if needs_input and not s_input.strip():
                        st.warning("⚠️ Dur yolcu! Önce yukarıdaki sarı 'VERİ GİRİŞİ' kutusuna bir değer yazmalısın!")
                    else:
                        st.session_state.current_code = user_code
                        st.session_state.user_input_val = s_input
                        if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                            st.session_state.cevap_dogru = True; st.balloons(); st.rerun()
                        else:
                            st.session_state.error_count += 1; st.rerun()
            with b2:
                if st.button('🔄 SIFIRLA', use_container_width=True): 
                    st.session_state.reset_trigger += 1; st.rerun()

        elif st.session_state.cevap_dogru:
            st.success(f'✅ Harika iş {u["ad_soyad"].split()[0]}! (+{p_xp} XP)')
            # HİBRİT TERMİNAL ÇIKTISI
            if 'input' in st.session_state.current_code:
                output = kod_calistir_cikti_al(st.session_state.current_code, st.session_state.get('user_input_val', ''))
            else:
                output = egz.get('beklenen_cikti', '')
            st.markdown(f'<div class="terminal-label">🖥️ SİBER-ÇIKTI</div><div class="cyber-terminal">{output if output else "Bu kod çıktı vermez."}</div>', unsafe_allow_html=True)
            
            if st.button('SIRADAKİ GÖREVE GEÇ ➡️', type='primary', use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f'{int(u["mevcut_modul"])+1}.1', int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)

        elif e_count >= 4:
            st.warning('🚨 Çözümü incele ve devam et:')
            st.code(egz['cozum'], language='python')
            output = egz.get('beklenen_cikti', '')
            st.markdown(f'<div class="terminal-label">🖥️ SİBER-ÇIKTI (ÇÖZÜM)</div><div class="cyber-terminal">{output if output else "Bu kod çıktı vermez."}</div>', unsafe_allow_html=True)
            
            if st.button('DEVAM ET ➡️', type='primary', use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f'{int(u["mevcut_modul"])+1}.1', int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, 'Çözüm İncelendi', egz['id'], n_id, n_m)

    with cr:
        # ÖĞRENCİ DURUM RAPORU
        st.markdown(f'''
            <div class="my-stats-card">
                <div style="font-size:0.75rem; color:#00E5FF; font-weight:bold; letter-spacing:1px;">📊 DURUM RAPORUN</div>
                <div class="my-stats-grid">
                    <div class="my-stat-box"><div class="my-stat-label">SINIFIM</div><div class="my-stat-val">#{sinif_sira}</div></div>
                    <div class="my-stat-box"><div class="my-stat-label">OKULUM</div><div class="my-stat-val">#{okul_sira}</div></div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
