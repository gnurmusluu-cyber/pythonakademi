import streamlit as st
import pandas as pd

def rütbe_ata(xp):
    if xp >= 1000: return "🏆 Bilge", "badge-bilge"
    if xp >= 500: return "🔥 Savaşçı", "badge-savasci"
    if xp >= 200: return "🐍 Pythonist", "badge-pythonist"
    return "🥚 Çömez", "badge-comez"

def liderlik_tablosu_goster(supabase, current_user=None):
    # --- 0. LİDERLER PANELİ CSS (MAKSİMUM KONTRAST & OKUNABİLİRLİK) ---
    st.markdown('''
        <style>
        /* ZİRVEDEKİ ŞUBE PANOSU */
        .top-class-card {
            background: linear-gradient(135deg, rgba(0, 229, 255, 0.2) 0%, rgba(173, 255, 47, 0.1) 100%);
            border: 1px solid #00E5FF;
            border-radius: 12px;
            padding: 10px;
            text-align: center;
            margin-bottom: 15px;
        }
        .top-class-title { font-size: 0.7rem; color: #ADFF2F; font-weight: 800; letter-spacing: 2px; }
        .top-class-name { font-size: 1.4rem; color: white; font-weight: 900; margin-top: 2px; }

        /* TAB TASARIMI: YÜKSEK KONTRAST (OKUNABİLİRLİK GARANTİLİ) */
        .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #0e1117; padding: 5px; border-radius: 8px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #1c2128 !important;
            color: #AAAAAA !important; /* Pasif yazı gri */
            border: 1px solid #30363d !important;
            border-radius: 5px !important;
            padding: 10px 15px !important;
            font-weight: 800 !important;
            font-size: 0.85rem !important;
            transition: 0.2s;
        }

        /* TIKLANDIĞINDA: SİYAH ÜZERİNE PARLAK CYAN */
        .stTabs [aria-selected="true"] {
            background-color: #00E5FF !important; 
            color: #000000 !important; /* Maksimum okunabilirlik için siyah metin */
            border: 1px solid #FFFFFF !important;
            box-shadow: 0 0 12px rgba(0, 229, 255, 0.5);
        }

        /* LİSTE ALANI (SCROLL) */
        .list-scroll-vfinal {
            max-height: 350px; /* Her ekrana sığması için optimize edildi */
            overflow-y: auto;
            margin-top: 10px;
            padding-right: 5px;
        }
        .list-scroll-vfinal::-webkit-scrollbar { width: 3px; }
        .list-scroll-vfinal::-webkit-scrollbar-thumb { background: #00E5FF; border-radius: 10px; }

        /* SATIR TASARIMI */
        .rank-row {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 8px 12px;
            margin-bottom: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .row-me { border: 2px solid #ADFF2F !important; background: #0d1117 !important; }
        
        .row-left { display: flex; align-items: center; gap: 10px; }
        .row-idx { color: #00E5FF; font-weight: 900; font-size: 0.95rem; width: 30px; }
        .row-name { font-weight: 700; font-size: 0.9rem; color: #FFFFFF; }
        .row-xp { color: #ADFF2F; font-weight: 900; font-family: monospace; font-size: 0.95rem; }

        .badge-slim {
            font-size: 0.55rem; padding: 1px 5px; border-radius: 3px;
            font-weight: 800; text-transform: uppercase;
        }
        .badge-bilge { background: #FFD700; color: #000; }
        .badge-comez { background: #333; color: #aaa; }
        </style>
    ''', unsafe_allow_html=True)

    try:
        res = supabase.table("kullanicilar").select("*").execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

        if not df.empty:
            # 1. ZİRVEDEKİ ŞUBE PANOSU (DASHBOARD STYLE)
            class_stats = df.groupby('sinif')['toplam_puan'].mean().sort_values(ascending=False).reset_index()
            winner = class_stats.iloc[0]
            st.markdown(f'''
                <div class="top-class-card">
                    <div class="top-class-title">👑 ZİRVEDEKİ ŞUBE</div>
                    <div class="top-class-name">{winner['sinif']}</div>
                    <div style="color: #ADFF2F; font-size: 0.75rem; font-weight:bold;">AVG: {int(winner['toplam_puan'])} XP</div>
                </div>
            ''', unsafe_allow_html=True)

            # 2. TABS (İSTEDİĞİN BAŞLIKLARLA MÜHÜRLENDİ)
            t_sinif, t_okul = st.tabs(["📍 SINIF LİDERLERİ", "🌍 OKUL LİDERLERİ"])

            with t_sinif:
                if current_user:
                    sinif_list = df[df['sinif'] == current_user['sinif']].sort_values(by="toplam_puan", ascending=False)
                    st.markdown('<div class="list-scroll-vfinal">', unsafe_allow_html=True)
                    for i, r in enumerate(sinif_list.itertuples(), 1):
                        rn, rc = rütbe_ata(r.toplam_puan)
                        me_cls = "row-me" if r.ogrenci_no == current_user['ogrenci_no'] else ""
                        st.markdown(f'''
                            <div class="rank-row {me_cls}">
                                <div class="row-left">
                                    <span class="row-idx">#{i:02d}</span>
                                    <div>
                                        <div class="row-name">{r.ad_soyad[:18]}</div>
                                        <span class="badge-slim {rc}">{rn}</span>
                                    </div>
                                </div>
                                <span class="row-xp">{int(r.toplam_puan)}</span>
                            </div>
                        ''', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("Siber-geçiş bekleniyor...")

            with t_okul:
                okul_list = df.sort_values(by="toplam_puan", ascending=False).head(30)
                st.markdown('<div class="list-scroll-vfinal">', unsafe_allow_html=True)
                for i, r in enumerate(okul_list.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:02d}"
                    st.markdown(f'''
                        <div class="rank-row">
                            <div class="row-left">
                                <span class="row-idx" style="font-size:1.1rem;">{icon}</span>
                                <div>
                                    <div class="row-name">{r.ad_soyad[:18]}</div>
                                    <span class="badge-slim {rc}">{rn}</span>
                                </div>
                            </div>
                            <span class="row-xp">{int(r.toplam_puan)}</span>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"ERR_RANK_SYSTEM: {e}")
