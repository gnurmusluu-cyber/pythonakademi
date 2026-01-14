import streamlit as st
import pandas as pd

def rütbe_ata(xp):
    if xp >= 1000: return "🏆 Bilge", "badge-bilge"
    if xp >= 500: return "🔥 Savaşçı", "badge-savasci"
    if xp >= 200: return "🐍 Pythonist", "badge-pythonist"
    return "🥚 Çömez", "badge-comez"

def liderlik_tablosu_goster(supabase, current_user=None):
    # --- 0. SİBER-ESTETİK CSS (GLASSMORPHISM & NEON MINIMALISM) ---
    st.markdown('''
        <style>
        /* GENEL BAŞLIK: LASER-CUT STYLE */
        .cyber-title {
            color: #00E5FF;
            font-family: 'Fira Code', monospace;
            font-size: 1.1rem;
            font-weight: 900;
            text-align: center;
            letter-spacing: 3px;
            margin-bottom: 20px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(0, 229, 255, 0.3);
            text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
        }

        /* ŞAMPİYON PANO (ZARİF & CAM EFEKTİ) */
        .champion-glass-pano {
            background: rgba(0, 229, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 229, 255, 0.2);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }
        .pano-sub { color: #ADFF2F; font-size: 0.7rem; font-weight: 800; letter-spacing: 2px; }
        .pano-main { color: #FFFFFF; font-size: 1.6rem; font-weight: 900; margin: 5px 0; }

        /* TAB TASARIMI (SADECE ALT ÇİZGİ) */
        .stTabs [data-baseweb="tab-list"] { gap: 15px; }
        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            border: none !important;
            color: #555 !important;
            font-size: 0.85rem !important;
            font-weight: 700 !important;
            padding: 5px 0 !important;
        }
        .stTabs [aria-selected="true"] {
            color: #00E5FF !important;
            border-bottom: 2px solid #00E5FF !important;
        }

        /* LİSTE TASARIMI (TEMİZ & AKICI) */
        .rank-scroll-box { max-height: 400px; overflow-y: auto; padding-right: 5px; }
        .rank-scroll-box::-webkit-scrollbar { width: 2px; }
        .rank-scroll-box::-webkit-scrollbar-thumb { background: rgba(0, 229, 255, 0.3); }

        .rank-item {
            display: flex; justify-content: space-between; align-items: center;
            padding: 10px 5px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            transition: 0.2s;
        }
        .rank-item:hover { background: rgba(0, 229, 255, 0.03); }
        
        .is-me-item { background: rgba(173, 255, 47, 0.05) !important; border-left: 3px solid #ADFF2F; padding-left: 10px; }

        .item-rank-num { color: #00E5FF; font-family: monospace; font-weight: bold; width: 25px; }
        .item-name { color: #E0E0E0; font-size: 0.9rem; }
        .item-xp { color: #ADFF2F; font-weight: bold; font-family: 'Fira Code', monospace; }

        .badge-slim { font-size: 0.6rem; padding: 1px 4px; border-radius: 3px; font-weight: 900; }
        .badge-bilge { background: #FFD700; color: #000; }
        .badge-comez { background: #333; color: #888; }
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
                <div class="champion-glass-pano">
                    <div class="pano-sub">👑 SİSTEM LİDERİ ŞUBE</div>
                    <div class="pano-main">{winner['sinif']}</div>
                    <div style="color:rgba(0,229,255,0.6); font-size:0.75rem; font-family:monospace;">AVERAGE_XP: {int(winner['toplam_puan'])}</div>
                </div>
            ''', unsafe_allow_html=True)

        # --- 2. ANA BAŞLIK ---
        st.markdown('<div class="cyber-title">ONUR KÜRSÜSÜ</div>', unsafe_allow_html=True)

        t1, t2 = st.tabs(["🌍 Okul Geneli", "📍 Sınıf Sıralamam"])
        
        with t1:
            if not df.empty:
                top_okul = df.sort_values(by="toplam_puan", ascending=False).head(20)
                st.markdown('<div class="rank-scroll-box">', unsafe_allow_html=True)
                for i, r in enumerate(top_okul.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    st.markdown(f'''
                        <div class="rank-item">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <span class="item-rank-num">{i:02d}</span>
                                <div>
                                    <div class="item-name">{r.ad_soyad[:18]}</div>
                                    <span class="badge-slim {rc}">{rn}</span>
                                </div>
                            </div>
                            <div class="item-xp">{int(r.toplam_puan)}</div>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with t2:
            if current_user and not df.empty:
                df_sinif = df[df['sinif'] == current_user['sinif']].sort_values(by="toplam_puan", ascending=False)
                st.markdown('<div class="rank-scroll-box">', unsafe_allow_html=True)
                for i, r in enumerate(df_sinif.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    is_me = "is-me-item" if r.ogrenci_no == current_user['ogrenci_no'] else ""
                    st.markdown(f'''
                        <div class="rank-item {is_me}">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <span class="item-rank-num">#{i:02d}</span>
                                <div>
                                    <div class="item-name">{r.ad_soyad[:18]}</div>
                                    <span class="badge-slim {rc}">{rn}</span>
                                </div>
                            </div>
                            <div class="item-xp">{int(r.toplam_puan)}</div>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"RANK_DATA_ERROR: {e}")
