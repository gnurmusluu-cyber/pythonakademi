import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import os

# --- 1. TASARIM VE SAYFA AYARLARI ---
st.set_page_config(layout="wide", page_title="Pito Python Akademi", initial_sidebar_state="collapsed")

SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]
RUTBELER = ["🥚 Yeni Başlayan", "🌱 Python Çırağı", "🪵 Kod Oduncusu", "🧱 Mantık Mimarı", "🌀 Döngü Ustası", "📋 Liste Uzmanı", "📦 Fonksiyon Kaptanı", "🤖 OOP Robotu", "🏆 Python Kahramanı"]

st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem; background-color: #f0f2f6;}
    .pito-bubble {
        position: relative; background: #ffffff; border: 2px solid #3a7bd5;
        border-radius: 15px; padding: 25px; margin-bottom: 20px; color: #1e1e1e;
        font-weight: 500; font-size: 1.1rem; box-shadow: 4px 4px 15px rgba(0,0,0,0.05);
        line-height: 1.7;
    }
    .pito-bubble:after {
        content: ''; position: absolute; bottom: -20px; left: 40px;
        border-width: 20px 20px 0; border-style: solid; border-color: #3a7bd5 transparent;
    }
    .solution-guide {
        background-color: #fef2f2 !important; border: 2px solid #ef4444 !important;
        border-radius: 12px; padding: 20px; margin: 15px 0; color: #1e1e1e !important;
    }
    .hint-guide {
        background-color: #fffbeb !important; border: 2px solid #f59e0b !important;
        border-radius: 12px; padding: 20px; margin: 15px 0; color: #1e1e1e !important;
    }
    .leaderboard-card {
        background: linear-gradient(135deg, #1e1e1e, #2d2d2d);
        border: 1px solid #444; border-radius: 12px; padding: 10px; margin-bottom: 8px; color: white;
    }
    .stButton > button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important;
        color: white !important; font-weight: bold; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        if df is None or df.empty: return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        df["Okul No"] = df["Okul No"].astype(str).str.split('.').str[0].str.strip()
        df["Puan"] = pd.to_numeric(df["Puan"], errors='coerce').fillna(0).astype(int)
        return df.dropna(subset=["Okul No"])
    except: return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])

def force_save():
    try:
        no = str(st.session_state.student_no).strip()
        df_all = get_db()
        if df_all.empty and st.session_state.db_module > 0: return # Veri Zırhı
        df_clean = df_all[df_all["Okul No"] != no]
        prog = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = RUTBELER[min(sum(st.session_state.completed_modules), 8)]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, int(st.session_state.total_score), rank, prog, int(st.session_state.db_module), int(st.session_state.db_exercise), datetime.now().strftime("%H:%M:%S")]], columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

# --- 3. SESSION STATE ---
if 'is_logged_in' not in st.session_state:
    for k, v in {'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8, 
                 'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0, 
                 'scored_exercises': set(), 'db_module': 0, 'db_exercise': 0, 'is_logged_in': False, 
                 'current_potential_score': 20, 'celebrated': False, 'fail_count': 0, 
                 'feedback_msg': "", 'last_output': ""}.items():
        st.session_state[k] = v

