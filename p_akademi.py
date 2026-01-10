import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import os
import base64

# --- 1. TASARIM VE SAYFA AYARLARI ---
st.set_page_config(layout="wide", page_title="Pito Python Akademi", initial_sidebar_state="collapsed")

# --- 2. HAFIZA BAŞLATMA (HATA ÖNLEYİCİ) ---
initial_states = {
    'is_logged_in': False, 'student_name': "", 'student_no': "", 'student_class': "",
    'completed_modules': [False]*8, 'current_module': 0, 'current_exercise': 0,
    'exercise_passed': False, 'total_score': 0, 'scored_exercises': set(),
    'db_module': 0, 'db_exercise': 0, 'current_potential_score': 20,
    'celebrated': False, 'rejected_user': False, 'pito_emotion': "pito_merhaba"
}

for key, value in initial_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- 3. GIF OYNATICI (BASE64) ---
def get_pito_gif(gif_name, width=280):
    gif_path = f"assets/{gif_name}.gif"
    if os.path.exists(gif_path):
        with open(gif_path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
        return f'<div style="text-align: center;"><img src="data:image/gif;base64,{encoded}" width="{width}"></div>'
    return f'<div style="text-align: center;"><img src="https://img.icons8.com/fluency/200/robot-viewer.png" width="{width}"></div>'

SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]
RUTBELER = ["🥚 Yeni Başlayan", "🌱 Python Çırağı", "🪵 Kod Oduncusu", "🧱 Mantık Mimarı", "🌀 Döngü Ustası", "📋 Liste Uzmanı", "📦 Fonksiyon Kaptanı", "🤖 OOP Robotu", "🏆 Python Kahramanı"]

