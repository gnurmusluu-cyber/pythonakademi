import streamlit as st
import pandas as pd

def rütbe_ata(xp):
    """XP değerine göre rütbe ve CSS sınıfı döner."""
    if xp >= 1000: return "🏆 Bilge", "badge-bilge"
    if xp >= 500: return "🔥 Savaşçı", "badge-savasci"
    if xp >= 200: return "🐍 Pythonist", "badge-pythonist"
    return "🥚 Çömez", "badge-comez"

def liderlik_tablosu_goster(supabase, current_user=None):
    """Siber-Buz temalı, kompakt ve kaydırılabilir liderlik tablosu."""
    
    # --- 0. SİBER-TABLO CSS (KOMPAKT MÜHÜR) ---
    st.markdown('''
        <style>
        /* TAB TASARIMI (DAHA KÜÇÜK) */
        .stTabs [data-baseweb="tab-list"] { gap: 5px; }
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(0, 229, 255, 0.05) !important;
            border: 1px solid rgba(0, 229, 255, 0.1) !important;
            border-radius: 8px 8px 0 0 !important;
            padding: 6px 10px !important;
            font-size: 0.8rem !important;
        }

        /* LİDERLİK LİSTESİ KONTEYNERI (SCROLLABLE) */
        .leaderboard-scroll {
            max-height: 400px; /* Ekrana sığması için yükseklik sınırı */
            overflow-y: auto;
            padding-right: 5px;
        }
        .leaderboard-scroll::-webkit-scrollbar { width: 3px; }
        .leaderboard-scroll::-webkit-scrollbar-thumb { background: #00E5FF; border-radius: 10px; }

        /* LİDER KARTLARI (ULTRA KOMPAKT) */
        .leader-card {
            background: rgba(22, 27, 34, 0.7) !important;
            border: 1px solid rgba(0, 229, 255, 0.1);
            border-radius: 10px;
            padding: 6px 12px;
            margin-bottom: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .rank-badge {
            display: inline-block;
            padding: 1px 6px;
            border-radius: 10px;
            font-size: 0.65rem;
            font-weight: 800;
        }
        .badge-bilge { background: #FFD700; color: #000; }
        .badge-savasci { background: #FF4500; color: #fff; }
        .badge-pythonist { background: #00E5FF; color: #000; }
        .badge-comez { background: #333; color: #aaa; }

        .xp-val {
            font-family: 'Fira Code', monospace;
            color: #ADFF2F;
            font-weight: bold;
            font-size: 0.9rem;
        }
        
        /* AKTİF KULLANICI VURGUSU */
        .me-highlight {
            border: 1px solid #ADFF2F !important;
            background: rgba(173, 255, 47, 0.05) !important;
        }
        </style>
    ''', unsafe_allow_html=True)

    st.markdown("<h4 style='text-align:center; color:#00E5FF;'>🏆 ONUR KÜRSÜSÜ</h4>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🌍 Okul", "📍 Sınıf", "🏫 Şubeler"])
    
    try:
        res = supabase.table("kullanicilar").select("*").execute()
        if not res.data:
            st.info("Veri girişi bekleniyor...")
            return
            
        df = pd.DataFrame(res.data)

        # --- 🌍 TAB 1: OKUL GENELİ ---
        with t1:
            top_okul = df.sort_values(by="toplam_puan", ascending=False).head(20)
            st.markdown('<div class="leaderboard-scroll">', unsafe_allow_html=True)
            for i, r in enumerate(top_okul.itertuples(), 1):
                rn, rc = rütbe_ata(r.toplam_puan)
                rank_label = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                st.markdown(f'''
                    <div class="leader-card">
                        <div>
                            <span style="color:#00E5FF; font-size:0.75rem;">{rank_label}</span>
                            <b style="font-size:0.8rem;">{r.ad_soyad[:15]}</b><br>
                            <span class="rank-badge {rc}">{rn}</span>
                        </div>
                        <div class="xp-val">{int(r.toplam_puan)}</div>
                    </div>
                ''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # --- 📍 TAB 2: SINIFIM ---
        with t2:
            if current_user:
                df_sinif = df[df['sinif'] == current_user['sinif']].sort_values(by="toplam_puan", ascending=False)
                st.markdown('<div class="leaderboard-scroll">', unsafe_allow_html=True)
                for i, r in enumerate(df_sinif.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    is_me = "me-highlight" if r.ogrenci_no == current_user['ogrenci_no'] else ""
                    st.markdown(f'''
                        <div class="leader-card {is_me}">
                            <div>
                                <span style="color:#aaa; font-size:0.7rem;">#{i}</span>
                                <b style="font-size:0.8rem;">{r.ad_soyad[:15]}</b><br>
                                <span class="rank-badge {rc}">{rn}</span>
                            </div>
                            <div class="xp-val">{int(r.toplam_puan)}</div>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Giriş yapmalısın.")

        # --- 🏫 TAB 3: ŞUBE SIRALAMASI ---
        with t3:
            class_stats = df.groupby('sinif')['toplam_puan'].mean().sort_values(ascending=False).reset_index()
            st.markdown('<div class="leaderboard-scroll">', unsafe_allow_html=True)
            for i, r in enumerate(class_stats.itertuples(), 1):
                st.markdown(f'''
                    <div class="leader-card">
                        <div style="font-size:0.8rem;"><b>{i}. {r.sinif}</b></div>
                        <div class="xp-val" style="font-size:0.8rem;">{int(r.toplam_puan)} Ort</div>
                    </div>
                ''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Sistem Hatası: {e}")