PITO_IMG = "assets/pito.png"
def show_pito_img(width=180):
    if os.path.exists(PITO_IMG): st.image(PITO_IMG, width=width)
    else: st.image("https://img.icons8.com/fluency/180/robot-viewer.png", width=width)

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.is_logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba Geleceğin Yazılımcısı! Ben <b>Pito</b>. Bugün seninle Python dünyasında bir keşfe çıkacağız. Hazır mısın?</div>', unsafe_allow_html=True)
        show_pito_img(180)
        in_no = st.text_input("Okul Numaran:", key="login_field").strip()
        if in_no and in_no.isdigit():
            df = get_db()
            user_data = df[df["Okul No"] == in_no]
            if not user_data.empty:
                row = user_data.iloc[0]
                st.info(f"🔍 Hoş geldin **{row['Öğrencinin Adı']} ({row['Sınıf']})**.")
                if st.button("✅ Maceraya Başla"):
                    m_v, e_v = int(row['Mevcut Modül']), int(row['Mevcut Egzersiz'])
                    st.session_state.update({'student_no': in_no, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': m_v, 'db_exercise': e_v, 'current_module': m_v, 'current_exercise': e_v, 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True, 'current_potential_score': 20})
                    st.rerun()
            else:
                in_name = st.text_input("Adın Soyadın:")
                in_class = st.selectbox("Sınıfın:", SINIFLAR)
                if st.button("Kayıt Ol ve Başla ✨") and in_name:
                    st.session_state.update({'student_no': in_no, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True, 'current_potential_score': 20})
                    force_save(); st.rerun()
    st.stop()

# --- 5. EKSİKSİZ UZMAN EĞİTMEN MÜFREDATI ---
training_data = [
    {"module_title": "1. Değişkenler: Hafıza Kutuları", "exercises": [
        {"msg": "**Pito'un Notu:** Değişkenler, verileri sakladığımız kutulardır. `=` işareti ile kutuya bir değer koyarız (atama yaparız).\n\n**Görev:** `yas` ismindeki değişkene **15** sayısal değerini ata.", "task": "yas = ___", "check": lambda c, o, i: "15" in c, "solution": "yas = 15", "hint": "Boşluğa sadece 15 yazmalısın."},
        {"msg": "**Pito'nun Notu:** Metinleri (String) saklarken tırnak (' ') kullanırız. İsimlerde rakam kullanmamaya dikkat etmelisin.\n\n**Görev:** `isim` değişkenine tırnaklar içinde **'Pito'** değerini ata.", "task": "isim = ___", "check": lambda c, o, i: "'Pito'" in c or '"Pito"' in c, "solution": "isim = 'Pito'", "hint": "Boşluğa 'Pito' yaz."},
        {"msg": "**Pito'nun Notu:** `print()` Python'ın dünyayla konuşma yoludur. Parantez içine yazdığın her şey ekrana basılır.\n\n**Görev:** Ekrana tam olarak **'Merhaba'** yazdırmak için boşluğu doldur.", "task": "print('___')", "check": lambda c, o, i: "Merhaba" in o, "solution": "print('Merhaba')", "hint": "Tırnaklar arasına Merhaba yaz."},
        {"msg": "**Pito'nun Notu:** Virgül (`,`) farklı tiplerdeki verileri birleştirerek aynı satırda yazdırır.\n\n**Görev:** 'Puan:' metninin yanına **100** sayısını eklemek için boşluğa 100 yaz.", "task": "print('Puan:', ___)", "check": lambda c, o, i: "100" in o, "solution": "print('Puan:', 100)", "hint": "Virgülden sonra 100 yaz."},
        {"msg": "**Pito'nun Notu:** `input()` programı durdurur ve senden bir bilgi girmeni bekler.\n\n**Görev:** Kullanıcıya 'Adın:' sorusunu sormak için boşluğa **input** fonksiyonunu yaz.", "task": "ad = ___('Adın: ')", "check": lambda c, o, i: "input" in c, "solution": "ad = input('Adın: ')", "hint": "Veri almak için input kelimesini kullanmalısın."}
    ]},
    {"module_title": "2. Karar Yapıları: If-Else Mantığı", "exercises": [
        {"msg": "**Pito'nun Notu:** `if` (eğer) bloğu bir şart doğruysa çalışır. Eşitlik kontrolü için `==` (çift eşittir) kullanılır.\n\n**Görev:** `s` 10'a eşitse 'OK' yazdıran operatörü (**==**) boşluğa yaz.", "task": "s = 10\nif s ___ 10: print('OK')", "check": lambda c, o, i: "==" in c, "solution": "if s == 10:", "hint": "Eşitlik kontrolü için iki tane eşittir kullan."},
        {"msg": "**Pito'nun Notu:** `else:` (değilse) bloğu, 'if' şartı sağlanmadığında devreye giren alternatiftir.\n\n**Görev:** Şart sağlanmazsa 'Hata' yazdıran yolu tamamlamak için boşluğa **else** yaz.", "task": "if 5 > 10: pass\n___: print('Hata')", "check": lambda c, o, i: "else" in c, "solution": "else:", "hint": "Sadece else: yazman yeterli."},
        {"msg": "**Pito'nun Notu:** `elif` (else if), birden fazla şartı sırayla denetlemek için kullanılır.\n\n**Görev:** Puan 50'den büyükse 'Geçti' yazacak ikinci şartı eklemek için boşluğa **elif** yaz.", "task": "p = 60\nif p < 50: pass\n___ p > 50: print('Geçti')", "check": lambda c, o, i: "elif" in c, "solution": "elif p > 50:", "hint": "Şartları birbirine bağlayan elif kelimesini kullan."},
        {"msg": "**Pito'nun Notu:** `and` bağlacı her iki şartın da 'True' (doğru) olmasını bekler.\n\n**Görev:** Her iki şartın da doğru olduğunu kontrol etmek için boşluğa **and** yaz.", "task": "if 1==1 ___ 2==2: print('OK')", "check": lambda c, o, i: "and" in c, "solution": "and", "hint": "Türkçesi 've' olan and bağlacını yaz."},
        {"msg": "**Pito'nun Notu:** `!=` operatörü 'eşit değilse' anlamına gelir.\n\n**Görev:** `s` sıfıra eşit değilse 'Var' yazdıracak operatörü (**!=**) boşluğa koy.", "task": "s = 5\nif s ___ 0: print('Var')", "check": lambda c, o, i: "!=" in c, "solution": "if s != 0:", "hint": "Ünlem ve eşittir işaretlerini birleştir."}
    ]},
    {"module_title": "3. Döngüler: Tekrarın Gücü", "exercises": [
        {"msg": "**Konu:** `for` döngüsü bir aralıkta (range) tekrar yapar.\n\n**Görev:** 5 kez dönecek bir döngü için boşluğa **range** yaz.", "task": "for i in ___(5): print(i)", "check": lambda c, o, i: "range" in c, "solution": "for i in range(5):", "hint": "range(5) yazmalısın."},
        {"msg": "**Konu:** `while` şart doğru oldukça döner.\n\n**Görev:** Boşluğa **while** yazarak i sıfır oldukça sürecek döngüyü başlat.", "task": "i = 0\n___ i == 0: print('X'); i += 1", "check": lambda c, o, i: "while" in c, "solution": "while i == 0:", "hint": "while ile başlat."},
        {"msg": "**Konu:** `break` döngüyü anında kırmaya yarar.\n\n**Görev:** i değeri 1 olduğunda döngüden çıkmak için boşluğa **break** yaz.", "task": "for i in range(5):\n if i == 1: ___\n print(i)", "check": lambda c, o, i: "break" in c, "solution": "break", "hint": "break kelimesini kullan."},
        {"msg": "**Konu:** `continue` o adımı atlar ve başa döner.\n\n**Görev:** 1 değerini atlatmak için boşluğa **continue** yaz.", "task": "for i in range(3):\n if i == 1: ___\n print(i)", "check": lambda c, o, i: "continue" in c, "solution": "continue", "hint": "continue yaz."},
        {"msg": "**Konu:** Listelerde gezinmek için `in` kullanılır.\n\n**Görev:** Listedeki elemanları çekmek için boşluğa **in** yaz.", "task": "for x ___ ['A', 'B']: print(x)", "check": lambda c, o, i: "in" in c, "solution": "for x in", "hint": "in anahtarını kullan."}
    ]},
    {"module_title": "4. Listeler: Veri Sepetleri", "exercises": [
        {"msg": "**Konu:** Listeler birden fazla veriyi tek sepette tutar ve `[]` ile tanımlanır.\n\n**Görev:** Boşluğa **10** yazarak listeyi tamamla.", "task": "L = [___, 20]", "check": lambda c, o, i: "10" in c, "solution": "L = [10, 20]", "hint": "Sadece 10 yaz."},
        {"msg": "**Konu:** İlk elemanın indeksi her zaman **0**'dır.\n\n**Görev:** İlk elemana (50) erişmek için boşluğa **0** yaz.", "task": "L = [50, 60]\nprint(L[___])", "check": lambda c, o, i: "50" in o, "solution": "L[0]", "hint": "Sıfırıncı indeks."},
        {"msg": "**Konu:** `.append()` sona yeni eleman ekler.\n\n**Görev:** Boşluğa **append** metodunu yaz.", "task": "L = [10]\nL.___ (30)", "check": lambda c, o, i: "append" in c, "solution": "L.append(30)", "hint": "append metodunu yaz."},
        {"msg": "**Konu:** `len()` listenin eleman sayısını sayar.\n\n**Görev:** Boşluğa **len** yazarak boyutu ölç.", "task": "L = [1, 2, 3]\nprint(___(L))", "check": lambda c, o, i: "3" in o, "solution": "len(L)", "hint": "len fonksiyonunu kullan."},
        {"msg": "**Konu:** `.pop()` son elemanı siler.\n\n**Görev:** Boşluğa **pop** yazarak son elemanı at.", "task": "L = [1, 2]\nL.___()", "check": lambda c, o, i: "pop" in c, "solution": "L.pop()", "hint": "pop metodunu yaz."}
    ]},
    {"module_title": "5. Fonksiyonlar: İş Paketleri", "exercises": [
        {"msg": "**Konu:** Fonksiyonlar tekrarı önler. `def` (tanımla) ile başlar.\n\n**Görev:** 'pito' fonksiyonunu tanımlamaya başlayan **def** kelimesini boşluğa yaz.", "task": "___ pito(): print('Hi')", "check": lambda c, o, i: "def" in c, "solution": "def pito():", "hint": "def yaz."},
        {"msg": "**Konu:** `return` sonucu dışa fırlatır.\n\n**Görev:** 5 döndürmek için boşluğa **return** yaz.", "task": "def f(): ___ 5", "check": lambda c, o, i: "return" in c, "solution": "return 5", "hint": "return kullan."},
        {"msg": "**Konu:** Fonksiyonlar parantez `()` ile çağrılır.\n\n**Görev:** Boşluğa **selam()** yazarak fonksiyonu çalıştır.", "task": "def selam(): print('X')\n___", "check": lambda c, o, i: "selam()" in c, "solution": "selam()", "hint": "Fonksiyonu çağır."},
        {"msg": "**Konu:** Parantez içine parametre yazılabilir.\n\n**Görev:** `x` isminde parametre almak için parantez içine **x** yaz.", "task": "def f(___): print(x)", "check": lambda c, o, i: "(x)" in c, "solution": "def f(x):", "hint": "x harfini koy."},
        {"msg": "**Konu:** Fonksiyonlar karmaşıklığı azaltır.\n\n**Görev:** Boşluğa **def** yazarak süreci bitir.", "task": "___ test(): pass", "check": lambda c, o, i: "def" in c, "solution": "def test():", "hint": "def yaz."}
    ]},
    {"module_title": "6. Sözlükler: Anahtar ve Değer", "exercises": [
        {"msg": "**Pito'nun Notu:** **Sözlükler (Dictionary)**, `{anahtar: değer}` çiftleriyle çalışır. Rehberdeki 'isim' bir anahtardır (key), 'Pito' ise değerdir (value).\n\n**Görev:** 'ad' anahtarına karşılık gelen değer boşluğuna tırnaklar içinde **'Pito'** yaz.", "task": "d = {'ad': '___'}", "check": lambda c, o, i: "Pito" in o, "solution": "d = {'ad': 'Pito'}", "hint": "Boşluğa 'Pito' yaz."},
        {"msg": "**Konu:** Sözlük değerine anahtarı köşeli parantez `[]` içinde yazarak ulaşırız.\n\n**Görev:** 'yas' değerini çekmek için boşluğa tırnaklı şekilde **'yas'** yaz.", "task": "d = {'yas': 15}\nprint(d[___])", "check": lambda c, o, i: "'yas'" in c or '"yas"' in c, "solution": "d['yas']", "hint": "Anahtar ismi yas'tır."},
        {"msg": "**Konu:** `.keys()` tüm etiketleri (anahtarları) listeler.\n\n**Görev:** Boşluğa **keys** yazarak anahtarları çekmeyi sağla.", "task": "d = {'a':1}\nprint(d.___())", "check": lambda c, o, i: "keys" in c, "solution": "d.keys()", "hint": "keys yazmalısın."},
        {"msg": "**Konu:** **Tuple**, listeye benzer ama `()` ile kurulur ve içeriği asla değiştirilemez.\n\n**Görev:** Boşluğa sadece **1** yazarak demeti tamamla.", "task": "t = (___, 2)", "check": lambda c, o, i: "1" in c, "solution": "t = (1, 2)", "hint": "1 yaz."},
        {"msg": "**Konu:** Boş bir sözlük süslü parantezlerle kurulur.\n\n**Görev:** Boşluğa **{}** yazarak boş bir sözlük kur.", "task": "d = ___", "check": lambda c, o, i: "{}" in c, "solution": "d = {}", "hint": "Süslü parantezleri koy."}
    ]},
    {"module_title": "7. OOP: Nesne Tabanlı Dünya", "exercises": [
        {"msg": "**Pito'nun Notu:** `class` bir taslaktır (fabrikadır). Nesne (object) ise o kalıptan çıkan üründür.\n\n**Görev:** 'Robot' isminde bir kalıp oluşturmak için boşluğa **class** anahtar kelimesini yaz.", "task": "___ Robot: pass", "check": lambda c, o, i: "class" in c, "solution": "class Robot:", "hint": "Sınıf için class yaz."},
        {"msg": "**Konu:** Kalıptan nesne üretmek için sınıf ismini parantezle `()` çağırırız.\n\n**Görev:** Robot sınıfından r nesnesi üretmek için boşluğa **Robot()** yaz.", "task": "class Robot: pass\nr = ___", "check": lambda c, o, i: "Robot()" in c, "solution": "r = Robot()", "hint": "Sınıf ismini parantezle yaz."},
        {"msg": "**Konu:** Özellikler nokta (`.`) ile atanır.\n\n**Görev:** Robotun rengini 'Mavi' yapmak için boşluğa **renk** yaz.", "task": "class R: pass\nr = R()\nr.___ = 'Mavi'", "check": lambda c, o, i: "renk" in c, "solution": "r.renk = 'Mavi'", "hint": "Özellik adı: renk."},
        {"msg": "**Pito'nun Notu:** `self` nesnenin kendisidir ve metodların ilk parametresi olmalıdır.\n\n**Görev:** Parantez içine **self** anahtarını yaz.", "task": "class R:\n def ses(___): print('Bip')", "check": lambda c, o, i: "self" in c, "solution": "def ses(self):", "hint": "self yaz."},
        {"msg": "**Konu:** Metodlar nesne isminden sonra nokta ile çağrılır.\n\n**Görev:** `s()` metodunu çalıştırmak için boşluğa **s()** yaz.", "task": "class R:\n def s(self): print('X')\nr = R()\nr.___()", "check": lambda c, o, i: "s()" in c, "solution": "r.s()", "hint": "Metot ismi s()."}
    ]},
    {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [
        {"msg": "**Konu:** Program kapanınca veriler silinir. Saklamak için `open()` fonksiyonu kullanılır. **'w'** (write) yazma modudur.\n\n**Görev:** n.txt dosyasını yazma modunda açmak için ilk boşluğa **open**, mod için ikinci boşluğa **w** yaz.", "task": "f = ___('n.txt', '___')", "check": lambda c, o, i: "open" in c and "w" in c, "solution": "open('n.txt', 'w')", "hint": "open ve w kullan."},
        {"msg": "**Konu:** `.write()` dosyaya veri mühürler.\n\n**Görev:** Dosyaya 'X' yazmak için boşluğa **write** yaz.", "task": "f = open('t.txt', 'w')\nf.___('X')\nf.close()", "check": lambda c, o, i: "write" in c, "solution": "f.write('X')", "hint": "write yaz."},
        {"msg": "**Konu:** Okuma için **'r'** (read) modu kullanılır.\n\n**Görev:** Dosyayı okuma modunda açmak için boşluğa **r** harfini koy.", "task": "f = open('t.txt', '___')", "check": lambda c, o, i: "r" in c, "solution": "f = open('t.txt', 'r')", "hint": "r yaz."},
        {"msg": "**Konu:** `.read()` içeriği programa getirir.\n\n**Görev:** İçeriği almak için boşluğa **read** yaz.", "task": "f = open('t.txt', 'r')\nprint(f.___())", "check": lambda c, o, i: "read" in c, "solution": "f.read()", "hint": "read yaz."},
        {"msg": "**Konu:** `.close()` hayati önem taşır; dosyayı kapatmalısın.\n\n**Görev:** Dosyayı kapatmak için boşluğa **close** yaz.", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o, i: "close" in c, "solution": "f.close()", "hint": "close yaz."}
    ]}
]

# --- 6. ARA YÜZ DÜZENİ ---
col_main, col_side = st.columns([3, 1])

selectable_indices = list(range(min(st.session_state.db_module + 1, 8)))
module_labels = [f"{'✅' if i < st.session_state.db_module else '📖'} Modül {i+1}: {training_data[i]['module_title']}" for i in selectable_indices]

with col_main:
    st.markdown(f"#### 👋 {RUTBELER[min(sum(st.session_state.completed_modules), 8)]} {st.session_state.student_name} ({st.session_state.student_class}) | ⭐ Puan: {int(st.session_state.total_score)}")
    
    if st.session_state.db_module >= 8:
        if not st.session_state.celebrated: st.balloons(); st.session_state.celebrated = True
        st.success("🎉 Tebrikler! Tüm macerayı bitirdin.")
    
    sel_mod_label = st.selectbox("Eğitim Modülü Seç:", module_labels, index=min(st.session_state.current_module, len(module_labels)-1))
    new_m_idx = selectable_indices[module_labels.index(sel_mod_label)]
    
    if new_m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': new_m_idx, 'current_exercise': 0, 'fail_count': 0, 'exercise_passed': False, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
        st.rerun()

    st.divider()
    curr_ex = training_data[st.session_state.current_module]["exercises"][st.session_state.current_exercise]
    is_review_mode = (st.session_state.current_module < st.session_state.db_module)

    # GERİ BİLDİRİM PANELİ (FIXED)
    if st.session_state.feedback_msg:
        if "✅" in st.session_state.feedback_msg: st.success(st.session_state.feedback_msg)
        else: st.error(st.session_state.feedback_msg)

    c_img, c_msg = st.columns([1, 4])
    with c_img: show_pito_img(140)
    with c_msg:
        st.info(f"##### 🗣️ Pito'nun Notu:\n{curr_ex['msg']}")
        status = "🔒 İnceleme Modu (Arşiv)" if is_review_mode else f"🎁 Puan: {st.session_state.current_potential_score} | ❌ Hata: {st.session_state.fail_count}/4"
        st.caption(f"Adım: {st.session_state.current_exercise + 1}/5 | {status}")

    def run_pito_code(c, user_input="Pito"):
        if "___" in c: return "⚠️ Boşluk Hatası"
        old_stdout, new_stdout = sys.stdout, StringIO()
        sys.stdout = new_stdout
        try:
            exec(c, {"print": print, "input": lambda p: str(user_input), "int": int, "str": str, "len": len, "open": open, "range": range, "s": 10, "L": [10, 20], "d":{'ad':'Pito', 'yas':15, 'a':1}, "t":(1,2), "Robot": lambda: None, "R": lambda: None})
            sys.stdout = old_stdout
            return new_stdout.getvalue()
        except Exception as e:
            sys.stdout = old_stdout
            return f"❌ Python Hatası: {e}"

    if is_review_mode:
        st.markdown(f'<div class="solution-guide"><div class="solution-header">📖 Arşiv: Soru ve Çözüm</div><b>Pito\'nun Görevi:</b><br>{curr_ex["msg"]}</div>', unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")
    else:
        if st.session_state.fail_count < 4 and not st.session_state.exercise_passed:
            code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=200, key=f"ace_{st.session_state.current_module}_{st.session_state.current_exercise}", auto_update=True)
            if st.button("🔍 Kodumu Kontrol Et", use_container_width=True):
                if "___" in code:
                    st.session_state.feedback_msg = "⚠️ Lütfen önce kodun içindeki '___' alanlarını doldur!"
                    st.rerun()
                else:
                    out = run_pito_code(code)
                    if out.startswith("❌") or not curr_ex.get('check', lambda c, o, i: True)(code, out, ""):
                        st.session_state.fail_count += 1
                        st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                        if st.session_state.fail_count == 1: st.session_state.feedback_msg = "❌ Bu birinci hatan tekrar dene. Her hatada kazanacağın 5 puan düşer."
                        elif st.session_state.fail_count == 2: st.session_state.feedback_msg = "❌ Bu 2. hatan. Kazanacağın puan 10'a düştü!"
                        elif st.session_state.fail_count == 3: st.session_state.feedback_msg = "❌ Bu 3. hatan ve son hakkın! Bir sonraki hatanda puan alamadan geçeceksin."
                        elif st.session_state.fail_count >= 4: st.session_state.exercise_passed = True; st.session_state.feedback_msg = "❌ Puan kazanamadın. Çözümü inceleyip sonraki adıma geçebilirsin."
                        st.rerun()
                    else:
                        st.session_state.feedback_msg = "✅ Harika! Görev başarıyla tamamlandı."
                        st.session_state.last_output = out
                        st.session_state.exercise_passed = True
                        ex_key = f"{st.session_state.current_module}_{st.session_state.current_exercise}"
                        if ex_key not in st.session_state.scored_exercises:
                            st.session_state.total_score += st.session_state.current_potential_score
                            st.session_state.scored_exercises.add(ex_key)
                            force_save()
                        st.rerun()
        
        if st.session_state.fail_count == 3:
            st.markdown(f"""<div class="hint-guide"><div class="hint-header">💡 Pito'dan İpucu</div>{curr_ex['hint']}</div>""", unsafe_allow_html=True)
        elif st.session_state.fail_count >= 4:
            st.markdown(f"""<div class="solution-guide"><div class="solution-header">✅ Doğru Çözüm Yolu</div></div>""", unsafe_allow_html=True)
            st.code(curr_ex['solution'], language="python")

    if st.session_state.exercise_passed or is_review_mode or st.session_state.fail_count >= 4:
        if st.session_state.last_output and not is_review_mode: 
            st.markdown("**Kod Çıktısı:**"); st.code(st.session_state.last_output)
        
        col_p, col_n = st.columns(2)
        with col_p:
            if st.session_state.current_exercise > 0:
                if st.button("⬅️ Önceki Adım"):
                    st.session_state.update({'current_exercise': st.session_state.current_exercise - 1, 'exercise_passed': False, 'fail_count': 0, 'feedback_msg': "", 'last_output': "", 'current_potential_score': 20})
                    st.rerun()
        with col_n:
            if st.session_state.current_exercise < 4:
                if st.button("➡️ Sonraki Adım"):
                    st.session_state.update({'current_exercise': st.session_state.current_exercise + 1, 'exercise_passed': False, 'fail_count': 0, 'feedback_msg': "", 'last_output': "", 'current_potential_score': 20})
                    st.rerun()
            elif st.session_state.current_module < 7:
                if st.button("🏆 Modülü Bitir ve Devam Et"):
                    if not is_review_mode:
                        st.session_state.db_module += 1; st.session_state.db_exercise = 0
                        st.session_state.completed_modules[st.session_state.current_module] = True
                        force_save()
                    st.session_state.update({'current_module': st.session_state.current_module + 1, 'current_exercise': 0, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': ""})
                    st.rerun()

with col_side:
    df_lb = get_db()
    st.markdown("### 🏅 Şampiyon Sınıf")
    if not df_lb.empty:
        class_stats = df_lb.groupby("Sınıf")["Puan"].sum().reset_index()
        top_class = class_stats.sort_values(by="Puan", ascending=False).head(1).iloc[0]
        st.markdown(f'<div class="leaderboard-card" style="background: linear-gradient(135deg, #FFD700, #DAA520); color: black;"><b>Sınıf: {top_class["Sınıf"]}</b><br>Toplam: {int(top_class["Puan"])} Puan</div>', unsafe_allow_html=True)
    
    st.markdown("### 🏆 En İyi Kodlamacılar")
    tab_c, tab_s = st.tabs(["👥 Sınıfım", "🏫 Okul Geneli"])
    for t, d in zip([tab_c, tab_s], [df_lb[df_lb["Sınıf"] == st.session_state.student_class], df_lb]):
        with t:
            if not d.empty:
                for _, r in d.sort_values(by="Puan", ascending=False).head(10).iterrows():
                    st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]} ({r["Sınıf"]})</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)