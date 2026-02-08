import streamlit as st
import pandas as pd

def rütbe_ata(xp):
    if xp >= 1000: return "🏆 Bilge", "badge-bilge"
    if xp >= 500: return "🔥 Savaşçı", "badge-savasci"
    if xp >= 200: return "🐍 Pythonist", "badge-pythonist"
    return "🥚 Çömez", "badge-comez"

def liderlik_tablosu_goster(supabase, current_user=None):
    # CSS kodlarını buraya (öncekiyle aynı) ekleyebilirsin
    try:
        # HIZ OPTİMİZASYONU: Sadece ilk 20 kişiyi çek
        res = supabase.table("kullanicilar").select("*").order("toplam_puan", desc=True).limit(20).execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

        if not df.empty:
            # ZİRVEDEKİ ŞUBE (Filtreleme aynı kalıyor)
            aktif_df = df[df['toplam_puan'] > 0]
            if not aktif_df.empty:
                class_stats = aktif_df.groupby('sinif')['toplam_puan'].mean().sort_values(ascending=False).reset_index()
                winner = class_stats.iloc[0]
                st.markdown(f'''<div class="top-class-card">
                    <div class="top-class-title">👑 ZİRVEDEKİ ŞUBE</div>
                    <div class="top-class-name">{winner['sinif']}</div>
                </div>''', unsafe_allow_html=True)

            t_sinif, t_okul = st.tabs(["📍 SINIF", "🌍 OKUL (TOP 20)"])
            with t_sinif:
                if current_user:
                    # Sadece mevcut sınıftakileri filtrele
                    sinif_list = df[df['sinif'] == current_user['sinif']].sort_values(by="toplam_puan", ascending=False)
                    for i, r in enumerate(sinif_list.itertuples(), 1):
                        rn, rc = rütbe_ata(r.toplam_puan)
                        me = "row-me" if r.ogrenci_no == current_user['ogrenci_no'] else ""
                        st.markdown(f'<div class="rank-row {me}">{r.ad_soyad[:15]} - {int(r.toplam_puan)} XP</div>', unsafe_allow_html=True)
            with t_okul:
                for i, r in enumerate(df.itertuples(), 1):
                    st.markdown(f'<div class="rank-row">#{i} {r.ad_soyad[:15]} - {int(r.toplam_puan)} XP</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Siber-hata: {e}")
