import streamlit as st
import pandas as pd

def rütbe_ata(xp):
    if xp >= 1000: return "🏆 Bilge", "badge-bilge"
    if xp >= 500: return "🔥 Savaşçı", "badge-savasci"
    if xp >= 200: return "🐍 Pythonist", "badge-pythonist"
    return "🥚 Çömez", "badge-comez"

def liderlik_tablosu_goster(supabase, current_user=None):
    # --- 0. NANO-SİBER CSS (MAKSİMUM DİKEY TASARRUF) ---
    st.markdown('''
        <style>
        /* ZİRVEDEKİ ŞUBE: MİKRO SATIR */
        .micro-champ {
            background: rgba(173, 255, 47, 0.05);
            border: 1px solid #ADFF2F;
            border-radius: 4px;
            padding: 4px 10px;
            text-align: center;
            margin-bottom: 8px;
            font-size: 0.8rem;
        }

        /* TAB TASARIMI: ULTRA-İNCE HUD */
        .stTabs [data-baseweb="tab-list"] { gap: 2px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #1c2128 !important;
            color: #888 !important;
            border-radius: 4px 4px 0 0 !important;
            padding: 5px 10px !important;
            font-size: 0.75rem !important;
            height: 30px !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #00E5FF !important;
            color: #000 !important;
            font-weight: 900 !important;
        }

        /* NANO-SCROLL (260PX SABİT) */
        .nano-scroll { 
            max-height: 260px; 
            overflow-y: auto; 
            padding-right: 3px;
            margin-top: 5px;
        }
        .nano-scroll::-webkit-scrollbar { width: 2px; }
        .nano-scroll::-webkit-scrollbar-thumb { background: #00E5FF; }

        /* VERİ SATIRLARI (HÜCRESEL YAPI) */
        .nano-row {
            display: flex; justify-content: space-between; align-items: center;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 4px;
            padding: 4px 8px;
            margin-bottom: 3px;
        }
        .is-me-nano { border: 1.5px solid #ADFF2F !important; background: #0d1117 !important; }

        .n-rank { color: #00E5FF; font-weight: 900; font-size: 0.8rem; width: 25px; }
        .n-name { color: #FFFFFF; font-size: 0.8rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .n-xp { color: #ADFF2F; font-family: 'Fira Code', monospace; font-size: 0.8rem; font-weight: bold; }

        .n-badge {
            font-size: 0.5rem; padding: 0px 3px; border-radius: 2px;
            text-transform: uppercase; font-weight: bold; margin-top: -2px;
        }
        .badge-bilge { background: #FFD700; color: #000; }
        .badge-comez { background: #333; color: #888; }
        </style>
    ''', unsafe_allow_html=True)

    try:
        res = supabase.table("kullanicilar").select("*").execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

        # --- 1. MİKRO ŞAMPİYON SATIRI ---
        if not df.empty:
            class_stats = df.groupby('sinif')['toplam_puan'].mean().sort_values(ascending=False).reset_index()
            winner = class_stats.iloc[0]
            st.markdown(f'''
                <div class="micro-champ">
                    <span style="color:#ADFF2F; font-weight:bold;">👑 ZİRVE:</span>
                    <span style="color:#FFF;"> {winner['sinif']} Şubesi</span>
                </div>
            ''', unsafe_allow_html=True)

        # --- 2. TABS (SINIF SOLDA, OKUL SAĞDA) ---
        t1, t2 = st.tabs(["📍 SINIFIM", "🌍 OKUL"])
        
        with t1: # SINIF SIRALAMASI
            if current_user and not df.empty:
                df_sinif = df[df['sinif'] == current_user['sinif']].sort_values(by="toplam_puan", ascending=False)
                st.markdown('<div class="nano-scroll">', unsafe_allow_html=True)
                for i, r in enumerate(df_sinif.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    is_me = "is-me-nano" if r.ogrenci_no == current_user['ogrenci_no'] else ""
                    st.markdown(f'''
                        <div class="nano-row {is_me}">
                            <div style="display:flex; align-items:center; gap:6px;">
                                <span class="n-rank">#{i:02d}</span>
                                <div>
                                    <div class="n-name">{r.ad_soyad[:12]}</div>
                                    <span class="n-badge {rc}">{rn}</span>
                                </div>
                            </div>
                            <div class="n-xp">{int(r.toplam_puan)}</div>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with t2: # OKUL GENELİ
            if not df.empty:
                top_okul = df.sort_values(by="toplam_puan", ascending=False).head(30)
                st.markdown('<div class="nano-scroll">', unsafe_allow_html=True)
                for i, r in enumerate(top_okul.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:02d}"
                    st.markdown(f'''
                        <div class="nano-row">
                            <div style="display:flex; align-items:center; gap:6px;">
                                <span class="n-rank">{icon}</span>
                                <div>
                                    <div class="n-name">{r.ad_soyad[:12]}</div>
                                    <span class="n-badge {rc}">{rn}</span>
                                </div>
                            </div>
                            <div class="n-xp">{int(r.toplam_puan)}</div>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"ERR_RANK: {e}")
