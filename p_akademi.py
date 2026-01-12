import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import time
import base64

# --- GENEL KONFİGÜRASYON ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", initial_sidebar_state="expanded")

# --- GÖRSEL TASARIM VE CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 15px; height: 3.5em; font-weight: bold; background-color: #2E7D32; color: white; transition: 0.3s; }
    .stButton>button:hover { background-color: #D32F2F; transform: scale(1.02); }
    .stTextInput>div>div>input { border: 3px solid #2E7D32; border-radius: 12px; font-size: 20px; text-align: center; background-color: #F1F8E9; }
    .stTextInput>div>div>input:focus { border: 3px solid #FF4B4B !important; box-shadow: 0 0 10px #FF4B4B; }
    .pito-note { background-color: #E8F5E9; padding: 20px; border-radius: 15px; border-left: 10px solid #2E7D32; margin-bottom: 15px; font-size: 1.1em; }
    .sidebar-card { background: #FFFFFF; padding: 10px; border-radius: 10px; border: 1px solid #DDD; margin-bottom: 8px; font-size: 0.9em; }
    </style>
""", unsafe_allow_html=True)

# --- VERİ TABANI BAĞLANTISI ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        return conn.read(spreadsheet=SHEET_URL, ttl=0)
    except Exception:
        st.error("Veri tabanı okuma hatası! Lütfen bağlantıyı kontrol edin.")
        return pd.DataFrame()

def save_data(df):
    try:
        conn.update(spreadsheet=SHEET_URL, data=df)
    except Exception:
        st.error("Üzerine yazma hatası! Veri kaybını önlemek için işlem durduruldu.")

# --- GIF YÖNETİMİ ---
def get_pito_gif(emotion):
    try:
        with open(f"assets/pito_{emotion}.gif", "rb") as f:
            data = f.read()
            return f'data:image/gif;base64,{base64.b64encode(data).decode()}'
    except: return None

def display_pito(emotion):
    gif = get_pito_gif(emotion)
    if gif:
        st.markdown(f'<div style="text-align:center;"><img src="{gif}" width="230"></div>', unsafe_allow_html=True)
    else:
        st.warning(f"pito_{emotion}.gif dosyası assets klasöründe bulunamadı!")

# --- OYUNLAŞTIRMA VE RÜTBELER ---
RÜTBELER = ["🥚 Yeni Başlayan", "🌱 Python Çırağı", "🪵 Kod Oduncusu", "🧱 Mantık Mimarı", "🌀 Döngü Ustası", "📋 Liste Uzmanı", "📦 Fonksiyon Kaptanı", "🤖 OOP Robotu", "🏆 Python Kahramanı"]

def get_rank(points):
    idx = min(len(RÜTBELER)-1, int(points // 250))
    return RÜTBELER[idx]

# --- 12 MODÜL VE 60 EGZERSİZLİK TAM MÜFREDAT ---
MÜFREDAT = {
    1: {"başlık": "Python'a Merhaba", "not": "Python, bilgisayarla konuşmamızı sağlayan en popüler dillerden biridir. `print()` komutu parantez içindeki metni ekrana yazdırır. Unutma; metinler mutlaka tırnak `\" \"` içinde olmalı!", 
        "egz": [
            {"q": "'Selam' yazdır.", "c": "print(___)", "a": "'Selam'"},
            {"q": "Sayılar tırnaksız yazılır. 2026 yazdır.", "c": "print(___)", "a": "2026"},
            {"q": "Komutlar küçük harfle yazılır.", "c": "___('Test')", "a": "print"},
            {"q": "Parantezi kapatmayı unutma.", "c": "print('Pito'___", "a": ")"},
            {"q": "Alt alta çıktı almak için iki kez print kullan.", "c": "print('A')\n___('B')", "a": "print"}
        ]},
    2: {"başlık": "Değişken Kutuları", "not": "Değişkenler bilgi saklayan kutulardır. `x = 5` yazdığında 'x' kutusuna 5 koyarsın. İsimlerde boşluk yerine alt çizgi `_` kullanılır.",
        "egz": [
            {"q": "puan değişkenine 10 ata.", "c": "puan ___ 10", "a": "="},
            {"q": "isim değişkenine 'Pito' ata.", "c": "isim = ___", "a": "'Pito'"},
            {"q": "Değişkeni yazdır.", "c": "x=2; print(___)", "a": "x"},
            {"q": "Doğru değişken ismini tamamla.", "c": "okul___no = 1", "a": "_"},
            {"q": "İki sayıyı topla.", "c": "a=5; b=2; print(a ___ b)", "a": "+"}
        ]},
    3: {"başlık": "Girdi ve Çıktı (Input)", "not": "Kullanıcıdan veri almak için `input()` kullanılır. Sayısal veri alacaksan bunu `int()` ile sarmalamalısın!",
        "egz": [
            {"q": "İsim iste.", "c": "ad = ___('Adın?')", "a": "input"},
            {"q": "Gelen veriyi tam sayıya çevir.", "c": "yas = ___(input())", "a": "int"},
            {"q": "Mesaj ekle.", "c": "input(___)", "a": "'Sayı gir:'"},
            {"q": "Girdiyi 'veri' değişkenine ata.", "c": "___ = input()", "a": "veri"},
            {"q": "Ondalıklı sayı için float kullan.", "c": "boy = ___(input())", "a": "float"}
        ]},
    4: {"başlık": "Matematiksel İşlemler", "not": "Python'da `+`, `-`, `*`, `/` temeldir. `%` kalanı verir, `**` ise bir sayının üssünü (kuvvetini) alır.",
        "egz": [
            {"q": "10'un 3'e bölümünden kalanı bul.", "c": "print(10 ___ 3)", "a": "%"},
            {"q": "2'nin 3. kuvvetini al.", "c": "print(2 ___ 3)", "a": "**"},
            {"q": "Tam bölme yap (küsüratsız).", "c": "print(10 ___ 3)", "a": "//"},
            {"q": "Çarpma işlemi yap.", "c": "print(5 ___ 4)", "a": "*"},
            {"q": "Çıkarma işlemi yap.", "c": "print(10 ___ 5)", "a": "-"}
        ]},
    5: {"başlık": "Karar Yapıları (If-Else)", "not": "Şartlı durumlardır. 'Eğer' için `if`, 'değilse' için `else` kullanılır. Şartın sonuna `:` koymalısın!",
        "egz": [
            {"q": "Eğer x büyükse 5'ten.", "c": "___ x > 5:", "a": "if"},
            {"q": "Eşitlik kontrolü yap.", "c": "if x ___ 10:", "a": "=="},
            {"q": "Hiçbiri değilse bloğu.", "c": "___:", "a": "else"},
            {"q": "İki nokta eksik!", "c": "if x < 3___", "a": ":"},
            {"q": "İkinci bir şart ekle.", "c": "___ x == 0:", "a": "elif"}
        ]},
    6: {"başlık": "While Döngüsü", "not": "Şart doğru olduğu sürece kodun tekrar çalışmasını sağlar. Sonsuz döngüye girmemek için şartı bozacak bir adım eklemelisin.",
        "egz": [
            {"q": "Döngüyü başlat.", "c": "___ x < 5:", "a": "while"},
            {"q": "Döngüyü zorla durdur.", "c": "if x == 1: ___", "a": "break"},
            {"q": "Bir sonraki tura atla.", "c": "if x == 2: ___", "a": "continue"},
            {"q": "x değerini 1 artır.", "c": "x = x ___ 1", "a": "+"},
            {"q": "x değerini 1 azalt.", "c": "x = x ___ 1", "a": "-"}
        ]},
    7: {"başlık": "For Döngüsü ve Range", "not": "`for` döngüsü bir liste veya sayı aralığında (`range`) gezinmek için harikadır.",
        "egz": [
            {"q": "3 kez dönecek bir range yaz.", "c": "for i in range(___):", "a": "3"},
            {"q": "Liste içinde gez.", "c": "for eleman ___ liste:", "a": "in"},
            {"q": "Döngü komutunu yaz.", "c": "___ i in range(5):", "a": "for"},
            {"q": "Sayı aralığı belirle.", "c": "for i in ___(0, 10):", "a": "range"},
            {"q": "İkişer artırarak dön.", "c": "range(0, 10, ___)", "a": "2"}
        ]},
    8: {"başlık": "Listeler (Arrays)", "not": "Listeler birden fazla veriyi tek değişkende tutar. İlk eleman her zaman 0. indextedir.",
        "egz": [
            {"q": "Liste açılış parantezini koy.", "c": "liste = ___1, 2, 3]", "a": "["},
            {"q": "Listenin sonuna 'Elma' ekle.", "c": "liste.___('Elma')", "a": "append"},
            {"q": "0. elemanı yazdır.", "c": "print(liste___0___)", "a": "[0]"},
            {"q": "Listenin uzunluğunu bul.", "c": "___(liste)", "a": "len"},
            {"q": "Son elemanı sil ve getir.", "c": "liste.___( )", "a": "pop"}
        ]},
    9: {"başlık": "Metin (String) Metodları", "not": "Metinleri büyütmek, küçültmek veya parçalamak için metodlar kullanılır. Örneğin `.upper()` hepsini büyük yapar.",
        "egz": [
            {"q": "Tüm harfleri büyük yap.", "c": "metin.___()", "a": "upper"},
            {"q": "Tüm harfleri küçük yap.", "c": "metin.___()", "a": "lower"},
            {"q": "Metni boşluklardan parçala.", "c": "metin.___(' ')", "a": "split"},
            {"q": "Metnin uzunluğunu bul.", "c": "___('Pito')", "a": "len"},
            {"q": "Metin 'P' ile mi başlıyor?", "c": "metin.___('P')", "a": "startswith"}
        ]},
    10: {"başlık": "Fonksiyonlar (Def)", "not": "Tekrar eden işleri `def` ile paketleriz. Çağırdığımızda içindeki kodlar çalışır.",
         "egz": [
            {"q": "Fonksiyon tanımla.", "c": "___ selamla():", "a": "def"},
            {"q": "Sonucu dışarı aktar.", "c": "___ sonuc", "a": "return"},
            {"q": "Parametre ekle.", "c": "def topla(a, ___):", "a": "b"},
            {"q": "Fonksiyonu çağır.", "c": "topla___", "a": "()"},
            {"q": "İki nokta koy.", "c": "def test()___", "a": ":"}
        ]},
    11: {"başlık": "Hata Yakalama (Try-Except)", "not": "Programın çökmesini engellemek için `try` bloğu kullanılır. Hata olursa `except` çalışır.",
         "egz": [
            {"q": "Hata olabilecek kodu içine al.", "c": "___:", "a": "try"},
            {"q": "Hata durumunda çalışacak blok.", "c": "___:", "a": "except"},
            {"q": "Sıfıra bölme hatası adı.", "c": "except ___:", "a": "ZeroDivisionError"},
            {"q": "Hata olsun olmasın çalışan blok.", "c": "___:", "a": "finally"},
            {"q": "Hata fırlatma komutu.", "c": "___ Exception('Hata!')", "a": "raise"}
        ]},
    12: {"başlık": "Kütüphaneler ve Sınıflar", "not": "Hazır kodları `import` ile çağırırız. Sınıflar (Class) ise nesne üretmemizi sağlayan kalıplardır.",
         "egz": [
            {"q": "Math kütüphanesini dahil et.", "c": "___ math", "a": "import"},
            {"q": "Sınıf tanımla.", "c": "___ Araba:", "a": "class"},
            {"q": "Sınıf içi başlatıcı metod.", "c": "def __init__(___):", "a": "self"},
            {"q": "Nesne üret.", "c": "araba1 = ___()", "a": "Araba"},
            {"q": "Rastgele sayı kütüphanesi.", "c": "import ___", "a": "random"}
        ]}
}

# --- SESSION STATE BAŞLATMA ---
if 'page' not in st.session_state:
    st.session_state.update({'page': 'login', 'user': None, 'attempts': 0, 'points': 20})

# --- LİDERLİK TABLOSU ---
df = load_data()
with st.sidebar:
    st.title("🏆 Liderlik Tablosu")
    if not df.empty:
        df['Puan'] = pd.to_numeric(df['Puan'], errors='coerce').fillna(0)
        st.subheader("Okul İlk 10")
        for _, r in df.nlargest(10, 'Puan').iterrows():
            st.markdown(f'<div class="sidebar-card"><b>{r["Öğrencinin Adı"]}</b><br>{r["Rütbe"]} | {int(r["Puan"])} Pts</div>', unsafe_allow_html=True)
        
        s_puan = df.groupby('Sınıf')['Puan'].sum()
        if not s_puan.empty:
            st.success(f"🥇 Şampiyon Sınıf: {s_puan.idxmax()}")

# --- ANA EKRAN MANTIĞI ---
if st.session_state.page == 'login':
    display_pito("merhaba")
    st.title("Pito Python Akademi")
    okul_no = st.text_input("Okul Numaranı Gir (Belirgin):", key="login_field")
    
    if okul_no:
        if not okul_no.isdigit():
            st.error("Lütfen sadece sayısal değer girin!")
        else:
            match = df[df['Okul No'].astype(str) == okul_no]
            if not match.empty:
                user = match.iloc[0]
                st.info(f"Hoş geldin **{user['Öğrencinin Adı']}**! Kaldığın yer: Modül {user['Mevcut Modül']}, Egzersiz {user['Mevcut Egzersiz']}")
                c1, c2 = st.columns(2)
                if c1.button("Evet, Benim! Devam Et"):
                    st.session_state.update({'user': user.to_dict(), 'page': 'academy'})
                    st.rerun()
                if c2.button("Hayır, Tekrar Gir"): st.rerun()
            else:
                st.warning("Kayıt bulunamadı. Yeni bir profil oluşturalım!")
                with st.form("yeni_kayit"):
                    ad = st.text_input("Adın Soyadın:")
                    snf = st.selectbox("Sınıfın:", ["9-A", "9-B", "10-A", "10-B", "11-A", "12-A"])
                    if st.form_submit_button("Kayıt Ol ve Başla"):
                        new = {"Okul No": int(okul_no), "Öğrencinin Adı": ad, "Sınıf": snf, "Puan": 0, "Rütbe": RÜTBELER[0], "Tamamlanan Modüller": 0, "Mevcut Modül": 1, "Mevcut Egzersiz": 1, "Tarih": time.strftime("%d-%m-%Y")}
                        df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
                        save_data(df); st.success("Kaydın yapıldı! Şimdi giriş yap."); time.sleep(1); st.rerun()

elif st.session_state.page == 'academy':
    user = st.session_state.user
    m_id = int(user['Mevcut Modül'])
    e_id = int(user['Mevcut Egzersiz'])
    
    # Mezuniyet
    if m_id > 12:
        display_pito("mezun"); st.balloons(); st.header("🎓 Tebrikler Mezun Oldun!")
        if st.button("Eğitimi Tekrar Al (Puan Sıfırlanır)"):
            user.update({'Mevcut Modül': 1, 'Mevcut Egzersiz': 1, 'Puan': 0})
            idx = df[df['Okul No'] == user['Okul No']].index[0]; df.iloc[idx] = user; save_data(df); st.rerun()
        if st.button("Liderlik Tablosunda Kal ve Çıkış Yap"): 
            st.session_state.page = 'login'; st.rerun()
        st.stop()

    st.progress(((m_id - 1) * 5 + (e_id - 1)) / 60)
    col_p, col_c = st.columns([1, 2])
    
    with col_p:
        if st.session_state.attempts >= 4: display_pito("hata")
        else: display_pito("dusunuyor")
        st.metric("Mevcut Puanın", int(user['Puan']))
        st.write(f"Rütbe: {user['Rütbe']}")

    with col_c:
        st.markdown(f"### Modül {m_id}: {MÜFREDAT[m_id]['başlık']}")
        st.markdown(f'<div class="pito-note"><b>🐍 Pito\'nun Notu:</b><br>{MÜFREDAT[m_id]["not"]}</div>', unsafe_allow_html=True)
        egz = MÜFREDAT[m_id]['egz'][e_id-1]
        st.subheader(f"Egzersiz {e_id}")
        st.info(egz['q'])
        st.code(egz['c'], language="python")
        
        ans = st.text_input("Boşluğu doldur (Veri girilmeden kontrol edilmez):", key=f"e_{m_id}_{e_id}")
        
        if st.button("Kontrol Et ✅"):
            if not ans: st.warning("⚠️ Lütfen boşluğu doldur!")
            elif ans.strip() == egz['a']:
                st.balloons(); display_pito("basari"); st.success(f"Harika! +{st.session_state.points} Puan kazandın.")
                st.code(f"Kod Çıktısı: {egz['a'].replace(\"'\",\"\")}")
                user['Puan'] += st.session_state.points
                user['Rütbe'] = get_rank(user['Puan'])
                if e_id < 5: user['Mevcut Egzersiz'] += 1
                else: user['Mevcut Modül'] += 1; user['Mevcut Egzersiz'] = 1
                idx = df[df['Okul No'] == user['Okul No']].index[0]; df.iloc[idx] = user; save_data(df)
                st.session_state.update({'attempts': 0, 'points': 20}); time.sleep(2); st.rerun()
            else:
                st.session_state.attempts += 1; st.session_state.points = max(0, st.session_state.points - 5)
                st.error(f"❌ {st.session_state.attempts}. hata! Puanın düşüyor.")
                if st.session_state.attempts == 3: st.warning(f"💡 İpucu: Cevap '{egz['a']}' olmalı.")
                if st.session_state.attempts >= 4:
                    st.error("❗ 4 hata yaptın, puan kazanamadın."); st.write(f"Doğru Çözüm: {egz['a']}")
                    if st.button("Sıradaki Adıma Geç ➡️"):
                        if e_id < 5: user['Mevcut Egzersiz'] += 1
                        else: user['Mevcut Modül'] += 1; user['Mevcut Egzersiz'] = 1
                        idx = df[df['Okul No'] == user['Okul No']].index[0]; df.iloc[idx] = user; save_data(df)
                        st.session_state.update({'attempts': 0, 'points': 20}); st.rerun()
