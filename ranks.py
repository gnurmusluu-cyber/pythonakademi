import streamlit as st
import pandas as pd

def rütbe_ata(xp):
    """XP değerine göre rütbe ve CSS sınıfı döner."""
    if xp >= 1000: return "🏆 Bilge", "badge-bilge"
    if xp >= 500: return "🔥 Savaşçı", "badge-savasci"
    if xp >= 200: return "🐍 Pythonist", "badge-pythonist"
    return "🥚 Çömez", "badge-comez"

def liderlik_tablosu_goster(supabase, current_user=None):
    """Gelişmiş pano ve kompakt liste yapısı."""
    
    # --- 0. SİBER-TABLO CSS (PANO VE LİSTE) ---
    st.markdown('''
        <style>
        /* ŞAMPİYON PANO TASARIMI */
        .champion-pano {
            background: linear-gradient(135deg, rgba(0, 229, 255, 0.15) 0%, rgba(173, 255, 47, 0.1) 100%);
            border: 1px solid #00E5FF;
            border-radius: 15px;
            padding: 15px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 0 20px rgba(0, 229, 255, 0.1);
        }
        .champion-title {
            color: #ADFF2F;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 5px;
        }
        .champion-name {
            color: #00E5FF;
            font-size: 1.6rem;
            font-weight: 900;
            text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
        }

        /* LİSTE KAYDIRMA ALANI */
        .rank-scroll-area {
            max-height: 380px;
            overflow-y: auto;
            padding-right: 8px;
        }
        .rank-scroll-area::-webkit-scrollbar { width: 3px; }
        .rank-scroll-area::-webkit-scrollbar-thumb { background: #00E5FF; border-radius: 10px; }

        /* KART TASARIMI (KOMPAKT) */
        .rank-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 10px;
            padding: 8px 12px;
            margin-bottom: 8px;
            border-left: 3px solid transparent;
        }
        .rank-row:hover { background: rgba(255, 255, 255, 0.05); }
        .is-me-row { border-left-color: #ADFF2F; background: rgba(173, 255, 47, 0.05); }

        .rank-info { display: flex; align-items: center; gap: 10px; }
        .rank-num { color: #888; font-size: 0.8rem; width: 20px; }
        .student-name { color: #E0E0E0; font-size: 0.9rem; font-weight: 600; }
        
        .xp-display {
            color: #ADFF2F;
            font-family: 'Fira Code', monospace;
            font-weight: bold;
            font-size: 0.9rem;
        }

        .badge-mini {
            font-size: 0.65rem;
            padding: 1px 6px;
            border-radius: 4px;
            font-weight: 800;
        }
        .badge-bilge { background: #FFD700; color: #000; }
        .badge-savasci { background: #FF4500; color: #fff; }
        .badge-pythonist { background: #00E5FF; color: #000; }
        .badge-comez { background: #333; color: #aaa; }
        </style>
    ''', unsafe_allow_html=True)

    try:
        res = supabase.table("kullanicilar").select("*").execute()
        if not res.data:
            st.info("Veri bekleniyor...")
            return
            
        df = pd.DataFrame(res.data)

        # --- 1. ŞAMPİYON PANO (EN ÜSTTE) ---
        class_stats = df.groupby('sinif')['toplam_puan'].mean().sort_values(ascending=False).reset_index()
        if not class_stats.empty:
            winner = class_stats.iloc[0]
            st.markdown(f'''
                <div class="champion-pano">
                    <div class="champion-title">👑 ZİRVEDEKİ ŞUBE</div>
                    <div class="champion-name">{winner['sinif']}</div>
                    <div style="color:#888; font-size:0.8rem; margin-top:5px;">Ortalama: {int(winner['toplam_puan'])} XP</div>
                </div>
            ''', unsafe_allow_html=True)

        # --- 2. KOMPAKT TABLAR ---
        t1, t2 = st.tabs(["🌍 Okul Onur Kürsüsü", "📍 Sınıf Sıralamam"])
        
        with t1:
            top_okul = df.sort_values(by="toplam_puan", ascending=False).head(30)
            st.markdown('<div class="rank-scroll-area">', unsafe_allow_html=True)
            for i, r in enumerate(top_okul.itertuples(), 1):
                rn, rc = rütbe_ata(r.toplam_puan)
                icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                st.markdown(f'''
                    <div class="rank-row">
                        <div class="rank-info">
                            <span class="rank-num">{icon}</span>
                            <div>
                                <div class="student-name">{r.ad_soyad[:18]}</div>
                                <span class="badge-mini {rc}">{rn}</span>
                            </div>
                        </div>
                        <div class="xp-display">{int(r.toplam_puan)}</div>
                    </div>
                ''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with t2:
            if current_user:
                df_sinif = df[df['sinif'] == current_user['sinif']].sort_values(by="toplam_puan", ascending=False)
                st.markdown('<div class="rank-scroll-area">', unsafe_allow_html=True)
                for i, r in enumerate(df_sinif.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    is_me = "is-me-row" if r.ogrenci_no == current_user['ogrenci_no'] else ""
                    st.markdown(f'''
                        <div class="rank-row {is_me}">
                            <div class="rank-info">
                                <span class="rank-num">#{i}</span>
                                <div>
                                    <div class="student-name">{r.ad_soyad[:18]}</div>
                                    <span class="badge-mini {rc}">{rn}</span>
                                </div>
                            </div>
                            <div class="xp-display">{int(r.toplam_puan)}</div>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Kendi sıranı görmek için siber-geçitten giriş yapmalısın.")

    except Exception as e:
        st.error(f"Sistem Hatası: {e}")
