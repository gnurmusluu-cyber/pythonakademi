import streamlit as st
import random
import os
import base64
import pandas as pd
import sys as system_sys
import io
import html

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- 1. YAPI KONTROLÜ (SÖZLÜK MÜ LİSTE Mİ?) ---
    if isinstance(mufredat, dict) and "pito_akademi_mufredat" in mufredat:
        mufredat_list = mufredat["pito_akademi_mufredat"]
    else:
        mufredat_list = mufredat

    e_count = st.session_state.get('error_count', 0)
    err_anim_toggle = 'A' if e_count % 2 == 0 else 'B'
    
    # --- KOD ÇIKTISINI YAKALAMA MOTORU ---
    def kod_calistir_cikti_al(kod, giris_verisi=''):
        buffer = io.StringIO()
        old_stdout = system_sys.stdout
        system_sys.stdout = buffer
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

    # --- 0. SİBER-GÖRSEL ZIRH (NİHAİ ESTETİK) ---
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

        /* PİTO 75PX */
        .hud-pito-gif img {{
            width: 75px !important; height: 75px !important;
            border-radius: 50%; border: 3px solid #00E5FF;
            object-fit: cover; background: #000; margin-right: 20px;
        }}

        /* İSTATİSTİK KAPSÜLLERİ */
        .hud-stats-container {{ display: flex; gap: 12px; align-items: center; }}
        .hud-capsule {{
            background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(0, 229, 255, 0.3);
            padding: 6px 14px; border-radius: 50px; display: flex; align-items: center; gap: 8px;
            font-family: 'Fira Code', monospace; font-size: 0.85rem; color: #E0E0E0;
        }}
        .hud-v-glow {{ color: #00E5FF; font-weight: 900; }}

        /* RÜTBE ROZETİ */
        .rank-badge {{
            background: #ADFF2F; color: black; padding: 2px 8px; border-radius: 4px;
            font-weight: 900; font-size: 0.75rem; margin-left: 10px; text-transform: uppercase;
        }}

        /* TERMİNAL VE GÖREV KUTUSU */
        .cyber-terminal {{
            background-color: #000; color: #ADFF2F; font-family: 'Courier New', monospace;
            padding: 15px; border-radius: 8px; border: 1px solid #30363d; margin: 10px 0;
            white-space: pre-wrap; box-shadow: inset 0 0 10px rgba(173, 255, 47, 0.2);
        }}
        .gorev-box-html {{
            background: rgba(0, 229, 255, 0.05); border-left: 5px solid #00E5FF;
            padding: 15px; border-radius: 8px; color: #E0E0E0; margin-bottom: 20px;
        }}

        /* ANİMASYONLAR */
        @keyframes pulseErrA {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.4); color: #FF0000; }} }}
        .err-p-A {{ display: inline-block; animation: pulseErrA 0.7s ease-in-out; font-weight: 950 !important; }}
        .err-p-B {{ display: inline-block; animation: pulseErrA 0.7s ease-in-out; font-weight: 950 !important; }}
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. VERİ VE RÜTBE HESAPLAMA ---
    rn, rc = ranks_module.rütbe_ata(u['toplam_puan'])
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
        if os.path.exists(path): return f'data:image/gif;base64,{base64.b64encode(open(path, "rb").read()).decode()}'
        return ''

    err_class = f'err-p-{err_anim_toggle}' if e_count > 0 else ''
    success_class = 'success-pulse' if st.session_state.cevap_dogru else ''
    display_total = int(u['toplam_puan']) + (p_xp if st.session_state.cevap_dogru else 0)

    # HUD RENDER (👤 İSİM | 🎖️ RÜTBE)
    st.markdown(f'''
        <div class="cyber-hud">
            <div style="display: flex; align-items: center;">
                <div class="hud-pito-gif"><img src="{get_gif_b64(p_mod)}"></div>
                <div style="color: #E0E0E0; font-family: monospace;">
                    👤 <span style="color: #00E5FF; font-weight: bold;">{u['ad_soyad']}</span>
                    <span class="rank-badge">🎖️ {rn}</span>
                </div>
            </div>
            <div class="hud-stats-container">
                <div class="hud-capsule"><span>💎</span> <span class="hud-v-glow {err_class}">{p_xp} XP</span></div>
                <div class="hud-capsule"><span>⚠️</span> <span class="hud-v-glow {err_class}">{e_count}/4</span></div>
                <div class="hud-capsule" style="border-color: #ADFF2F;"><span>🏆</span> <span class="hud-v-glow {success_class}" style="color: #ADFF2F;">{display_total} XP</span></div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    # --- 2. ANA İÇERİK DÜZENİ ---
    m_idx = int(u['mevcut_modul']) - 1
    modul = mufredat_list[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    
    # İlerleme Çubukları
    st.markdown(f"🎓 **Modül {m_idx + 1}/{len(mufredat_list)}**")
    st.progress((m_idx + 1) / len(mufredat_list))

    cl, cr = st.columns([7.5, 2.5])
    
    with cl:
        # Navigasyon
        cn1, cn2, cn3 = st.columns([0.4, 0.4, 0.2])
        with cn1: st.markdown(f"💬 *{msgs['welcome'].format(u['ad_soyad'].split()[0])}*")
        with cn2: 
            if st.button("🔍 Geçmiş Egzersizler", use_container_width=True): st.session_state.in_review = True; st.rerun()
        with cn3:
            if st.button("🚪 Çıkış", use_container_width=True): st.session_state.user = None; st.rerun()

        with st.expander(f"📖 {modul['modul_adi']}", expanded=True):
            st.markdown(f"<div style='background:rgba(0,229,255,0.03); padding:15px; border-radius:10px;'>{modul['pito_anlatimi']}</div>", unsafe_allow_html=True)
            st.markdown(f"### 🎯 GÖREV {egz['id']}")
            st.markdown(f'<div class="gorev-box-html">💡 <b>YÖNERGE:</b> {egz["yonerge"]}</div>', unsafe_allow_html=True)

        # --- EDİTÖR VE PİTO MESAJLARI ---
        if not st.session_state.cevap_dogru and e_count < 4:
            # HATA MESAJLARI (Mühürlendi)
            if e_count > 0:
                lvl = f"level_{min(e_count, 4)}"
                p_msg = random.choice(msgs['errors'][lvl]).format(u['ad_soyad'].split()[0])
                st.error(f"🚨 **Pito:** {p_msg}")
                if e_count >= 3: st.warning(f"💡 **İpucu:** {egz['ipucu']}")

            # Akıllı Giriş Bariyeri
            has_input = 'input' in egz['dogru_cevap_kodu'] or 'input' in egz['sablon']
            has_output = 'print' in egz['dogru_cevap_kodu'] or egz.get('beklenen_cikti', '') != ""
            needs_input_ui = has_input and has_output
            
            s_input = ''
            if needs_input_ui:
                with st.popover('⌨️ VERİ GİRİŞİ YAP (GEREKLİ)', use_container_width=True):
                    s_input = st.text_input('Veri Gir:', placeholder='Örn: 5', key=f"in_{egz['id']}")

            if "reset_trigger" not in st.session_state: st.session_state.reset_trigger = 0
            user_code = st.text_area('Editor', value=egz['sablon'], height=180, key=f'ed_{egz["id"]}_{st.session_state.reset_trigger}', label_visibility='collapsed')
            
            b1, b2 = st.columns([4, 1.2])
            with b1:
                if st.button("KODU KONTROL ET 🚀", type="primary", use_container_width=True):
                    if needs_input_ui and not s_input.strip():
                        st.warning("⚠️ Önce veri girişi yapmalısın!")
                    else:
                        st.session_state.current_code = user_code
                        st.session_state.user_input_val = s_input
                        if normalize_fonksiyonu(user_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                            st.session_state.cevap_dogru = True; st.balloons(); st.rerun()
                        else: st.session_state.error_count += 1; st.rerun()
            with b2:
                if st.button("🔄 SIFIRLA", use_container_width=True): st.session_state.reset_trigger += 1; st.rerun()

        elif st.session_state.cevap_dogru:
            st.success(f"✅ Harika iş!")
            # Çıktı Mantığı
            if 'print' in st.session_state.current_code:
                output = kod_calistir_cikti_al(st.session_state.current_code, st.session_state.get('user_input_val', ''))
            else: output = egz.get('beklenen_cikti', '')
            st.markdown(f'<div class="cyber-terminal">{output if output else "Bu kod çıktı vermez."}</div>', unsafe_allow_html=True)
            
            if st.button("SIRADAKİ GÖREVE GEÇ ➡️", type="primary", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f'{int(u["mevcut_modul"])+1}.1', int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)

        elif e_count >= 4:
            st.warning("🚨 Çözümü incele:")
            st.code(egz['cozum'], language="python")
            if st.button("DEVAM ET ➡️", type="primary", use_container_width=True):
                s_idx = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_idx]['id'], u['mevcut_modul']) if s_idx < len(modul['egzersizler']) else (f'{int(u["mevcut_modul"])+1}.1', int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr:
        st.markdown(f'''<div class="my-stats-card"><div class="my-stats-grid"><div class="my-stat-box"><div class="my-stat-label">SINIFIM</div><div class="my-stat-val">#{sinif_sira}</div></div><div class="my-stat-box"><div class="my-stat-label">OKULUM</div><div class="my-stat-val">#{okul_sira}</div></div></div></div>''', unsafe_allow_html=True)
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
