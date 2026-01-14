import streamlit as st
import pandas as pd

def rütbe_ata(xp):
    """XP değerine göre rütbe ve CSS sınıfı döner."""
    if xp >= 1000: return "🏆 Bilge", "badge-bilge"
    if xp >= 500: return "🔥 Savaşçı", "badge-savasci"
    if xp >= 200: return "🐍 Pythonist", "badge-pythonist"
    return "🥚 Çömez", "badge-comez"

def liderlik_tablosu_goster(supabase, current_user=None):
    """Siber-Pano ve Neon Kürsü yapısı."""
    
    # --- 0. SİBER-ESTETİK CSS (KÜRSÜ VE PANO MÜHRÜ) ---
    st.markdown('''
        <style>
        /* ŞAMPİYON PANO GÜNCELLEME */
        .champion-pano {
            background: linear-gradient(135deg, rgba(0, 229, 255, 0.2) 0%, rgba(173, 255, 47, 0.1) 100%);
            border: 2px solid #00E5FF;
            border-radius: 15px;
            padding: 18px;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 0 25px rgba(0, 229, 255, 0.2);
        }
        .champion-title { color: #ADFF2F; font-size: 0.85rem; letter-spacing: 2px; font-weight: 900; }
        .champion-name { color: #00E5FF; font-size: 1.8rem; font-weight: 950; text-shadow: 0 0 15px #00E5FF; }

        /* LİDERLİK SATIRLARI (NEON KÜRSÜ) */
        .rank-scroll-area { max-height: 400px; overflow-y: auto; padding-right: 10px; }
        .rank-scroll-area::-webkit-scrollbar { width: 3px; }
        .rank-scroll-area::-webkit-scrollbar-thumb { background: #00E5FF; border-radius: 10px; }

        .rank-row {
            display: flex; justify-content: space-between; align-items: center;
            background: rgba(22, 27, 34, 0.8);
            border: 1px solid rgba(0, 229, 255, 0.1);
            border-radius: 12px;
            padding: 10px 15px;
            margin-bottom: 10px;
            transition: 0.3s;
        }
        .rank-row:hover { border-color: #00E5FF; transform: translateX(5px); }

        /* İLK 3 ÖZEL PARLAMA */
        .rank-1 { border: 1.5px solid #FFD700 !important; box-shadow: 0 0 15px rgba(255, 215, 0, 0.2); background: rgba(255, 215, 0, 0.05) !important; }
        .rank-2 { border: 1.5px solid #00E5FF !important; box-shadow: 0 0 15px rgba(0, 229, 255, 0.2); }
        .rank-3 { border: 1.5px solid #CD7F32 !important; box-shadow: 0 0 15px rgba(205, 127, 50, 0.2); }

        .is-me-row { border: 2px solid #ADFF2F !important; background: rgba(173, 255, 47, 0.08) !important; }

        .rank-num { font-size: 1.1rem; font-weight: 900; width: 30px; }
        .student-name { color: #FFFFFF; font-size: 0.95rem; font-weight: 700; }
        .xp-display { color: #ADFF2F; font-family: 'Fira Code', monospace; font-weight: 900; font-size: 1rem; }

        /* ROZETLER */
        .badge-mini { font-size: 0.65rem; padding: 2px 8px; border-radius: 5px; font-weight: 800; text-transform: uppercase; }
        .badge-bilge { background: #FFD700; color: #000; }
        .badge-savasci { background: #FF4500; color: #fff; }
        .badge-pythonist { background: #00E5FF; color: #000; }
        .badge-comez { background: #333; color: #aaa; }
        </style>
    ''', unsafe_allow_html=True)

    try:
        res = supabase.table("kullanicilar").select("*").execute()
        if not res.data:
            st.info("Siber-veri bekleniyor...")
            return
        df = pd.DataFrame(res.data)

        # --- 1. ŞAMPİYON PANO ---
        class_stats = df.groupby('sinif')['toplam_puan'].mean().sort_values(ascending=False).reset_index()
        if not class_stats.empty:
            winner = class_stats.iloc[0]
            st.markdown(f'''
                <div class="champion-pano">
                    <div class="champion-title">🏆 ZİRVEDEKİ ŞUBE</div>
                    <div class="champion-name">{winner['sinif']}</div>
                    <div style="color:#ADFF2F; font-size:0.85rem; font-weight:bold; margin-top:5px;">ORTALAMA: {int(winner['toplam_puan'])} XP</div>
                </div>
            ''', unsafe_allow_html=True)

        # --- 2. TABLAR ---
        t1, t2 = st.tabs(["🌍 Okul Onur Kürsüsü", "📍 Sınıf Sıralamam"])
        
        with t1:
            top_okul = df.sort_values(by="toplam_puan", ascending=False).head(30)
            st.markdown('<div class="rank-scroll-area">', unsafe_allow_html=True)
            for i, r in enumerate(top_okul.itertuples(), 1):
                rn, rc = rütbe_ata(r.toplam_puan)
                # Sıralama sınıfı belirleme
                special_cls = f"rank-{i}" if i <= 3 else ""
                icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}"
                
                st.markdown(f'''
                    <div class="rank-row {special_cls}">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <span class="rank-num">{icon}</span>
                            <div>
                                <div class="student-name">{r.ad_soyad[:20]}</div>
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
                    # Sınıf içinde de ilk 3 vurgusu olsun
                    special_cls = f"rank-{i}" if i <= 3 else ""
                    
                    st.markdown(f'''
                        <div class="rank-row {is_me} {special_cls}">
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <span class="rank-num">#{i}</span>
                                <div>
                                    <div class="student-name">{r.ad_soyad[:20]}</div>
                                    <span class="badge-mini {rc}">{rn}</span>
                                </div>
                            </div>
                            <div class="xp-display">{int(r.toplam_puan)}</div>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Lütfen giriş yap arkadaşım!")

    except Exception as e:
        st.error(f"Sistem Hatası: {e}")
