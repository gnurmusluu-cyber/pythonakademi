import streamlit as st
import random
import os
import base64
import pandas as pd
import sys as system_sys
import io
import html

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- 1. YAPI KONTROLÜ ---
    m_list = mufredat["pito_akademi_mufredat"] if isinstance(mufredat, dict) else mufredat

    # --- DURUM KONTROLÜ ---
    e_count = st.session_state.get('error_count', 0)
    # Çift kanal toggle: Hata sayısı değiştikçe animasyonu her seferinde yeniden tetikler.
    anim_toggle = 'A' if e_count % 2 == 0 else 'B'
    
    # --- KOD ÇIKTISINI YAKALAMA MOTORU ---
    def kod_calistir_cikti_al(kod, giris_verisi=''):
        buffer = io.StringIO()
        old_stdout = system_sys.stdout
        system_sys.stdout = buffer
        def mock_input(prompt=''): return giris_verisi
        exec_scope = {'__builtins__': __builtins__, 'input': mock_input}
        try:
            exec(kod, exec_scope)
            res = buffer.getvalue().strip()
            return html.escape(res) if res else ''
        except Exception as e:
            return f'⚠️ SİSTEM HATASI: {html.escape(str(e))}'
        finally:
            system_sys.stdout = old_stdout

    # --- 0. SİBER-GÖRSEL ZIRH (GELİŞMİŞ STATS TASARIMI) ---
    st.markdown(f'''
        <style>
        header[data-testid="stHeader"], [data-testid="stDecoration"], footer {{ display: none !important; }}
        .stApp {{ background-color: #0e1117 !important; }}
        [data-testid="stMainViewContainer"] {{ padding-top: 185px !important; }}

        /* HUD ANA PANEL */
        .cyber-hud {{
            position: fixed; top: 0; left: 0; right: 0; height: 120px;
            background-color: #0e1117 !important; border-bottom: 3px solid #00E5FF;
            z-index: 99999 !important; padding: 0 40px; display: flex;
            justify-content: space-between; align-items: center; box-shadow: 0 10px 40px #000;
        }}
        .hud-pito-gif img {{ width: 75px !important; height: 75px !important; border-radius: 50%; border: 3px solid #00E5FF; object-fit: cover; }}
        .rank-badge {{ background: #ADFF2F; color: black; padding: 2px 8px; border-radius: 4px; font-weight: 900; font-size: 0.75rem; margin-left: 10px; text-transform: uppercase; }}
        
        /* HUD STATS */
        .hud-stats-container {{ display: flex; gap: 12px; align-items: center; }}
        .hud-capsule {{
            background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(0, 229, 255, 0.3);
            padding: 6px 14px; border-radius: 50px; display: flex; align-items: center; gap: 8px; font-family: monospace; font-size: 0.85rem;
        }}

        /* SİBER-SIDEBAR STATS KARTI (FIXED) */
        .sidebar-stats-card {{
            background: rgba(0, 229, 255, 0.05); border: 2px solid rgba(0, 229, 255, 0.2);
            border-radius: 15px; padding: 15px; margin-bottom: 20px; text-align: center;
        }}
        .sidebar-stats-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }}
        .sidebar-stat-box {{ background: rgba(0, 0, 0, 0.4); padding: 10px; border-radius: 10px; border: 1px solid rgba(0, 229, 255, 0.1); }}
        .sidebar-stat-label {{ font-size: 0.65rem; color: #888; text-transform: uppercase; letter-spacing: 1px; font-weight: bold; }}
        .sidebar-stat-val {{ font-size: 1.2rem; color: #ADFF2F; font-weight: 950; font-family: 'Courier New', monospace; }}

        /* TERMİNAL VE GÖREV */
        .gorev-box-html {{ background: rgba(0, 229, 255, 0.05); border-left: 5px solid #00E5FF; padding: 15px; border-radius: 8px; color: #E0E0E0; margin-bottom: 20px; }}
        .cyber-terminal {{ background-color: #000; color: #ADFF2F; font-family: 'Courier New', monospace; padding: 15px; border-radius: 8px; border: 1px solid #30363d; margin: 10px 0; font-size: 0.9rem; }}

        /* ÇİFT KANALLI ANİMASYON */
        @keyframes pulseA {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.3); color: #FF0000; }} }}
        @keyframes pulseB {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.3); color: #FF0000; }} }}
        .anim-A {{ animation: pulseA 0.6s ease-in-out; display: inline-block; }}
        .anim-B {{ animation: pulseB 0.6s ease-in-out; display: inline-block; }}
        .success-pulse {{ animation: pulseA 0.7s ease-in-out; color: #ADFF2F !important; display: inline-block; }}
        </style>
    ''', unsafe_allow_html=True)

    # --- 1. VERİ VE RÜTBE ---
    rn, rc = ranks_module.rütbe_ata(u['toplam_puan'])
    p_xp = max(0, 20 - (e_count * 5))
    p_mod = emotions_module.pito_durum_belirle(e_count, st.session_state.cevap_dogru)
    
    try:
        res = supabase.table('kullanicilar').select('*').execute()
        df = pd.DataFrame(res.data).sort_values(by='toplam_puan', ascending=False).reset_index(drop=True)
        okul_sira = df[df['ogrenci_no'] == u['ogrenci_no']].index[0] + 1
        sinif_sira = df[df['sinif'] == u['sinif']].reset_index(drop=True)[df['ogrenci_no'] == u['ogrenci_no']].index[0] + 1
    except: okul_sira, sinif_sira = '?', '?'

    def get_gif_b64(mod):
        path = os.path.join(os.path.dirname(__file__), 'assets', f'pito_{mod}.gif')
        return f'data:image/gif;base64,{base64.b64encode(open(path, "rb").read()).decode()}' if os.path.exists(path) else ''

    active_anim = f'anim-{anim_toggle}' if e_count > 0 else ''
    success_c = 'success-pulse' if st.session_state.cevap_dogru else ''
    display_total = int(u['toplam_puan']) + (p_xp if st.session_state.cevap_dogru else 0)

    # HUD RENDER
    st.markdown(f'''
        <div class="cyber-hud">
            <div style="display: flex; align-items: center;">
                <div class="hud-pito-gif"><img src="{get_gif_b64(p_mod)}"></div>
                <div style="color: #E0E0E0; font-family: monospace;">👤 <b>{u['ad_soyad']}</b> <span class="rank-badge">🎖️ {rn}</span></div>
            </div>
            <div class="hud-stats-container">
                <div class="hud-capsule">💎 <span class="{active_anim if e_count > 0 else ''}" style="color:#00E5FF; font-weight:900;">{p_xp} XP</span></div>
                <div class="hud-capsule">⚠️ <span class="{active_anim}" style="color:#00E5FF; font-weight:900;">{e_count}/4</span></div>
                <div class="hud-capsule" style="border-color:#ADFF2F;">🏆 <span class="{success_c}" style="color:#ADFF2F; font-weight:900;">{display_total} XP</span></div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    # --- 2. ANA İÇERİK ---
    m_idx = int(u['mevcut_modul']) - 1
    modul = m_list[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])
    st.markdown(f'🎓 **Modül {m_idx + 1}/{len(m_list)}**')
    st.progress((m_idx + 1) / len(m_list))

    cl, cr = st.columns([7.5, 2.5])
    with cl:
        cn1, cn2, cn3 = st.columns([0.4, 0.4, 0.2])
        with cn1: st.markdown(f'💬 *{msgs["welcome"].format(u["ad_soyad"].split()[0])}*')
        with cn2: 
            if st.button("🔍 Geçmiş Egzersizler", use_container_width=True): st.session_state.in_review = True; st.rerun()
        with cn3:
            if st.button("🚪 Çıkış", use_container_width=True): st.session_state.user = None; st.rerun()

        with st.expander(f"📖 {modul['modul_adi']}", expanded=True):
            st.markdown(f"<div style='background:rgba(0,229,255,0.03); padding:15px; border-radius:10px;'>{modul['pito_anlatimi']}</div>", unsafe_allow_html=True)
            st.markdown(f"### 🎯 GÖREV {egz['id']}")
            st.markdown(f'''<div class="gorev-box-html">💡 <b>YÖNERGE:</b> {egz['yonerge']}</div>''', unsafe_allow_html=True)

        if not st.session_state.cevap_dogru and e_count < 4:
            # HATA FIRÇALARI
            if e_count > 0:
                p_msg = random.choice(msgs['errors'][f'level_{min(e_count, 4)}']).format(u['ad_soyad'].split()[0])
                st.error(f"🚨 **Pito:** {p_msg}")
                if e_count >= 3: st.warning(f"💡 **İpucu:** {egz['ipucu']}")

            # INPUT KONTROLÜ
            has_in = 'input' in egz['dogru_cevap_kodu'] or 'input' in egz['sablon']
            has_out = 'print' in egz['dogru_cevap_kodu'] or egz.get('beklenen_cikti', '') != ''
            s_input = ''
            if has_in and has_out:
                with st.popover('⌨️ VERİ GİRİŞİ YAP (GEREKLİ)', use_container_width=True):
                    s_input = st.text_input('Veri:', placeholder='Örn: 5', key=f'in_{egz["id"]}')

            if 'reset_trigger' not in st.session_state: st.session_state.reset_trigger = 0
            u_code = st.text_area('Editor', value=egz['sablon'], height=180, key=f'ed_{egz["id"]}_{st.session_state.reset_trigger}', label_visibility='collapsed')
            
            b1, b2 = st.columns([4, 1.2])
            with b1:
                if st.button("KODU KONTROL ET 🚀", type="primary", use_container_width=True):
                    # 🚨 BOŞLUK / DEĞİŞİKLİK KONTROLÜ (FIXED)
                    if u_code.strip() == egz['sablon'].strip():
                        st.warning("⚠️ Lütfen önce boşluğu doldur veya kodda değişiklik yap!")
                    elif (has_in and has_out) and not s_input.strip():
                        st.warning("⚠️ Önce veri girişi yapmalısın!")
                    else:
                        st.session_state.current_code = u_code
                        st.session_state.user_input_val = s_input
                        if normalize_fonksiyonu(u_code) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                            st.session_state.cevap_dogru = True; st.balloons(); st.rerun()
                        else:
                            st.session_state.error_count += 1; st.rerun()
            with b2:
                if st.button("🔄 SIFIRLA", use_container_width=True): st.session_state.reset_trigger += 1; st.rerun()

        elif st.session_state.cevap_dogru:
            st.success("✅ Harika iş!")
            out = kod_calistir_cikti_al(st.session_state.current_code, st.session_state.get('user_input_val', '')) if 'print' in st.session_state.current_code else egz.get('beklenen_cikti', '')
            st.markdown(f'<div class="terminal-label">🖥️ SİBER-ÇIKTI</div><div class="cyber-terminal">{out if out else "Bu kod çıktı vermez."}</div>', unsafe_allow_html=True)
            if st.button("SIRADAKİ GÖREVE GEÇ ➡️", type="primary", use_container_width=True):
                s_i = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_i]['id'], u['mevcut_modul']) if s_i < len(modul['egzersizler']) else (f'{int(u["mevcut_modul"])+1}.1', int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(p_xp, st.session_state.current_code, egz['id'], n_id, n_m)

        elif e_count >= 4:
            st.warning("🚨 Pes etme yok, çözümü incele:")
            st.code(egz['cozum'], language="python")
            out = egz.get('beklenen_cikti', '')
            st.markdown(f'<div class="terminal-label">🖥️ SİBER-ÇIKTI (ÇÖZÜM)</div><div class="cyber-terminal">{out if out else "Bu kod çıktı vermez."}</div>', unsafe_allow_html=True)
            if st.button("DEVAM ET ➡️", type="primary", use_container_width=True):
                s_i = modul['egzersizler'].index(egz) + 1
                n_id, n_m = (modul['egzersizler'][s_i]['id'], u['mevcut_modul']) if s_i < len(modul['egzersizler']) else (f'{int(u["mevcut_modul"])+1}.1', int(u['mevcut_modul']) + 1)
                ilerleme_fonksiyonu(0, "Çözüm İncelendi", egz['id'], n_id, n_m)

    with cr:
        # SİBER-SIDEBAR STATS KARTI (NİHAİ MÜHÜR)
        st.markdown(f'''
            <div class="sidebar-stats-card">
                <div style="font-size:0.8rem; color:#00E5FF; font-weight:bold; letter-spacing:1px;">📊 SİBER DURUM</div>
                <div class="sidebar-stats-grid">
                    <div class="sidebar-stat-box"><div class="sidebar-stat-label">SINIFIM</div><div class="sidebar-stat-val">#{sinif_sira}</div></div>
                    <div class="sidebar-stat-box"><div class="sidebar-stat-label">OKULUM</div><div class="sidebar-stat-val">#{okul_sira}</div></div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
