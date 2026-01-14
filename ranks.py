import streamlit as st
import pandas as pd

def rütbe_ata(xp):
    """XP değerine göre rütbe ve CSS sınıfı döner."""
    if xp >= 1000: return "🏆 Bilge", "badge-bilge"
    if xp >= 500: return "🔥 Savaşçı", "badge-savasci"
    if xp >= 200: return "🐍 Pythonist", "badge-pythonist"
    return "🥚 Çömez", "badge-comez"

def liderlik_tablosu_goster(supabase, current_user=None):
    # --- 0. SİBER-KOMUTA PANELİ (SCROLL & CONTRAST MÜHRÜ) ---
    st.markdown('''
        <style>
        /* ŞAMPİYON PANO (ZİRVEDEKİ ŞUBE) */
        .champion-pano-v4 {
            background-color: #000000;
            border: 2px solid #ADFF2F;
            border-left: 8px solid #ADFF2F;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            margin-bottom: 25px;
        }
        .pano-title { color: #ADFF2F; font-size: 0.75rem; font-weight: 900; letter-spacing: 2px; }
        .pano-val { color: #FFFFFF; font-size: 1.7rem; font-weight: 950; margin-top: 5px; }

        /* TAB TASARIMI: YÜKSEK KONTRASTLI SEKMELER */
        .stTabs [data-baseweb="tab-list"] { 
            gap: 12px; background-color: #0e1117; 
            padding: 8px; border-radius: 10px; 
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #1c2128 !important;
            color: #AAAAAA !important;
            border: 1px solid #30363d !important;
            border-radius: 6px !important;
            padding: 10px 15px !important;
            font-weight: 800 !important;
            font-size: 0.85rem !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #00E5FF !important;
            color: #000000 !important;
            border: 1px solid #FFFFFF !important;
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
        }

        /* KAYDIRILABİLİR LİSTE ALANI (EKRANA SIĞMA GARANTİLİ) */
        .scroll-v4 { 
            max-height: 420px; 
            overflow-y: auto; 
            padding-right: 10px;
            margin-top: 15px;
        }
        .scroll-v4::-webkit-scrollbar { width: 5px; }
        .scroll-v4::-webkit-scrollbar-thumb { background: #00E5FF; border-radius: 10px; }

        /* VERİ SATIRLARI (KOMPAKT HUD) */
        .row-v4 {
            display: flex; justify-content: space-between; align-items: center;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 8px;
        }
        .is-me-v4 { border: 2px solid #ADFF2F !important; background: #0d1117 !important; }

        .rank-num-v4 { color: #00E5FF; font-weight: 950; font-size: 1rem; width: 35px; }
        .name-v4 { color: #FFFFFF; font-weight: 700; font-size: 0.9rem; }
        .xp-v4 { color: #ADFF2F; font-family: 'Fira Code', monospace; font-weight: 900; font-size: 1rem; }

        .badge-v4 {
            font-size: 0.6rem; padding: 2px 6px; border-radius: 4px;
            font-weight: 900; text-transform: uppercase;
        }
        .badge-bilge { background: #FFD700; color: #000; }
        .badge-savasci { background: #FF4500; color: #fff; }
        .badge-pythonist { background: #00E5FF; color: #000; }
        .badge-comez { background: #30363d; color: #888; }
        </style>
    ''', unsafe_allow_html=True)

    try:
        res = supabase.table("kullanicilar").select("*").execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

        # --- 1. ŞAMPİYON PANO (ZİRVEDEKİ ŞUBE) ---
        if not df.empty:
            class_stats = df.groupby('sinif')['toplam_puan'].mean().sort_values(ascending=False).reset_index()
            winner = class_stats.iloc[0]
            st.markdown(f'''
                <div class="champion-pano-v4">
                    <div class="pano-title">🛰️ ZİRVEDEKİ ŞUBE</div>
                    <div class="pano-val">{winner['sinif']}</div>
                    <div style="color:#ADFF2F; font-size:0.8rem; font-weight:bold; font-family:monospace;">LDR_AVG: {int(winner['toplam_puan'])} XP</div>
                </div>
            ''', unsafe_allow_html=True)

        # --- 2. TABS (SINIF SIRALAMAM SOLDA) ---
        t1, t2 = st.tabs(["📍 SINIF SIRALAMAM", "🌍 OKUL LİDERLERİ"])
        
        with t1: # SINIF SIRALAMASI
            if current_user and not df.empty:
                df_sinif = df[df['sinif'] == current_user['sinif']].sort_values(by="toplam_puan", ascending=False)
                st.markdown('<div class="scroll-v4">', unsafe_allow_html=True)
                for i, r in enumerate(df_sinif.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    is_me = "is-me-v4" if r.ogrenci_no == current_user['ogrenci_no'] else ""
                    st.markdown(f'''
                        <div class="row-v4 {is_me}">
                            <div style="display:flex; align-items:center; gap:12px;">
                                <span class="rank-num-v4">#{i:02d}</span>
                                <div>
                                    <div class="name-v4">{r.ad_soyad[:15]}</div>
                                    <span class="badge-v4 {rc}">{rn}</span>
                                </div>
                            </div>
                            <div class="xp-v4">{int(r.toplam_puan)}</div>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Erişim için siber-geçiş gerekiyor.")

        with t2: # OKUL GENELİ
            if not df.empty:
                top_okul = df.sort_values(by="toplam_puan", ascending=False).head(30)
                st.markdown('<div class="scroll-v4">', unsafe_allow_html=True)
                for i, r in enumerate(top_okul.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:02d}"
                    st.markdown(f'''
                        <div class="row-v4">
                            <div style="display:flex; align-items:center; gap:12px;">
                                <span class="rank-num-v4">{icon}</span>
                                <div>
                                    <div class="name-v4">{r.ad_soyad[:15]}</div>
                                    <span class="badge-v4 {rc}">{rn}</span>
                                </div>
                            </div>
                            <div class="xp-v4">{int(r.toplam_puan)}</div>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"RANK_DATA_ERR: {e}")
