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
        border-radius: 15px; padding: 20px; margin-bottom: 20px; color: #1e1e1e;
        font-weight: 500; font-size: 1.05rem; box-shadow: 4px 4px 15px rgba(0,0,0,0.05);
        line-height: 1.6;
    }
    .pito-bubble:after {
        content: ''; position: absolute; bottom: -20px; left: 40px;
        border-width: 20px 20px 0; border-style: solid; border-color: #3a7bd5 transparent;
    }
    .solution-guide {
        background-color: #fef2f2 !important; border: 2px solid #ef4444 !important;
        border-radius: 12px; padding: 20px; margin: 15px 0; color: #1e1e1e !important;
    }
    .solution-header { color: #ef4444; font-weight: bold; font-size: 1.1rem; margin-bottom: 8px; }
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
        rank = RUTBELER[sum(st.session_state.completed_modules)]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, int(st.session_state.total_score), rank, prog, int(st.session_state.db_module), int(st.session_state.db_exercise), datetime.now().strftime("%H:%M:%S")]], columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

# --- 3. SESSION STATE ---
if 'is_logged_in' not in st.session_state:
    for k, v in {'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8, 
                 'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0, 
                 'scored_exercises': set(), 'db_module': 0, 'db_exercise': 0, 'is_logged_in': False, 
                 'current_potential_score': 20, 'celebrated': False, 'rejected_user': False, 
                 'fail_count': 0, 'feedback_msg': "", 'last_output': ""}.items():
        st.session_state[k] = v

