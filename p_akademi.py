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
        font-weight: 500; font-size: 1.05rem; box-shadow: 4px 4px 15px rgba(0,0,0,0.05);
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
        df["Okul No"] = df["Okul No"].astype(str).str.split('.').str[0].str.strip()
        df["Puan"] = pd.to_numeric(df["Puan"], errors='coerce').fillna(0).astype(int)
        return df.dropna(subset=["Okul No"])
    except: return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])

def force_save():
    try:
        no = str(st.session_state.student_no).strip()
        df_all = get_db()
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

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.is_logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba Geleceğin Yazılımcısı! Ben <b>Pito</b>. Python dünyasına adım atmaya hazır mısın?</div>', unsafe_allow_html=True)
        st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/180/robot-viewer.png", width=180)
        in_no = st.text_input("Okul Numaran:", key="login_field").strip()
        if in_no and in_no.isdigit():
            df = get_db()
            user_data = df[df["Okul No"] == in_no]
            if not user_data.empty:
                row = user_data.iloc[0]
                st.info(f"🔍 Hoş geldin **{row['Öğrencinin Adı']} ({row['Sınıf']})**.")
                if st.button("✅ Maceraya Başla"):
                    m_v, e_v = int(row['Mevcut Modül']), int(row['Mevcut Egzersiz'])
                    st.session_state.update({'student_no': in_no, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': m_v, 'db_exercise': e_v, 'current_module': min(m_v, 7), 'current_exercise': min(e_v, 4), 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True})
                    st.rerun()
            else:
                in_name = st.text_input("Adın Soyadın:")
                in_class = st.selectbox("Sınıfın:", SINIFLAR)
                if st.button("Kayıt Ol ve Başla ✨") and in_name:
                    st.session_state.update({'student_no': in_no, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True})
                    force_save(); st.rerun()
    st.stop()

# --- 5. UZMAN EĞİTMEN MÜFREDATI (3-8 ARASI YENİDEN YAZILDI) ---
training_data = [
    {"module_title": "1. İletişim ve Çıktı", "exercises": [
        {"msg": "**Konu:** Python'da `print()` bilgisayarın sesidir.\n\n**Görev:** Ekrana tam olarak **'Merhaba Pito'** yazdır.", "task": "print('___')", "check": lambda c, o, i: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')", "hint": "Metinleri tırnak (' ') içine yazmalısın.", "has_output": True},
        {"msg": "**Konu:** Sayılar tırnak gerektirmez.\n\n**Görev:** Sadece sayısal olan **100** değerini bas.", "task": "print(___)", "check": lambda c, o, i: "100" in o, "solution": "print(100)", "hint": "Sadece rakamları yaz!", "has_output": True},
        {"msg": "**Konu:** Virgül veri tiplerini birleştirir.\n\n**Görev:** **'Puan:'** metni ile **100** sayısını yan yana yaz.", "task": "print('Puan:', ___)", "check": lambda c, o, i: "100" in o, "solution": "print('Puan:', 100)", "hint": "Virgülden sonra 100 ekle.", "has_output": True},
        {"msg": "**Konu:** `#` yorum satırı oluşturur.\n\n**Görev:** Bu satırı yorum satırına dönüştür.", "task": "___ bu bir yorumdur", "check": lambda c, o, i: "#" in c, "solution": "# bu bir yorumdur", "hint": "Satırın en başına # koy.", "has_output": False},
        {"msg": "**Konu:** `\\n` alt satıra geçer.\n\n**Görev:** 'Üst' ve 'Alt' kelimelerini alt alta yazdır.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o, i: "\n" in o, "solution": "print('Üst\\nAlt')", "hint": "Tırnak içine \\n yazmalısın.", "has_output": True}
    ]},
    {"module_title": "2. Değişkenler ve input()", "exercises": [
        {"msg": "**Konu:** Değişkenler veriyi saklar.\n\n**Görev:** **yas** değişkenine **15** ata.", "task": "yas = ___\nprint(yas)", "check": lambda c, o, i: "15" in o, "solution": "yas = 15", "hint": "yas = 15 yazmalısın.", "has_output": True},
        {"msg": "**Konu:** İsimlerde tırnak kullanılır.\n\n**Görev:** **isim** değişkenine **'Pito'** ata.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o, i: "Pito" in o, "solution": "isim = 'Pito'", "hint": "Tırnakların arasına Pito yaz.", "has_output": True},
        {"msg": "**Konu:** `input()` veri alır.\n\n**Görev:** Kullanıcıdan **'Adın: '** girişi iste.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o, i: "input" in c, "solution": "ad = input('Adın: ')", "hint": "input() fonksiyonunu kullan.", "has_output": True, "force_text": True},
        {"msg": "**Konu:** `str()` metne çevirir.\n\n**Görev:** 10 sayısını metne dönüştür.", "task": "s = 10\nprint(___(s))", "check": lambda c, o, i: "str" in c, "solution": "print(str(s))", "hint": "str yazmalısın.", "has_output": True},
        {"msg": "**Konu:** `int()` sayıya çevirir.\n\n**Görev:** Girdi al, sayıya çevir ve 1 ekle.", "task": "n = ___(___('S: '))\nprint(n + 1)", "check": lambda c, o, i: "int" in c and (str(int(i if i.isdigit() else 0) + 1) in o), "solution": "n = int(input('10'))", "hint": "Dışa int, içe input yaz.", "has_output": True}
    ]},
    {"module_title": "3. Karar Yapıları (If/Else)", "exercises": [
        {"msg": "**Konu:** `if` ile kontrol sağlarız.\n\n**Görev:** Eğer sayı 10'a eşitse 'Tamam' yazdır.", "task": "s = 10\nif s ___ 10: print('Tamam')", "check": lambda c, o, i: "==" in c, "solution": "if s == 10:", "hint": "Eşitlik için çift eşittir (==) kullanılır.", "has_output": True},
        {"msg": "**Konu:** Şart yanlışsa `else` çalışır.\n\n**Görev:** Sayı 5'ten büyük değilse 'Hata' yazdır.", "task": "s = 3\nif s > 5: pass\n___: print('Hata')", "check": lambda c, o, i: "else" in c, "solution": "else:", "hint": "Sadece else: yazmalısın.", "has_output": True},
        {"msg": "**Konu:** `elif` çoklu şart sağlar.\n\n**Görev:** Puan 50'den büyükse 'Geçti' yazan bir yapı kur.", "task": "p = 60\nif p < 50: pass\n___ p > 50: print('Geçti')", "check": lambda c, o, i: "elif" in c, "solution": "elif p > 50:", "hint": "İkinci şart için elif kullanılır.", "has_output": True},
        {"msg": "**Konu:** `and` her iki şartın doğruluğunu bekler.\n\n**Görev:** Hem 1 hem 2 doğru mu kontrol et.", "task": "if 1==1 ___ 2==2: print('OK')", "check": lambda c, o, i: "and" in c, "solution": "and", "hint": "Ve anlamına gelen and bağlacını yaz.", "has_output": True},
        {"msg": "**Konu:** `!=` eşit değilse demektir.\n\n**Görev:** Sayı 0 değilse 'Var' yazdır.", "task": "s = 5\nif s ___ 0: print('Var')", "check": lambda c, o, i: "!=" in c, "solution": "if s != 0:", "hint": "Eşit değildir operatörü != şeklindedir.", "has_output": True}
    ]},
    {"module_title": "4. Döngüler (For/While)", "exercises": [
        {"msg": "**Konu:** `range()` sayı üretir.\n\n**Görev:** Döngüyü 5 kez döndür.", "task": "for i in ___(5): print(i)", "check": lambda c, o, i: "range" in c, "solution": "for i in range(5):", "hint": "Aralık üretici range fonksiyonunu yaz.", "has_output": True},
        {"msg": "**Konu:** `while` şart sürdükçe döner.\n\n**Görev:** i sıfır olduğu sürece dönen döngü kur.", "task": "i = 0\n___ i == 0: print('X'); i += 1", "check": lambda c, o, i: "while" in c, "solution": "while i == 0:", "hint": "While döngüsünü başlat.", "has_output": True},
        {"msg": "**Konu:** `break` döngüyü kırar.\n\n**Görev:** Şart sağlanınca döngüyü bitir.", "task": "for i in range(10):\n if i == 1: ___\n print(i)", "check": lambda c, o, i: "break" in c, "solution": "break", "hint": "Kırmak için break yaz.", "has_output": True},
        {"msg": "**Konu:** `continue` adımı atlar.\n\n**Görev:** 1 değerini atla.", "task": "for i in range(3):\n if i == 1: ___\n print(i)", "check": lambda c, o, i: "continue" in c, "solution": "continue", "hint": "Atlamak için continue yaz.", "has_output": True},
        {"msg": "**Konu:** Listede gezinme.\n\n**Görev:** Listedeki her 'x'i yazdır.", "task": "for x ___ ['A', 'B']: print(x)", "check": lambda c, o, i: "in" in c, "solution": "for x in", "hint": "İçinde operatörü in'i kullan.", "has_output": True}
    ]},
    {"module_title": "5. Listeler", "exercises": [
        {"msg": "**Konu:** Listeler `[]` ile kurulur.\n\n**Görev:** Boşluğa 10 değerini ekleyerek liste oluştur.", "task": "L = [___, 20]", "check": lambda c, o, i: "10" in c, "solution": "L = [10, 20]", "hint": "Sadece 10 yaz.", "has_output": False},
        {"msg": "**Konu:** İndeks 0'dan başlar.\n\n**Görev:** Listenin ilk elemanına (50) eriş.", "task": "L = [50, 60]\nprint(L[___])", "check": lambda c, o, i: "0" in o, "solution": "L[0]", "hint": "İlk indeks her zaman 0'dır.", "has_output": True},
        {"msg": "**Konu:** `.append()` sona ekler.\n\n**Görev:** Listeye 30 ekle.", "task": "L = [10]\nL.___ (30)\nprint(L)", "check": lambda c, o, i: "append" in c, "solution": "L.append(30)", "hint": "Eklemek için append metodunu yaz.", "has_output": True},
        {"msg": "**Konu:** `len()` boyutu verir.\n\n**Görev:** Listenin uzunluğunu bul.", "task": "L = [1, 2, 3]\nprint(___(L))", "check": lambda c, o, i: "len" in c, "solution": "len(L)", "hint": "Len fonksiyonunu kullan.", "has_output": True},
        {"msg": "**Konu:** `.pop()` sonuncuyu atar.\n\n**Görev:** Son elemanı sil.", "task": "L = [1, 2]\nL.___()\nprint(L)", "check": lambda c, o, i: "pop" in c, "solution": "L.pop()", "hint": "Pop metodunu yaz.", "has_output": True}
    ]},
    {"module_title": "6. Fonksiyonlar ve Veri Yapıları", "exercises": [
        {"msg": "**Konu:** `def` fonksiyon tanımlar.\n\n**Görev:** 'pito' fonksiyonunu başlat.", "task": "___ pito(): print('Hi')", "check": lambda c, o, i: "def" in c, "solution": "def pito():", "hint": "Def yazmalısın.", "has_output": False},
        {"msg": "**Konu:** Sözlükler `{anahtar: değer}` şeklindedir.\n\n**Görev:** 'ad' anahtarına 'Pito' ata.", "task": "d = {'ad': '___'}\nprint(d['ad'])", "check": lambda c, o, i: "Pito" in o, "solution": "d = {'ad': 'Pito'}", "hint": "Değer kısmına Pito yaz.", "has_output": True},
        {"msg": "**Konu:** Tuple `()` değiştirilemez.\n\n**Görev:** (1, 2) şeklinde bir demet oluştur.", "task": "t = (___, 2)", "check": lambda c, o, i: "1" in c, "solution": "t = (1, 2)", "hint": "Boşluğa 1 yaz.", "has_output": False},
        {"msg": "**Konu:** `.keys()` anahtarları getirir.\n\n**Görev:** Sözlük anahtarlarını çağır.", "task": "d = {'a':1}\nprint(d.___())", "check": lambda c, o, i: "keys" in c, "solution": "d.keys()", "hint": "Keys metodunu yaz.", "has_output": True},
        {"msg": "**Konu:** `return` sonuç döndürür.\n\n**Görev:** 5 döndüren fonksiyon yaz.", "task": "def f(): ___ 5", "check": lambda c, o, i: "return" in c, "solution": "return 5", "hint": "Döndürmek için return kullan.", "has_output": False}
    ]},
    {"module_title": "7. OOP: Nesne Tabanlı", "exercises": [
        {"msg": "**Konu:** `class` bir şablondur.\n\n**Görev:** Robot sınıfı tanımla.", "task": "___ Robot: pass", "check": lambda c, o, i: "class" in c, "solution": "class Robot:", "hint": "Sınıf için class yaz.", "has_output": False},
        {"msg": "**Konu:** Nesne üretimi.\n\n**Görev:** Robot'tan r nesnesi üret.", "task": "class Robot: pass\nr = ___()", "check": lambda c, o, i: "Robot()" in c, "solution": "r = Robot()", "hint": "Sınıf ismini fonksiyon gibi çağır.", "has_output": False},
        {"msg": "**Konu:** Nitelik atama.\n\n**Görev:** Nesnenin rengini 'Mavi' yap.", "task": "class R: pass\nr = R()\nr.___ = 'Mavi'\nprint(r.renk)", "check": lambda c, o, i: "renk" in c, "solution": "r.renk = 'Mavi'", "hint": "Noktadan sonra renk yaz.", "has_output": True},
        {"msg": "**Konu:** `self` nesnenin kendisidir.\n\n**Görev:** Metot tanımla.", "task": "class R:\n def ses(___): print('Bip')", "check": lambda c, o, i: "self" in c, "solution": "def ses(self):", "hint": "Parantez içine self yaz.", "has_output": False},
        {"msg": "**Konu:** Metot çağırma.\n\n**Görev:** r nesnesinin s() metodunu çalıştır.", "task": "class R:\n def s(self): print('X')\nr = R()\nr.___()", "check": lambda c, o, i: "s()" in c, "solution": "r.s()", "hint": "Metot ismini yaz.", "has_output": True}
    ]},
    {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [
        {"msg": "**Konu:** `open('w')` yazmak için açar.\n\n**Görev:** test.txt'yi yazma modunda aç.", "task": "f = ___('test.txt', '___')", "check": lambda c, o, i: "open" in c and "w" in c, "solution": "open('test.txt', 'w')", "hint": "Açmak için open, mod için w kullan.", "has_output": False},
        {"msg": "**Konu:** `.write()` içerik yazar.\n\n**Görev:** Dosyaya 'Selam' yaz.", "task": "f = open('t.txt', 'w')\nf.___('Selam')\nf.close()", "check": lambda c, o, i: "write" in c, "solution": "f.write('Selam')", "hint": "Write metodunu kullan.", "has_output": False},
        {"msg": "**Konu:** `open('r')` okumak içindir.\n\n**Görev:** Okuma modunda aç.", "task": "f = open('t.txt', '___')", "check": lambda c, o, i: "r" in c, "solution": "f = open('t.txt', 'r')", "hint": "Okuma modu r'dir.", "has_output": False},
        {"msg": "**Konu:** `.read()` tümünü okur.\n\n**Görev:** İçeriği oku.", "task": "f = open('t.txt', 'r')\nprint(f.___())", "check": lambda c, o, i: "read" in c, "solution": "f.read()", "hint": "Read metodunu yaz.", "has_output": True},
        {"msg": "**Konu:** `.close()` dosyayı kapatır.\n\n**Görev:** Kaynağı serbest bırak.", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o, i: "close" in c, "solution": "f.close()", "hint": "Kapatmak için close yaz.", "has_output": False}
    ]}
]

# --- 6. ARA YÜZ DÜZENİ ---
col_main, col_side = st.columns([3, 1])
m_idx = max(0, min(st.session_state.current_module, len(training_data) - 1))
curr_module_exercises = training_data[m_idx]["exercises"]
e_idx = max(0, min(st.session_state.current_exercise, len(curr_module_exercises) - 1))

with col_main:
    st.markdown(f"#### 👋 {RUTBELER[min(sum(st.session_state.completed_modules), 8)]} {st.session_state.student_name} ({st.session_state.student_class}) | ⭐ Puan: {int(st.session_state.total_score)}")
    
    if st.session_state.db_module >= 8:
        if not st.session_state.celebrated: st.balloons(); st.session_state.celebrated = True
        st.success(f"🎉 Tebrikler {st.session_state.student_name}! Tüm Python macerasını başarıyla tamamladın.")
        if st.button("🔄 Eğitimi Tekrar Al"):
            st.session_state.update({'db_module':0,'db_exercise':0,'total_score':0,'current_module':0,'current_exercise':0,'completed_modules':[False]*8,'scored_exercises':set(),'celebrated':False,'fail_count':0,'feedback_msg':"", 'last_output':""})
            force_save(); st.rerun()
        st.divider()

    module_labels = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} Modül {i+1}: {training_data[i]['module_title']}" for i in range(len(training_data))]
    sel_mod_label = st.selectbox("Eğitim Modülü Seç:", module_labels, index=m_idx)
    new_m_idx = module_labels.index(sel_mod_label)
    if new_m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': new_m_idx, 'current_exercise': 0, 'fail_count': 0, 'exercise_passed': False, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
        st.rerun()

    st.divider()
    curr_ex = curr_module_exercises[e_idx]
    is_locked = (st.session_state.current_module < st.session_state.db_module) or (st.session_state.db_module >= 8)

    c_img, c_msg = st.columns([1, 4])
    with c_img: st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/200/robot-viewer.png", width=140)
    with c_msg:
        st.info(f"##### 🗣️ Pito'nun Notu:\n{curr_ex['msg']}")
        st.caption(f"Adım: {e_idx + 1}/5 | " + ("🔒 Arşiv" if is_locked else f"🎁 Puan: {st.session_state.current_potential_score} | ❌ Hata: {st.session_state.fail_count}/4"))

    if st.session_state.fail_count == 3 and not is_locked:
        st.markdown(f"""<div class="hint-guide"><div class="hint-header">💡 Pito'dan İpucu</div>{curr_ex['hint']}</div>""", unsafe_allow_html=True)
    elif st.session_state.fail_count >= 4 and not is_locked:
        st.error("❌ Maalesef bu adımdan puan alamadın. İşte öğrenmen için çözüm yolu:")
        st.markdown(f"""<div class="solution-guide"><div class="solution-header">✅ Doğru Çözüm Yolu</div></div>""", unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")

    def run_pito_code(c, user_input="Pito"):
        if "___" in c: return "⚠️ Boşluk Hatası"
        old_stdout, new_stdout = sys.stdout, StringIO()
        sys.stdout = new_stdout
        try:
            mock_globals = {"input": lambda p: str(user_input), "print": print, "int": int, "str": str, "len": len, "open": open, "range": range, "s": 10, "L": [10], "d":{'ad':'Pito'}, "t":(1,2), "ad": "Pito"}
            exec(c, mock_globals)
            sys.stdout = old_stdout
            return new_stdout.getvalue()
        except Exception as e:
            sys.stdout = old_stdout
            return f"❌ Python Hatası: {e}"

    if is_locked:
        st.markdown(f'<div class="solution-guide"><div class="solution-header">📖 Çözüm Arşivi</div></div>', unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")
    else:
        if st.session_state.fail_count < 4 and not st.session_state.exercise_passed:
            code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=200, key=f"ace_{st.session_state.current_module}_{e_idx}", auto_update=True)
            has_input = "input(" in code
            u_in = ""
            if has_input:
                st.markdown('<div style="border: 2px solid #3a7bd5; padding: 10px; border-radius: 10px; background-color: #e0f2fe; color: #0369a1; font-weight: bold;">⚡ Pito Bekliyor: Aşağıdaki kutuya bir veri yazmalısın!</div>', unsafe_allow_html=True)
                u_in = st.text_input("Giriş simülasyonu (Buraya yazınız):", key=f"term_{st.session_state.current_module}_{e_idx}")
            
            if st.button("🔍 Kodumu Kontrol Et", use_container_width=True):
                if "___" in code:
                    st.session_state.feedback_msg = "⚠️ Lütfen önce kodun içindeki '___' alanlarını doldur!"
                    st.rerun()
                elif has_input and not u_in.strip():
                    st.session_state.feedback_msg = "🔴 DUR! Giriş kutusuna bir veri girmelisin!"
                    st.rerun()
                elif curr_ex.get("force_text") and any(char.isdigit() for char in u_in):
                    st.session_state.feedback_msg = "🤔 İsimlerde rakam olmaz, lütfen sadece metin gir!"
                    st.rerun()
                else:
                    out = run_pito_code(code, u_in or "10")
                    if out.startswith("❌") or not curr_ex['check'](code, out, u_in or "10"):
                        st.session_state.fail_count += 1
                        st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                        if st.session_state.fail_count >= 4:
                            st.session_state.exercise_passed = True
                            if e_idx == 4: st.session_state.completed_modules[st.session_state.current_module] = True
                        else:
                            st.session_state.feedback_msg = f"❌ bu {st.session_state.fail_count}. hatan"
                        st.rerun()
                    else:
                        st.session_state.feedback_msg = "✅ Harika!"
                        st.session_state.last_output = out
                        st.session_state.exercise_passed = True
                        if f"{st.session_state.current_module}_{e_idx}" not in st.session_state.scored_exercises:
                            st.session_state.total_score += st.session_state.current_potential_score
                            st.session_state.scored_exercises.add(f"{st.session_state.current_module}_{e_idx}")
                            if st.session_state.db_exercise < 4: st.session_state.db_exercise += 1
                            else: st.session_state.db_module += 1; st.session_state.db_exercise = 0; st.session_state.completed_modules[st.session_state.current_module] = True
                            force_save()
                        st.rerun()

    if st.session_state.exercise_passed:
        if st.session_state.fail_count < 4:
            st.success(st.session_state.feedback_msg if st.session_state.feedback_msg else "✅ Görev tamamlandı.")
            if st.session_state.last_output:
                st.markdown("**Kod Çıktısı:**"); st.code(st.session_state.last_output)
        
        if e_idx < 4:
            if st.button("➡️ Sonraki Adım", use_container_width=True):
                st.session_state.update({'current_exercise': e_idx + 1, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
                st.rerun()
        elif st.session_state.current_module < 7:
            if st.button("🏆 Modülü Tamamla", use_container_width=True):
                st.session_state.update({'current_module': st.session_state.current_module + 1, 'current_exercise': 0, 'fail_count': 0, 'exercise_passed': False, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
                st.rerun()
    elif st.session_state.feedback_msg:
        st.error(st.session_state.feedback_msg)

with col_side:
    df_lb = get_db()
    st.markdown("### 🏅 Şampiyon Sınıf")
    class_stats = df_lb.groupby("Sınıf")["Puan"].sum().reset_index()
    if not class_stats.empty:
        top_class = class_stats.sort_values(by="Puan", ascending=False).head(1).iloc[0]
        st.markdown(f'<div class="leaderboard-card" style="background: linear-gradient(135deg, #FFD700, #DAA520); color: black;"><b>Sınıf: {top_class["Sınıf"]}</b><br>Toplam: {int(top_class["Puan"])} Puan</div>', unsafe_allow_html=True)
    
    st.markdown("### 🏆 En İyi Kodlamacılar")
    tab_class, tab_school = st.tabs(["👥 Sınıfım", "🏫 Okul Geneli"])
    for t, d in zip([tab_class, tab_school], [df_lb[df_lb["Sınıf"] == st.session_state.student_class], df_lb]):
        with t:
            if not d.empty:
                for _, r in d.sort_values(by="Puan", ascending=False).head(10).iterrows():
                    st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]} ({r["Sınıf"]})</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)