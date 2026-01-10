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

SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]
RUTBELER = [
    "🥚 Yeni Başlayan", "🌱 Python Çırağı", "🪵 Kod Oduncusu", "🧱 Mantık Mimarı", 
    "🌀 Döngü Ustası", "📋 Liste Uzmanı", "📦 Fonksiyon Kaptanı", "🤖 OOP Robotu", "🏆 Python Kahramanı"
]

# --- 2. BEYAZ ZEMİN VE GÖRÜNÜRLÜK ZIRHI (CSS) ---
st.markdown("""
    <style>
    /* Uygulama Arka Planını Beyaz Yap ve Metinleri Sabitle */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"] {
        background-color: #FFFFFF !important;
    }
    header {visibility: hidden;}
    html, body, [class*="st-"] { color: #1E293B !important; font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, [data-testid="stWidgetLabel"] p {
        color: #1E293B !important;
    }

    /* Widget (Giriş Kutuları ve Menüler) Görünürlük Garantisi */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, div[data-baseweb="base-input"] {
        background-color: #F8FAFC !important;
        color: #1E293B !important;
        border: 2px solid #E2E8F0 !important;
    }
    input { color: #1E293B !important; background-color: transparent !important; }
    div[data-baseweb="popover"] li { color: #1E293B !important; background-color: #FFFFFF !important; }

    /* Pito Konuşma Balonu */
    .pito-bubble {
        position: relative; background: #F8FAFC; border: 2px solid #3a7bd5;
        border-radius: 15px; padding: 20px; margin-bottom: 20px; color: #1E293B !important;
        font-weight: 500; font-size: 1.1rem; box-shadow: 4px 4px 15px rgba(0,0,0,0.05);
    }
    .pito-bubble:after {
        content: ''; position: absolute; bottom: -20px; left: 40px;
        border-width: 20px 20px 0; border-style: solid; border-color: #3a7bd5 transparent;
    }
    
    /* Çözüm Rehberi Kutusu */
    .solution-guide {
        background-color: #f8fafc !important;
        border: 2px solid #3a7bd5 !important;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        color: #1e1e1e !important;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .solution-header { color: #3a7bd5; font-weight: bold; font-size: 1.2rem; margin-bottom: 10px; }

    .leaderboard-card {
        background: linear-gradient(135deg, #1e1e1e, #2d2d2d);
        border: 1px solid #444; border-radius: 12px; padding: 10px; margin-bottom: 8px; color: white;
    }
    .champion-card {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        border: 2px solid #FFF; border-radius: 15px; padding: 15px; margin-top: 20px; color: #1e1e1e;
        text-align: center; font-weight: bold; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4);
    }
    .stButton > button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important;
        color: white !important; font-weight: bold; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. VERİ TABANI VE HAFIZA ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        df["Okul No"] = df["Okul No"].astype(str).str.split('.').str[0].str.strip()
        for col in ["Puan", "Mevcut Modül", "Mevcut Egzersiz"]:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        return df.dropna(subset=["Okul No"])
    except: return pd.DataFrame()

def force_save():
    try:
        no = str(st.session_state.student_no).strip()
        df_all = get_db()
        df_clean = df_all[df_all["Okul No"] != no]
        progress = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = RUTBELER[sum(st.session_state.completed_modules)]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, int(st.session_state.total_score), rank, progress, int(st.session_state.db_module), int(st.session_state.db_exercise), datetime.now().strftime("%H:%M:%S")]], columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

if 'is_logged_in' not in st.session_state:
    for k, v in {'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8, 
                  'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0, 
                  'scored_exercises': set(), 'db_module': 0, 'db_exercise': 0, 'is_logged_in': False, 
                  'current_potential_score': 20, 'celebrated': False, 'rejected_user': False}.items():
        st.session_state[k] = v

PITO_IMG = "assets/pito.png"

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.is_logged_in:
    st.markdown("<br>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba! Ben <b>Pito</b>. Python Dünyası\'na hoş geldin.</div>', unsafe_allow_html=True)
        st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/180/robot-viewer.png", width=180)
        if st.session_state.rejected_user: st.warning("⚠️ O halde kendi okul numaranı gir!")
        in_no_raw = st.text_input("Okul Numaran (Sadece Rakam):", key="login_field").strip()
        if in_no_raw and in_no_raw.isdigit():
            df = get_db()
            user_data = df[df["Okul No"] == in_no_raw] if not df.empty else pd.DataFrame()
            if not user_data.empty:
                row = user_data.iloc[0]
                st.info(f"🔍 Bu numara **{row['Öğrencinin Adı']}** adına kayıtlı.")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Evet, Benim"):
                        mv, ev = int(row['Mevcut Modül']), int(row['Mevcut Egzersiz'])
                        st.session_state.update({'student_no': in_no_raw, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': mv, 'db_exercise': ev, 'current_module': min(mv, 7), 'current_exercise': ev, 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True})
                        st.rerun()
                with c2:
                    if st.button("❌ Hayır, Değilim"):
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

# --- 5. EKSİKSİZ 8 MODÜLLÜK MÜFREDAT ---
training_data = [
    {"module_title": "1. Giriş ve Çıktı İşlemleri", "exercises": [
        {"msg": "Programımızın dış dünyayla iletişim kurmasını sağlayan temel komut **print()** fonksiyonudur. Metinsel ifadeleri mutlaka **tırnak** içinde yazmalısın. Hadi dene: Ekrana **'Merhaba Pito'** yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')"},
        {"msg": "Python'da matematiksel değer olan sayıları ekrana yazdırırken **tırnak işareti kullanmayız.** Şimdi ekrana **100** sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o, "solution": "print(100)"},
        {"msg": "print() içinde farklı verileri ayırmak için **virgül (,)** kullanırız. Hadi dene: **'Puan:'** metni ile **100** sayısını yan yana yazdır.", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o, "solution": "print('Puan:', 100)"},
        {"msg": "**# (Diyez)** işaretiyle başlayan satırlar Python tarafından okunmaz. Buna 'Yorum Satırı' denir. Hadi dene: Bir **yorum satırı** oluştur.", "task": "___ Bu bir yorumdur", "check": lambda c, o: "#" in c, "solution": "# Kodlarımı buraya yazıyorum"},
        {"msg": "Alt satıra geçmek için **'\\n'** karakteri kullanılır. Hadi dene: **'Üst'** ve **'Alt'** kelimelerini tek print içinde farklı satırlarda yazdır.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o, "solution": "print('Üst\\nAlt')"}
    ]},
    {"module_title": "2. Değişkenler: Bilgi Depolama", "exercises": [
        {"msg": "Değişkenler bilgileri hafızada saklamaya yarar. yas = 15 yazarak bir tam sayı değişkeni oluştur ve yazdır.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o, "solution": "yas = 15\nprint(yas)"},
        {"msg": "Hadi dene: **isim** adında bir değişken oluştur, içine **'Pito'** değerini ata ve ekrana yazdır.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o, "solution": "isim = 'Pito'\nprint(isim)"},
        {"msg": "**input()** ile kullanıcıdan bilgi alırız. Hadi dene: **'Adın: '** sorusuyla kullanıcıdan isim al ve yazdır.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c, "solution": "ad = input('Adın: ')\nprint(ad)"},
        {"msg": "**str()** sayısal veriyi metne dönüştürür. Hadi dene: **s = 10** değişkenini metne çevirip yazdır.", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c, "solution": "s = 10\nprint(str(s))"},
        {"msg": "Matematiksel işlem için veriyi **int()** ile tam sayıya çevirmelisin. Hadi dene: n değişkenine bir **input** al ve bunu **int**'e çevir.", "task": "n = ___(___('S: '))\nprint(n + 1)", "check": lambda c, o: "int" in c and "input" in c, "solution": "n = int(input('10'))\nprint(n+1)"}
    ]},
    {"module_title": "3. Karar Yapıları", "exercises": [
        {"msg": "Eşitlik kontrolü için **'=='** kullanılır. Hadi dene: Eğer 10 sayısı **10'a eşitse** ekrana 'X' yazdır.", "task": "if 10 ___ 10: print('X')", "check": lambda c, o: "==" in c, "solution": "if 10 == 10: print('X')"},
        {"msg": "Şart sağlanmıyorsa **'else:'** bloğu çalışır. Hadi dene: 5 sayısı 10'dan büyük değilse ekrana **'Y'** yazdıracak bir else bloğu kur.", "task": "if 5>10: pass\n___: print('Y')", "check": lambda c, o: "else" in c, "solution": "if 5>10: pass\nelse: print('Y')"},
        {"msg": "**'>='** büyük veya eşiti kontrol eder. Hadi dene: Eğer 5 sayısı **5'ten büyük veya eşitse** ekrana 'Z' yazdır.", "task": "if 5 ___ 5: print('Z')", "check": lambda c, o: ">=" in c, "solution": "if 5 >= 5: print('Z')"},
        {"msg": "**'and'** ile iki koşulun da doğru olması istenir. Hadi dene: Eğer 1 eşit 1 **ve** 2 eşit 2 ise 'OK' yazdır.", "task": "if 1==1 ___ 2==2: print('OK')", "check": lambda c, o: "and" in c, "solution": "if 1==1 and 2==2: print('OK')"},
        {"msg": "**'elif'** ilk şart yanlışsa alternatif şartı denetler. Hadi dene: 5>10 değilse ama **5==5 ise** 'A' yazdır.", "task": "if 5>10: pass\n___ 5==5: print('A')", "check": lambda c, o: "elif" in c, "solution": "if 5>10: pass\nelif 5==5: print('A')"}
    ]},
    {"module_title": "4. Döngüler: Tekrarlanan İşler", "exercises": [
        {"msg": "**'for'** döngüsü ve **range(3)** ile 3 kez tekrar yapabilirsin. Hadi dene: 3 kez 'X' yazdır.", "task": "for i in ___(3): print('X')", "check": lambda c, o: o.count("X")==3, "solution": "for i in range(3): print('X')"},
        {"msg": "**'while'** şart doğruyken çalışır. Hadi dene: **i<1** şartı doğruyken ekrana 'Y' yazdıran döngüyü kur.", "task": "i=0\n___ i<1: print('Y'); i+=1", "check": lambda c, o: "while" in c, "solution": "i=0\nwhile i<1: print('Y'); i+=1"},
        {"msg": "**'break'** döngüyü bitirir. Hadi dene: i değeri 1 olduğunda döngüyü **bitir**.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "break" in c, "solution": "for i in range(3):\n    if i==1: break\n    print(i)"},
        {"msg": "**'continue'** o adımı atlar. Hadi dene: i değeri 1 olduğunda o adımı **atla**.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "continue" in c, "solution": "for i in range(3):\n    if i==1: continue\n    print(i)"},
        {"msg": "Döngü sayacı olan **i** değişkenini ekrana yazdırarak tur numarasını görebilirsin.", "task": "for i in range(2): print(___)", "check": lambda c, o: "1" in o, "solution": "for i in range(2): print(i)"}
    ]},
    {"module_title": "5. Listeler", "exercises": [
        {"msg": "Listeler `[]` içinde saklanır. Hadi dene: **10** ve **20** sayılarından oluşan bir liste oluştur.", "task": "L = [___, 20]", "check": lambda c, o: "10" in c, "solution": "L=[10, 20]\nprint(L)"},
        {"msg": "Listenin ilk elemanına ulaşmak için `[0]` indeksini kullanırız. Hadi dene: **L** listesinin **ilk elemanına** eriş.", "task": "L=[5,6]\nprint(L[___])", "check": lambda c, o: "5" in o, "solution": "L=[5,6]\nprint(L[0])"},
        {"msg": "**len()** listenin boyutunu verir. Hadi dene: L listesinin eleman sayısını yazdır.", "task": "L=[1,2]\nprint(___(L))", "check": lambda c, o: "2" in o, "solution": "L=[1,2]\nprint(len(L))"},
        {"msg": "**append()** ile listeye veri eklenir. Hadi dene: L listesine **30** sayısını ekle.", "task": "L=[10]\nL.___(___)\nprint(L)", "check": lambda c, o: "30" in o, "solution": "L=[10]\nL.append(30)\nprint(L)"},
        {"msg": "**pop()** listeden eleman siler. Hadi dene: Listeden son elemanı **sil**.", "task": "L=[1,2]\nL.___()\nprint(L)", "check": lambda c, o: "1" in o, "solution": "L=[1,2]\nL.pop()\nprint(L)"}
    ]},
    {"module_title": "6. Fonksiyonlar ve Veriler", "exercises": [
        {"msg": "**def** ile f isminde bir fonksiyon tanımla.", "task": "___ f(): print('X')", "check": lambda c, o: "def" in c, "solution": "def f(): print('X')"},
        {"msg": "**Tuple (Demet)** değiştirilemez. Hadi dene: **1** ve **2** rakamlı bir demet oluştur.", "task": "t = (___, 2)\nprint(t)", "check": lambda c, o: "1" in c, "solution": "t = (1, 2)\nprint(t)"},
        {"msg": "**Sözlükler** Anahtar:Değer tutar. Hadi dene: **'ad'** anahtarına **'Pito'** değerini ata.", "task": "d = {'ad': '___'}\nprint(d['ad'])", "check": lambda c, o: "Pito" in c, "solution": "d = {'ad': 'Pito'}\nprint(d['ad'])"},
        {"msg": "**keys()** anahtarları getirir. Hadi dene: d sözlüğündeki anahtarları yazdır.", "task": "d={'a':1}\nprint(d.___())", "check": lambda c, o: "keys" in c, "solution": "d={'a':1}\nprint(d.keys())"},
        {"msg": "**Set (Küme)** benzersiz veri tutar. Hadi dene: Tekrarlayan sayıları olan bir küme oluştur.", "task": "s = {1, 2, ___}\nprint(s)", "check": lambda c, o: "1" in c, "solution": "s = {1, 2, 1}\nprint(s)"}
    ]},
    {"module_title": "7. OOP", "exercises": [
        {"msg": "**class** yazarak **Robot** sınıfı oluştur.", "task": "___ Robot: pass", "check": lambda c, o: "class" in c, "solution": "class Robot: pass"},
        {"msg": "**R** sınıfını kullanarak **p** adında bir nesne oluştur.", "task": "class R: pass\np = ___()", "check": lambda c, o: "R()" in c, "solution": "class R: pass\np = R()"},
        {"msg": "Robota **renk** niteliği olarak **'Mavi'** ata.", "task": "class R: pass\np=R()\np.___ = 'Mavi'\nprint(p.renk)", "check": lambda c, o: "renk" in c, "solution": "class R: pass\np=R()\np.renk = 'Mavi'\nprint(p.renk)"},
        {"msg": "Robota **ses** metodu ekle.", "task": "class R:\n def ___(self):\n  print('Bip!')", "check": lambda c, o: "ses" in c, "solution": "class R:\n    def ses(self):\n        print('Bip!')"},
        {"msg": "**r** üzerinden **s** metodunu çağır.", "task": "class R:\n def s(self): print('X')\nr=R()\nr.___()", "check": lambda c, o: "s()" in c, "solution": "class R:\n    def s(self):\n        print('X')\nr=R()\nr.s()"}
    ]},
    {"module_title": "8. Dosya Yönetimi", "exercises": [
        {"msg": "**open()** ile dosya açılır. **'w'** (write) kipi yazmak içindir.", "task": "dosya = ___('n.txt', '___')", "check": lambda c, o: "open" in c and "'w'" in c, "solution": "dosya = open('n.txt', 'w')\nprint('Açıldı.')"},
        {"msg": "**write()** dosyaya yazı yazar. Hadi dene: Dosyaya **'Pito'** yazdır ve dosyayı kapat.", "task": "f = open('t.txt', 'w'); f.___('Pito'); f.close()", "check": lambda c, o: "write" in c, "solution": "f = open('t.txt', 'w'); f.write('Pito'); f.close()"},
        {"msg": "**'r'** (read) kipi yalnızca okumak içindir. t.txt dosyasını okuma modunda aç.", "task": "f = open('t.txt', '___')", "check": lambda c, o: "'r'" in c, "solution": "f = open('t.txt', 'r'); f.close()"},
        {"msg": "**read()** tüm içeriği okur. Hadi dene: Dosyayı oku ve print ile ekrana yazdır.", "task": "f = open('t.txt', 'r')\nprint(f.___())\nf.close()", "check": lambda c, o: "read" in c, "solution": "f = open('t.txt', 'w'); f.write('Pito Akademi'); f.close(); f = open('t.txt', 'r'); print(f.read()); f.close()"},
        {"msg": "İş bitince dosya mutlaka **close()** ile kapatılmalıdır. Hadi dene: Dosyayı kapat.", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o: "close" in c, "solution": "f = open('t.txt', 'r'); f.close()"}
    ]}
]

# --- 6. ARA YÜZ DÜZENİ ---
col_main, col_side = st.columns([3, 1])

# Güvenli İndeks Kontrolü (Hataları Önler)
m_idx = min(st.session_state.current_module, len(training_data)-1)
if st.session_state.current_exercise >= len(training_data[m_idx]["exercises"]):
    st.session_state.current_exercise = 0

completed_count = sum(st.session_state.completed_modules)
student_rank = RUTBELER[min(completed_count, 8)]

with col_main:
    st.markdown(f"#### 👋 {student_rank} {st.session_state.student_name} | ⭐ Puan: {int(st.session_state.total_score)}")
    
    if st.session_state.db_module >= 8:
        if not st.session_state.celebrated: st.balloons(); st.session_state.celebrated = True
        st.success("### 🎉 Tebrikler! Eğitimi Başarıyla Tamamladın.")
        if st.button("🔄 Eğitimi Tekrar Al (Sıfırla)"):
            st.session_state.update({'db_module': 0, 'db_exercise': 0, 'total_score': 0, 'current_module': 0, 'current_exercise': 0, 'completed_modules': [False]*8, 'scored_exercises': set(), 'celebrated': False})
            force_save(); st.rerun()

    mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} Modül {i+1}" for i in range(len(training_data))]
    sel_mod = st.selectbox("Modül Seç:", mod_titles, index=m_idx)
    new_m_idx = mod_titles.index(sel_mod)
    if new_m_idx != st.session_state.current_module:
        st.session_state.current_module, st.session_state.current_exercise = new_m_idx, 0
        st.rerun()

    st.divider()
    e_idx = st.session_state.current_exercise
    curr_ex = training_data[m_idx]["exercises"][e_idx]
    is_locked = (m_idx < st.session_state.db_module) or (st.session_state.db_module >= 8)

    c_img, c_msg = st.columns([1, 4])
    with c_img: st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/200/robot-viewer.png", width=140)
    with c_msg:
        st.info(f"##### 🗣️ Pito:\n{curr_ex['msg']}")
        st.caption(f"Adım: {e_idx + 1}/5 " + ("🔒 İnceleme Modu" if is_locked else f"🎁 Puan: {st.session_state.current_potential_score}"))

    code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=200, readonly=is_locked, key=f"ace_{m_idx}_{e_idx}", auto_update=True)

    def run_pito_code(c, user_input="Pito"):
        old_stdout, new_stdout = sys.stdout, StringIO()
        sys.stdout = new_stdout
        try:
            safe_code = c.replace("___", "None")
            exec(safe_code, {"input": lambda p: str(user_input), "print": print, "int": int, "str": str, "len": len, "open": open, "range": range})
            sys.stdout = old_stdout
            return new_stdout.getvalue()
        except Exception as e:
            sys.stdout = old_stdout
            return f"Hata: {e}"

    # --- İNCELEME MODU ÇÖZÜM REHBERİ ---
    if is_locked:
        st.markdown(f"""
            <div class="solution-guide">
                <div class="solution-header">✅ Pito'nun Çözüm Rehberi</div>
                <b>Nasıl Yapılır?</b><br>{curr_ex['msg']}<br><br>
                <b>Doğru Kod Yapısı:</b>
            </div>
        """, unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")
        sol_out = run_pito_code(curr_ex['solution'], "Pito") 
        st.markdown("<b>Muhtemel Çıktı:</b>", unsafe_allow_html=True)
        st.code(sol_out if sol_out else "Kod başarıyla çalıştırıldı.")
    else:
        u_in = st.text_input("Giriş yap:", key=f"term_{m_idx}_{e_idx}") if "input(" in code else ""
        if st.button("🔍 Kontrol Et", use_container_width=True):
            out = run_pito_code(code, u_in or "Pito")
            if out.startswith("Hata:"): st.error(out)
            else:
                st.subheader("📟 Çıktı")
                st.code(out if out else "Kod çalıştı!")
                if curr_ex['check'](code, out) and "___" not in code:
                    st.session_state.exercise_passed = True
                    if f"{m_idx}_{e_idx}" not in st.session_state.scored_exercises:
                        st.session_state.total_score += st.session_state.current_potential_score
                        st.session_state.scored_exercises.add(f"{m_idx}_{e_idx}")
                        if st.session_state.db_exercise < len(training_data[m_idx]["exercises"]) - 1: st.session_state.db_exercise += 1
                        else: 
                            st.session_state.db_module += 1; st.session_state.db_exercise = 0
                            st.session_state.completed_modules[m_idx] = True
                        force_save()
                    st.success("Tebrikler! ✅")
                else: st.warning("Hatalı!")

    c_back, c_next = st.columns(2)
    with c_back:
        if is_locked and e_idx > 0:
            if st.button("⬅️ Önceki Adım"): st.session_state.current_exercise -= 1; st.rerun()
    with c_next:
        if st.session_state.exercise_passed or is_locked:
            if e_idx < len(training_data[m_idx]["exercises"]) - 1:
                if st.button("➡️ Sonraki Adıma Geç"): st.session_state.current_exercise += 1; st.session_state.exercise_passed = False; st.rerun()
            elif m_idx < len(training_data) - 1:
                if st.button("🏆 Modülü Bitir"): st.session_state.current_module += 1; st.session_state.current_exercise = 0; st.rerun()

with col_side:
    st.markdown(f"### 🏆 Liderlik Tablosu")
    df_lb = get_db()
    tab_class, tab_school = st.tabs(["👥 Sınıfım", "🏫 Okul"])
    with tab_class:
        df_class_lb = df_lb[df_lb["Sınıf"] == st.session_state.student_class]
        if not df_class_lb.empty:
            for i, (_, r) in enumerate(df_class_lb.sort_values(by="Puan", ascending=False).head(10).iterrows()):
                st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)
    with tab_school:
        if not df_lb.empty:
            for i, (_, r) in enumerate(df_lb.sort_values(by="Puan", ascending=False).head(10).iterrows()):
                st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]} ({r["Sınıf"]})</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)