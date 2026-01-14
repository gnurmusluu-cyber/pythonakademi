import streamlit as st
import pandas as pd

def rütbe_ata(xp):
    """XP değerine göre rütbe ve CSS sınıfı döner."""
    if xp >= 1000: return "🏆 Bilge", "badge-bilge"
    if xp >= 500: return "🔥 Savaşçı", "badge-savasci"
    if xp >= 200: return "🐍 Pythonist", "badge-pythonist"
    return "🥚 Çömez", "badge-comez"

def liderlik_tablosu_goster(supabase, current_user=None):
    """Siber-Buz temalı, gelişmiş liderlik tablosu motoru."""
    
    # --- 0. SİBER-TABLO CSS (ONUR KÜRSÜSÜ ÖZEL) ---
    st.markdown('''
        <style>
        /* TAB TASARIMI */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(0, 229, 255, 0.05) !important;
            border: 1px solid rgba(0, 229, 255, 0.2) !important;
            border-radius: 10px 10px 0 0 !important;
            color: #888 !important;
            padding: 10px 20px !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(0, 229, 255, 0.15) !important;
            border-color: #00E5FF !important;
            color: #00E5FF !important;
            font-weight: bold !important;
        }

        /* LİDER KARTLARI (GLASSMORPHISM) */
        .leader-card {
            background: rgba(22, 27, 34, 0.6) !important;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 229, 255, 0.15);
            border-radius: 12px;
            padding: 12px 18px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: 0.3s ease;
        }
        .leader-card:hover {
            border-color: #00E5FF;
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.2);
            transform: translateX(5px);
        }

        /* RÜTBE ROZETLERİ */
        .rank-badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 900;
            text-transform: uppercase;
            margin-top: 4px;
        }
        .badge-bilge { background: linear-gradient(90deg, #FFD700, #FFA500); color: #000; box-shadow: 0 0 10px #FFD700; }
        .badge-savasci { background: linear-gradient(90deg, #FF4500, #FF0000); color: #fff; box-shadow: 0 0 10px #FF4500; }
        .badge-pythonist { background: linear-gradient(90deg, #00E5FF, #008B8B); color: #000; box-shadow: 0 0 10px #00E5FF; }
        .badge-comez { background: #333; color: #aaa; }

        /* XP DEĞERİ */
        .xp-val {
            font-family: 'Fira Code', monospace;
            color: #ADFF2F;
            font-weight: bold;
            font-size: 1.1rem;
            text-shadow: 0 0 8px rgba(173, 255, 47, 0.4);
        }
        
        /* KULLANICI VURGUSU (ACTIVE) */
        .me-highlight {
            border: 2px solid #ADFF2F !important;
            background: rgba(173, 255, 47, 0.05) !important;
            box-shadow: 0 0 20px rgba(173, 255, 47, 0.1) !important;
        }
        </style>
    ''', unsafe_allow_html=True)

    st.markdown("<h3 style='text-align:center; color:#00E5FF; text-shadow: 0 0 15px #00E5FF; margin-bottom:20px;'>🏆 ONUR KÜRSÜSÜ</h3>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🌍 Okul Geneli", "📍 Sınıfım", "🏫 Şampiyon Sınıf"])
    
    try:
        res = supabase.table("kullanicilar").select("*").execute()
        if not res.data:
            st.info("Henüz veri girişi yapılmamış arkadaşım.")
            return
            
        df = pd.DataFrame(res.data)

        # --- 🌍 TAB 1: OKUL GENELİ (TOP 10) ---
        with t1:
            top_okul = df.sort_values(by="toplam_puan", ascending=False).head(10)
            for i, r in enumerate(top_okul.itertuples(), 1):
                rn, rc = rütbe_ata(r.toplam_puan)
                # İlk 3'e özel ikonlar
                rank_icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                st.markdown(f'''
                    <div class="leader-card">
                        <div>
                            <span style="color:#00E5FF; font-weight:bold; margin-right:8px;">{rank_icon}</span>
                            <b>{r.ad_soyad}</b> <br>
                            <span class="rank-badge {rc}">{rn}</span>
                        </div>
                        <div class="xp-val">{int(r.toplam_puan)} XP</div>
                    </div>
                ''', unsafe_allow_html=True)

        # --- 📍 TAB 2: SINIFIM ---
        with t2:
            if current_user:
                df_sinif = df[df['sinif'] == current_user['sinif']].sort_values(by="toplam_puan", ascending=False)
                for i, r in enumerate(df_sinif.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    is_me = "me-highlight" if r.ogrenci_no == current_user['ogrenci_no'] else ""
                    st.markdown(f'''
                        <div class="leader-card {is_me}">
                            <div>
                                <span style="color:#aaa; font-size:0.8rem; margin-right:8px;">#{i}</span>
                                <b>{r.ad_soyad}</b> <br>
                                <span class="rank-badge {rc}">{rn}</span>
                            </div>
                            <div class="xp-val">{int(r.toplam_puan)} XP</div>
                        </div>
                    ''', unsafe_allow_html=True)
            else:
                st.info("Sıralamanı görmek için giriş yapmalısın arkadaşım.")

        # --- 🏫 TAB 3: ŞAMPİYON SINIF (ORTALAMA) ---
        with t3:
            class_stats = df.groupby('sinif')['toplam_puan'].mean().sort_values(ascending=False).reset_index()
            if not class_stats.empty:
                winner = class_stats.iloc[0]['sinif']
                st.markdown(f'''
                    <div style="background:rgba(173, 255, 47, 0.1); padding:15px; border-radius:12px; border:1px solid #ADFF2F; text-align:center; margin-bottom:20px;">
                        👑 Zirvedeki Sınıf: <b style="color:#ADFF2F; font-size:1.2rem;">{winner}</b>
                    </div>
                ''', unsafe_allow_html=True)
                
                for i, r in enumerate(class_stats.itertuples(), 1):
                    st.markdown(f'''
                        <div class="leader-card">
                            <div><b>{i}. {r.sinif} Şubesi</b></div>
                            <div class="xp-val" style="font-size:0.9rem;">Ort: {int(r.toplam_puan)} XP</div>
                        </div>
                    ''', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Liderlik tablosu yüklenirken bir sorun oluştu arkadaşım: {e}")
