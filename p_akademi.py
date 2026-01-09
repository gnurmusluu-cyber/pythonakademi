import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import os

# --- 1. SAYFA VE TASARIM AYARLARI ---
st.set_page_config(layout="wide", page_title="Pito Python Akademi", initial_sidebar_state="collapsed")

SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]

st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem;}
    .pito-bubble {
        position: relative; background: #f0f2f6; border: 2px solid #3a7bd5;
        border-radius: 15px; padding: 20px; margin-bottom: 20px; color: #1e1e1e;
        font-weight: 500; font-size: 1.1rem; box-shadow: 4px 4px 10px rgba(0,0,0,0.1);
    }
    .pito-bubble:after {
        content: ''; position: absolute; bottom: -20px; left: 40px;
        border-width: 20px 20px 0; border-style: solid; border-color: #3a7bd5 transparent;
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

# --- 2. VERİ TABANI YÖNETİMİ ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        df["Okul No"] = df["Okul No"].astype(str).str.split('.').str[0].str.strip()
        return df.dropna(subset=["Okul No"])
    except:
        return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])

def force_save():
    try:
        no = str(st.session_state.student_no).strip()
        score = int(st.session_state.total_score)
        df_all = get_db()
        df_clean = df_all[df_all["Okul No"] != no]
        progress = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = "🌱 Python Çırağı" if score < 200 else "💻 Kod Yazarı" if score < 500 else "🏆 Python Ustası"
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, score, rank, progress, st.session_state.db_module, st.session_state.db_exercise, datetime.now().strftime("%H:%M:%S")]], 
                               columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

# --- 3. SESSION STATE BAŞLATMA ---
if 'is_logged_in' not in st.session_state:
    for k, v in {'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8, 
                 'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0, 
                 'scored_exercises': set(), 'db_module': 0, 'db_exercise': 0, 'is_logged_in': False, 
                 'current_potential_score': 20}.items():
        st.session_state[k] = v

