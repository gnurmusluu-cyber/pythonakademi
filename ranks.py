import streamlit as st
import pandas as pd

def rütbe_ata(xp):
    if xp >= 1000: return "🏆 Bilge", "badge-bilge"
    if xp >= 500: return "🔥 Savaşçı", "badge-savasci"
    if xp >= 200: return "🐍 Pythonist", "badge-pythonist"
    return "🥚 Çömez", "badge-comez"

def liderlik_tablosu_goster(supabase, current_user=None):
    # --- 0. SİBER-BAŞLIK VE TAB TASARIMI (HUD MÜHRÜ) ---
    st.markdown('''
        <style>
        /* ANA BAŞLIK: SİBER-PLAKA */
        .cyber-header {
            background: linear-gradient(90deg, transparent, rgba(0, 229, 255, 0.1), transparent);
            border-top: 1px solid #00E5FF;
            border-bottom: 1px solid #00E5FF;
            padding: 12px 0;
            margin-bottom: 25px;
            text-align: center;
        }
        .cyber-header h3 {
            color: #00E5FF;
            text-transform: uppercase;
            letter-spacing: 5px; /* Siber-boşluk */
            text-shadow: 0 0 15px #00E5FF;
            margin: 0;
            font-family: 'Fira Code', monospace;
            font-size: 1.1rem !important;
            font-weight: 900;
        }

        /* TAB TASARIMI: SİBER-SEKMELER */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
        .stTabs [data-baseweb="tab"] {
            height: 38px;
            background-color: rgba(22, 27, 34, 0.8) !important;
            border: 1px solid rgba(0, 229, 255, 0.2) !important;
            border-radius: 4px !important;
            color: #666 !important;
            transition: 0.3s;
            font-family: 'Fira Code', monospace;
            font-size: 0.75rem !important;
        }
        .stTabs [aria-selected="true"] {
            border-color: #00E5FF !important;
            color: #00E5FF !important;
            background-color: rgba(0, 229, 255, 0.1) !important;
            box-shadow: inset 0 0 10px rgba(0, 229, 255, 0.2);
        }

        /* ŞAMPİYON PANO (YENİLENMİŞ) */
        .champion-pano {
            background: rgba(0, 229, 255, 0.05);
            border: 1px solid #00E5FF;
            border-left: 6px solid #00E5FF;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 30px;
            position: relative;
        }
        .champion-pano:before {
            content: "SYSTEM_ALPHA_RANK";
            position: absolute; top: 2px; right: 8px;
            font-size: 0.55rem; color: rgba(0, 229, 255, 0.3);
            font-family: monospace;
        }
        .champion-title { color: #ADFF2F; font-size: 0.75rem; font-weight: 900; letter-spacing: 1.5px; }
        .champion-name { color: #FFFFFF; font-size: 1.7rem; font-weight: 950; text-shadow: 0 0 10px rgba(255,255,255,0.2); }

        /* LİSTE TASARIMI */
        .rank-scroll-area { max-height: 380px; overflow-y: auto; padding-right: 8px; }
        .rank-row {
            display: flex; justify-content: space-between; align-items: center;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 4px;
            padding: 10px 12px;
            margin-bottom: 8px;
        }
        .rank-num { font-family: 'Fira Code', monospace; font-weight: bold; width: 25px; color: #00E5FF; font-size: 0.9rem; }
        .xp-val { color: #ADFF2F; font-family: 'Fira Code', monospace; font-weight: bold; font-size: 0.95rem; }
        </style>
    ''', unsafe_allow_html=True)

    try:
        res = supabase.table("kullanicilar").select("*").execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

        # --- 1. ŞAMPİYON PANO ---
        if not df.empty:
            class_stats = df.groupby('sinif')['toplam_puan'].mean().sort_values(ascending=False).reset_index()
            winner = class_stats.iloc[0]
            st.markdown(f'''
                <div class="champion-pano">
                    <div class="champion-title">🏆 ZİRVEDEKİ ŞUBE</div>
                    <div class="champion-name">{winner['sinif']}</div>
                    <div style="color:#00E5FF; font-size:0.85rem; font-family:monospace; margin-top:5px;">AVG_SCORE: {int(winner['toplam_puan'])} XP</div>
                </div>
            ''', unsafe_allow_html=True)

        # --- 2. ANA BAŞLIK (SİBER-PLAKA) ---
        st.markdown('<div class="cyber-header"><h3>Onur Kürsüsü</h3></div>', unsafe_allow_html=True)

        t1, t2 = st.tabs(["[ 🌍 OKUL ]", "[ 📍 SINIF ]"])
        
        with t1:
            if not df.empty:
                top_okul = df.sort_values(by="toplam_puan", ascending=False).head(20)
                st.markdown('<div class="rank-scroll-area">', unsafe_allow_html=True)
                for i, r in enumerate(top_okul.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    st.markdown(f'''
                        <div class="rank-row">
                            <div style="display:flex; align-items:center; gap:12px;">
                                <span class="rank-num">{i:02d}</span>
                                <div>
                                    <div style="color:#FFF; font-size:0.9rem; font-weight:600;">{r.ad_soyad[:18]}</div>
                                    <span class="badge-mini {rc}" style="font-size:0.6rem; padding:1px 5px; border-radius:2px; font-weight:800; text-transform:uppercase;">{rn}</span>
                                </div>
                            </div>
                            <div class="xp-val">{int(r.toplam_puan)}</div>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with t2:
            if current_user and not df.empty:
                df_sinif = df[df['sinif'] == current_user['sinif']].sort_values(by="toplam_puan", ascending=False)
                st.markdown('<div class="rank-scroll-area">', unsafe_allow_html=True)
                for i, r in enumerate(df_sinif.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    is_me = "border-color:#ADFF2F; background:rgba(173,255,47,0.05);" if r.ogrenci_no == current_user['ogrenci_no'] else ""
                    st.markdown(f'''
                        <div class="rank-row" style="{is_me}">
                            <div style="display:flex; align-items:center; gap:12px;">
                                <span class="rank-num">#{i:02d}</span>
                                <div>
                                    <div style="color:#FFF; font-size:0.9rem; font-weight:600;">{r.ad_soyad[:18]}</div>
                                    <span class="badge-mini {rc}" style="font-size:0.6rem; padding:1px 5px; border-radius:2px; font-weight:800; text-transform:uppercase;">{rn}</span>
                                </div>
                            </div>
                            <div class="xp-val">{int(r.toplam_puan)}</div>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"RANK_INIT_ERR: {e}")
