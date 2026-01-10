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
        font-weight: 500; font-size: 1.1rem; box-shadow: 4px 4px 15px rgba(0,0,0,0.05);
    }
    .pito-bubble:after {
        content: ''; position: absolute; bottom: -20px; left: 40px;
        border-width: 20px 20px 0; border-style: solid; border-color: #3a7bd5 transparent;
    }
    .solution-guide {
        background-color: #f8fafc !important; border: 2px solid #3a7bd5 !important;
        border-radius: 12px; padding: 20px; margin: 15px 0; color: #1e1e1e !important;
    }
    .solution-header { color: #3a7bd5; font-weight: bold; font-size: 1.1rem; margin-bottom: 8px; }
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

def get_db(use_cache=True):
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=60 if use_cache else 0)
        df["Okul No"] = df["Okul No"].astype(str).str.split('.').str[0].str.strip()
        df["Puan"] = pd.to_numeric(df["Puan"], errors='coerce').fillna(0).astype(int)
        return df.dropna(subset=["Okul No"])
    except: return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])

def force_save():
    try:
        no = str(st.session_state.student_no).strip()
        df_all = get_db(use_cache=False)
        df_clean = df_all[df_all["Okul No"] != no]
        prog = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = RUTBELER[sum(st.session_state.completed_modules)]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, int(st.session_state.total_score), rank, prog, st.session_state.db_module, st.session_state.db_exercise, datetime.now().strftime("%H:%M:%S")]], columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

# --- 3. SESSION STATE ---
if 'is_logged_in' not in st.session_state:
    for k, v in {'student_name': "", 'student_no': "", 'student_class': "", 'completed_modules': [False]*8, 'current_module': 0, 'current_exercise': 0, 'exercise_passed': False, 'total_score': 0, 'scored_exercises': set(), 'db_module': 0, 'db_exercise': 0, 'is_logged_in': False, 'current_potential_score': 20, 'celebrated': False, 'rejected_user': False}.items():
        st.session_state[k] = v

PITO_IMG = "assets/pito.png"

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.is_logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba! Ben <b>Pito</b>. Python Dünyası\'na hoş geldin.</div>', unsafe_allow_html=True)
        st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/180/robot-viewer.png", width=180)
        if st.session_state.rejected_user: st.warning("⚠️ Lütfen kendi okul numaranı gir!")
        in_no = st.text_input("Okul Numaran (Sadece Rakam):", key="login_field").strip()
        if in_no and in_no.isdigit():
            df = get_db(use_cache=False)
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