PITO_IMG = "assets/pito.png"

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.is_logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba! Ben <b>Pito</b>. Python dünyasına giriş yapmaya hazır mısın? Sana kodlamanın temelini adım adım öğreteceğim.</div>', unsafe_allow_html=True)
        st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/180/robot-viewer.png", width=180)
        in_no = st.text_input("Okul Numaran (Sadece Rakam):", key="login_field").strip()
        if in_no and in_no.isdigit():
            df = get_db()
            user_data = df[df["Okul No"] == in_no]
            if not user_data.empty:
                row = user_data.iloc[0]
                st.info(f"🔍 Hoş geldin **{row['Öğrencinin Adı']}**.")
                if st.button("✅ Maceraya Başla"):
                    m_v, e_v = int(row['Mevcut Modül']), int(row['Mevcut Egzersiz'])
                    st.session_state.update({'student_no': in_no, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': m_v, 'db_exercise': e_v, 'current_module': min(m_v, 7), 'current_exercise': e_v, 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True})
                    st.rerun()
            else:
                in_name = st.text_input("Adın Soyadın:")
                in_class = st.selectbox("Sınıfın:", SINIFLAR)
                if st.button("Kayıt Ol ve Başla ✨") and in_name:
                    st.session_state.update({'student_no': in_no, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True})
                    force_save(); st.rerun()
    st.stop()

# --- 5. MÜFREDAT VE ÇÖZÜMLER ---
training_data = [
    {"module_title": "1. Merhaba Python: Giriş ve Çıktı", "exercises": [
        {"msg": "Python'da bilgisayarın bizimle konuşmasını sağlayan temel araç `print()` fonksiyonudur. İlk görevin; ekrana tam olarak **'Merhaba Pito'** yazdırmak.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')", "has_output": True},
        {"msg": "Sayılar metinlerden farklıdır; tırnak işaretine ihtiyaç duymazlar. Hadi, ekrana sadece **100** sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o, "solution": "print(100)", "has_output": True},
        {"msg": "Pito'nun puanını göstermek için önce **'Puan:'** metnini, yanına ise **100** sayısını ekle.", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o, "solution": "print('Puan:', 100)", "has_output": True},
        {"msg": "Kod yazarken bazen notlar bırakırız. Bir `#` kullanarak bu satırı yorum satırına dönüştür.", "task": "___ bu bir yorumdur", "check": lambda c, o: "#" in c, "solution": "# bu bir yorumdur", "has_output": False},
        {"msg": "Senden ricam; 'Üst' yazısından sonra alt satıra geçip 'Alt' yazısını bastırman.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o, "solution": "print('Üst\\nAlt')", "has_output": True}
    ]},
    {"module_title": "2. Bilgiyi Saklamak: Değişkenler ve input()", "exercises": [
        {"msg": "Değişkenler, verileri hafızada tutan kutulardır. **yas** kutusuna **15** değerini ata ve ekrana yazdır.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o, "solution": "yas = 15\nprint(yas)", "has_output": True},
        {"msg": "**isim** adlı değişkene **'Pito'** değerini ata ve sonucu gör.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o, "solution": "isim = 'Pito'\nprint(isim)", "has_output": True},
        {"msg": "`input()` ile kullanıcıdan bir giriş iste. Parantez içine **'Adın: '** yaz.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c, "solution": "ad = input('Adın: ')\nprint(ad)", "has_output": True},
        {"msg": "Değişkeni metne çeviren `str()` fonksiyonunu kullanarak **s**'yi yazdır.", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c, "solution": "s = 10\nprint(str(s))", "has_output": True},
        {"msg": "Kullanıcıdan bir sayı iste, onu tam sayıya çevir ve 1 ekleyip yazdır.", "task": "n = ___(___('S: '))\nprint(n + 1)", "check": lambda c, o: "int" in c and "11" in o, "solution": "n = int(input('10'))\nprint(n+1)", "has_output": True}
    ]},
    {"module_title": "3. Karar Verme: İf ve Karşılaştırmalar", "exercises": [
        {"msg": "İki değerin eşitliğini kontrol etmek için `==` kullanırız. 10'un 10'a eşitliğini kontrol et.", "task": "if 10 ___ 10: print('Eşit!')", "check": lambda c, o: "==" in c, "solution": "if 10 == 10: print('Eşit!')", "has_output": True},
        {"msg": "Şart gerçekleşmediğinde `else:` bloğu çalışır. 5, 10'dan büyük değilse 'Hayır' yazdırılmasını sağla.", "task": "if 5>10: pass\n___: print('Hayır')", "check": lambda c, o: "else" in c, "solution": "if 5 > 10: pass\nelse: print('Hayır')", "has_output": True},
        {"msg": "Büyük veya eşittir kontrolü için `>=` kullanılır. Boşluğu doldur.", "task": "if 5 ___ 5: print('Tamam!')", "check": lambda c, o: ">=" in c, "solution": "if 5 >= 5: print('Tamam!')", "has_output": True},
        {"msg": "İki şartın da doğru olması için `and` bağlacını kullanırız. 1==1 ve 2==2 durumuna bak.", "task": "if 1==1 ___ 2==2: print('Mükemmel')", "check": lambda c, o: "and" in c, "solution": "if 1==1 and 2==2: print('Mükemmel')", "has_output": True},
        {"msg": "Birden fazla şartı sıralamak için `elif` kullanılır. 5'in 5'e eşitliğini kontrol eden bloğu yaz.", "task": "if 5>10: pass\n___ 5==5: print('Bulundu')", "check": lambda c, o: "elif" in c, "solution": "if 5 > 10: pass\nelif 5 == 5: print('Bulundu')", "has_output": True}
    ]},
    {"module_title": "4. Sürekli Tekrar: For ve While Döngüleri", "exercises": [
        {"msg": "Ekrana 3 kez 'Pito' yazdırmak için `range()` aralığını belirle.", "task": "for i in ___(3): print('Pito')", "check": lambda c, o: o.count("Pito")==3, "solution": "for i in range(3): print('Pito')", "has_output": True},
        {"msg": "`while` döngüsü için i, 1'den küçük olduğu sürece çalışacak komutu yaz.", "task": "i=0\n___ i<1: print('Dönüyor'); i+=1", "check": lambda c, o: "while" in c, "solution": "i=0\nwhile i<1: print('Dönüyor'); i+=1", "has_output": True},
        {"msg": "Şart sağlandığında döngüden aniden çıkmak için `break` kullan.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "break" in c, "solution": "for i in range(3):\n    if i == 1: break\n    print(i)", "has_output": True},
        {"msg": "Mevcut adımı atlayıp döngü başına dönmek için `continue` kullan.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "continue" in c, "solution": "for i in range(3):\n    if i == 1: continue\n    print(i)", "has_output": True},
        {"msg": "Döngü sayacını (`i`) ekrana bastıran kodu tamamla.", "task": "for i in range(2): print(___)", "check": lambda c, o: "1" in o, "solution": "for i in range(2): print(i)", "has_output": True}
    ]},
    {"module_title": "5. Gruplama ve Listeler", "exercises": [
        {"msg": "Listeye eksik olan **10** sayısını ekle.", "task": "L = [___, 20]", "check": lambda c, o: "10" in c, "solution": "L = [10, 20]", "has_output": False},
        {"msg": "İlk elemana (indeks 0) ulaşmak için boşluğu doldur.", "task": "L=[5,6]\nprint(L[___])", "check": lambda c, o: "5" in o, "solution": "L = [5, 6]\nprint(L[0])", "has_output": True},
        {"msg": "Listenin boyutunu `len()` fonksiyonuyla öğren ve yazdır.", "task": "L=[1,2]\nprint(___(L))", "check": lambda c, o: "2" in o, "solution": "L = [1, 2]\nprint(len(L))", "has_output": True},
        {"msg": "Mevcut bir listeye `.append()` ile sonuna **30** değerini ekle.", "task": "L=[10]\nL.___(___)\nprint(L)", "check": lambda c, o: "30" in o, "solution": "L = [10]\nL.append(30)\nprint(L)", "has_output": True},
        {"msg": "Listenin son elemanını `.pop()` metoduyla çıkar.", "task": "L=[1,2]\nL.___()\nprint(L)", "check": lambda c, o: "1" in o, "solution": "L = [1, 2]\nL.pop()\nprint(L)", "has_output": True}
    ]},
    {"module_title": "6. Fonksiyonlar ve Veri Yapıları", "exercises": [
        {"msg": "Bir fonksiyonu `def` anahtarı ile tanımlamaya başla.", "task": "___ selam(): print('Merhaba')", "check": lambda c, o: "def" in c, "solution": "def selam(): print('Merhaba')", "has_output": False},
        {"msg": "Normal parantez kullanarak (1, 2) şeklinde bir tuple oluştur.", "task": "t = (___, 2)\nprint(t)", "check": lambda c, o: "1" in c, "solution": "t = (1, 2)\nprint(t)", "has_output": True},
        {"msg": "Sözlüğe 'ad' anahtarı için **'Pito'** değerini ata.", "task": "d = {'ad': '___'}\nprint(d['ad'])", "check": lambda c, o: "Pito" in o, "solution": "d = {'ad': 'Pito'}\nprint(d['ad'])", "has_output": True},
        {"msg": "Sözlük anahtarlarını listelemek için `.keys()` kullan.", "task": "d={'a':1}\nprint(d.___())", "check": lambda c, o: "keys" in c, "solution": "d = {'a': 1}\nprint(d.keys())", "has_output": True},
        {"msg": "Süslü parantez ile benzersiz elemanlı bir küme (set) oluştur.", "task": "s = {1, 2, ___}\nprint(s)", "check": lambda c, o: "1" in c, "solution": "s = {1, 2, 1}\nprint(s)", "has_output": True}
    ]},
    {"module_title": "7. OOP: Nesne Tabanlı Programlama", "exercises": [
        {"msg": "`class` anahtar kelimesiyle yeni bir 'Robot' kalıbı tanımla.", "task": "___ Robot: pass", "check": lambda c, o: "class" in c, "solution": "class Robot: pass", "has_output": False},
        {"msg": "Robot sınıfından yeni bir nesne üret.", "task": "class R: pass\np = ___()", "check": lambda c, o: "R()" in c, "solution": "p = R()", "has_output": False},
        {"msg": "p nesnesinin **renk** özelliğine 'Mavi' değerini ata.", "task": "class R: pass\np=R()\np.___ = 'Mavi'\nprint(p.renk)", "check": lambda c, o: "renk" in c, "solution": "class R: pass\np = R()\np.renk = 'Mavi'\nprint(p.renk)", "has_output": True},
        {"msg": "Sınıf içine bir **ses** metodu tanımlarken `self` kullanmayı unutma.", "task": "class R:\n def ___(self):\n  print('Bip!')", "check": lambda c, o: "ses" in c, "solution": "class R:\n    def ses(self): print('Bip!')", "has_output": False},
        {"msg": "Tanımladığın bir metodu nesne üzerinden çağır.", "task": "class R:\n def s(self): print('X')\nr=R()\nr.___()", "check": lambda c, o: "s()" in c, "solution": "class R:\n    def s(self): print('X')\nr = R()\nr.s()", "has_output": True}
    ]},
    {"module_title": "8. Kalıcılık: Dosya Yönetimi", "exercises": [
        {"msg": "`open()` fonksiyonu ve yazma modu olan **'w'** kipiyle dosya aç.", "task": "dosya = ___('n.txt', '___')", "check": lambda c, o: "open" in c and "w" in c, "solution": "dosya = open('n.txt', 'w')", "has_output": False},
        {"msg": "Açılmış dosyaya `.write()` ile 'Pito' yazısını gönder.", "task": "f = open('t.txt', 'w'); f.___('Pito'); f.close()", "check": lambda c, o: "write" in c, "solution": "f = open('t.txt', 'w')\nf.write('Pito')\nf.close()", "has_output": False},
        {"msg": "Dosyayı okuma modu olan **'r'** kipiyle aç.", "task": "f = open('t.txt', '___')", "check": lambda c, o: "r" in c, "solution": "f = open('t.txt', 'r')", "has_output": False},
        {"msg": "Dosya içeriğini metin olarak getiren `.read()` kodunu yaz.", "task": "f = open('t.txt', 'r')\nprint(f.___())\nf.close()", "check": lambda c, o: "read" in c, "solution": "f = open('t.txt', 'r')\nprint(f.read())\nf.close()", "has_output": True},
        {"msg": "Dosyayı kapatan komutu tamamla.", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o: "close" in c, "solution": "f = open('t.txt', 'r')\nf.close()", "has_output": False}
    ]}
]

# --- 6. ARA YÜZ DÜZENİ ---
col_main, col_side = st.columns([3, 1])
m_idx = min(st.session_state.current_module, 7)
if st.session_state.current_exercise >= len(training_data[m_idx]["exercises"]):
    st.session_state.current_exercise = 0
e_idx = st.session_state.current_exercise

with col_main:
    rank_idx = sum(st.session_state.completed_modules)
    st.markdown(f"#### 👋 {RUTBELER[min(rank_idx, 8)]} {st.session_state.student_name} | ⭐ Puan: {int(st.session_state.total_score)}")
    
    if st.session_state.db_module >= 8:
        if not st.session_state.celebrated: st.balloons(); st.session_state.celebrated = True
        st.success("🎉 Tebrikler! Tüm macerayı başarıyla tamamladın.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Eğitimi Tekrar Al"):
                st.session_state.update({'db_module':0,'db_exercise':0,'total_score':0,'current_module':0,'current_exercise':0,'completed_modules':[False]*8,'scored_exercises':set(),'celebrated':False,'fail_count':0,'feedback_msg':"", 'last_output':""})
                force_save(); st.rerun()
        with c2:
            if st.button("🏆 Listede Kal"): st.info("Başarın kaydedildi!")
        st.divider()

    mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} Modül {i+1}" for i in range(8)]
    sel_mod = st.selectbox("Modül Seç:", mod_titles, index=m_idx)
    new_m_idx = mod_titles.index(sel_mod)
    if new_m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': new_m_idx, 'current_exercise': 0, 'fail_count': 0, 'exercise_passed': False, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
        st.rerun()

    st.divider()
    curr_ex = training_data[st.session_state.current_module]["exercises"][e_idx]
    is_locked = (st.session_state.current_module < st.session_state.db_module) or (st.session_state.db_module >= 8)

    c_img, c_msg = st.columns([1, 4])
    with c_img: st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/200/robot-viewer.png", width=140)
    with c_msg:
        st.info(f"##### 🗣️ Pito:\n{curr_ex['msg']}")
        st.caption(f"Adım: {e_idx + 1}/5 | " + ("🔒 İnceleme" if is_locked else f"🎁 Puan: {st.session_state.current_potential_score} | ❌ Hata: {st.session_state.fail_count}/4"))

    # --- KRİTİK: ÇÖZÜM REHBERİ (3. HATADA GÖRÜNÜR) ---
    if st.session_state.fail_count == 3 and not is_locked:
        st.markdown(f"""<div class="solution-guide"><div class="solution-header">💡 Pito'dan Yardım: Çözüm Yolu</div><b>Doğru Kod Yapısı:</b></div>""", unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")
        st.warning("⚠️ Çözüm açıldı! Şimdi son bir deneme hakkın var.")
    elif st.session_state.fail_count >= 4 and not is_locked:
        st.error("❌ Son hakkında da olmadı bu egzersizden puan alamadın şimdi sonraki adıma ilerle.")

    def run_pito_code(c, user_input="Pito", mod=0, step=0):
        if "___" in c: return "⚠️ Boşluk Hatası"
        if mod == 0 and step == 3: return "# bu bir yorumdur"
        old_stdout, new_stdout = sys.stdout, StringIO()
        sys.stdout = new_stdout
        try:
            mock_globals = {"input": lambda p: str(user_input), "print": print, "int": int, "str": str, "len": len, "open": open, "range": range, "s": 10, "L": [10], "d":{'ad':'Pito'}, "t":(1,2)}
            exec(c, mock_globals)
            sys.stdout = old_stdout
            return new_stdout.getvalue()
        except Exception as e:
            sys.stdout = old_stdout
            return f"❌ Python Hatası: {e}"

    if is_locked:
        st.markdown(f'<div class="solution-guide"><div class="solution-header">✅ Pito Çözüm Rehberi</div>{curr_ex["msg"]}</div>', unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")
        if curr_ex.get("has_output", False):
            st.markdown("<b>Muhtemel Çıktı:</b>", unsafe_allow_html=True)
            if st.session_state.current_module == 0 and e_idx == 3: st.code("# bu bir yorumdur")
            elif st.session_state.current_module == 1 and e_idx == 3: st.code("10")
            elif st.session_state.current_module == 1 and e_idx == 4: st.code("11")
            else: st.code(run_pito_code(curr_ex['solution'], "10", st.session_state.current_module, e_idx))
    else:
        # --- KOMUT PANELİ (4. HATADA GİZLENİR, 3. HATADA PANEL VE ÇÖZÜM BİRLİKTE GÖRÜNÜR) ---
        if st.session_state.fail_count < 4:
            code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=200, key=f"ace_{st.session_state.current_module}_{e_idx}", auto_update=True)
            
            # KRİTİK: ÇIKTIYI KOD BLOĞUNUN HEMEN ALTINDA GÖSTER
            if st.session_state.exercise_passed and st.session_state.last_output:
                st.markdown("**Kod Çıktısı:**")
                st.code(st.session_state.last_output)
            
            u_in = st.text_input("Giriş yap:", key=f"term_{st.session_state.current_module}_{e_idx}") if "input(" in code else ""
            
            if st.button("🔍 Kontrol Et", use_container_width=True):
                if "___" in code:
                    st.session_state.feedback_msg = "⚠️ Lütfen önce kodun içindeki '___' alanlarını doldur!"
                    st.rerun()
                else:
                    out = run_pito_code(code, u_in or "10", st.session_state.current_module, e_idx)
                    if out.startswith("❌") or not curr_ex['check'](code, out):
                        st.session_state.fail_count += 1
                        st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                        if st.session_state.fail_count >= 4:
                            st.session_state.exercise_passed = True
                            st.session_state.feedback_msg = ""
                        else:
                            st.session_state.feedback_msg = f"❌ bu {st.session_state.fail_count}. hatan"
                        st.rerun()
                    else:
                        st.session_state.feedback_msg = "✅ Tebrikler! Görev başarıyla tamamlandı."
                        st.session_state.last_output = out
                        st.session_state.exercise_passed = True
                        if f"{st.session_state.current_module}_{e_idx}" not in st.session_state.scored_exercises:
                            st.session_state.total_score += st.session_state.current_potential_score
                            st.session_state.scored_exercises.add(f"{st.session_state.current_module}_{e_idx}")
                            if st.session_state.db_exercise < len(training_data[st.session_state.current_module]["exercises"]) - 1:
                                st.session_state.db_exercise += 1
                            else:
                                st.session_state.db_module += 1; st.session_state.db_exercise = 0; st.session_state.completed_modules[st.session_state.current_module] = True
                            force_save()
                        st.rerun()

            if st.session_state.feedback_msg:
                if "Tebrikler" in st.session_state.feedback_msg: st.success(st.session_state.feedback_msg)
                elif "Lütfen" in st.session_state.feedback_msg: st.warning(st.session_state.feedback_msg)
                else: st.error(st.session_state.feedback_msg)

    c_b, c_n = st.columns(2)
    with c_b:
        if is_locked and e_idx > 0:
            if st.button("⬅️ Önceki"): st.session_state.current_exercise -= 1; st.rerun()
    with c_n:
        if st.session_state.exercise_passed or is_locked:
            if e_idx < len(training_data[st.session_state.current_module]["exercises"]) - 1:
                if st.button("➡️ Sonraki"): 
                    st.session_state.update({'current_exercise': e_idx + 1, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
                    st.rerun()
            elif st.session_state.current_module < 7:
                if st.button("🏆 Modülü Bitir"): 
                    st.session_state.update({'current_module': st.session_state.current_module + 1, 'current_exercise': 0, 'fail_count': 0, 'exercise_passed': False, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
                    st.rerun()

with col_side:
    st.markdown("### 🏆 Liderlik Tablosu")
    df_lb = get_db()
    tab_class, tab_school = st.tabs(["👥 Sınıf", "🏫 Okul"])
    for t, d in zip([tab_class, tab_school], [df_lb[df_lb["Sınıf"] == st.session_state.student_class], df_lb]):
        with t:
            if not d.empty:
                for _, r in d.sort_values(by="Puan", ascending=False).head(10).iterrows():
                    st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)