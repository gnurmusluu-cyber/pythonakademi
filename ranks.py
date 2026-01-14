import streamlit as st
import pandas as pd

def rütbe_ata(xp):
    if xp >= 1000: return "🏆 Bilge", "badge-bilge"
    if xp >= 500: return "🔥 Savaşçı", "badge-savasci"
    if xp >= 200: return "🐍 Pythonist", "badge-pythonist"
    return "🥚 Çömez", "badge-comez"

def liderlik_tablosu_goster(supabase, current_user=None):
    # --- 0. NANO-SİBER CSS (THE FINAL SPACE SAVER) ---
    st.markdown('''
        <style>
        /* TÜM BOŞLUKLARI SIFIRLA */
        [data-testid="column"] > div { padding: 0 !important; }
        .nano-container { margin-top: -10px; }

        /* MİKRO ŞAMPİYON ŞERİDİ */
        .nano-champ {
            background: rgba(173, 255, 47, 0.08);
            border: 1px solid rgba(173, 255, 47, 0.4);
            border-radius: 4px;
            padding: 2px 5px;
            text-align: center;
            margin-bottom: 5px;
            font-size: 0.6rem;
            color: #ADFF2F;
            font-weight: 800;
        }

        /* HUD TABLARI (SİBER-DÜĞMELER) */
        .stTabs [data-baseweb="tab-list"] { gap: 2px; background: transparent; }
        .stTabs [data-baseweb="tab"] {
            padding: 2px 6px !important;
            font-size: 0.6rem !important;
            height: 22px !important;
            border-radius: 3px 3px 0 0 !important;
            background-color: #1c2128 !important;
            color: #777 !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #00E5FF !important;
            color: #000 !important;
            font-weight: 950 !important;
        }

        /* NANO-SCROLL (180PX - HER EKRANA SIĞAR) */
        .nano-scroll-area { 
            max-height: 180px; 
            overflow-y: auto; 
            margin-top: 2px;
            border-top: 1px solid #30363d;
        }
        .nano-scroll-area::-webkit-scrollbar { width: 2px; }
        .nano-scroll-area::-webkit-scrollbar-thumb { background: #00E5FF; }

        /* SATIRLAR (ATOMİK TASARIM) */
        .atom-row {
            display: flex; justify-content: space-between; align-items: center;
            background: #161b22;
            padding: 2px 5px;
            margin-bottom: 2px;
            border-radius: 2px;
            border: 1px solid #30363d;
        }
        .me-atom { border: 1.5px solid #ADFF2F !important; background: #0d1117 !important; }

        .atom-rank { color: #00E5FF; font-weight: 900; font-size: 0.65rem; width: 18px; }
        .atom-name { color: #FFF; font-size: 0.65rem; font-weight: 600; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; max-width: 65px; }
        .atom-xp { color: #ADFF2F; font-size: 0.65rem; font-weight: 900; font-family: monospace; }
        
        .atom-badge { font-size: 0.45rem; padding: 0px 2px; border-radius: 2px; text-transform: uppercase; font-weight: bold; }
        </style>
    ''', unsafe_allow_html=True)

    try:
        res = supabase.table("kullanicilar").select("*").execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

        st.markdown('<div class="nano-container">', unsafe_allow_html=True)

        # 1. MİKRO ŞAMPİYON
        if not df.empty:
            class_stats = df.groupby('sinif')['toplam_puan'].mean().sort_values(ascending=False).reset_index()
            winner = class_stats.iloc[0]
            st.markdown(f'<div class="nano-champ">👑 {winner["sinif"]} (AVG: {int(winner["toplam_puan"])})</div>', unsafe_allow_html=True)

        # 2. TABS (SINIF SOLDA)
        t1, t2 = st.tabs(["📍 SINIF", "🌍 OKUL"])
        
        with t1: # SINIF SIRALAMASI
            if current_user and not df.empty:
                df_sinif = df[df['sinif'] == current_user['sinif']].sort_values(by="toplam_puan", ascending=False)
                st.markdown('<div class="nano-scroll-area">', unsafe_allow_html=True)
                for i, r in enumerate(df_sinif.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    is_me = "me-atom" if r.ogrenci_no == current_user['ogrenci_no'] else ""
                    st.markdown(f'''
                        <div class="atom-row {is_me}">
                            <div style="display:flex; align-items:center; gap:4px;">
                                <span class="atom-rank">#{i:02d}</span>
                                <div>
                                    <div class="atom-name">{r.ad_soyad}</div>
                                    <span class="atom-badge {rc}">{rn}</span>
                                </div>
                            </div>
                            <span class="atom-xp">{int(r.toplam_puan)}</span>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with t2: # OKUL SIRALAMASI
            if not df.empty:
                top_okul = df.sort_values(by="toplam_puan", ascending=False).head(30)
                st.markdown('<div class="nano-scroll-area">', unsafe_allow_html=True)
                for i, r in enumerate(top_okul.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:02d}"
                    st.markdown(f'''
                        <div class="atom-row">
                            <div style="display:flex; align-items:center; gap:4px;">
                                <span class="atom-rank">{icon}</span>
                                <div>
                                    <div class="atom-name">{r.ad_soyad}</div>
                                    <span class="atom-badge {rc}">{rn}</span>
                                </div>
                            </div>
                            <span class="atom-xp">{int(r.toplam_puan)}</span>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"E: {e}")