# --- 5. EKSİKSİZ 8 MODÜLLÜK MÜFREDAT ---
training_data = [
    {"module_title": "1. Giriş ve Çıktı", "exercises": [
        {"msg": "Ekrana **'Merhaba Pito'** yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')"},
        {"msg": "Ekrana sadece **100** sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o, "solution": "print(100)"},
        {"msg": "**'Puan:'** metni ile **100** sayısını yan yana yazdır.", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o, "solution": "print('Puan:', 100)"},
        {"msg": "Bir **#** kullanarak yorum satırı oluştur.", "task": "___ bu bir yorumdur", "check": lambda c, o: "#" in c, "solution": "# bu bir yorumdur"},
        {"msg": "Alt alta **'Üst'** ve **'Alt'** yazdır.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o, "solution": "print('Üst\\nAlt')"}
    ]},
    {"module_title": "2. Değişkenler ve input()", "exercises": [
        {"msg": "**yas** değişkenine 15 ata.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o, "solution": "yas = 15"},
        {"msg": "**isim** değişkenine 'Pito' ata.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o, "solution": "isim = 'Pito'"},
        {"msg": "**input()** ile isim al.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c, "solution": "ad = input('Adın: ')"},
        {"msg": "Sayıyı metne çevir.", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c, "solution": "str(s)"},
        {"msg": "Girdiyi tam sayıya çevirip 1 ekle.", "task": "n = ___(___('S: '))\nprint(n + 1)", "check": lambda c, o: "int" in c and "11" in o, "solution": "int(input('10'))"}
    ]},
    {"module_title": "3. Karar Yapıları", "exercises": [
        {"msg": "Eşitlik için **==** kullan.", "task": "if 10 ___ 10: print('X')", "check": lambda c, o: "==" in c, "solution": "if 10 == 10: print('X')"},
        {"msg": "Şart yanlışsa **else:** çalıştır.", "task": "if 5>10: pass\n___: print('Y')", "check": lambda c, o: "else" in c, "solution": "else"},
        {"msg": "Büyük veya eşittir için **>=** kullan.", "task": "if 5 ___ 5: print('Z')", "check": lambda c, o: ">=" in c, "solution": ">="},
        {"msg": "**and** bağlacını kullan.", "task": "if 1==1 ___ 2==2: print('OK')", "check": lambda c, o: "and" in c, "solution": "and"},
        {"msg": "**elif** ile alternatif şart ekle.", "task": "if 5>10: pass\n___ 5==5: print('A')", "check": lambda c, o: "elif" in c, "solution": "elif"}
    ]},
    {"module_title": "4. Döngüler", "exercises": [
        {"msg": "3 tur dönmek için **range(3)** kullan.", "task": "for i in ___(3): print('X')", "check": lambda c, o: o.count("X")==3, "solution": "range(3)"},
        {"msg": "**while** ile döngü kur.", "task": "i=0\n___ i<1: print('Y'); i+=1", "check": lambda c, o: "while" in c, "solution": "while"},
        {"msg": "**break** ile bitir.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "break" in c, "solution": "break"},
        {"msg": "**continue** ile atla.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "continue" in c, "solution": "continue"},
        {"msg": "Sayacı (**i**) yazdır.", "task": "for i in range(2): print(___)", "check": lambda c, o: "1" in o, "solution": "i"}
    ]},
    {"module_title": "5. Listeler", "exercises": [
        {"msg": "Liste oluştur.", "task": "L = [___, 20]", "check": lambda c, o: "10" in c, "solution": "L=[10, 20]"},
        {"msg": "İndeks 0 ile ilk elemana eriş.", "task": "L=[5,6]\nprint(L[___])", "check": lambda c, o: "5" in o, "solution": "0"},
        {"msg": "**len()** ile boyut bul.", "task": "L=[1,2]\nprint(___(L))", "check": lambda c, o: "2" in o, "solution": "len"},
        {"msg": "**append()** ile 30 ekle.", "task": "L=[10]\nL.___(___)\nprint(L)", "check": lambda c, o: "30" in o, "solution": "append"},
        {"msg": "**pop()** ile sil.", "task": "L=[1,2]\nL.___()\nprint(L)", "check": lambda c, o: "1" in o, "solution": "pop"}
    ]},
    {"module_title": "6. Fonksiyonlar ve Veriler", "exercises": [
        {"msg": "**def** ile fonksiyon tanımla.", "task": "___ f(): print('X')", "check": lambda c, o: "def" in c, "solution": "def f(): print('X')"},
        {"msg": "**Tuple** (1, 2) oluştur.", "task": "t = (___, 2)\nprint(t)", "check": lambda c, o: "1" in c, "solution": "1"},
        {"msg": "Sözlüğe 'ad': 'Pito' ata.", "task": "d = {'ad': '___'}\nprint(d['ad'])", "check": lambda c, o: "Pito" in o, "solution": "Pito"},
        {"msg": "**keys()** anahtarları getirir.", "task": "d={'a':1}\nprint(d.___())", "check": lambda c, o: "keys" in c, "solution": "keys"},
        {"msg": "**Set** ile küme oluştur.", "task": "s = {1, 2, ___}\nprint(s)", "check": lambda c, o: "1" in c, "solution": "1"}
    ]},
    {"module_title": "7. OOP", "exercises": [
        {"msg": "**class** ile sınıf oluştur.", "task": "___ Robot: pass", "check": lambda c, o: "class" in c, "solution": "class Robot: pass"},
        {"msg": "**Robot()** ile nesne üret.", "task": "class R: pass\np = ___()", "check": lambda c, o: "R()" in c, "solution": "R()"},
        {"msg": "Nitelik ata: `p.renk`.", "task": "class R: pass\np=R()\np.___ = 'Mavi'\nprint(p.renk)", "check": lambda c, o: "renk" in c, "solution": "renk"},
        {"msg": "Metot tanımla (self).", "task": "class R:\n def ___(self):\n  print('Bip!')", "check": lambda c, o: "ses" in c, "solution": "ses"},
        {"msg": "Metodu çağır.", "task": "class R:\n def s(self): print('X')\nr=R()\nr.___()", "check": lambda c, o: "s()" in c, "solution": "s()"}
    ]},
    {"module_title": "8. Dosya Yönetimi", "exercises": [
        {"msg": "**open()** ve **'w'** kipiyle aç.", "task": "dosya = ___('n.txt', '___')", "check": lambda c, o: "open" in c and "w" in c, "solution": "open('n.txt', 'w')"},
        {"msg": "**write()** dosyaya yazı yazar.", "task": "f = open('t.txt', 'w'); f.___('Pito'); f.close()", "check": lambda c, o: "write" in c, "solution": "write"},
        {"msg": "**'r'** kipiyle oku.", "task": "f = open('t.txt', '___')", "check": lambda c, o: "r" in c, "solution": "r"},
        {"msg": "**read()** içeriği getir.", "task": "f = open('t.txt', 'r')\nprint(f.___())\nf.close()", "check": lambda c, o: "read" in c, "solution": "read"},
        {"msg": "**close()** hafızayı boşaltır.", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o: "close" in c, "solution": "close"}
    ]}
]

# --- 6. ARA YÜZ DÜZENİ ---
col_main, col_side = st.columns([3, 1])
m_idx = min(st.session_state.current_module, len(training_data)-1)
if st.session_state.current_exercise >= len(training_data[m_idx]["exercises"]): st.session_state.current_exercise = 0

with col_main:
    rank_idx = sum(st.session_state.completed_modules)
    st.markdown(f"#### 👋 {RUTBELER[min(rank_idx, 8)]} {st.session_state.student_name} | ⭐ Puan: {int(st.session_state.total_score)}")
    if st.session_state.db_module >= 8:
        if not st.session_state.celebrated: st.balloons(); st.session_state.celebrated = True
        st.success("🎉 Tebrikler! Eğitimi Bitirdin."); st.divider()

    mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} Modül {i+1}" for i in range(8)]
    # ValueError Fix: İndeks eşleştirme yöntemi kullanıldı
    sel_mod = st.selectbox("Modül Seç:", mod_titles, index=m_idx)
    new_m_idx = mod_titles.index(sel_mod)
    if new_m_idx != st.session_state.current_module:
        st.session_state.current_module, st.session_state.current_exercise = new_m_idx, 0; st.rerun()

    st.divider()
    e_idx = st.session_state.current_exercise
    curr_ex = training_data[st.session_state.current_module]["exercises"][e_idx]
    is_locked = (st.session_state.current_module < st.session_state.db_module) or (st.session_state.db_module >= 8)

    c_img, c_msg = st.columns([1, 4])
    with c_img: st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/200/robot-viewer.png", width=140)
    with c_msg:
        st.info(f"##### 🗣️ Pito:\n{curr_ex['msg']}")
        st.caption(f"Adım: {e_idx + 1}/5 " + ("🔒 İnceleme" if is_locked else f"🎁 Puan: {st.session_state.current_potential_score}"))

    code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=200, readonly=is_locked, key=f"ace_{st.session_state.current_module}_{e_idx}", auto_update=True)

    def run_pito_code(c, user_input="Pito", mod=0, step=0):
        # KRİTİK: BOŞLUK KONTROLÜ
        if "___" in c: return "⚠️ Boşluk Hatası: Lütfen kodun içindeki '___' alanlarını doldur!"
        # MODÜL 1 ADIM 4 ÖZEL ÇIKTI
        if mod == 0 and step == 3: return "# bu bir yorumdur"
        
        old_stdout, new_stdout = sys.stdout, StringIO()
        sys.stdout = new_stdout
        try:
            # Akıllı Mock Girdisi
            mock_val = "10" if "int(" in c else str(user_input)
            exec(c, {"input": lambda p: mock_val, "print": print, "int": int, "str": str, "len": len, "open": open, "range": range})
            sys.stdout = old_stdout
            return new_stdout.getvalue()
        except Exception as e:
            sys.stdout = old_stdout
            return f"❌ Python Hatası: {e}"

    if is_locked:
        st.markdown(f'<div class="solution-guide"><div class="solution-header">✅ Pito Çözüm Rehberi</div><b>Yönerge:</b> {curr_ex["msg"]}</div>', unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")
        sol_out = run_pito_code(curr_ex['solution'], "10", st.session_state.current_module, e_idx)
        st.markdown("<b>Muhtemel Çıktı:</b>", unsafe_allow_html=True)
        # MODÜL 2 ADIM 4 & 5 ÖZEL ÇIKTILAR
        if st.session_state.current_module == 1 and e_idx == 3: st.code("10")
        elif st.session_state.current_module == 1 and e_idx == 4: st.code("11")
        else: st.code(sol_out if sol_out else "Kod çalıştı.")
    else:
        u_in = st.text_input("Giriş yap:", key=f"term_{st.session_state.current_module}_{e_idx}") if "input(" in code else ""
        if st.button("🔍 Kontrol Et", use_container_width=True):
            out = run_pito_code(code, u_in or "10", st.session_state.current_module, e_idx)
            if out.startswith("⚠️") or out.startswith("❌"): st.error(out)
            else:
                # KRİTİK: MANTIKSAL DOĞRULAMA
                if curr_ex['check'](code, out):
                    st.success("Tebrikler! Görev başarıyla tamamlandı. ✅"); st.code(out)
                    st.session_state.exercise_passed = True
                    if f"{st.session_state.current_module}_{e_idx}" not in st.session_state.scored_exercises:
                        st.session_state.total_score += st.session_state.current_potential_score
                        st.session_state.scored_exercises.add(f"{st.session_state.current_module}_{e_idx}")
                        if st.session_state.db_exercise < 4: st.session_state.db_exercise += 1
                        else: st.session_state.db_module += 1; st.session_state.db_exercise = 0; st.session_state.completed_modules[st.session_state.current_module] = True
                        force_save()
                else:
                    st.warning("⚠️ Görev Tamamlanmadı: Kodun teknik olarak çalıştı ama sonuç Pito'nun istediği gibi değil. Yönergeyi tekrar oku!")
                    st.code(out if out else "[Çıktı Yok]")

    c_b, c_n = st.columns(2)
    with c_b:
        if is_locked and e_idx > 0:
            if st.button("⬅️ Önceki"): st.session_state.current_exercise -= 1; st.rerun()
    with c_n:
        if st.session_state.exercise_passed or is_locked:
            if e_idx < 4:
                if st.button("➡️ Sonraki"): st.session_state.current_exercise += 1; st.session_state.exercise_passed = False; st.rerun()
            elif st.session_state.current_module < 7:
                if st.button("🏆 Modülü Bitir"):
                    st.session_state.current_module += 1; st.session_state.current_exercise = 0; st.rerun()

with col_side:
    st.markdown("### 🏆 Liderlik Tablosu")
    df_lb = get_db()
    tab_class, tab_school = st.tabs(["👥 Sınıfım", "🏫 Okul"])
    for t, d in zip([tab_class, tab_school], [df_lb[df_lb["Sınıf"] == st.session_state.student_class], df_lb]):
        with t:
            if not d.empty:
                for i, (_, r) in enumerate(d.sort_values(by="Puan", ascending=False).head(10).iterrows()):
                    st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)