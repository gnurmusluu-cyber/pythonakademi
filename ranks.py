import streamlit as st
import pandas as pd

def rütbe_ata(xp):
    if xp >= 1000: return "🏆 Bilge", "badge-bilge"
    if xp >= 500: return "🔥 Savaşçı", "badge-savasci"
    if xp >= 200: return "🐍 Pythonist", "badge-pythonist"
    return "🥚 Çömez", "badge-comez"

def liderlik_tablosu_goster(supabase, current_user=None):
    # --- 0. MAKSİMUM OKUNABİLİRLİK VE KONTRAST MÜHRÜ ---
    st.markdown('''
        <style>
        /* SİBER-KOMUTA ANA BAŞLIĞI */
        .cyber-header-v2 {
            border-left: 5px solid #00E5FF;
            padding-left: 15px;
            margin-bottom: 25px;
            background: linear-gradient(90deg, rgba(0, 229, 255, 0.05), transparent);
        }
        .cyber-header-v2 h3 {
            color: #FFFFFF !important;
            font-family: 'Fira Code', monospace;
            font-size: 1.3rem !important;
            font-weight: 900 !important;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        /* TAB TASARIMI: FİZİKSEL PANEL TUŞLARI (EN YÜKSEK KONTRAST) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background-color: #0e1117;
            padding: 8px;
            border-radius: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #1c2128 !important; /* Koyu ve Net Arka Plan */
            color: #AAAAAA !important; 
            border: 1px solid #30363d !important;
            border-radius: 6px !important;
            padding: 12px 25px !important;
            font-weight: 800 !important;
            font-size: 1rem !important;
            transition: 0.2s;
        }

        /* AKTİF TUŞ: SİYAH ÜZERİNE PARLAK CYAN (OKUNABİLİRLİK ZİRVESİ) */
        .stTabs [aria-selected="true"] {
            background-color: #00E5FF !important; 
            color: #000000 !important; /* Siyah Metin, Beyazdan daha iyi okunur */
            border: 1px solid #FFFFFF !important;
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.5);
        }

        /* ŞAMPİYON PANO: KOMUTA EKRANI */
        .champion-command-box {
            background-color: #000000;
            border: 2px solid #ADFF2F;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            margin-bottom: 30px;
        }
        .cmd-title { color: #ADFF2F; font-size: 0.85rem; font-weight: 900; letter-spacing: 2px; }
        .cmd-value { color: #FFFFFF; font-size: 1.9rem; font-weight: 950; margin-top: 5px; text-shadow: 0 0 10px rgba(255,255,255,0.3); }

        /* VERİ LİSTESİ */
        .rank-scroll-v3 { max-height: 420px; overflow-y: auto; padding-right: 10px; }
        .rank-scroll-v3::-webkit-scrollbar { width: 5px; }
        .rank-scroll-v3::-webkit-scrollbar-thumb { background: #00E5FF; border-radius: 10px; }

        .data-row {
            display: flex; justify-content: space-between; align-items: center;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 10px;
            padding: 14px 18px;
            margin-bottom: 10px;
        }
        .is-me-highlight { border: 2px solid #ADFF2F !important; background: #0d1117 !important; }

        .row-rank { color: #00E5FF; font-weight: 950; font-size: 1.2rem; width: 40px; }
        .row-name { color: #FFFFFF; font-weight: 700; font-size: 1.05rem; }
        .row-xp { color: #ADFF2F; font-family: 'Fira Code', monospace; font-weight: 900; font-size: 1.15rem; }
        </style>
    ''', unsafe_allow_html=True)

    try:
        res = supabase.table("kullanicilar").select("*").execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

        # --- 1. KOMUTA PANOSU (ŞAMPİYON) ---
        if not df.empty:
            class_stats = df.groupby('sinif')['toplam_puan'].mean().sort_values(ascending=False).reset_index()
            winner = class_stats.iloc[0]
            st.markdown(f'''
                <div class="champion-command-box">
                    <div class="cmd-title">🛰️ ZİRVEDEKİ ŞUBE KOMUTANLIĞI</div>
                    <div class="cmd-value">{winner['sinif']}</div>
                    <div style="color:#ADFF2F; font-size:0.95rem; font-weight:bold; font-family:monospace; margin-top:5px;">AVG_SCORE: {int(winner['toplam_puan'])} XP</div>
                </div>
            ''', unsafe_allow_html=True)

        # --- 2. ANA BAŞLIK ---
        st.markdown('<div class="cyber-header-v2"><h3>Onur Kürsüsü</h3></div>', unsafe_allow_html=True)

        # --- 3. YÜKSEK KONTRASTLI PANEL TUŞLARI ---
        t1, t2 = st.tabs(["🌍 OKUL LİDERLERİ", "📍 SINIF SIRALAMAM"])
        
        with t1:
            if not df.empty:
                top_okul = df.sort_values(by="toplam_puan", ascending=False).head(20)
                st.markdown('<div class="rank-scroll-v3">', unsafe_allow_html=True)
                for i, r in enumerate(top_okul.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:02d}"
                    st.markdown(f'''
                        <div class="data-row">
                            <div style="display:flex; align-items:center; gap:15px;">
                                <span class="row-rank">{icon}</span>
                                <div>
                                    <div class="row-name">{r.ad_soyad[:20]}</div>
                                    <span class="badge-v3 {rc}" style="font-size:0.65rem; padding:2px 8px; border-radius:4px; font-weight:900; text-transform:uppercase;">{rn}</span>
                                </div>
                            </div>
                            <div class="row-xp">{int(r.toplam_puan)} XP</div>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with t2:
            if current_user and not df.empty:
                df_sinif = df[df['sinif'] == current_user['sinif']].sort_values(by="toplam_puan", ascending=False)
                st.markdown('<div class="rank-scroll-v3">', unsafe_allow_html=True)
                for i, r in enumerate(df_sinif.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    is_me = "is-me-highlight" if r.ogrenci_no == current_user['ogrenci_no'] else ""
                    st.markdown(f'''
                        <div class="data-row {is_me}">
                            <div style="display:flex; align-items:center; gap:15px;">
                                <span class="row-rank">#{i:02d}</span>
                                <div>
                                    <div class="row-name">{r.ad_soyad[:20]}</div>
                                    <span class="badge-v3 {rc}" style="font-size:0.65rem; padding:2px 8px; border-radius:4px; font-weight:900; text-transform:uppercase;">{rn}</span>
                                </div>
                            </div>
                            <div class="row-xp">{int(r.toplam_puan)} XP</div>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"RANK_DATA_SYNC_ERR: {e}")
