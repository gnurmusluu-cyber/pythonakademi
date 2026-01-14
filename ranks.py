import streamlit as st
import pandas as pd

def rütbe_ata(xp):
    if xp >= 1000: return "🏆 Bilge", "badge-bilge"
    if xp >= 500: return "🔥 Savaşçı", "badge-savasci"
    if xp >= 200: return "🐍 Pythonist", "badge-pythonist"
    return "🥚 Çömez", "badge-comez"

def liderlik_tablosu_goster(supabase, current_user=None):
    # --- 0. SİBER-DASHBOARD CSS (NET OKUNABİLİRLİK & FERAH TASARIM) ---
    st.markdown('''
        <style>
        /* ZİRVEDEKİ ŞUBE PANOSU (DASHBOARD WIDGET STYLE) */
        .top-class-card {
            background: linear-gradient(135deg, rgba(0, 229, 255, 0.2) 0%, rgba(173, 255, 47, 0.1) 100%);
            border: 1px solid #00E5FF;
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }
        .top-class-title { font-size: 0.8rem; color: #ADFF2F; font-weight: 800; letter-spacing: 2px; }
        .top-class-name { font-size: 1.6rem; color: white; font-weight: 900; margin-top: 5px; text-shadow: 0 0 10px rgba(0,229,255,0.5); }

        /* TAB TASARIMI (GÜÇLÜ KONTRAST) */
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            background: rgba(255, 255, 255, 0.05) !important;
            border-radius: 8px 8px 0 0 !important;
            padding: 12px 18px !important;
            color: #AAAAAA !important;
            font-weight: 700 !important;
            font-size: 0.9rem !important;
        }
        .stTabs [aria-selected="true"] {
            background: rgba(0, 229, 255, 0.15) !important;
            color: #00E5FF !important;
            border-bottom: 3px solid #00E5FF !important;
        }

        /* LİSTE ALANI (OTOMATİK SCROLL) */
        .list-container {
            max-height: 420px; /* Dikey sığma garantisi */
            overflow-y: auto;
            margin-top: 10px;
            padding-right: 8px;
        }
        .list-container::-webkit-scrollbar { width: 4px; }
        .list-container::-webkit-scrollbar-thumb { background: #00E5FF; border-radius: 10px; }

        /* SATIR TASARIMI (MODERN KART) */
        .rank-row {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 12px 15px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: 0.2s;
        }
        .rank-row:hover { background: rgba(255, 255, 255, 0.06); transform: translateX(5px); }
        .rank-row-me { border: 2.5px solid #ADFF2F !important; background: rgba(173, 255, 47, 0.08) !important; }
        
        /* İSİM VE SIRA */
        .row-left { display: flex; align-items: center; gap: 15px; }
        .row-index { color: #00E5FF; font-weight: 950; font-size: 1.1rem; width: 35px; }
        .row-user { display: flex; flex-direction: column; }
        .row-name { font-weight: 700; font-size: 1rem; color: #FFFFFF; }

        /* XP DEĞERİ */
        .row-xp { color: #ADFF2F; font-weight: 950; font-family: 'Fira Code', monospace; font-size: 1.1rem; }

        /* ROZETLER */
        .badge-slim {
            font-size: 0.65rem; padding: 2px 8px; border-radius: 4px;
            font-weight: 900; text-transform: uppercase; margin-top: 4px; width: fit-content;
        }
        .badge-bilge { background: #FFD700; color: #000; }
        .badge-savasci { background: #FF4500; color: #fff; }
        .badge-pythonist { background: #00E5FF; color: #000; }
        .badge-comez { background: #333; color: #888; }
        </style>
    ''', unsafe_allow_html=True)

    try:
        res = supabase.table("kullanicilar").select("*").execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

        if not df.empty:
            # 1. ZİRVEDEKİ ŞUBE PANOSU (MODERN WIDGET)
            class_stats = df.groupby('sinif')['toplam_puan'].mean().sort_values(ascending=False).reset_index()
            winner = class_stats.iloc[0]
            st.markdown(f'''
                <div class="top-class-card">
                    <div class="top-class-title">👑 ZİRVEDEKİ ŞUBE</div>
                    <div class="top-class-name">{winner['sinif']}</div>
                    <div style="color: #ADFF2F; font-size: 0.85rem; font-weight: 800; margin-top: 5px;">ORTALAMA: {int(winner['toplam_puan'])} XP</div>
                </div>
            ''', unsafe_allow_html=True)

            # 2. TABS (SINIF SOLDA, OKUL SAĞDA)
            st.markdown("<h4 style='text-align:center; color:#00E5FF; margin-bottom:15px; letter-spacing:2px;'>🏆 ONUR KÜRSÜSÜ</h4>", unsafe_allow_html=True)
            t_sinif, t_okul = st.tabs(["📍 SINIF SIRALAMAM", "🌍 OKUL GENELİ"])

            with t_sinif:
                if current_user:
                    sinif_list = df[df['sinif'] == current_user['sinif']].sort_values(by="toplam_puan", ascending=False)
                    st.markdown('<div class="list-container">', unsafe_allow_html=True)
                    for i, r in enumerate(sinif_list.itertuples(), 1):
                        rn, rc = rütbe_ata(r.toplam_puan)
                        me_cls = "rank-row-me" if r.ogrenci_no == current_user['ogrenci_no'] else ""
                        st.markdown(f'''
                            <div class="rank-row {me_cls}">
                                <div class="row-left">
                                    <span class="row-index">#{i:02d}</span>
                                    <div class="row-user">
                                        <span class="row-name">{r.ad_soyad}</span>
                                        <span class="badge-slim {rc}">{rn}</span>
                                    </div>
                                </div>
                                <span class="row-xp">{int(r.toplam_puan)}</span>
                            </div>
                        ''', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("Kendi sıralamanı görmek için giriş yapmalısın arkadaşım.")

            with t_okul:
                okul_list = df.sort_values(by="toplam_puan", ascending=False).head(30)
                st.markdown('<div class="list-container">', unsafe_allow_html=True)
                for i, r in enumerate(okul_list.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:02d}"
                    st.markdown(f'''
                        <div class="rank-row">
                            <div class="row-left">
                                <span class="row-index" style="font-size:1.3rem;">{icon}</span>
                                <div class="row-user">
                                    <span class="row-name">{r.ad_soyad}</span>
                                    <span class="badge-slim {rc}">{rn}</span>
                                </div>
                            </div>
                            <span class="row-xp">{int(r.toplam_puan)}</span>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Sıralama verisi çekilemedi: {e}")
