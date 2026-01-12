import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import time
import base64

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pito Python Akademi", layout="wide", initial_sidebar_state="expanded")

# --- GÖRSEL TASARIM ---
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
    return conn.read(spreadsheet=SHEET_URL, ttl=0)

def save_data(df):
    conn.update(spreadsheet=SHEET_URL, data=df)

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

# --- RÜTBELER VE MÜFREDAT ---
RÜTBELER = ["🥚 Yeni Başlayan", "🌱 Python Çırağı", "🪵 Kod Oduncusu", "🧱 Mantık Mimarı", "🌀 Döngü Ustası", "📋 Liste Uzmanı", "📦 Fonksiyon Kaptanı", "🤖 OOP Robotu", "🏆 Python Kahramanı"]

def get_rank(points):
    idx = min(len(RÜTBELER)-1, int(points // 250))
    return RÜTBELER[idx]

MÜFREDAT = {
    1: {"başlık": "Merhaba Python", "not": "Python'da `print()` komutu ekrana yazı yazdırır. Metinler tırnak içinde olmalıdır.", 
        "egz": [{"q": "'Selam' yazdır.", "c": "print(___)", "a": "'Selam'"}, {"q": "2026 yazdır.", "c": "print(___)", "a": "2026"}, {"q": "Küçük harf kullan.", "c": "___('Test')", "a": "print"}, {"q": "Kapat.", "c": "print('Pito'___", "a": ")"}, {"q": "Alt alta.", "c": "print('A')\n___('B')", "a": "print"}]},
    2: {"başlık": "Değişkenler", "not": "Verileri saklamak için değişkenleri kullanırız. Örn: `sayi = 10`",
        "egz": [{"q": "x'e 5 ata.", "c": "x ___ 5", "a": "="}, {"q": "ad ata.", "c": "ad = ___", "a": "'Pito'"}, {"q": "Yazdır.", "c": "x=2; print(___)", "a": "x"}, {"q": "Alt çizgi.", "c": "okul___no = 1", "a": "_"}, {"q": "Topla.", "c": "a=5; b=2; print(a ___ b)", "a": "+"}]},
    3: {"başlık": "Veri Girişi", "not": "`input()` ile kullanıcıdan veri alırız. Sayılar için `int()` şart!",
        "egz": [{"q": "İsim al.", "c": "ad = ___('Adın?')", "a": "input"}, {"q": "Sayıya çevir.", "c": "yas = ___(input())", "a": "int"}, {"q": "Mesaj.", "c": "input(___)", "a": "'Giriş:'"}, {"q": "Değişken.", "c": "___ = input()", "a": "veri"}, {"q": "Ondalıklı.", "c": "boy = ___(input())", "a": "float"}]},
    4: {"başlık": "Matematik", "not": "Matematik operatörleri: `+`, `-`, `*`, `/`. Kalan için `%`, kuvvet için `**`.",
        "egz": [{"q": "Kalanı bul.", "c": "10 ___ 3", "a": "%"}, {"q": "Kuvvet.", "c": "2 ___ 3", "a": "**"}, {"q": "Tam bölme.", "c": "10 ___ 3", "a": "//"}, {"q": "Çarp.", "c": "5 ___ 4", "a": "*"}, {"q": "Çıkar.", "c": "10 ___ 5", "a": "-"}]},
    5: {"başlık": "Karar (If)", "not": "Şartlı durumlar: `if x > 5:`. Şartın sonuna `:` koymayı unutma.",
        "egz": [{"q": "Eğer.", "c": "___ x > 5:", "a": "if"}, {"q": "Eşitlik.", "c": "if x ___ 10:", "a": "=="}, {"q": "Değilse.", "c": "___:", "a": "else"}, {"q": "İki nokta.", "c": "if x < 3___", "a": ":"}, {"q": "Ek şart.", "c": "___ x == 0:", "a": "elif"}]},
    6: {"başlık": "While Döngüsü", "not": "Şart doğru olduğu sürece çalışır: `while x < 5:`.",
        "egz": [{"q": "Başlat.", "c": "___ x < 5:", "a": "while"}, {"q": "Durdur.", "c": "if x == 1: ___", "a": "break"}, {"q": "Atla.", "c": "if x == 2: ___", "a": "continue"}, {"q": "Artır.", "c": "x = x ___ 1", "a": "+"}, {"q": "Azalt.", "c": "x = x ___ 1", "a": "-"}]},
    7: {"başlık": "For Döngüsü", "not": "`for i in range(5):` belirli sayıda tekrar sağlar.",
        "egz": [{"q": "Aralık.", "c": "for i in range(___):", "a": "3"}, {"q": "İçinde.", "c": "for x ___ liste:", "a": "in"}, {"q": "Döngü.", "c": "___ i in range(5):", "a": "for"}, {"q": "Komut.", "c": "for i in ___(0, 5):", "a": "range"}, {"q": "Artış.", "c": "range(0, 5, ___)", "a": "1"}]},
    8: {"başlık": "Listeler", "not": "Birden fazla veriyi `[]` içinde saklarız.",
        "egz": [{"q": "Parantez.", "c": "liste = ___1, 2]", "a": "["}, {"q": "Ekle.", "c": "liste.___('A')", "a": "append"}, {"q": "Index.", "c": "print(liste___0___)", "a": "[0]"}, {"q": "Uzunluk.", "c": "___(liste)", "a": "len"}, {"q": "Sil.", "c": "liste.___( )", "a": "pop"}]},
    9: {"başlık": "Metinler", "not": "Metin metodları: `.upper()`, `.lower()`, `.split()`.",
        "egz": [{"q": "Büyük yap.", "c": "m.___()", "a": "upper"}, {"q": "Küçük yap.", "c": "m.___()", "a": "lower"}, {"q": "Parçala.", "c": "m.___(' ')", "a": "split"}, {"q": "Uzunluk.", "c": "___('Pito')", "a": "len"}, {"q": "Başlangıç.", "c": "m.___('P')", "a": "startswith"}]},
    10: {"başlık": "Fonksiyonlar", "not": "Kodları `def` ile paketleriz.",
         "egz": [{"q": "Tanımla.", "c": "___ test():", "a": "def"}, {"q": "Döndür.", "c": "___ x", "a": "return"}, {"q": "Parametre.", "c": "def f(a, ___):", "a": "b"}, {"q": "Çağır.", "c": "test___", "a": "()"}, {"q": "İşaret.", "c": "def f()___", "a": ":"}]},
    11: {"başlık": "Hata Yakalama", "not": "`try-except` ile programın çökmesini önleriz.",
         "egz": [{"q": "Dene.", "c": "___:", "a": "try"}, {"q": "Hata.", "c": "___:", "a": "except"}, {"q": "Tür.", "c": "except ___:", "a": "ValueError"}, {"q": "Sonra.", "c": "___:", "a": "finally"}, {"q": "Fırlat.", "c": "___ Exception()", "a": "raise"}]},
    12: {"başlık": "Sınıflar", "not": "OOP temelleri: `class` ve `self` kullanımı.",
         "egz": [{"q": "Kütüphane.", "c": "___ math", "a": "import"}, {"q": "Sınıf.", "c": "___ Araba:", "a": "class"}, {"q": "Metod.", "c": "def __init__(___):", "a": "self"}, {"q": "Nesne.", "c": "a = ___()", "a": "Araba"}, {"q": "Rastgele.", "c": "import ___", "a": "random"}]}
}

# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.update({'page': 'login', 'user': None, 'attempts': 0, 'points': 20})

# --- SIDEBAR ---
df = load_data()
with st.sidebar:
    st.title("🏆 Liderlik Tablosu")
    if not df.empty:
        df['Puan'] = pd.to_numeric(df['Puan'], errors='coerce').fillna(0)
        st.subheader("Okul İlk 10")
        for _, r in df.nlargest(10, 'Puan').iterrows():
            st.markdown(f'<div class="sidebar-card"><b>{r["Öğrencinin Adı"]}</b><br>{r["Rütbe"]} | {int(r["Puan"])} Pts</div>', unsafe_allow_html=True)

# --- ANA MOTOR ---
if st.session_state.page == 'login':
    display_pito("merhaba")
    st.title("Pito Python Akademi")
    okul_no = st.text_input("Okul Numaranı Gir:", key="login_field")
    if okul_no:
        match = df[df['Okul No'].astype(str) == okul_no]
        if not match.empty:
            user = match.iloc[0]
            st.info(f"Hoş geldin **{user['Öğrencinin Adı']}**!")
            if st.button("Evet, Benim! Devam Et"):
                st.session_state.update({'user': user.to_dict(), 'page': 'academy'})
                st.rerun()
        else:
            st.warning("Kayıt bulunamadı. Yeni profil oluştur!")
            with st.form("yeni"):
                ad = st.text_input("Ad Soyad:")
                snf = st.selectbox("Sınıf:", ["9-A", "9-B", "10-A", "10-B"])
                if st.form_submit_button("Kayıt Ol"):
                    new = {"Okul No": int(okul_no), "Öğrencinin Adı": ad, "Sınıf": snf, "Puan": 0, "Rütbe": RÜTBELER[0], "Mevcut Modül": 1, "Mevcut Egzersiz": 1, "Tarih": time.strftime("%d-%m-%Y")}
                    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
                    save_data(df); st.success("Kayıt başarılı! Giris yap."); st.rerun()

elif st.session_state.page == 'academy':
    user = st.session_state.user
    m_id, e_id = int(user['Mevcut Modül']), int(user['Mevcut Egzersiz'])
    if m_id > 12:
        display_pito("mezun"); st.balloons(); st.header("🎓 Tebrikler!")
        if st.button("Sıfırla"):
            user.update({'Mevcut Modül': 1, 'Mevcut Egzersiz': 1, 'Puan': 0})
            idx = df[df['Okul No'] == user['Okul No']].index[0]; df.iloc[idx] = user; save_data(df); st.rerun()
        st.stop()

    st.progress(((m_id - 1) * 5 + (e_id - 1)) / 60)
    col_p, col_c = st.columns([1, 2])
    with col_p:
        display_pito("hata" if st.session_state.attempts >= 4 else "dusunuyor")
        st.metric("Puanın", int(user['Puan']))
    with col_c:
        st.markdown(f"### Modül {m_id}: {MÜFREDAT[m_id]['başlık']}")
        st.markdown(f'<div class="pito-note">{MÜFREDAT[m_id]["not"]}</div>', unsafe_allow_html=True)
        egz = MÜFREDAT[m_id]['egz'][e_id-1]
        st.info(egz['q']); st.code(egz['c'], language="python")
        ans = st.text_input("Cevabın:", key=f"e_{m_id}_{e_id}")
        
        if st.button("Kontrol Et ✅"):
            if not ans: st.warning("Boş bırakma!")
            elif ans.strip() == egz['a']:
                st.balloons(); display_pito("basari"); st.success(f"+{st.session_state.points} Puan!")
                # Çıktı kısmındaki syntax hatası giderildi:
                temiz_cikti = str(egz['a']).replace("'", "").replace('"', "")
                st.code(f"Kod Çıktısı: {temiz_cikti}")
                user['Puan'] += st.session_state.points
                user['Rütbe'] = get_rank(user['Puan'])
                if e_id < 5: user['Mevcut Egzersiz'] += 1
                else: user['Mevcut Modül'] += 1; user['Mevcut Egzersiz'] = 1
                idx = df[df['Okul No'] == user['Okul No']].index[0]; df.iloc[idx] = user; save_data(df)
                st.session_state.update({'attempts': 0, 'points': 20}); time.sleep(2); st.rerun()
            else:
                st.session_state.attempts += 1; st.session_state.points = max(0, st.session_state.points - 5)
                if st.session_state.attempts == 3: st.warning(f"💡 İpucu: '{egz['a']}'")
                if st.session_state.attempts >= 4:
                    st.error(f"Doğru: {egz['a']}")
                    if st.button("Geç"):
                        if e_id < 5: user['Mevcut Egzersiz'] += 1
                        else: user['Mevcut Modül'] += 1; user['Mevcut Egzersiz'] = 1
                        idx = df[df['Okul No'] == user['Okul No']].index[0]; df.iloc[idx] = user; save_data(df)
                        st.session_state.update({'attempts': 0, 'points': 20}); st.rerun()
