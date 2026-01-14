import streamlit as st
import pandas as pd

def rütbe_ata(xp):
    if xp >= 1000: return "🏆 Bilge", "badge-bilge"
    if xp >= 500: return "🔥 Savaşçı", "badge-savasci"
    if xp >= 200: return "🐍 Pythonist", "badge-pythonist"
    return "🥚 Çömez", "badge-comez"

def liderlik_tablosu_goster(supabase, current_user=None):
    # --- 0. SİBER-KOMUTA PANELİ (ULTRA-KOMPAKT & SCROLL MÜHRÜ) ---
    st.markdown('''
        <style>
        /* ZİRVEDEKİ ŞUBE: İNCE HUD ŞERİDİ */
        .champion-strip {
            background: rgba(173, 255, 47, 0.1);
            border: 1px solid #ADFF2F;
            border-radius: 6px;
            padding: 8px;
            text-align: center;
            margin-bottom: 15px;
        }
        .strip-text { color: #ADFF2F; font-size: 0.75rem; font-weight: 900; letter-spacing: 1px; }
        .strip-val { color: #FFFFFF; font-size: 1.1rem; font-weight: 950; margin-left: 10px; }

        /* TAB TASARIMI: YÜKSEK KONTRASTLI VE KÜÇÜK */
        .stTabs [data-baseweb="tab-list"] { gap: 5px; background-color: #0e1117; padding: 2px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #1c2128 !important;
            color: #888 !important;
            border: 1px solid #30363d !important;
            border-radius: 4px !important;
            padding: 8px 12px !important;
            font-size: 0.8rem !important;
            height: 35px !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #00E5FF !important;
            color: #000000 !important;
            font-weight: 900 !important;
        }

        /* KAYDIRILABİLİR ALAN (300PX SABİT) */
        .scroll-v5 { 
            max-height: 300px; 
            overflow-y: auto; 
            padding-right: 5px;
            margin-top: 10px;
        }
        .scroll-v5::-webkit-scrollbar { width: 3px; }
        .scroll-v5::-webkit-scrollbar-thumb { background: #00E5FF; }

        /* VERİ SATIRLARI (İNCE TASARIM) */
        .row-v5 {
            display: flex; justify-content: space-between; align-items: center;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 6px 10px;
            margin-bottom: 5px;
        }
        .is-me-v5 { border: 1.5px solid #ADFF2F !important; background: #0d1117 !important; }

        .rank-v5 { color: #00E5FF; font-weight: 950; font-size: 0.9rem; width: 30px; }
        .name-v5 { color: #FFFFFF; font-weight: 700; font-size: 0.85rem; }
        .xp-v5 { color: #ADFF2F; font-family: 'Fira Code', monospace; font-weight: 900; font-size: 0.9rem; }

        .badge-v5 {
            font-size: 0.55rem; padding: 1px 4px; border-radius: 3px;
            font-weight: 900; text-transform: uppercase;
        }
        .badge-bilge { background: #FFD700; color: #000; }
        .badge-pythonist { background: #00E5FF; color: #000; }
        </style>
    ''', unsafe_allow_html=True)

    try:
        res = supabase.table("kullanicilar").select("*").execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

        # --- 1. ZİRVEDEKİ ŞUBE ŞERİDİ ---
        if not df.empty:
            class_stats = df.groupby('sinif')['toplam_puan'].mean().sort_values(ascending=False).reset_index()
            winner = class_stats.iloc[0]
            st.markdown(f'''
                <div class="champion-strip">
                    <span class="strip-text">👑 ZİRVEDEKİ ŞUBE:</span>
                    <span class="strip-val">{winner['sinif']}</span>
                </div>
            ''', unsafe_allow_html=True)

        # --- 2. TABS (SINIF SOLDA, OKUL SAĞDA) ---
        t1, t2 = st.tabs(["📍 SINIFIM", "🌍 OKUL"])
        
        with t1: # SINIF SIRALAMASI
            if current_user and not df.empty:
                df_sinif = df[df['sinif'] == current_user['sinif']].sort_values(by="toplam_puan", ascending=False)
                st.markdown('<div class="scroll-v5">', unsafe_allow_html=True)
                for i, r in enumerate(df_sinif.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    is_me = "is-me-v5" if r.ogrenci_no == current_user['ogrenci_no'] else ""
                    st.markdown(f'''
                        <div class="row-v5 {is_me}">
                            <div style="display:flex; align-items:center; gap:8px;">
                                <span class="rank-v5">#{i:02d}</span>
                                <div>
                                    <div class="name-v5">{r.ad_soyad[:15]}</div>
                                    <span class="badge-v5 {rc}">{rn}</span>
                                </div>
                            </div>
                            <div class="xp-v5">{int(r.toplam_puan)}</div>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with t2: # OKUL GENELİ
            if not df.empty:
                top_okul = df.sort_values(by="toplam_puan", ascending=False).head(30)
                st.markdown('<div class="scroll-v5">', unsafe_allow_html=True)
                for i, r in enumerate(top_okul.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:02d}"
                    st.markdown(f'''
                        <div class="row-v5">
                            <div style="display:flex; align-items:center; gap:8px;">
                                <span class="rank-v5">{icon}</span>
                                <div>
                                    <div class="name-v5">{r.ad_soyad[:15]}</div>
                                    <span class="badge-v5 {rc}">{rn}</span>
                                </div>
                            </div>
                            <div class="xp-v5">{int(r.toplam_puan)}</div>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Sistem Hatası: {e}")
