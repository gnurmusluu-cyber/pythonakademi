import streamlit as st
import pandas as pd

def rütbe_ata(xp):
    """XP değerine göre rütbe ve CSS sınıfı döner."""
    if xp >= 1000:
        return "🏆 Bilge", "badge-bilge"
    elif xp >= 500:
        return "🔥 Savaşçı", "badge-savasci"
    elif xp >= 200:
        return "🐍 Pythonist", "badge-pythonist"
    else:
        return "🥚 Çömez", "badge-comez"

def liderlik_tablosu_goster(supabase, current_user=None):
    """Liderlik tablosunu ve şube şampiyonunu optimize şekilde gösterir."""
    
    # --- SİBER TABLO TASARIMI (CSS) ---
    st.markdown('''
        <style>
        .rank-card {
            background: rgba(0, 229, 255, 0.05);
            border: 1px solid rgba(0, 229, 255, 0.2);
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
        }
        .rank-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            margin: 4px 0;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 6px;
            font-family: monospace;
            font-size: 0.85rem;
        }
        .row-me {
            border: 1px solid #ADFF2F;
            background: rgba(173, 255, 47, 0.1);
        }
        .top-class-card {
            background: linear-gradient(45deg, #1a1a1a, #000);
            border: 2px solid #FFD700;
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
        }
        .top-class-title { color: #FFD700; font-size: 0.7rem; font-weight: bold; letter-spacing: 2px; }
        .top-class-name { color: #fff; font-size: 1.8rem; font-weight: 900; }
        </style>
    ''', unsafe_allow_html=True)

    try:
        # --- HIZ OPTİMİZASYONU: Sadece aktif ve ilk 20 öğrenciyi çek ---
        res = supabase.table("kullanicilar").select("ad_soyad, toplam_puan, sinif, ogrenci_no").order("toplam_puan", desc=True).limit(20).execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

        if not df.empty:
            # 1. ZİRVEDEKİ ŞUBE HESAPLAMA (Ortalama Puan)
            # Not: Tüm tablo yerine ilk 20 üzerinden hızlı bir trend gösterir.
            if 'toplam_puan' in df.columns:
                class_stats = df.groupby('sinif')['toplam_puan'].mean().sort_values(ascending=False).reset_index()
                if not class_stats.empty:
                    winner = class_stats.iloc[0]
                    st.markdown(f'''
                        <div class="top-class-card">
                            <div class="top-class-title">👑 LİDER ŞUBE (TREND)</div>
                            <div class="top-class-name">{winner['sinif']}</div>
                        </div>
                    ''', unsafe_allow_html=True)

            # 2. TABLO GÖRÜNÜMÜ (SINIF VE OKUL SEKMELERİ)
            t_sinif, t_okul = st.tabs(["📍 SINIFIM", "🌍 OKUL TOP 20"])
            
            with t_sinif:
                if current_user:
                    # Sadece mevcut kullanıcının sınıfındaki arkadaşları
                    # (Bu veri zaten çekilen ilk 20 içindeyse gösterilir, tam liste için limit kaldırılmalıdır)
                    sinif_df = df[df['sinif'] == current_user['sinif']]
                    if not sinif_df.empty:
                        for r in sinif_df.itertuples():
                            me_style = "row-me" if r.ogrenci_no == current_user['ogrenci_no'] else ""
                            st.markdown(f'''
                                <div class="rank-row {me_style}">
                                    <span>{r.ad_soyad[:12]}..</span>
                                    <span style="color:#ADFF2F;">{int(r.toplam_puan)} XP</span>
                                </div>
                            ''', unsafe_allow_html=True)
                    else:
                        st.info("Sınıfından kimse henüz ilk 20'de değil. Çalışmaya devam!")

            with t_okul:
                for i, r in enumerate(df.itertuples(), 1):
                    me_style = "row-me" if current_user and r.ogrenci_no == current_user['ogrenci_no'] else ""
                    st.markdown(f'''
                        <div class="rank-row {me_style}">
                            <span>#{i} {r.ad_soyad[:12]}..</span>
                            <span style="color:#00E5FF;">{int(r.toplam_puan)} XP</span>
                        </div>
                    ''', unsafe_allow_html=True)
        else:
            st.write("Henüz siber-iz bırakan kimse yok...")

    except Exception as e:
        st.error(f"Siber-Tablo Hatası: {e}")
