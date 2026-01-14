import streamlit as st
import random
import pandas as pd

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- 0. SİBER-HUD VE EDİTÖR CSS ---
    st.markdown("""
        <style>
        /* ANA PANEL VE KARTLAR */
        .hero-panel {
            background: rgba(0, 229, 255, 0.05);
            border-left: 5px solid #00E5FF;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        /* ÖĞRENCİ ÖZEL İSTATİSTİK KARTI */
        .student-stats-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
        }
        .stat-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 10px;
        }
        .stat-item {
            background: rgba(0, 229, 255, 0.05);
            padding: 8px;
            border-radius: 6px;
            border: 1px solid rgba(0, 229, 255, 0.1);
        }
        .stat-label { font-size: 0.7rem; color: #888; text-transform: uppercase; }
        .stat-value { font-size: 1.1rem; color: #ADFF2F; font-weight: 900; font-family: monospace; }
        
        /* EDİTÖR */
        div[data-testid="stTextArea"] textarea {
            background-color: #0e1117 !important;
            color: #ADFF2F !important;
            font-family: 'Courier New', monospace !important;
            border: 1px solid #30363d !important;
        }
        </style>
    """, unsafe_allow_html=True)

    m_idx = int(u['mevcut_modul']) - 1
    total_m = len(mufredat)
    ad_k = u['ad_soyad'].split()[0]

    # --- 1. SIRALAMA HESAPLAMA MOTORU ---
    try:
        res = supabase.table("kullanicilar").select("*").execute()
        all_users = pd.DataFrame(res.data)
        
        # Okul Sıralaması
        all_users = all_users.sort_values(by="toplam_puan", ascending=False).reset_index(drop=True)
        okul_sira = all_users[all_users['ogrenci_no'] == u['ogrenci_no']].index[0] + 1
        
        # Sınıf Sıralaması
        sinif_users = all_users[all_users['sinif'] == u['sinif']].sort_values(by="toplam_puan", ascending=False).reset_index(drop=True)
        sinif_sira = sinif_users[sinif_users['ogrenci_no'] == u['ogrenci_no']].index[0] + 1
    except:
        okul_sira, sinif_sira = "?", "?"

    # --- 2. ÜST İLERLEME ÇUBUKLARI ---
    st.progress(min((m_idx) / total_m, 1.0))
    
    modul = mufredat[m_idx]
    egz = next((e for e in modul['egzersizler'] if e['id'] == str(u['mevcut_egzersiz'])), modul['egzersizler'][0])

    # --- 3. ANA DÜZEN ---
    cl, cr = st.columns([7, 3])
    
    with cl:
        # Hero Panel
        rn, rc = ranks_module.rütbe_ata(u['toplam_puan'])
        st.markdown(f"""
            <div class='hero-panel'>
                <h3 style='margin:0; color:#00E5FF;'>🚀 {modul['modul_adi']}</h3>
                <p style='margin:5px 0 0 0;'>{u['ad_soyad']} | <b style='color:#ADFF2F;'>{rn}</b></p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📖 KONU ANLATIMI", expanded=True):
            st.markdown(f"<div style='background:#000; padding:15px; border-radius:10px;'>{modul.get('pito_anlatimi', '...')}</div>", unsafe_allow_html=True)
        
        # Editör ve Görev Akışı (Mevcut mantık korunur)
        st.markdown(f"**GÖREV {egz['id']}:** {egz['yonerge']}")
        
        k_i = st.text_area("Editor", value=egz['sablon'], height=180, label_visibility="collapsed")
        
        if st.button("Kodu Kontrol Et 🔍", use_container_width=True):
            if normalize_fonksiyonu(k_i) == normalize_fonksiyonu(egz['dogru_cevap_kodu']):
                st.session_state.cevap_dogru = True
                st.balloons()
            else:
                st.session_state.error_count += 1
            st.rerun()

    with cr:
        # --- ÖĞRENCİ SİBER-STAT KARTI ---
        st.markdown(f'''
            <div class="student-stats-card">
                <div style="font-size:0.8rem; color:#00E5FF; font-weight:bold;">SİBER DURUMUN</div>
                <div class="stat-grid">
                    <div class="stat-item">
                        <div class="stat-label">SINIFIM</div>
                        <div class="stat-value">#{sinif_sira}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">OKULUM</div>
                        <div class="stat-value">#{okul_sira}</div>
                    </div>
                </div>
                <div style="margin-top:10px; font-size:0.9rem;">
                    Toplam: <b style="color:#ADFF2F;">{int(u['toplam_puan'])} XP</b>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
        # Liderlik Tablosu
        ranks_module.liderlik_tablosu_goster(supabase, current_user=u)