st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem;}
    .pito-bubble {
        position: relative; background: #f0f2f6; border: 2px solid #3a7bd5;
        border-radius: 15px; padding: 25px; margin: 0 auto 30px auto; color: #1e1e1e;
        font-weight: 500; font-size: 1.2rem; text-align: center; max-width: 650px;
        box-shadow: 4px 4px 15px rgba(0,0,0,0.1);
    }
    .pito-bubble:after {
        content: ''; position: absolute; bottom: -20px; left: 50%; transform: translateX(-50%);
        border-width: 20px 20px 0; border-style: solid; border-color: #3a7bd5 transparent;
    }
    .leaderboard-card { background: linear-gradient(135deg, #1e1e1e, #2d2d2d); border-radius: 12px; padding: 10px; margin-bottom: 8px; color: white; border: 1px solid #444; }
    .champion-card { background: linear-gradient(135deg, #FFD700, #FFA500); border-radius: 15px; padding: 15px; margin-top: 20px; color: #1e1e1e; text-align: center; font-weight: bold; }
    .stButton > button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important; color: white !important; font-weight: bold; border: none; }
    .retrain-btn > button { background: linear-gradient(45deg, #e53935, #e35d5b) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. VERİ TABANI YÖNETİMİ ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db(use_cache=True):
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=0 if not use_cache else 60)
        if df is None or df.empty: return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        df["Okul No"] = df["Okul No"].astype(str).str.split('.').str[0].str.strip()
        df["Puan"] = pd.to_numeric(df["Puan"], errors='coerce').fillna(0).astype(int)
        df["Mevcut Modül"] = pd.to_numeric(df["Mevcut Modül"], errors='coerce').fillna(0).astype(int)
        df["Mevcut Egzersiz"] = pd.to_numeric(df["Mevcut Egzersiz"], errors='coerce').fillna(0).astype(int)
        return df.dropna(subset=["Okul No"])
    except: return pd.DataFrame()

def force_save():
    try:
        no = str(st.session_state.student_no).strip()
        df_all = get_db(use_cache=False)
        df_clean = df_all[df_all["Okul No"] != no]
        progress = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = RUTBELER[sum(st.session_state.completed_modules)]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, int(st.session_state.total_score), rank, progress, int(st.session_state.db_module), int(st.session_state.db_exercise), datetime.now().strftime("%H:%M:%S")]], columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

# --- 5. GİRİŞ EKRANI ---
if not st.session_state.is_logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba! Ben <b>Pito</b>.<br>Python Dünyası\'na hoş geldin maceracı!</div>', unsafe_allow_html=True)
        st.markdown(get_pito_gif("pito_merhaba", width=320), unsafe_allow_html=True)
        if st.session_state.rejected_user: st.warning("⚠️ O halde kendi okul numaranı gir!")
        in_no_raw = st.text_input("Okul Numaran:", key="login_field").strip()
        if in_no_raw and not in_no_raw.isdigit(): st.error("⚠️ Sadece rakam giriniz!")
        elif in_no_raw:
            if st.session_state.rejected_user: st.session_state.rejected_user = False
            df = get_db(use_cache=False)
            user_data = df[df["Okul No"] == in_no_raw] if not df.empty else pd.DataFrame()
            if not user_data.empty:
                row = user_data.iloc[0]
                st.info(f"🔍 Bu numara **{row['Öğrencinin Adı']}** adına kayıtlı.")
                st.markdown("<h4 style='text-align: center;'>Sen bu kişi misin? 🤔</h4>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Evet, Benim"):
                        m_v = int(row['Mevcut Modül'])
                        e_v = int(row['Mevcut Egzersiz'])
                        st.session_state.update({
                            'student_no': in_no_raw, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"],
                            'total_score': int(row["Puan"]), 'db_module': m_v, 'db_exercise': e_v,
                            'current_module': min(m_v, 7), 'current_exercise': e_v if m_v < 8 else 0,
                            'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")],
                            'is_logged_in': True, 'pito_emotion': "pito_dusunuyor" if m_v < 8 else "pito_mezun"
                        })
                        st.rerun()
                with c2:
                    if st.button("❌ Hayır, Ben Değilim"):
                        st.session_state.rejected_user = True
                        if "login_field" in st.session_state: del st.session_state["login_field"]
                        st.rerun()
            else:
                in_name = st.text_input("Adın Soyadın:", key="new_name")
                in_class = st.selectbox("Sınıfın:", SINIFLAR, key="new_class")
                if st.button("Maceraya Başla! ✨") and in_name:
                    st.session_state.update({'student_no': in_no_raw, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True})
                    force_save(); st.rerun()
    st.stop()

# --- 6. MÜFREDAT KONU ANLATIMI VE EGZERSİZLER ---
training_data = [
    {"module_title": "1. Giriş ve Çıktı", "exercises": [
        {"msg": "Python'da ekrana bir yazı yazdırmak için **print()** fonksiyonunu kullanırız. Metinsel ifadeleri mutlaka **tek veya çift tırnak** içine almalısın. Hadi dene: Ekrana **'Merhaba Pito'** yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')"},
        {"msg": "Matematiksel değer olan sayıları ekrana yazdırırken **tırnak işareti kullanmayız.** Şimdi ekrana **100** sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o, "solution": "print(100)"},
        {"msg": "Birden fazla veriyi aynı satırda yazdırmak için aralarına **virgül (,)** koyarız. Virgül, otomatik olarak bir boşluk bırakır. Hadi dene: **'Puan:'** yazısı ile **100** sayısını yan yana yazdır.", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o, "solution": "print('Puan:', 100)"},
        {"msg": "**# (Diyez)** işaretiyle başlayan satırlar Python tarafından okunmaz. Bunlara 'Yorum Satırı' denir ve kendimize not bırakmak için kullanırız. Hadi dene: Bir **#** işareti koyarak yanına **Not** yaz.", "task": "___ Bu bir nottur", "check": lambda c, o: "#" in c, "solution": "# Notum"},
        {"msg": "Yazıları farklı satırlara geçirmek için metin içinde **'\\n'** karakterini kullanırız. Hadi dene: Tek bir print içinde **'Üst'** ve **'Alt'** kelimelerini alt alta yazdır.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o, "solution": "print('Üst' + '\\n' + 'Alt')"}
    ]},
    {"module_title": "2. Değişkenler ve Bilgi Saklama", "exercises": [
        {"msg": "Değişkenler, bilgileri hafızada tutan isimli kutulardır. **yas = 15** yazdığında 'yas' isminde bir kutu oluşturup içine 15 sayısını koymuş olursun. Hadi dene: **yas** değişkenine **15** ata ve yazdır.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o, "solution": "yas = 15\nprint(yas)"},
        {"msg": "Değişkenlere metin de atayabiliriz. Hadi dene: **isim** adında bir değişken oluştur, içine **'Pito'** değerini ata ve ekrana yazdır.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o, "solution": "isim = 'Pito'\nprint(isim)"},
        {"msg": "**input()** fonksiyonu ile dışarıdan (kullanıcıdan) bilgi alırız. Hadi dene: **'Adın: '** sorusuyla bir input al, bunu **ad** değişkenine ata ve yazdır.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c, "solution": "ad = input('Adın: ')\nprint(ad)"},
        {"msg": "Bazen sayıları metne çevirmemiz gerekir. Bunun için **str()** fonksiyonunu kullanırız. Hadi dene: **s = 10** değişkenini metne çevirip yazdır.", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c, "solution": "s = 10\nprint(str(s))"},
        {"msg": "Kullanıcıdan gelen her bilgi metin olarak algılanır. Eğer matematiksel işlem yapacaksan bunu **int()** ile tam sayıya çevirmelisin. Hadi dene: n değişkenine gelen **input** değerini **int**'e çevir.", "task": "n = ___(___('Sayı: '))\nprint(n + 1)", "check": lambda c, o: "int" in c and "input" in c, "solution": "n = int(input('10'))\nprint(n + 1)"}
    ]},
    {"module_title": "3. Karar Yapıları (If-Else)", "exercises": [
        {"msg": "Bilgisayarların seçim yapması için **if** kullanırız. Eşitliği kontrol etmek için tek değil, **çift eşittir (==)** kullanılır. Hadi dene: Eğer 10 sayısı **10'a eşitse** ekrana 'X' yazdır.", "task": "if 10 ___ 10: print('X')", "check": lambda c, o: "==" in c, "solution": "if 10 == 10: print('X')"},
        {"msg": "Şart sağlanmadığında çalışacak bölüm **else:** bloğudur. Hadi dene: 5 sayısı 10'dan büyük değilse ekrana **'Y'** yazdıracak bir else bloğu kur.", "task": "if 5>10: pass\n___: print('Y')", "check": lambda c, o: "else" in c, "solution": "if 5>10: pass\nelse: print('Y')"},
        {"msg": "**'>='** operatörü büyük veya eşiti kontrol eder. Hadi dene: Eğer 5 sayısı **5'ten büyük veya eşitse** ekrana 'Z' yazdır.", "task": "if 5 ___ 5: print('Z')", "check": lambda c, o: ">=" in c, "solution": "if 5 >= 5: print('Z')"},
        {"msg": "**'and'** anahtar kelimesi ile iki koşulun da aynı anda doğru olması istenir. Hadi dene: Eğer 1 eşit 1 **ve** 2 eşit 2 ise ekrana 'OK' yazdır.", "task": "if 1==1 ___ 2==2: print('OK')", "check": lambda c, o: "and" in c, "solution": "if 1==1 and 2==2: print('OK')"},
        {"msg": "**'elif'** (else if), ilk şart yanlışsa başka bir şartı kontrol eder. Hadi dene: 5>10 yanlışsa ama **5==5 doğruysa** ekrana 'A' yazdır.", "task": "if 5>10: pass\n___ 5==5: print('A')", "check": lambda c, o: "elif" in c, "solution": "if 5>10: pass\nelif 5==5: print('A')"}
    ]},
    {"module_title": "4. Döngüler (Loops)", "exercises": [
        {"msg": "**'for'** döngüsü ve **range()** fonksiyonu ile bir işlemi defalarca tekrarlayabilirsin. Hadi dene: **range(3)** kullanarak 3 kez 'X' yazdır.", "task": "for i in ___(3): print('X')", "check": lambda c, o: o.count("X")==3, "solution": "for i in range(3): print('X')"},
        {"msg": "**'while'** döngüsü, yanındaki şart doğru olduğu sürece çalışmaya devam eder. Hadi dene: **i<1** doğruyken 'Y' yazdıran döngüyü kur.", "task": "i=0\n___ i<1: print('Y'); i+=1", "check": lambda c, o: "while" in c, "solution": "i=0\nwhile i<1: print('Y'); i+=1"},
        {"msg": "**'break'** komutu döngüyü o an bitirir. Hadi dene: i değeri 1 olduğunda döngüyü **sonlandır**.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "break" in c, "solution": "for i in range(3):\n    if i==1: break\n    print(i)"},
        {"msg": "**'continue'** komutu döngüde o adımı atlayıp bir sonrakine geçer. Hadi dene: i değeri 1 olduğunda o adımı **atla**.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "continue" in c, "solution": "for i in range(3):\n    if i==1: continue\n    print(i)"},
        {"msg": "Döngü sayacı olan **i** değişkeni her turda değişir. Hadi dene: Döngü içindeki **i** sayacını print ile ekrana yazdır.", "task": "for i in range(2): print(___)", "check": lambda c, o: "1" in o, "solution": "for i in range(2): print(i)"}
    ]},
    {"module_title": "5. Listeler (Lists)", "exercises": [
        {"msg": "Listeler birçok veriyi bir arada tutar ve **[]** köşeli parantez ile gösterilir. Hadi dene: **10** ve **20** sayılarından oluşan bir liste oluştur.", "task": "L = [___, 20]", "check": lambda c, o: "10" in c, "solution": "L = [10, 20]\nprint(L)"},
        {"msg": "Listenin elemanlarına 0'dan başlayarak erişiriz. **L[0]** ilk elemanı verir. Hadi dene: L listesinin **ilk elemanına** (0. indeks) eriş.", "task": "L=[5,6]\nprint(L[___])", "check": lambda c, o: "5" in o, "solution": "L=[5,6]\nprint(L[0])"},
        {"msg": "**len()** fonksiyonu listenin içinde kaç tane eleman olduğunu söyler. Hadi dene: L listesinin eleman sayısını ekrana yazdır.", "task": "L=[1,2]\nprint(___(L))", "check": lambda c, o: "2" in o, "solution": "L=[1,2]\nprint(len(L))"},
        {"msg": "**append()** metodu listenin en sonuna yeni bir eleman ekler. Hadi dene: L listesine **30** sayısını ekle.", "task": "L=[10]\nL.___(___)\nprint(L)", "check": lambda c, o: "30" in o, "solution": "L=[10]\nL.append(30)\nprint(L)"},
        {"msg": "**pop()** metodu listeden bir eleman siler (genelde son elemanı). Hadi dene: Listeden son elemanı **çıkart**.", "task": "L=[1,2]\nL.___()\nprint(L)", "check": lambda c, o: "1" in o, "solution": "L=[1,2]\nL.pop()\nprint(L)"}
    ]},
    {"module_title": "6. Fonksiyonlar ve Veri Türleri", "exercises": [
        {"msg": "Fonksiyonlar bir kez yazılıp defalarca kullanılan kod bloklarıdır ve **def** ile tanımlanır. Hadi dene: **f** adında bir fonksiyon tanımla.", "task": "___ f(): print('X')", "check": lambda c, o: "def" in c, "solution": "def f(): print('X')\nf()"},
        {"msg": "**Tuple (Demet)** listeye benzer ama içindeki veriler değiştirilemez. **()** parantez ile oluşturulur. Hadi dene: **1** rakamlı bir demet oluştur.", "task": "t = (___, 2)\nprint(t)", "check": lambda c, o: "1" in c, "solution": "t = (1, 2)\nprint(t)"},
        {"msg": "**Sözlükler (Dict)** Anahtar:Değer mantığıyla çalışır. Hadi dene: **'ad'** anahtarına **'Pito'** değerini eşle ve yazdır.", "task": "d = {'ad': '___'}\nprint(d['ad'])", "check": lambda c, o: "Pito" in c, "solution": "d = {'ad': 'Pito'}\nprint(d['ad'])"},
        {"msg": "**keys()** metodu sözlükteki tüm anahtar isimlerini listeler. Hadi dene: d sözlüğündeki anahtarları ekrana getir.", "task": "d={'a':1}\nprint(d.___())", "check": lambda c, o: "keys" in c, "solution": "d={'a':1}\nprint(d.keys())"},
        {"msg": "**Set (Küme)** içinde her veriden sadece bir tane barındırır. Hadi dene: Aynı sayıların olduğu ama küme sayesinde teke düşen bir küme oluştur.", "task": "s = {1, 2, ___}\nprint(s)", "check": lambda c, o: "1" in c, "solution": "s = {1, 2, 1}\nprint(s)"}
    ]},
    {"module_title": "7. Nesne Tabanlı Programlama (OOP)", "exercises": [
        {"msg": "**Sınıf (Class)** bir nesnenin taslağıdır. **class** yazarak bir **Robot** taslağı oluştur.", "task": "___ Robot: pass", "check": lambda c, o: "class" in c, "solution": "class Robot: pass"},
        {"msg": "Taslaktan gerçek bir nesne üretmeye 'örnekleme' denir. Hadi dene: **R** sınıfından **p** adında bir nesne üret.", "task": "class R: pass\np = ___()", "check": lambda c, o: "R()" in c, "solution": "class R: pass\np = R()"},
        {"msg": "Nesnelere özellik ekleyebiliriz. Hadi dene: Robota **renk** özelliği olarak **'Mavi'** ata.", "task": "class R: pass\np=R()\np.___ = 'Mavi'\nprint(p.renk)", "check": lambda c, o: "renk" in c, "solution": "class R: pass\np=R()\np.renk = 'Mavi'\nprint(p.renk)"},
        {"msg": "Sınıf içindeki fonksiyonlara 'Metot' denir ve ilk parametresi mutlaka **self** olmalıdır. Hadi dene: Robota bir **ses** metodu ekle.", "task": "class R:\n def ___(self):\n  print('Bip!')", "check": lambda c, o: "ses" in c, "solution": "class R:\n    def ses(self): print('Bip!')\nr = R()\nr.ses()"},
        {"msg": "Bir metodu çalıştırmak için **nesne.metot()** yazılır. Hadi dene: **r** nesnesi üzerinden **s** metodunu çağır.", "task": "class R:\n def s(self): print('X')\nr=R()\nr.___()", "check": lambda c, o: "s()" in c, "solution": "class R:\n    def s(self): print('X')\nr=R()\nr.s()"}
    ]},
    {"module_title": "8. Dosya Yönetimi", "exercises": [
        {"msg": "**open()** ile dosya açarız. **'w'** kipi yazmak (write) içindir. Hadi dene: n.txt dosyasını yazma modunda aç.", "task": "dosya = ___('n.txt', '___')", "check": lambda c, o: "open" in c, "solution": "f = open('n.txt', 'w')\nf.write('Test')\nf.close()"},
        {"msg": "**write()** metodu dosyanın içine yazı yazar. Hadi dene: Dosyaya **'Pito'** yazdır ve dosyayı kapat.", "task": "f = open('t.txt', 'w'); f.___('Pito'); f.close()", "check": lambda c, o: "write" in c, "solution": "f = open('t.txt', 'w'); f.write('Pito'); f.close()"},
        {"msg": "**'r'** kipi sadece okumak (read) içindir. Hadi dene: t.txt dosyasını okuma modunda aç.", "task": "f = open('t.txt', '___')", "check": lambda c, o: "'r'" in c, "solution": "f = open('t.txt', 'r'); f.close()"},
        {"msg": "**read()** metodu dosyanın tüm içeriğini okuyup getirir. Hadi dene: Dosyayı oku ve içeriği ekrana yazdır.", "task": "f = open('t.txt', 'r')\nprint(f.___())\nf.close()", "check": lambda c, o: "read" in c, "solution": "f = open('t.txt', 'w'); f.write('Pito'); f.close()\nf = open('t.txt', 'r'); print(f.read()); f.close()"},
        {"msg": "Dosya ile işimiz bittiğinde **close()** ile mutlaka kapatmalıyız. Hadi dene: Dosyayı güvenle kapat.", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o: "close" in c, "solution": "f = open('t.txt', 'r'); f.close()"}
    ]}
]

# --- 7. KOD ÇALIŞTIRMA FONKSİYONU ---
def run_pito_code(c, user_input="10"):
    old_stdout, new_stdout = sys.stdout, StringIO()
    sys.stdout = new_stdout
    if "input(" in c and not user_input: return "⚠️ Terminale veri gir!"
    try:
        safe_code = c.replace("___", "None")
        exec(safe_code, {"input": lambda p: str(user_input), "print": print, "int": int, "str": str, "len": len, "open": open, "range": range})
        sys.stdout = old_stdout
        return new_stdout.getvalue()
    except Exception as e: 
        sys.stdout = old_stdout
        return f"Hata: {e}"

# --- 8. ARA YÜZ DÜZENİ ---
col_main, col_side = st.columns([3, 1])
student_rank = RUTBELER[sum(st.session_state.completed_modules)]

with col_main:
    st.markdown(f"#### 👋 {student_rank} {st.session_state.student_name} | ⭐ Puan: {int(st.session_state.total_score)}")
    
    if st.session_state.db_module >= 8:
        if not st.session_state.celebrated:
            st.balloons(); st.session_state.celebrated = True
            st.session_state.pito_emotion = "pito_mezun"
        st.success("### 🎉 Tebrikler! Eğitimi Başarıyla Tamamladın.")
        st.markdown('<div class="pito-bubble">Python yolculuğunu bitirdin! Puanın kaydedildi. Aşağıdan içerikleri inceleyebilir veya sıfırdan başlayabilirsin.</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="retrain-btn">', unsafe_allow_html=True)
            if st.button("🔄 Eğitimi Tekrar Al (Puan Sıfırlanır)"):
                st.session_state.update({'db_module': 0, 'db_exercise': 0, 'total_score': 0, 'current_module': 0, 'current_exercise': 0, 'completed_modules': [False]*8, 'scored_exercises': set(), 'celebrated': False, 'pito_emotion': "pito_dusunuyor"})
                force_save(); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            if st.button("🏆 Liderlik Listesinde Kal"): st.info("Puanın korunacak!")

    mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} Modül {i+1}" for i in range(8)]
    sel_mod = st.selectbox("Ders Seç (İnceleme Modu):", mod_titles, index=st.session_state.current_module)
    m_idx = mod_titles.index(sel_mod)
    if m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': m_idx, 'current_exercise': 0})
        st.rerun()

    st.divider()
    e_idx = st.session_state.current_exercise
    curr_ex = training_data[m_idx]["exercises"][e_idx]
    is_locked = (m_idx < st.session_state.db_module)

    cp1, cp2 = st.columns([1, 4])
    with cp1: st.markdown(get_pito_gif(st.session_state.pito_emotion, width=180), unsafe_allow_html=True)
    with cp2:
        st.info(f"##### 🗣️ Pito:\n{curr_ex['msg']}")
        st.caption(f"Adım: {e_idx + 1}/5 | " + ("🔒 İnceleme Modu" if is_locked else f"🎁 Puan: {st.session_state.current_potential_score}"))

    code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=180, readonly=is_locked, key=f"ace_{m_idx}_{e_idx}", auto_update=True)

    if is_locked:
        st.success(f"**✅ Pito'nun Çözümü:**")
        st.code(curr_ex['solution'], language="python")
        sol_out = run_pito_code(curr_ex['solution'], "10") 
        st.markdown(f"**📟 Beklenen Çıktı:**")
        st.code(sol_out if sol_out else "Kod çalıştı!")
    else:
        u_in = st.text_input("👇 Terminal:", key=f"t_{m_idx}_{e_idx}") if "input(" in code else ""
        if st.button("🔍 Kontrol Et"):
            out = run_pito_code(code, u_in)
            if "⚠️" in out or "Hata" in out:
                st.error(out); st.session_state.pito_emotion = "pito_hata"
            else:
                st.code(out)
                if curr_ex['check'](code, out) and "___" not in code:
                    st.session_state.update({'exercise_passed': True, 'pito_emotion': "pito_basari"})
                    if f"{m_idx}_{e_idx}" not in st.session_state.scored_exercises:
                        st.session_state.total_score += st.session_state.current_potential_score
                        st.session_state.scored_exercises.add(f"{m_idx}_{e_idx}")
                        if st.session_state.db_exercise < 4: st.session_state.db_exercise += 1
                        else:
                            st.session_state.db_module += 1; st.session_state.db_exercise = 0; st.session_state.completed_modules[m_idx] = True
                        force_save()
                    st.success("Tebrikler! ✅")
                else: st.session_state.pito_emotion = "pito_hata"; st.warning("Hatalı!")
            st.rerun()

    if st.session_state.exercise_passed or is_locked:
        c_back, c_next = st.columns(2)
        with c_back:
            if e_idx > 0:
                if st.button("⬅️ Önceki"): st.session_state.current_exercise -= 1; st.rerun()
        with c_next:
            if e_idx < 4:
                if st.button("➡️ Sonraki"): st.session_state.update({'current_exercise': e_idx + 1, 'exercise_passed': False, 'pito_emotion': "pito_dusunuyor"}); st.rerun()
            elif m_idx < 7:
                if st.button("🏆 Modülü Bitir"): st.session_state.update({'current_module': m_idx + 1, 'current_exercise': 0, 'pito_emotion': "pito_dusunuyor"}); st.rerun()

with col_side:
    st.markdown("### 🏆 Liderler")
    df = get_db()
    t1, t2 = st.tabs(["👥 Sınıf", "🏫 Okul"])
    with t1:
        if not df.empty:
            df_c = df[df["Sınıf"] == st.session_state.student_class].sort_values("Puan", ascending=False).head(10)
            for _, r in df_c.iterrows(): st.markdown(f'<div class="leaderboard-card"><b>{r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)
    with t2:
        if not df.empty:
            df_s = df.sort_values("Puan", ascending=False).head(10)
            for _, r in df_s.iterrows(): st.markdown(f'<div class="leaderboard-card"><b>{r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)
    if not df.empty:
        sums = df.groupby("Sınıf")["Puan"].sum()
        if not sums.empty: st.markdown(f'<div class="champion-card">🏆 Şampiyon Sınıf<br>{sums.idxmax()}</div>', unsafe_allow_html=True)