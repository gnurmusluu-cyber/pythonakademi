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
    .solution-header { color: #ef4444; font-weight: bold; font-size: 1.1rem; margin-bottom: 8px; }
    .hint-header { color: #f59e0b; font-weight: bold; font-size: 1.1rem; margin-bottom: 8px; }
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
        if df_all.empty and st.session_state.db_module > 0: return # Veri zırhı
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

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.is_logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba! Ben <b>Pito</b>. Nusaybin Süleyman Bölünmez Anadolu Lisesi için hazırlanan Python yolculuğuna hoş geldin!</div>', unsafe_allow_html=True)
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

# --- 5. EKSİKSİZ EĞİTMEN MÜFREDATI ---
training_data = [
    {"module_title": "1. Değişkenler: Hafıza Kutuları", "exercises": [
        {"msg": "**Pito'nun Notu:** Değişkenler, bilgisayarın hafızasındaki kutulardır. `=` işareti ile bu kutulara isim verip içine değer koyarız.\n\n**Görev:** `yas` ismindeki değişkene (kutuya) **15** sayısal değerini ata.", "task": "yas = ___", "check": lambda c, o, i: "15" in c, "solution": "yas = 15", "hint": "Boşluğa sadece 15 yazmalısın."},
        {"msg": "**Pito'nun Notu:** Metinleri (String) saklarken mutlaka tırnak (' ') kullanmalısın.\n\n**Görev:** `isim` değişkenine tırnaklar içinde **'Pito'** değerini ata.", "task": "isim = ___", "check": lambda c, o, i: "'Pito'" in c or '"Pito"' in c, "solution": "isim = 'Pito'", "hint": "Boşluğa 'Pito' yazmalısın (tırnaklar dahil)."},
        {"msg": "**Pito'nun Notu:** `print()` fonksiyonu, parantez içindeki değeri ekrana yazdırır.\n\n**Görev:** Ekrana tam olarak **'Merhaba'** yazdırmak için boşluğu doldur.", "task": "print('___')", "check": lambda c, o, i: "Merhaba" in o, "solution": "print('Merhaba')", "hint": "Boşluğa Merhaba yaz."},
        {"msg": "**Pito'nun Notu:** Virgül (`,`) farklı tipteki verileri aynı satırda basar.\n\n**Görev:** 'Puan:' metninin yanına **100** sayısını eklemek için boşluğa 100 yaz.", "task": "print('Puan:', ___)", "check": lambda c, o, i: "100" in o, "solution": "print('Puan:', 100)", "hint": "Virgülden sonra 100 yaz."},
        {"msg": "**Pito'nun Notu:** `input()` ile kullanıcıdan veri alırız.\n\n**Görev:** Kullanıcıya 'Adın:' sorusunu sormak için boşluğa **input** yaz.", "task": "ad = ___('Adın: ')", "check": lambda c, o, i: "input" in c, "solution": "ad = input('Adın: ')", "hint": "Kullanıcı girişi fonksiyonu input() kelimesidir."}
    ]},
    {"module_title": "2. Karar Yapıları: Mantık Kapıları", "exercises": [
        {"msg": "**Pito'nun Notu:** `if` (eğer) bloğu bir şart doğruysa çalışır. Eşitlik kontrolü için `==` (çift eşittir) kullanılır.\n\n**Görev:** `s` değişkeni 10'a eşitse 'Tamam' yazdıran operatörü (**==**) boşluğa yaz.", "task": "s = 10\nif s ___ 10: print('Tamam')", "check": lambda c, o, i: "==" in c, "solution": "if s == 10:", "hint": "Eşitlik için çift eşittir kullan."},
        {"msg": "**Pito'nun Notu:** `else:` (değilse) bloğu, 'if' şartı sağlanmadığında devreye girer.\n\n**Görev:** Şart sağlanmazsa 'Hata' yazdıran bloğu tamamlamak için boşluğa **else** yaz.", "task": "if 5 > 10: pass\n___: print('Hata')", "check": lambda c, o, i: "else" in c, "solution": "else:", "hint": "Sadece else: yazman yeterli."},
        {"msg": "**Pito'nun Notu:** `elif` birden fazla şartı sırayla denetler.\n\n**Görev:** Puan 50'den büyükse 'Geçti' yazan şartı eklemek için boşluğa **elif** yaz.", "task": "p = 60\nif p < 50: pass\n___ p > 50: print('Geçti')", "check": lambda c, o, i: "elif" in c, "solution": "elif p > 50:", "hint": "elif anahtar kelimesini kullan."},
        {"msg": "**Pito'nun Notu:** `and` bağlacı her iki şartın da doğru olmasını bekler.\n\n**Görev:** Her iki şartın da doğru olduğunu kontrol etmek için boşluğa **and** yaz.", "task": "if 1==1 ___ 2==2: print('OK')", "check": lambda c, o, i: "and" in c, "solution": "and", "hint": "ve anlamına gelen and yaz."},
        {"msg": "**Pito'nun Notu:** `!=` operatörü 'eşit değilse' demektir.\n\n**Görev:** `s` sıfıra eşit değilse 'Var' yazdıracak operatörü (**!=**) boşluğa koy.", "task": "s = 5\nif s ___ 0: print('Var')", "check": lambda c, o, i: "!=" in c, "solution": "if s != 0:", "hint": "!= operatörünü kullan."}
    ]},
    {"module_title": "3. Döngüler: Tekrarın Gücü", "exercises": [
        {"msg": "**Pito'nun Notu:** `for` döngüsü bir aralıkta (range) tekrar yapar.\n\n**Görev:** 5 kez dönen döngü kurmak için boşluğa **range** yaz.", "task": "for i in ___(5): print(i)", "check": lambda c, o, i: "range" in c, "solution": "for i in range(5):", "hint": "range() fonksiyonunu çağır."},
        {"msg": "**Pito'nun Notu:** `while` döngüsü bir şart 'True' (doğru) olduğu sürece döner.\n\n**Görev:** Boşluğa **while** yazarak döngüyü başlat.", "task": "i = 0\n___ i == 0: print('X'); i += 1", "check": lambda c, o, i: "while" in c, "solution": "while i == 0:", "hint": "Döngü başlatan while kelimesini yaz."},
        {"msg": "**Pito'nun Notu:** `break` döngüyü anında sonlandırır.\n\n**Görev:** Döngüden çıkmak için boşluğa **break** yaz.", "task": "for i in range(5):\n if i == 1: ___\n print(i)", "check": lambda c, o, i: "break" in c, "solution": "break", "hint": "break kelimesini kullan."},
        {"msg": "**Pito'nun Notu:** `continue` o turu atlar ve başa döner.\n\n**Görev:** 1 değerini atlatmak için boşluğa **continue** yaz.", "task": "for i in range(3):\n if i == 1: ___\n print(i)", "check": lambda c, o, i: "continue" in c, "solution": "continue", "hint": "continue kelimesini yaz."},
        {"msg": "**Pito'nun Notu:** Listelerde gezinmek için `in` kullanılır.\n\n**Görev:** Listedeki elemanları almak için boşluğa **in** yaz.", "task": "for x ___ ['A', 'B']: print(x)", "check": lambda c, o, i: "in" in c, "solution": "for x in", "hint": "in anahtarını kullan."}
    ]},
    {"module_title": "4. Listeler: Veri Sepeti", "exercises": [
        {"msg": "**Pito'nun Notu:** Listeler `[]` ile tanımlanır.\n\n**Görev:** Boşluğa **10** yazarak listeyi tamamla.", "task": "L = [___, 20]", "check": lambda c, o, i: "10" in c, "solution": "L = [10, 20]", "hint": "Sadece 10 yaz."},
        {"msg": "**Pito'nun Notu:** İlk elemanın indeksi her zaman **0**'dır.\n\n**Görev:** İlk elemana (50) erişmek için boşluğa **0** yaz.", "task": "L = [50, 60]\nprint(L[___])", "check": lambda c, o, i: "50" in o, "solution": "L[0]", "hint": "Sıfırıncı indeks."},
        {"msg": "**Pito'nun Notu:** `.append()` sona yeni eleman ekler.\n\n**Görev:** Boşluğa **append** metodunu yaz.", "task": "L = [10]\nL.___ (30)", "check": lambda c, o, i: "append" in c, "solution": "L.append(30)", "hint": "append metodunu yaz."},
        {"msg": "**Pito'nun Notu:** `len()` listenin eleman sayısını sayar.\n\n**Görev:** Boşluğa **len** yazarak boyutu ölç.", "task": "L = [1, 2, 3]\nprint(___(L))", "check": lambda c, o, i: "3" in o, "solution": "len(L)", "hint": "len fonksiyonunu kullan."},
        {"msg": "**Pito'nun Notu:** `.pop()` son elemanı siler.\n\n**Görev:** Boşluğa **pop** yazarak son elemanı at.", "task": "L = [1, 2]\nL.___()", "check": lambda c, o, i: "pop" in c, "solution": "L.pop()", "hint": "pop metodunu yaz."}
    ]},
    {"module_title": "5. Fonksiyonlar: İş Parçacıkları", "exercises": [
        {"msg": "**Pito'nun Notu:** Fonksiyonlar `def` ile tanımlanır.\n\n**Görev:** Boşluğa **def** yazarak fonksiyonu başlat.", "task": "___ selam(): print('Merhaba')", "check": lambda c, o, i: "def" in c, "solution": "def selam():", "hint": "def yaz."},
        {"msg": "**Pito'nun Notu:** `return` sonucu dışa fırlatır.\n\n**Görev:** 5 döndürmek için boşluğa **return** yaz.", "task": "def f(): ___ 5", "check": lambda c, o, i: "return" in c, "solution": "return 5", "hint": "return kullan."},
        {"msg": "**Pito'nun Notu:** Fonksiyonlar isimi ve parantez `()` ile çağrılır.\n\n**Görev:** Boşluğa **selam()** yazarak fonksiyonu çalıştır.", "task": "def selam(): print('X')\n___", "check": lambda c, o, i: "selam()" in c, "solution": "selam()", "hint": "Fonksiyonu çağır."},
        {"msg": "**Pito'nun Notu:** Parantez içine parametre yazılabilir.\n\n**Görev:** `x` isminde bir parametre almak için parantez içine **x** yaz.", "task": "def f(___): print(x)", "check": lambda c, o, i: "(x)" in c, "solution": "def f(x):", "hint": "x harfini koy."},
        {"msg": "**Pito'nun Notu:** Fonksiyonlar karmaşıklığı azaltır.\n\n**Görev:** Boşluğa **def** yazarak süreci bitir.", "task": "___ test(): pass", "check": lambda c, o, i: "def" in c, "solution": "def test():", "hint": "def yaz."}
    ]},
    {"module_title": "6. Sözlükler: Etiketli Veriler", "exercises": [
        {"msg": "**Pito'nun Notu:** Sözlükler `{anahtar: değer}` çiftleriyle çalışır. Bir etikete (key) bir veri (value) bağlarız.\n\n**Görev:** 'ad' anahtarına karşılık gelen değer boşluğuna tırnaklar içinde **'Pito'** yaz.", "task": "d = {'ad': '___'}", "check": lambda c, o, i: "'Pito'" in c or '"Pito"' in c, "solution": "d = {'ad': 'Pito'}", "hint": "Boşluğa 'Pito' yaz."},
        {"msg": "**Pito'nun Notu:** Sözlük değerine anahtarı köşeli parantez `[]` içinde yazarak ulaşırız.\n\n**Görev:** 'yas' değerini çekmek için boşluğa **'yas'** yaz.", "task": "d = {'yas': 15}\nprint(d[___])", "check": lambda c, o, i: "'yas'" in c or '"yas"' in c, "solution": "d['yas']", "hint": "Anahtarı tırnakla yaz."},
        {"msg": "**Pito'nun Notu:** Sözlüğe yeni veri eklemek için `sozluk['yeni'] = deger` kullanılır.\n\n**Görev:** Boşluğa **'sehir'** anahtarını yazarak veri ekle.", "task": "d = {}\nd[___] = 'Mardin'", "check": lambda c, o, i: "'sehir'" in c or '"sehir"' in c, "solution": "d['sehir'] = 'Mardin'", "hint": "sehir yaz."},
        {"msg": "**Pito'nun Notu:** `.keys()` tüm etiketleri (anahtarları) verir.\n\n**Görev:** Boşluğa **keys** metodunu yaz.", "task": "d = {'a': 1}\nprint(d.___())", "check": lambda c, o, i: "keys" in c, "solution": "d.keys()", "hint": "keys yaz."},
        {"msg": "**Pito'nun Notu:** `.values()` ise sadece değerleri verir.\n\n**Görev:** Boşluğa **values** yazarak değerleri al.", "task": "d = {'a': 1}\nprint(d.___())", "check": lambda c, o, i: "values" in c, "solution": "d.values()", "hint": "values yaz."}
    ]},
    {"module_title": "7. OOP: Nesne Fabrikası", "exercises": [
        {"msg": "**Pito'nun Notu:** `class` bir taslaktır (kalıptır). Ondan ürünler (nesneler) üretiriz.\n\n**Görev:** 'Robot' isminde bir kalıp oluşturmak için boşluğa **class** yaz.", "task": "___ Robot: pass", "check": lambda c, o, i: "class" in c, "solution": "class Robot:", "hint": "class yaz."},
        {"msg": "**Pito'nun Notu:** Kalıptan nesne üretmek için sınıf ismini fonksiyon gibi çağırırız.\n\n**Görev:** Robot sınıfından r nesnesi üretmek için boşluğa **Robot()** yaz.", "task": "class Robot: pass\nr = ___", "check": lambda c, o, i: "Robot()" in c, "solution": "r = Robot()", "hint": "Sınıf ismini parantezle yaz."},
        {"msg": "**Pito'nun Notu:** Nesnelerin özellikleri (attribute) nokta (`.`) ile atanır.\n\n**Görev:** Robotun rengini 'Mavi' yapmak için boşluğa **renk** yaz.", "task": "class R: pass\nr = R()\nr.___ = 'Mavi'", "check": lambda c, o, i: "renk" in c, "solution": "r.renk = 'Mavi'", "hint": "Özellik adı: renk."},
        {"msg": "**Pito'nun Notu:** `self` nesnenin kendisidir ve metodların ilk parametresi olmalıdır.\n\n**Görev:** Parantez içine **self** anahtarını yaz.", "task": "class R:\n def ses(___): print('Bip')", "check": lambda c, o, i: "self" in c, "solution": "def ses(self):", "hint": "self yaz."},
        {"msg": "**Pito'nun Notu:** Metodlar nesne isminden sonra nokta ile çağrılır.\n\n**Görev:** `s()` metodunu çalıştırmak için boşluğa **s()** yaz.", "task": "class R:\n def s(self): print('X')\nr = R()\nr.___()", "check": lambda c, o, i: "s()" in c, "solution": "r.s()", "hint": "Metot ismi s()."}
    ]},
    {"module_title": "8. Dosya Yönetimi: Kalıcı Hafıza", "exercises": [
        {"msg": "**Pito'nun Notu:** Dosya açmak için `open()` kullanılır. **'w'** (write) yazma modudur.\n\n**Görev:** Dosyayı yazma modunda açmak için boşlukları **open** ve **'w'** ile doldur.", "task": "f = ___('test.txt', ___)", "check": lambda c, o, i: "open" in c and "'w'" in c, "solution": "open('test.txt', 'w')", "hint": "open ve 'w' kullan."},
        {"msg": "**Pito'nun Notu:** `.write()` dosyaya veri yazar.\n\n**Görev:** Boşluğa **write** metodunu yaz.", "task": "f = open('t.txt', 'w')\nf.___('Merhaba')", "check": lambda c, o, i: "write" in c, "solution": "f.write('Merhaba')", "hint": "write yaz."},
        {"msg": "**Pito'nun Notu:** Okumak için **'r'** (read) modu kullanılır.\n\n**Görev:** Boşluğa **'r'** yazarak okuma modunu ayarla.", "task": "f = open('t.txt', ___)", "check": lambda c, o, i: "'r'" in c, "solution": "f = open('t.txt', 'r')", "hint": "'r' yaz."},
        {"msg": "**Pito'nun Notu:** `.read()` tüm içeriği bir kerede çeker.\n\n**Görev:** Boşluğa **read** yaz.", "task": "f = open('t.txt', 'r')\nprint(f.___())", "check": lambda c, o, i: "read" in c, "solution": "f.read()", "hint": "read yaz."},
        {"msg": "**Pito'nun Notu:** İş bitince `.close()` ile dosya mutlaka kapatılmalıdır.\n\n**Görev:** Dosyayı kapatmak için boşluğa **close** yaz.", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o, i: "close" in c, "solution": "f.close()", "hint": "close yaz."}
    ]}
]

# --- 6. ANA ARAYÜZ MANTIK ---
col_main, col_side = st.columns([3, 1])

# SIRALI İLERLEME KONTROLÜ
# Öğrenci sadece bitirdiği (db_module) kadar olan modülleri seçebilir.
selectable_indices = list(range(min(st.session_state.db_module + 1, 8)))
module_labels = [f"{'✅' if i < st.session_state.db_module else '📖'} Modül {i+1}: {training_data[i]['module_title']}" for i in selectable_indices]

with col_main:
    st.markdown(f"#### 👋 {RUTBELER[min(sum(st.session_state.completed_modules), 8)]} {st.session_state.student_name} ({st.session_state.student_class}) | ⭐ Puan: {int(st.session_state.total_score)}")
    
    if st.session_state.db_module >= 8:
        if not st.session_state.celebrated: st.balloons(); st.session_state.celebrated = True
        st.success(f"🎉 Tebrikler! Tüm Python macerasını bitirdin.")
    
    sel_mod_label = st.selectbox("Gitmek İstediğin Modülü Seç:", module_labels, index=min(st.session_state.current_module, len(module_labels)-1))
    new_m_idx = selectable_indices[module_labels.index(sel_mod_label)]
    
    if new_m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': new_m_idx, 'current_exercise': 0, 'fail_count': 0, 'exercise_passed': False, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
        st.rerun()

    st.divider()
    curr_ex = training_data[st.session_state.current_module]["exercises"][st.session_state.current_exercise]
    
    # İNCELEME MODU (GEÇMİŞ MODÜLLER)
    is_review_mode = (st.session_state.current_module < st.session_state.db_module)

    c_img, c_msg = st.columns([1, 4])
    with c_img: st.image("https://img.icons8.com/fluency/200/robot-viewer.png", width=140)
    with c_msg:
        st.info(f"##### 🗣️ Pito'nun Notu:\n{curr_ex['msg']}")
        status = "🔒 İnceleme Modu (Arşiv)" if is_review_mode else f"🎁 Puan: {st.session_state.current_potential_score} | ❌ Hata: {st.session_state.fail_count}/4"
        st.caption(f"Adım: {st.session_state.current_exercise + 1}/5 | {status}")

    def run_pito_code(c):
        if "___" in c: return "⚠️ Boşluk Hatası"
        old_stdout, new_stdout = sys.stdout, StringIO()
        sys.stdout = new_stdout
        try:
            exec(c, {"print": print, "input": lambda x: "10", "range": range, "s": 10, "L": [10], "d":{}, "Robot": lambda: None})
            sys.stdout = old_stdout
            return new_stdout.getvalue()
        except Exception as e:
            sys.stdout = old_stdout
            return f"❌ Hata: {e}"

    if is_review_mode:
        st.markdown('<div class="solution-guide"><div class="solution-header">📖 Arşiv Kaydı</div>Görevi zaten tamamladın. İşte doğru çözüm yolu:</div>', unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")
    else:
        if st.session_state.fail_count < 4 and not st.session_state.exercise_passed:
            code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=180, key=f"ace_{st.session_state.current_module}_{st.session_state.current_exercise}")
            if st.button("🔍 Kodumu Kontrol Et"):
                if "___" in code:
                    st.session_state.feedback_msg = "⚠️ Önce boşluğu doldur!"
                else:
                    out = run_pito_code(code)
                    if out.startswith("❌") or not curr_ex.get('check', lambda c, o, i: True)(code, out, ""):
                        st.session_state.fail_count += 1
                        st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                        if st.session_state.fail_count >= 4: st.session_state.exercise_passed = True
                        st.rerun()
                    else:
                        st.session_state.feedback_msg = "✅ Harika!"
                        st.session_state.last_output = out
                        st.session_state.exercise_passed = True
                        exercise_key = f"{st.session_state.current_module}_{st.session_state.current_exercise}"
                        if exercise_key not in st.session_state.scored_exercises:
                            st.session_state.total_score += st.session_state.current_potential_score
                            st.session_state.scored_exercises.add(exercise_key)
                            force_save()
                        st.rerun()
        
        if st.session_state.fail_count == 3:
            st.markdown(f'<div class="hint-guide"><div class="hint-header">💡 İpucu</div>{curr_ex["hint"]}</div>', unsafe_allow_html=True)
        elif st.session_state.fail_count >= 4:
            st.error("❌ Puan alamadın. İşte doğru çözüm:")
            st.markdown(f'<div class="solution-guide"><div class="solution-header">✅ Doğru Çözüm</div></div>', unsafe_allow_html=True)
            st.code(curr_ex['solution'], language="python")

    # NAVİGASYON (HİÇBİR ZAMAN KİLİTLENMEZ)
    if st.session_state.exercise_passed or is_review_mode or st.session_state.fail_count >= 4:
        col_prev, col_next = st.columns(2)
        with col_prev:
            if st.session_state.current_exercise > 0:
                if st.button("⬅️ Önceki Adım"):
                    st.session_state.update({'current_exercise': st.session_state.current_exercise - 1, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
                    st.rerun()
        with col_next:
            if st.session_state.current_exercise < 4:
                if st.button("➡️ Sonraki Adım"):
                    st.session_state.update({'current_exercise': st.session_state.current_exercise + 1, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
                    st.rerun()
            elif st.session_state.current_module < 7:
                if st.button("🏆 Modülü Bitir ve Devam Et"):
                    if not is_review_mode:
                        st.session_state.db_module += 1
                        st.session_state.db_exercise = 0
                        st.session_state.completed_modules[st.session_state.current_module] = True
                        force_save()
                    st.session_state.update({'current_module': st.session_state.current_module + 1, 'current_exercise': 0, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20})
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