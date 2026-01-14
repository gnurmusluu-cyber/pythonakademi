import streamlit as st
import pandas as pd

def rütbe_ata(xp):
    if xp >= 1000: return "🏆 Bilge", "badge-bilge"
    if xp >= 500: return "🔥 Savaşçı", "badge-savasci"
    if xp >= 200: return "🐍 Pythonist", "badge-pythonist"
    return "🥚 Çömez", "badge-comez"

def liderlik_tablosu_goster(supabase, current_user=None):
    # --- 0. OKUNABİLİRLİK VE KONTRAST MÜHRÜ ---
    st.markdown('''
        <style>
        /* ANA BAŞLIK: NET VE GÜÇLÜ */
        .cyber-title {
            color: #FFFFFF;
            font-family: 'Fira Code', monospace;
            font-size: 1.2rem;
            font-weight: 900;
            text-align: center;
            letter-spacing: 2px;
            margin-bottom: 20px;
            text-shadow: 0 0 10px rgba(0, 229, 255, 0.8);
        }

        /* TAB TASARIMI (OKUNABİLİRLİK ODAKLI) */
        .stTabs [data-baseweb="tab-list"] { 
            gap: 10px; 
            border-bottom: 1px solid rgba(0, 229, 255, 0.2);
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: transparent !important;
            color: #888888 !important; /* Pasifken gri, göz yormaz */
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            padding: 10px 15px !important;
            transition: 0.3s;
        }

        /* TIKLANDIĞINDA (AKTİF DURUM) */
        .stTabs [aria-selected="true"] {
            color: #00E5FF !important; /* Parlak Cyan metin */
            background-color: rgba(0, 229, 255, 0.1) !important;
            border-bottom: 3px solid #00E5FF !important;
            text-shadow: 0 0 8px rgba(0, 229, 255, 0.5);
        }

        /* ŞAMPİYON PANO (ZARİF & NET) */
        .champion-glass-pano {
            background: rgba(0, 229, 255, 0.08);
            border: 1px solid #00E5FF;
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            margin-bottom: 25px;
        }
        .pano-sub { color: #ADFF2F; font-size: 0.75rem; font-weight: 800; letter-spacing: 2px; }
        .pano-main { color: #FFFFFF; font-size: 1.7rem; font-weight: 950; margin: 5px 0; }

        /* LİSTE TASARIMI */
        .rank-scroll-box { max-height: 400px; overflow-y: auto; padding-right: 5px; }
        .rank-scroll-box::-webkit-scrollbar { width: 3px; }
        .rank-scroll-area::-webkit-scrollbar-thumb { background: #00E5FF; }

        .rank-item {
            display: flex; justify-content: space-between; align-items: center;
            padding: 12px 10px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 8px;
            margin-bottom: 8px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .is-me-item { 
            border: 1px solid #ADFF2F !important; 
            background: rgba(173, 255, 47, 0.05) !important; 
        }

        .item-rank-num { color: #00E5FF; font-family: 'Fira Code', monospace; font-weight: bold; width: 30px; }
        .item-name { color: #FFFFFF; font-size: 0.95rem; font-weight: 600; }
        .item-xp { color: #ADFF2F; font-weight: bold; font-family: 'Fira Code', monospace; font-size: 1rem; }
        </style>
    ''', unsafe_allow_html=True)

    try:
        res = supabase.table("kullanicilar").select("*").execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

        # --- 1. ŞAMPİYON PANO (BAĞIMSIZ ÜST PANEL) ---
        if not df.empty:
            class_stats = df.groupby('sinif')['toplam_puan'].mean().sort_values(ascending=False).reset_index()
            winner = class_stats.iloc[0]
            st.markdown(f'''
                <div class="champion-glass-pano">
                    <div class="pano-sub">👑 SİBER LİDER ŞUBE</div>
                    <div class="pano-main">{winner['sinif']}</div>
                    <div style="color:#00E5FF; font-size:0.8rem; font-family:monospace; font-weight:bold;">PUAN ORTALAMASI: {int(winner['toplam_puan'])} XP</div>
                </div>
            ''', unsafe_allow_html=True)

        # --- 2. ANA BAŞLIK ---
        st.markdown('<div class="cyber-title">ONUR KÜRSÜSÜ</div>', unsafe_allow_html=True)

        # --- 3. YÜKSEK KONTRASTLI TABLAR ---
        t1, t2 = st.tabs(["🌎 Okul Geneli", "📍 Sınıf Sıralamam"])
        
        with t1:
            if not df.empty:
                top_okul = df.sort_values(by="toplam_puan", ascending=False).head(20)
                st.markdown('<div class="rank-scroll-box">', unsafe_allow_html=True)
                for i, r in enumerate(top_okul.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:02d}"
                    st.markdown(f'''
                        <div class="rank-item">
                            <div style="display:flex; align-items:center; gap:12px;">
                                <span class="item-rank-num">{icon}</span>
                                <div>
                                    <div class="item-name">{r.ad_soyad[:20]}</div>
                                    <span class="badge-mini {rc}" style="font-size:0.65rem; padding:2px 6px; border-radius:4px; font-weight:800; text-transform:uppercase;">{rn}</span>
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
                            <div style="display:flex; align-items:center; gap:12px;">
                                <span class="item-rank-num">#{i:02d}</span>
                                <div>
                                    <div class="item-name">{r.ad_soyad[:20]}</div>
                                    <span class="badge-mini {rc}" style="font-size:0.65rem; padding:2px 6px; border-radius:4px; font-weight:800; text-transform:uppercase;">{rn}</span>
                                </div>
                            </div>
                            <div class="item-xp">{int(r.toplam_puan)}</div>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"VERİ HATASI: {e}")
