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

st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem;}
    .pito-bubble {
        position: relative; background: #f0f2f6; border: 2px solid #3a7bd5;
        border-radius: 15px; padding: 20px; margin-bottom: 20px; color: #1e1e1e;
        font-weight: 500; font-size: 1.1rem; box-shadow: 4px 4px 15px rgba(0,0,0,0.1);
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
    .restart-btn > button { background: linear-gradient(45deg, #e53935, #e35d5b) !important; }
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
        rank = "🌱 Python Çırağı" if score < 250 else "💻 Kod Yazarı" if score < 600 else "🏆 Python Ustası"
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, score, rank, progress, st.session_state.db_module, st.session_state.db_exercise, datetime.now().strftime("%H:%M:%S")]], 
                               columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

# --- 3. SESSION STATE ---
if 'is_logged_in' not in st.session_state:
    for k, v in {'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8, 
                 'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0, 
                 'scored_exercises': set(), 'db_module': 0, 'db_exercise': 0, 'is_logged_in': False, 
                 'current_potential_score': 20}.items():
        st.session_state[k] = v

PITO_IMG = "assets/pito.png"

# --- 4. GİRİŞ EKRANI (TAM SENKRONİZE) ---
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
                st.success(f"Puanın: {row['Puan']} | " + (f"Eğitimi Tamamladın! 🏆" if m_v >= 8 else f"Kaldığın Yer: Modül {m_v+1}, Adım {e_v+1}"))
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🚀 Devam Et"):
                        st.session_state.student_no, st.session_state.student_name, st.session_state.student_class = str(row["Okul No"]), row["Öğrencinin Adı"], row["Sınıf"]
                        st.session_state.total_score, st.session_state.db_module, st.session_state.db_exercise = int(row["Puan"]), m_v, e_v
                        st.session_state.current_module, st.session_state.current_exercise = min(m_v, 7), e_v
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
                st.info("Seni henüz tanımıyorum. Bilgilerini tamamla:")
                in_name = st.text_input("Adın Soyadın:", key="new_name")
                in_class = st.selectbox("Sınıfın:", SINIFLAR, key="new_class")
                if st.button("Maceraya Başla! ✨"):
                    if in_name.strip():
                        st.session_state.student_no, st.session_state.student_name, st.session_state.student_class = in_no_raw, in_name.strip(), in_class
                        st.session_state.is_logged_in = True; force_save(); st.rerun()
    st.stop()

# --- 5. DETAYLI KONU ANLATIMLI MÜFREDAT VE ÇÖZÜMLER ---
training_data = [
    {"module_title": "1. Giriş ve Çıktı", "exercises": [
        {"msg": "Programımızın dış dünyayla iletişim kurmasının en temel yolu **print()** fonksiyonudur. Parantez içine yazdığımız her şey terminal ekranında görünür. Metinsel ifadeleri mutlaka **tırnak** içinde yazmalısın. Hadi dene: Ekrana 'Merhaba Pito' yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')"},
        {"msg": "Python'da matematiksel değer olan sayıları ekrana yazdırırken **tırnak işareti kullanmayız.** Şimdi ekrana 100 sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o, "solution": "print(100)"},
        {"msg": "print() içinde farklı verileri ayırmak için **virgül (,)** kullanırız. Virgül, otomatik olarak araya bir boşluk bırakır. 'Puan:' metni ile 100 sayısını yan yana yazdır.", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o, "solution": "print('Puan:', 100)"},
        {"msg": "**# (Diyez)** işaretiyle başlayan satırlar Python tarafından okunmaz. Buna 'Yorum Satırı' denir. Bir yorum satırı ekle.", "task": "___ Bu bir yorumdur", "check": lambda c, o: "#" in c, "solution": "# Bu bir yorumdur"},
        {"msg": "Metinlerin içinde bir alt satıra geçmek için özel karakter: **'\\n'**. Üst ve Alt kelimelerini farklı satırlarda yazdır.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o, "solution": "print('Üst' + '\\n' + 'Alt')"}
    ]},
    {"module_title": "2. Değişkenler", "exercises": [
        {"msg": "Değişkenler bilgileri hafızada saklamaya yarar. yas = 15 yazarak bir tam sayı değişkeni oluştur ve yazdır.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o, "solution": "yas = 15\nprint(yas)"},
        {"msg": "Metinleri saklarken tırnak kullanılır. Hadi dene: **isim** adında bir değişken oluştur, içine **'Pito'** değerini ata ve ekrana yazdır.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o, "solution": "isim = 'Pito'\nprint(isim)"},
        {"msg": "input() kullanıcıdan bilgi almamızı sağlar. 'Adın: ' sorusuyla bir isim al.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c, "solution": "ad = input('Adın: ')\nprint(ad)"},
        {"msg": "str() fonksiyonu sayısal bir veriyi metne dönüştürür. 10 sayısını metne çevir.", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c, "solution": "s = 10\nprint(str(s))"},
        {"msg": "int() ile kullanıcı girişlerini tam sayıya çevirmelisin. (Sayısal veri girilmelidir)", "task": "n = ___(___('S: '))\nprint(n + 1)", "check": lambda c, o: "int" in c, "solution": "n = int(input('10'))\nprint(n + 1)"}
    ]},
    {"module_title": "3. Karar Yapıları", "exercises": [{"msg": "Eşitlik kontrolü için '==' kullanılır.", "task": "if 10 ___ 10: print('X')", "check": lambda c, o: "==" in c, "solution": "if 10 == 10: print('X')"}, {"msg": "'>=' büyük eşit kontrolü sağlar.", "task": "if 5 ___ 5: print('Z')", "check": lambda c, o: ">=" in c, "solution": "if 5 >= 5: print('Z')"}, {"msg": "else: bloğu koşul yanlışsa çalışır.", "task": "if 5>10: pass\n___: print('Y')", "check": lambda c, o: "else" in c, "solution": "if 5>10: pass\nelse: print('Y')"}, {"msg": "'and' ile iki koşulun da doğru olması gerekir.", "task": "if 1==1 ___ 2==2: print('OK')", "check": lambda c, o: "and" in c, "solution": "if 1==1 and 2==2: print('OK')"}, {"msg": "'elif' ile ek koşullar eklenir.", "task": "if 5>10: pass\n___ 5==5: print('A')", "check": lambda c, o: "elif" in c, "solution": "if 5>10: pass\nelif 5==5: print('A')"}]},
    {"module_title": "4. Döngüler", "exercises": [{"msg": "3 kez dönen for döngüsü kur.", "task": "for i in ___(3): print('X')", "check": lambda c, o: o.count("X")==3, "solution": "for i in range(3): print('X')"}, {"msg": "while döngüsü başlat.", "task": "i=0\n___ i<1: print('Y'); i+=1", "check": lambda c, o: "while" in c, "solution": "i=0\nwhile i<1: print('Y'); i+=1"}, {"msg": "'break' döngüyü aniden bitirir.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "break" in c, "solution": "for i in range(3):\n if i==1: break\n print(i)"}, {"msg": "'continue' o adımı pas geçer.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "continue" in c, "solution": "for i in range(3):\n if i==1: continue\n print(i)"}, {"msg": "Döngü sayacını (i) ekrana yazdır.", "task": "for i in range(2): print(___)", "check": lambda c, o: "1" in o, "solution": "for i in range(2): print(i)"}]},
    {"module_title": "5. Listeler", "exercises": [{"msg": "Listeler [] içinde veri tutar. [10, 20] oluştur.", "task": "L = [___, 20]", "check": lambda c, o: "10" in c, "solution": "L=[10, 20]\nprint(L)"}, {"msg": "Listenin 0. indeksine eriş.", "task": "L=[5,6]\nprint(L[___])", "check": lambda c, o: "5" in o, "solution": "L=[5,6]\nprint(L[0])"}, {"msg": "len() fonksiyonu boyut verir.", "task": "L=[1,2]\nprint(___(L))", "check": lambda c, o: "2" in o, "solution": "L=[1,2]\nprint(len(L))"}, {"msg": "append() ile listeye 30 ekle.", "task": "L=[10]\nL.___(___)\nprint(L)", "check": lambda c, o: "30" in o, "solution": "L=[10]\nL.append(30)\nprint(L)"}, {"msg": "pop() ile son elemanı sil.", "task": "L=[1,2]\nL.___()\nprint(L)", "check": lambda c, o: "1" in o, "solution": "L=[1,2]\nL.pop()\nprint(L)"}]},
    {"module_title": "6. Fonksiyonlar ve Gelişmiş Veriler", "exercises": [
        {"msg": "**Fonksiyonlar**, tekrar kullanılabilen kod paketleridir. 'def' kelimesiyle tanımlanır.", "task": "___ f(): print('X')", "check": lambda c, o: "def" in c, "solution": "def f(): print('X')"},
        {"msg": "**Tuple (Demet)**, listeye benzer ama **değiştirilemez**. () kullanılır.", "task": "t = (___, 2)\nprint(t)", "check": lambda c, o: "1" in c, "solution": "t = (1, 2)\nprint(t)"},
        {"msg": "**Sözlükler**, 'Anahtar: Değer' çifti tutar. 'ad' anahtarına 'Pito' ata.", "task": "d = {'ad': '___'}\nprint(d['ad'])", "check": lambda c, o: "Pito" in c, "solution": "d = {'ad': 'Pito'}\nprint(d['ad'])"},
        {"msg": "keys() metodu sözlükteki tüm anahtarları verir.", "task": "d={'a':1}\nprint(d.___())", "check": lambda c, o: "keys" in c, "solution": "d={'a':1}\nprint(d.keys())"},
        {"msg": "**Set (Küme)**, benzersiz koleksiyondur. {1, 2, 1} ile oluştur.", "task": "s = {1, 2, ___}\nprint(s)", "check": lambda c, o: "1" in c, "solution": "s = {1, 2, 1}\nprint(s)"}
    ]},
    {"module_title": "7. OOP (Sınıf ve Metotlar)", "exercises": [
        {"msg": "class (küçük harf!) ile sınıf oluştur.", "task": "___ Robot: pass", "check": lambda c, o: "class" in c, "solution": "class Robot: pass"},
        {"msg": "Nesne üret.", "task": "class R: pass\np = ___()", "check": lambda c, o: "R()" in c, "solution": "class R: pass\np = R()"},
        {"msg": "Nitelik ata. Robota 'renk' niteliği olarak 'Mavi' ata.", "task": "class R: pass\np=R()\np.___ = 'Mavi'", "check": lambda c, o: "renk" in c, "solution": "class R: pass\np=R()\np.renk = 'Mavi'"},
        {"msg": "**Metotlar**, sınıf içi fonksiyonlardır. İlk parametresi her zaman **self** olmalıdır. Hadi dene: Robota **ses** adında bir metot ekle ve içine print('Bip!') yaz.", "task": "class R:\n def ___(self):\n  print('Bip!')", "check": lambda c, o: "ses" in c, "solution": "class R:\n def ses(self):\n  print('Bip!')"},
        {"msg": "Metodu çalıştırmak için **nesne_adi.metot_adi()** kullanılır.", "task": "class R: def s(self): print('X')\nr=R()\nr.___()", "check": lambda c, o: "s()" in c, "solution": "class R: def s(self): print('X')\nr=R()\nr.s()"}
    ]},
    {"module_title": "8. Dosya Yönetimi", "exercises": [
        {"msg": "open() fonksiyonu kapıyı açar. **'w' (write)** kipi yazmak içindir.", "task": "dosya = ___('n.txt', '___')", "check": lambda c, o: "open" in c and "'w'" in c, "solution": "dosya = open('n.txt', 'w')\nprint('Açıldı.')"},
        {"msg": "**write()** metodu dosyaya bilgi yazar. 'Pito' yazdır ve kapat.", "task": "f = open('t.txt', 'w'); f.___('Pito'); f.close()", "check": lambda c, o: "write" in c, "solution": "f = open('t.txt', 'w'); f.write('Pito'); f.close()"},
        {"msg": "**'r' (read)** kipi yalnızca okunabilir demektir.", "task": "f = open('t.txt', '___')", "check": lambda c, o: "'r'" in c, "solution": "f = open('t.txt', 'r'); f.close()"},
        {"msg": "**read()** metodu içeriği bütünüyle getirir.", "task": "f = open('t.txt', 'r'); print(f.___()); f.close()", "check": lambda c, o: "read" in c, "solution": "f = open('t.txt', 'w'); f.write('Pito Akademi'); f.close(); f = open('t.txt', 'r'); print(f.read()); f.close()"},
        {"msg": "Dosyayı mutlaka close() ile kapatmalısın.", "task": "f = open('t.txt', 'r'); f.___()", "check": lambda c, o: "close" in c, "solution": "f = open('t.txt', 'r'); f.close()"}
    ]}
]

# --- 6. ARA YÜZ DÜZENİ ---
col_main, col_side = st.columns([3, 1])

with col_main:
    st.markdown(f"#### 👋 {st.session_state.student_name} | ⭐ Puan: {st.session_state.total_score}")
    
    # MEZUN MODU KONTROLÜ (Balonlar buradan kaldırıldı)
    if st.session_state.db_module >= 8:
        st.success("### 🎉 Tebrikler! Eğitimi Başarıyla Tamamladın.")
        st.markdown('<div class="pito-bubble">Harikasın! Python yolculuğunu bitirdin. Aşağıdan modülleri inceleyebilir veya baştan başlayabilirsin.</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="restart-btn">', unsafe_allow_html=True)
            if st.button("🔄 Eğitimi Tekrar Al (Puan Sıfırlanır)"):
                # TÜM KOORDİNATLARI TAM SIFIRLIYORUZ
                st.session_state.db_module, st.session_state.db_exercise, st.session_state.total_score = 0, 0, 0
                st.session_state.current_module, st.session_state.current_exercise = 0, 0
                st.session_state.completed_modules = [False]*8; st.session_state.scored_exercises = set()
                force_save(); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            if st.button("🏆 Liderlik Listesinde Kal"): st.info("Liderlik listesindesin.")

        st.divider(); st.subheader("📖 Modülleri Gözden Geçir (İnceleme Modu)")

    # MODÜL BAŞLIKLARI
    mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} Modül {i+1}" for i in range(8)]
    
    # GÜNCEL GÖREVİME DÖN
    if st.session_state.current_module != st.session_state.db_module and st.session_state.db_module < 8:
        if st.button(f"🔙 Güncel Görevime Dön (Modül {st.session_state.db_module + 1})", use_container_width=True):
            st.session_state.current_module, st.session_state.current_exercise = st.session_state.db_module, st.session_state.db_exercise
            st.rerun()

    sel_mod = st.selectbox("Modül Seç:", mod_titles, index=st.session_state.current_module)
    m_idx = mod_titles.index(sel_mod)
    
    if m_idx != st.session_state.current_module:
        st.session_state.current_module = m_idx
        st.session_state.current_exercise = st.session_state.db_exercise if (m_idx == st.session_state.db_module and st.session_state.db_module < 8) else 0
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
        u_in = st.text_input("👇 Pito Terminali: Bir değer yaz ve Kontrol Et'e bas:")

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
                st.warning(f"Hatalı! Puanın düşüyor.")

    c_back, c_next = st.columns(2)
    with c_back:
        if is_locked and e_idx > 0:
            if st.button("⬅️ Önceki Adım"): st.session_state.current_exercise -= 1; st.rerun()
    with c_next:
        if st.session_state.exercise_passed or is_locked:
            if e_idx < 4:
                if st.button("➡️ Sonraki Adıma Geç"):
                    st.session_state.current_exercise += 1; st.session_state.exercise_passed = False; st.rerun()
            else:
                if st.button("🏆 Modülü Bitir"):
                    if st.session_state.current_module < 7:
                        st.session_state.current_module += 1; st.session_state.current_exercise = 0; st.rerun()
                    else:
                        # SADECE 8. MODÜL SONUNDA BALONLAR UÇSUN
                        st.balloons(); st.rerun()

with col_side:
    st.markdown(f"### 🏆 Sınıf Liderleri")
    df_lb = get_db()
    df_class = df_lb[df_lb["Sınıf"] == st.session_state.student_class]
    if not df_class.empty:
        df_sort = df_class.sort_values(by="Puan", ascending=False).drop_duplicates(subset=["Okul No"]).head(10)
        for i, (_, r) in enumerate(df_sort.iterrows()):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "⭐"
            st.markdown(f'<div class="leaderboard-card"><b>{medal} {r["Öğrencinin Adı"]}</b><br>{r["Puan"]} Puan</div>', unsafe_allow_html=True)