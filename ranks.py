import streamlit as st
import pandas as pd

def rütbe_ata(xp):
    """XP değerine göre rütbe ve CSS sınıfı döner."""
    if xp >= 1000: return "🏆 Bilge", "badge-bilge"
    if xp >= 500: return "🔥 Savaşçı", "badge-savasci"
    if xp >= 200: return "🐍 Pythonist", "badge-pythonist"
    return "🥚 Çömez", "badge-comez"

def liderlik_tablosu_goster(supabase, current_user=None):
    """Okul, Sınıf ve Şampiyon Sınıf tablolarını hesaplar ve gösterir."""
    st.markdown("<h3 style='text-align:center; color:#ADFF2F;'>🏆 ONUR KÜRSÜSÜ</h3>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🌍 Okul Geneli", "📍 Sınıfım", "🏫 Şampiyon Sınıf"])
    
    try:
        # Veriyi çek
        res = supabase.table("kullanicilar").select("*").execute()
        if not res.data:
            st.info("Henüz veri girişi yapılmamış arkadaşım.")
            return
            
        df = pd.DataFrame(res.data)

        # --- 🌍 TAB 1: OKUL GENELİ ---
        with t1:
            top_okul = df.sort_values(by="toplam_puan", ascending=False).head(10)
            for i, r in enumerate(top_okul.itertuples(), 1):
                rn, rc = rütbe_ata(r.toplam_puan)
                st.markdown(f"<div class='leader-card'><div><b>{i}. {r.ad_soyad}</b> <br><span class='rank-badge {rc}'>{rn}</span></div><code>{int(r.toplam_puan)} XP</code></div>", unsafe_allow_html=True)

        # --- 📍 TAB 2: SINIFIM ---
        with t2:
            if current_user:
                df_sinif = df[df['sinif'] == current_user['sinif']].sort_values(by="toplam_puan", ascending=False)
                for i, r in enumerate(df_sinif.itertuples(), 1):
                    rn, rc = rütbe_ata(r.toplam_puan)
                    # Aktif kullanıcıyı vurgula
                    border = "border: 2px solid #ADFF2F;" if r.ogrenci_no == current_user['ogrenci_no'] else ""
                    st.markdown(f"<div class='leader-card' style='{border}'><div><b>{i}. {r.ad_soyad}</b> <br><span class='rank-badge {rc}'>{rn}</span></div><code>{int(r.toplam_puan)} XP</code></div>", unsafe_allow_html=True)
            else:
                st.write("Sıralamanı görmek için giriş yapmalısın.")

        # --- 🏫 TAB 3: ŞAMPİYON SINIF ---
        with t3:
            # Sınıf ortalamalarını hesapla
            class_stats = df.groupby('sinif')['toplam_puan'].mean().sort_values(ascending=False).reset_index()
            if not class_stats.empty:
                st.markdown(f"<div class='pito-notu' style='text-align:center;'>👑 Zirvedeki Sınıf: <b style='color:#ADFF2F;'>{class_stats.iloc[0]['sinif']}</b></div>", unsafe_allow_html=True)
                for i, r in enumerate(class_stats.itertuples(), 1):
                    st.markdown(f"<div class='leader-card'><div><b>{i}. {r.sinif} Şubesi</b></div><code>Ort: {int(r.toplam_puan)} XP</code></div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Liderlik tablosu yüklenirken bir sorun oluştu arkadaşım: {e}")