PITO_IMG = "assets/pito.png"

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.is_logged_in:
    st.markdown("<br>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba ben <b>Pito</b>! Haydi birlikte Python\'ın eğlenceli dünyasına dalalım.</div>', unsafe_allow_html=True)
        st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/180/robot-viewer.png", width=180)
        in_no_raw = st.text_input("Okul Numaran:", key="login_field").strip()
        if in_no_raw:
            df = get_db()
            user_data = df[df["Okul No"] == in_no_raw]
            if not user_data.empty:
                row = user_data.iloc[0]
                m_v, e_v = int(row['Mevcut Modül']), int(row['Mevcut Egzersiz'])
                st.markdown(f"### Hoş geldin, **{row['Öğrencinin Adı']}**! 👋")
                st.success(f"Puanın: {row['Puan']} | Kaldığın Yer: Modül {m_v+1}, Adım {e_v+1}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🚀 Devam Et"):
                        st.session_state.student_no, st.session_state.student_name, st.session_state.student_class = str(row["Okul No"]), row["Öğrencinin Adı"], row["Sınıf"]
                        st.session_state.total_score, st.session_state.db_module, st.session_state.db_exercise = int(row["Puan"]), m_v, e_v
                        st.session_state.current_module, st.session_state.current_exercise = m_v, e_v
                        st.session_state.completed_modules = [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")]
                        st.session_state.is_logged_in = True; st.rerun()
                with c2:
                    if st.button("📚 İncele"):
                        st.session_state.student_no, st.session_state.student_name, st.session_state.student_class = str(row["Okul No"]), row["Öğrencinin Adı"], row["Sınıf"]
                        st.session_state.total_score, st.session_state.db_module, st.session_state.db_exercise = int(row["Puan"]), m_v, e_v
                        st.session_state.current_module, st.session_state.current_exercise = 0, 0
                        st.session_state.completed_modules = [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")]
                        st.session_state.is_logged_in = True; st.rerun()
            else:
                st.info("Seni tanımıyorum. Bilgilerini tamamla:")
                in_name = st.text_input("Adın Soyadın:", key="new_name")
                in_class = st.selectbox("Sınıfın:", SINIFLAR, key="new_class")
                if st.button("Maceraya Başla! ✨"):
                    if in_name.strip():
                        st.session_state.student_no, st.session_state.student_name, st.session_state.student_class = in_no_raw, in_name.strip(), in_class
                        st.session_state.is_logged_in = True; force_save(); st.rerun()
    st.stop()

# --- 5. EKSİKSİZ MÜFREDAT VE ÇÖZÜMLER ---
training_data = [
    {"module_title": "1. Giriş ve Çıktı", "exercises": [
        {"msg": "print() fonksiyonu ekrana çıktı almamızı sağlar. Hadi dene: Ekrana 'Merhaba Pito' yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')"},
        {"msg": "sayıları ekrana yazdırmak için tırnak işareti kullanmamıza gerek yoktur. Şimdi 100 sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o, "solution": "print(100)"},
        {"msg": "print() fonksiyonu içerisinde aralarına virgül koyarak birden fazla veriyi sıralayıp ekrana yazdırabiliriz. 'Puan:' metni ile 100 sayısını yan yana yazdır.", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o, "solution": "print('Puan:', 100)"},
        {"msg": "Kodlarımıza açıklama eklemek için # (diyez) işaretini kullanırız. Bu satırlar Python tarafından çalıştırılmaz. Bir yorum satırı ekle.", "task": "___ Bu bir yorumdur", "check": lambda c, o: "#" in c, "solution": "# Bu bir yorumdur"},
        {"msg": "Metin içerisinde bir alt satıra geçmek için \\n karakterini kullanırız. Üst ve Alt kelimelerini farklı satırlarda yazdır.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o, "solution": "print('Üst' + '\\n' + 'Alt')"}
    ]},
    {"module_title": "2. Değişkenler", "exercises": [
        {"msg": "Değişkenler bilgi saklamamıza yarar. yas = 15 tanımla ve yazdır.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o, "solution": "yas = 15\nprint(yas)"},
        {"msg": "isim = 'Pito' değişkeni tanımla ve yazdır.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o, "solution": "isim = 'Pito'\nprint(isim)"},
        {"msg": "input() kullanıcıdan bilgi almamızı sağlar. 'Adın: ' sorusuyla bir isim al.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c, "solution": "ad = input('Adın: ')\nprint(ad)"},
        {"msg": "str() sayıları metne çevirir. 10 sayısını metne çevir.", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c, "solution": "s = 10\nprint(str(s))"},
        {"msg": "int() ile girişi tam sayıya çevirmelisin.", "task": "n = ___(___('S: '))\nprint(n + 1)", "check": lambda c, o: "int" in c, "solution": "n = int('10')\nprint(n + 1)"}
    ]},
    {"module_title": "3. Karar Yapıları", "exercises": [
        {"msg": "== ile eşitlik kontrolü yap.", "task": "if 10 ___ 10: print('X')", "check": lambda c, o: "==" in c, "solution": "if 10 == 10: print('X')"},
        {"msg": "else: yapısı kur.", "task": "if 5>10: pass\n___: print('Y')", "check": lambda c, o: "else" in c, "solution": "if 5>10: pass\nelse: print('Y')"},
        {"msg": ">= büyük eşit kontrolü.", "task": "if 5 ___ 5: print('Z')", "check": lambda c, o: ">=" in c, "solution": "if 5 >= 5: print('Z')"},
        {"msg": "and ile iki koşulu birleştir.", "task": "if 1==1 ___ 2==2: print('OK')", "check": lambda c, o: "and" in c, "solution": "if 1==1 and 2==2: print('OK')"},
        {"msg": "elif ile ek koşul ekle.", "task": "if 5>10: pass\n___ 5==5: print('A')", "check": lambda c, o: "elif" in c, "solution": "if 5>10: pass\nelif 5==5: print('A')"}
    ]},
    {"module_title": "4. Döngüler", "exercises": [
        {"msg": "3 kez dönen for döngüsü.", "task": "for i in ___(3): print('X')", "check": lambda c, o: o.count("X")==3, "solution": "for i in range(3): print('X')"},
        {"msg": "i sayacını yazdır.", "task": "for i in range(2): print(___)", "check": lambda c, o: "1" in o, "solution": "for i in range(2): print(i)"},
        {"msg": "while döngüsü başlat.", "task": "i=0\n___ i<1: print('Y'); i+=1", "check": lambda c, o: "while" in c, "solution": "i=0\nwhile i<1: print('Y'); i+=1"},
        {"msg": "break ile döngüyü kır.", "task": "for i in range(3): if i==1: ___\n print(i)", "check": lambda c, o: "break" in c, "solution": "for i in range(3): if i==1: break\n print(i)"},
        {"msg": "continue ile adımı atla.", "task": "for i in range(3): if i==1: ___\n print(i)", "check": lambda c, o: "continue" in c, "solution": "for i in range(3): if i==1: continue\n print(i)"}
    ]},
    {"module_title": "5. Listeler & Fonksiyonlar", "exercises": [
        {"msg": "Liste oluştur [10, 20].", "task": "L = [___, 20]", "check": lambda c, o: "10" in c, "solution": "L = [10, 20]\nprint(L)"},
        {"msg": "0. indekse eriş.", "task": "L=[5,6]\nprint(L[___])", "check": lambda c, o: "5" in o, "solution": "L=[5,6]\nprint(L[0])"},
        {"msg": "len() ile boyut bul.", "task": "L=[1,2]\nprint(___(L))", "check": lambda c, o: "2" in o, "solution": "L=[1,2]\nprint(len(L))"},
        {"msg": "def ile fonksiyon tanımla.", "task": "___ f(): print('X')", "check": lambda c, o: "def" in c, "solution": "def f(): print('X')"},
        {"msg": "f() fonksiyonunu çağır.", "task": "def f(): print('X')\n___", "check": lambda c, o: "f()" in c, "solution": "def f(): print('X')\nf()"}
    ]},
    {"module_title": "6. İleri Veri Yapıları", "exercises": [
        {"msg": "Tuple (1, 2) tanımla.", "task": "t = (___, 2)", "check": lambda c, o: "1" in c, "solution": "t = (1, 2)\nprint(t)"},
        {"msg": "Sözlük değeri ata.", "task": "d = {'ad': '___'}", "check": lambda c, o: "Pito" in c, "solution": "d = {'ad': 'Pito'}\nprint(d['ad'])"},
        {"msg": "keys() ile anahtarları çek.", "task": "d={'a':1}\nprint(d.___())", "check": lambda c, o: "keys" in c, "solution": "d={'a':1}\nprint(d.keys())"},
        {"msg": "set() tanımla.", "task": "s = {1, 2, ___}", "check": lambda c, o: "1" in c, "solution": "s = {1, 2, 1}"},
        {"msg": "pop() ile son elemanı sil.", "task": "L=[1,2]\nL.___()\nprint(L)", "check": lambda c, o: "1" in o, "solution": "L=[1,2]\nL.pop()\nprint(L)"}
    ]},
    {"module_title": "7. OOP", "exercises": [
        {"msg": "class ile sınıf tanımla.", "task": "___ Robot: pass", "check": lambda c, o: "class" in c, "solution": "class Robot: pass"},
        {"msg": "Nesne üret.", "task": "class R: pass\np = ___()", "check": lambda c, o: "R()" in c, "solution": "class R: pass\np = R()"},
        {"msg": "Renk niteliği ata.", "task": "class R: pass\np=R()\np.___ = 'Mavi'", "check": lambda c, o: "renk" in c, "solution": "class R: pass\np=R()\np.renk = 'Mavi'"},
        {"msg": "Metot ekle.", "task": "class R: def ___(self): pass", "check": lambda c, o: "ses" in c, "solution": "class R: def ses(self): pass"},
        {"msg": "Metodu çağır.", "task": "class R: def s(self): print('X')\nr=R()\nr.___()", "check": lambda c, o: "s()" in c, "solution": "class R: def s(self): print('X')\nr=R()\nr.s()"}
    ]},
    {"module_title": "8. Dosyalar", "exercises": [
        {"msg": "open() ile dosya aç.", "task": "f = ___('n.txt', 'w')", "check": lambda c, o: "open" in c, "solution": "f = open('n.txt', 'w')"},
        {"msg": "write() ile yaz.", "task": "f=open('t.txt','w')\nf.___('X')", "check": lambda c, o: "write" in c, "solution": "f=open('t.txt','w')\nf.write('X')"},
        {"msg": "'r' moduyla oku.", "task": "f=open('t.txt', '___')", "check": lambda c, o: "r" in c, "solution": "f=open('t.txt', 'r')"},
        {"msg": "read() ile oku.", "task": "f=open('t.txt','r')\nprint(f.___())", "check": lambda c, o: "read" in c, "solution": "f=open('t.txt','r')\nprint(f.read())"},
        {"msg": "close() ile kapat.", "task": "f=open('t.txt','r')\nf.___()", "check": lambda c, o: "close" in c, "solution": "f=open('t.txt','r')\nf.close()"}
    ]}
]

# --- 6. ARA YÜZ DÜZENİ ---
col_main, col_side = st.columns([3, 1])

with col_main:
    st.markdown(f"#### 👋 {st.session_state.student_name} | ⭐ Puan: {st.session_state.total_score}")
    mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} {m['module_title']}" for i, m in enumerate(training_data)]
    
    if st.session_state.current_module != st.session_state.db_module or st.session_state.current_exercise != st.session_state.db_exercise:
        if st.button(f"🔙 Güncel Görevime Dön (Modül {st.session_state.db_module + 1}, Adım {st.session_state.db_exercise + 1})", use_container_width=True):
            st.session_state.current_module = st.session_state.db_module
            st.session_state.current_exercise = st.session_state.db_exercise
            st.session_state[f"sel_{st.session_state.student_no}"] = mod_titles[st.session_state.db_module]
            st.rerun()

    sel_mod = st.selectbox("Modül Seç:", mod_titles, key=f"sel_{st.session_state.student_no}")
    m_idx = mod_titles.index(sel_mod)
    
    if m_idx != st.session_state.current_module:
        st.session_state.current_module = m_idx
        st.session_state.current_exercise = st.session_state.db_exercise if m_idx == st.session_state.db_module else 0
        st.session_state.current_potential_score = 20; st.rerun()

    st.divider()
    e_idx = st.session_state.current_exercise
    curr_ex = training_data[m_idx]["exercises"][e_idx]
    is_locked = (m_idx < st.session_state.db_module) or (m_idx == st.session_state.db_module and e_idx < st.session_state.db_exercise)

    c_img, c_msg = st.columns([1, 4])
    with c_img: st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/200/robot-viewer.png", width=140)
    with c_msg:
        st.info(f"##### 🗣️ Pito:\n{curr_ex['msg']}")
        st.caption(f"Adım: {e_idx + 1}/5 {'🔒 Tamamlandı' if is_locked else f'🎁 Kazanılacak Puan: {st.session_state.current_potential_score}'}")

    code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=200, readonly=is_locked, key=f"ace_{m_idx}_{e_idx}")

    def run_pito_code(c, user_input=""):
        old_stdout, new_stdout = sys.stdout, StringIO()
        sys.stdout = new_stdout
        try:
            exec(c, {"input": lambda p: user_input if user_input else "10"})
            sys.stdout = old_stdout
            return new_stdout.getvalue()
        except Exception as e:
            sys.stdout = old_stdout
            return f"Hata: {e}"

    u_in = ""
    if "input(" in code and not is_locked:
        u_in = st.text_input("👇 Pito Terminali: Bir isim veya sayı yaz ve Kontrol Et'e bas:")

    if is_locked:
        st.subheader("📟 Sonuç (İnceleme Modu)")
        st.code(run_pito_code(curr_ex['solution']) if curr_ex['solution'] else "Hazır.")
    else:
        if st.button("🔍 Kontrol Et", use_container_width=True):
            out = run_pito_code(code.replace("___", "None"), u_in)
            st.subheader("📟 Çıktı")
            st.code(out if out else "Kod çalıştı!")
            if curr_ex['check'](code, out) and "___" not in code:
                st.session_state.exercise_passed = True
                if f"{m_idx}_{e_idx}" not in st.session_state.scored_exercises:
                    st.session_state.total_score += st.session_state.current_potential_score
                    st.session_state.scored_exercises.add(f"{m_idx}_{e_idx}")
                    if st.session_state.db_exercise < 4: st.session_state.db_exercise += 1
                    else:
                        st.session_state.db_module += 1; st.session_state.db_exercise = 0
                        st.session_state.completed_modules[m_idx] = True
                    force_save()
                st.success("Tebrikler! ✅")
            else:
                st.session_state.current_potential_score = max(5, st.session_state.current_potential_score - 5)
                st.warning(f"Hatalı! Puanın {st.session_state.current_potential_score}'ye düştü.")

    if st.session_state.exercise_passed or is_locked:
        if e_idx < 4:
            if st.button("➡️ Sonraki Adıma Geç"):
                st.session_state.current_exercise += 1; st.session_state.exercise_passed = False; st.session_state.current_potential_score = 20; st.rerun()
        else:
            # BUTON HATASI ÇÖZÜMÜ: Modül bitince bir sonraki taze modüle ışınlan
            if st.button("🏆 Modülü Bitir"):
                if st.session_state.current_module < 7:
                    st.session_state.current_module += 1
                    st.session_state.current_exercise = 0
                    st.session_state[f"sel_{st.session_state.student_no}"] = mod_titles[st.session_state.current_module]
                    st.balloons(); st.rerun()
                else:
                    st.success("Tebrikler! Tüm eğitim başarıyla tamamlandı. 🎓"); st.balloons()

with col_side:
    st.markdown(f"### 🏆 Sınıf Liderleri")
    df_lb = get_db()
    df_class = df_lb[df_lb["Sınıf"] == st.session_state.student_class]
    if not df_class.empty:
        df_sort = df_class.sort_values(by="Puan", ascending=False).drop_duplicates(subset=["Okul No"]).head(10)
        for i, (_, r) in enumerate(df_sort.iterrows()):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "⭐"
            st.markdown(f'<div class="leaderboard-card"><b>{medal} {r["Öğrencinin Adı"]}</b><br>{r["Puan"]} Puan</div>', unsafe_allow_html=True)