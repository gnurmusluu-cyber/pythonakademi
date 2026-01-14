import streamlit as st
import pandas as pd

def rütbe_ata(xp):
    if xp >= 1000: return "🏆 Bilge", "badge-bilge"
    if xp >= 500: return "🔥 Savaşçı", "badge-savasci"
    if xp >= 200: return "🐍 Pythonist", "badge-pythonist"
    return "🥚 Çömez", "badge-comez"

def liderlik_tablosu_goster(supabase, current_user=None):
    # --- 0. MİKRO-SİBER TASARIM (MAKSİMUM ALAN TASARRUFU) ---
    st.markdown('''
        <style>
        /* MİKRO ŞAMPİYON ŞERİDİ */
        .micro-champ-v7 {
            background: rgba(173, 255, 47, 0.05);
            border: 1px solid rgba(173, 255, 47, 0.3);
            border-radius: 4px;
            padding: 3px 8px;
            text-align: center;
            margin-bottom: 5px;
            font-size: 0.65rem;
            color: #ADFF2F;
        }

        /* HUD TABLARI (ULTRA KÜÇÜK) */
        .stTabs [data-baseweb="tab-list"] { gap: 2px; }
        .stTabs [data-baseweb="tab"] {
            padding: 4px 8px !important;
            font-size: 0.65rem !important;
            height: 25px !important;
            border-radius: 4px 4px 0 0 !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #00E5FF !important;
            color: #000 !important;
            font-weight: 900 !important;
        }

        /* NANO-SCROLL (200PX SABİT YÜKSEKLİK) */
        .nano-scroll-v7 { 
            max-height: 200px; 
            overflow-y: auto; 
            margin-top: 3px;
        }
        .nano-scroll-v7::-webkit-scrollbar { width: 2px; }
        .nano-scroll-v7::-webkit-scrollbar-thumb { background: #00E5FF; }

        /* SATIRLAR (HÜCRESEL TASARIM) */
        .nano-row-v7 {
            display: flex; justify-content: space-between; align-items: center;
            background: #161b22;
            padding: 3px 6px;
            margin-bottom: 2px;
            border-radius: 3px;
            border: 1px solid #30363d;
        }
        .me-v7 { border-color: #ADFF2F !important; background: #0d1117 !important; }

        .n-txt-rank { color: #00E5FF; font-weight: 900; font-size: 0.7rem; width: 20px; }
        .n-txt-name { color: #FFF; font-size: 0.7rem; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; max-width: 70px; }
        .n-txt-xp { color: #ADFF2F; font-size: 0.7rem; font-weight: bold; font-family: monospace; }
        
        .badge-nano { font-size: 0.5rem; padding: 0px 2px; border-radius: 2px; }
        </style>
    ''', unsafe_allow_html=True)

    try:
        res = supabase.table("kullanicilar").select("*").execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

        # --- 1. MİKRO ŞAMPİYON SATIRI ---
        if not df.empty:
            class_stats = df.groupby('sinif')['toplam_puan'].mean().sort_values(ascending=False).reset_index()
            winner = class_stats.iloc[0]
            st.markdown(f'<div class="micro-champ-v7">👑 <b>{winner["sinif"]}</b> (AVG: {int(winner["toplam_puan"])} XP)</div>', unsafe_allow_html=True)

        # --- 2. TABS (SINIF SOLDA, OKUL SAĞDA) ---
        t1, t2 = st.tabs(["📍 SINIF", "🌍 OKUL"])
        
        with t1: # SINIF SIRALAMASI
            if current_user and not df.empty:
                df_sinif = df[df['sinif'] == current_user['sinif']].sort_values(by="toplam_puan", ascending=False)
                st.markdown('<div class="nano-scroll-v7">', unsafe_allow_html=True)
                for i, r in enumerate(df_sinif.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    is_me = "me-v7" if r.ogrenci_no == current_user['ogrenci_no'] else ""
                    st.markdown(f'''
                        <div class="nano-row-v7 {is_me}">
                            <div style="display:flex; align-items:center; gap:5px;">
                                <span class="n-txt-rank">#{i:02d}</span>
                                <div>
                                    <div class="n-txt-name">{r.ad_soyad}</div>
                                    <span class="badge-nano {rc}">{rn}</span>
                                </div>
                            </div>
                            <span class="n-txt-xp">{int(r.toplam_puan)}</span>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with t2: # OKUL SIRALAMASI
            if not df.empty:
                top_okul = df.sort_values(by="toplam_puan", ascending=False).head(30)
                st.markdown('<div class="nano-scroll-v7">', unsafe_allow_html=True)
                for i, r in enumerate(top_okul.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:02d}"
                    st.markdown(f'''
                        <div class="nano-row-v7">
                            <div style="display:flex; align-items:center; gap:5px;">
                                <span class="n-txt-rank">{icon}</span>
                                <div>
                                    <div class="n-txt-name">{r.ad_soyad}</div>
                                    <span class="badge-nano {rc}">{rn}</span>
                                </div>
                            </div>
                            <span class="n-txt-xp">{int(r.toplam_puan)}</span>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Sistem Hatası: {e}")
