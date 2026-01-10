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
                 'current_potential_score': 20, 'fail_count': 0, 'feedback_msg': "", 'last_output': ""}.items():
        st.session_state[k] = v

PITO_IMG = "assets/pito.png"

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.is_logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba! Ben <b>Pito</b>. Python dünyasına hoş geldin. Hazırsan hemen başlayalım!</div>', unsafe_allow_html=True)
        st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/180/robot-viewer.png", width=180)
        in_no = st.text_input("Okul Numaran:", key="login_field").strip()
        if in_no and in_no.isdigit():
            df = get_db()
            user_data = df[df["Okul No"] == in_no]
            if not user_data.empty:
                row = user_data.iloc[0]
                st.info(f"🔍 Hoş geldin **{row['Öğrencinin Adı']}**.")
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

# --- 5. UZMAN EĞİTMEN MÜFREDATI (KORUNAN İÇERİK) ---
training_data = [
    {"module_title": "Merhaba Python: Giriş ve Çıktı", "exercises": [
        {"msg": "**Konu Özeti:** Python'da bilgisayarın bizimle konuşmasını sağlayan temel araç `print()` fonksiyonudur.\n\n**Görev:** Ekrana tam olarak **'Merhaba Pito'** yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')", "hint": "Metinleri tırnak (' ') içine yazmalısın. 'Merhaba Pito' yazmayı dene!", "has_output": True},
        {"msg": "**Konu Özeti:** Sayılar metinlerden farklıdır; tırnak işaretine ihtiyaç duymazlar.\n\n**Görev:** Ekrana sadece sayısal değer olan **100** değerini bas.", "task": "print(___)", "check": lambda c, o: "100" in o, "solution": "print(100)", "hint": "Sayıları yazarken tırnak kullanma, sadece 100 yaz!", "has_output": True},
        {"msg": "**Konu Özeti:** Virgül (`,`) Python'da sihirli bir birleştiricidir.\n\n**Görev:** Önce **'Puan:'** metnini, yanına ise **100** sayısını yazdır.", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o, "solution": "print('Puan:', 100)", "hint": "Virgülden sonra sayısal değeri (100) eklemelisin.", "has_output": True},
        {"msg": "**Konu Özeti:** İyi bir yazılımcı koduna notlar bırakır. `#` işareti 'yorum satırı' demektir.\n\n**Görev:** Bir `#` işareti ekleyerek bu satırı yorum satırına dönüştür.", "task": "___ bu bir yorumdur", "check": lambda c, o: "#" in c, "solution": "# bu bir yorumdur", "hint": "Satırın en başına kare (#) işaretini koymalısın.", "has_output": False},
        {"msg": "**Konu Özeti:** Metinlerin içinde alt satıra geçmek için `\\n` karakteri kullanılır.\n\n**Görev:** 'Üst' kelimesinden sonra alt satıra geçip 'Alt' yazmasını sağla.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o, "solution": "print('Üst\\nAlt')", "hint": "Alt satıra geçmek için tırnak içinde \\n kullanmalısın.", "has_output": True}
    ]},
    {"module_title": "Değişkenler ve input(): Veriyi Hafızada Tutmak", "exercises": [
        {"msg": "**Konu Özeti:** Değişkenler verileri sakladığımız kutulardır. `=` işareti atama yapar.\n\n**Görev:** **yas** ismindeki değişkene **15** değerini ata.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o, "solution": "yas = 15\nprint(yas)", "hint": "Eşittir işaretinden sonra 15 yazmalısın.", "has_output": True},
        {"msg": "**Konu Özeti:** Metinsel veriyi saklarken tırnak kullanmayı asla unutma.\n\n**Görev:** **isim** değişkenine **'Pito'** metnini ata.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o, "solution": "isim = 'Pito'\nprint(isim)", "hint": "Tırnakların arasına Pito yazmalısın.", "has_output": True},
        {"msg": "**Konu Özeti:** `input()` programı durdurur ve klavyeden giriş bekler.\n\n**Görev:** Kullanıcıya **'Adın: '** sorusunu soran girdi komutunu tamamla.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c, "solution": "ad = input('Adın: ')\nprint(ad)", "hint": "Kullanıcıdan veri almak için 'input' fonksiyonunu kullan.", "has_output": True},
        {"msg": "**Konu Özeti:** Sayıları metne çevirmek için `str()` fonksiyonu kullanılır.\n\n**Görev:** 10 sayısını metne çevirerek ekrana basılmasını sağla.", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c, "solution": "s = 10\nprint(str(s))", "hint": "Kısaltma olarak 'str' yazmalısın.", "has_output": True},
        {"msg": "**Konu Özeti:** `input()` ile gelen her şey metindir. Matematik için `int()` ile tam sayıya çevirmelisin.\n\n**Görev:** Kullanıcıdan sayı al, tam sayıya çevir ve 1 ekleyip yazdır.", "task": "n = ___(___('S: '))\nprint(n + 1)", "check": lambda c, o: "int" in c and "11" in o, "solution": "n = int(input('10'))\nprint(n+1)", "hint": "Dıştaki boşluğa 'int', içteki boşluğa 'input' yaz.", "has_output": True}
    ]},
    # Diger modüller baseline yapısında ancak ipucu alanları eklenmiş şekilde devam eder...
    {"module_title": "Karar Verme", "exercises": [{"msg": "Eşitlik kontrolü (==) yap.", "task": "if 10 ___ 10: print('X')", "check": lambda c, o: "==" in c, "solution": "if 10 == 10: print('X')", "hint": "Çift eşittir (==) kullan.", "has_output": True}]*5},
    {"module_title": "Döngüler", "exercises": [{"msg": "3 tur için range kullan.", "task": "for i in ___(3): print('X')", "check": lambda c, o: "range" in c, "solution": "for i in range(3): print('X')", "hint": "range fonksiyonunu kullan.", "has_output": True}]*5},
    {"module_title": "Listeler", "exercises": [{"msg": "Liste oluştur.", "task": "L = [___, 20]", "check": lambda c, o: "10" in c, "solution": "L = [10, 20]", "hint": "Listeye 10 ekle.", "has_output": False}]*5},
    {"module_title": "Fonksiyonlar", "exercises": [{"msg": "def ile tanımla.", "task": "___ f(): print('X')", "check": lambda c, o: "def" in c, "solution": "def f(): print('X')", "hint": "def yazmalısın.", "has_output": False}]*5},
    {"module_title": "OOP", "exercises": [{"msg": "class ile sınıf oluştur.", "task": "___ Robot: pass", "check": lambda c, o: "class" in c, "solution": "class Robot: pass", "hint": "class yazmalısın.", "has_output": False}]*5},
    {"module_title": "Dosya Yönetimi", "exercises": [{"msg": "Dosya aç.", "task": "f = ___('a.txt', 'w')", "check": lambda c, o: "open" in c, "solution": "f = open('a.txt', 'w')", "hint": "open fonksiyonunu kullan.", "has_output": False}]*5},
]

# --- 6. ARA YÜZ DÜZENİ ---
col_main, col_side = st.columns([3, 1])
m_idx = min(st.session_state.current_module, 7)

# GÜVENLİ İNDEKS KONTROLÜ (IndexError Kalkanı)
try:
    curr_module_exercises = training_data[m_idx]["exercises"]
except IndexError:
    st.session_state.current_module = 0
    st.rerun()

e_idx = min(st.session_state.current_exercise, len(curr_module_exercises) - 1)

with col_main:
    st.markdown(f"#### 👋 {RUTBELER[min(sum(st.session_state.completed_modules), 8)]} {st.session_state.student_name} | ⭐ Puan: {int(st.session_state.total_score)}")
    
    if st.session_state.db_module >= 8:
        st.balloons()
        st.success("🎉 Tebrikler! Tüm macerayı tamamladın.")
        if st.button("🔄 Eğitimi Tekrar Al"):
            st.session_state.update({'db_module':0,'db_exercise':0,'total_score':0,'current_module':0,'current_exercise':0,'completed_modules':[False]*8,'scored_exercises':set(),'fail_count':0,'feedback_msg':"", 'last_output':""})
            force_save(); st.rerun()
        st.divider()

    # DİNAMİK MODÜL LİSTESİ
    module_labels = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} Modül {i+1}: {training_data[i]['module_title']}" for i in range(8)]
    sel_mod_label = st.selectbox("Eğitim Modülü Seç:", module_labels, index=m_idx)
    new_m_idx = module_labels.index(sel_mod_label)
    
    if new_m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': new_m_idx, 'current_exercise': 0, 'fail_count': 0, 'exercise_passed': False, 'feedback_msg': "", 'last_output': ""})
        st.rerun()

    st.divider()
    curr_ex = curr_module_exercises[e_idx]
    is_locked = (st.session_state.current_module < st.session_state.db_module) or (st.session_state.db_module >= 8)

    c_img, c_msg = st.columns([1, 4])
    with c_img: st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/200/robot-viewer.png", width=140)
    with c_msg:
        st.info(f"##### 🗣️ Pito'nun Notu:\n{curr_ex['msg']}")
        st.caption(f"Adım: {e_idx + 1}/5 | " + ("🔒 Arşiv" if is_locked else f"🎁 Puan: {st.session_state.current_potential_score} | ❌ Hata: {st.session_state.fail_count}/4"))

    # --- KADEMELİ HATA VE İPUCU MANTIĞI ---
    if st.session_state.fail_count == 3 and not is_locked:
        st.markdown(f"""<div class="hint-guide"><div class="hint-header">💡 Pito'dan İpucu</div>{curr_ex['hint']}</div>""", unsafe_allow_html=True)
    elif st.session_state.fail_count >= 4 and not is_locked:
        st.error("❌ Maalesef bu adımdan puan alamadın. İşte çözüm yolu:")
        st.code(curr_ex['solution'], language="python")

    def run_pito_code(c, user_input="Pito", mod=0, step=0):
        if "___" in c: return "⚠️ Boşluk Hatası"
        if mod == 0 and step == 3: return "# bu bir yorumdur"
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
        st.markdown(f'<div class="solution-guide"><div class="solution-header">📖 Pito Arşiv Rehberi</div></div>', unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")
    else:
        # --- KOMUT PANELİ (4. HATADA GİZLENİR) ---
        if st.session_state.fail_count < 4 and not st.session_state.exercise_passed:
            code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=200, key=f"ace_{st.session_state.current_module}_{e_idx}", auto_update=True)
            u_in = st.text_input("Giriş simülasyonu:", key=f"term_{st.session_state.current_module}_{e_idx}") if "input(" in code else ""
            
            if st.button("🔍 Kodumu Kontrol Et", use_container_width=True):
                if "___" in code:
                    st.session_state.feedback_msg = "⚠️ Lütfen önce boşlukları doldur!"
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
                        st.session_state.feedback_msg = "✅ Tebrikler!"
                        st.session_state.last_output = out
                        st.session_state.exercise_passed = True
                        # Puanlama
                        if f"{st.session_state.current_module}_{e_idx}" not in st.session_state.scored_exercises:
                            st.session_state.total_score += st.session_state.current_potential_score
                            st.session_state.scored_exercises.add(f"{st.session_state.current_module}_{e_idx}")
                            # Kayıt
                            if st.session_state.db_exercise < 4:
                                st.session_state.db_exercise += 1
                            else:
                                st.session_state.db_module += 1; st.session_state.db_exercise = 0; st.session_state.completed_modules[st.session_state.current_module] = True
                            force_save()
                        st.rerun()

    # --- MESAJ VE ÇIKTI GÖSTERİMİ ---
    if st.session_state.exercise_passed:
        if st.session_state.fail_count < 4:
            st.success("✅ Tebrikler! Görev başarıyla tamamlandı.")
            if st.session_state.last_output:
                st.markdown("**Kod Çıktısı:**")
                st.code(st.session_state.last_output)
        
        # KRİTİK: İLERLEME BUTONU MANTIĞI
        if e_idx < 4:
            if st.button("➡️ Sonraki Adım", use_container_width=True):
                st.session_state.update({'current_exercise': e_idx + 1, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
                st.rerun()
        elif st.session_state.current_module < 7:
            if st.button("🏆 Modülü Tamamla", use_container_width=True):
                st.session_state.update({'current_module': st.session_state.current_module + 1, 'current_exercise': 0, 'exercise_passed': False, 'fail_count': 0, 'current_potential_score': 20, 'feedback_msg': "", 'last_output': ""})
                st.rerun()
    elif st.session_state.feedback_msg:
        st.error(st.session_state.feedback_msg)

with col_side:
    st.markdown("### 🏆 En İyiler")
    df_lb = get_db()
    tab_class, tab_school = st.tabs(["👥 Sınıf", "🏫 Okul"])
    for t, d in zip([tab_class, tab_school], [df_lb[df_lb["Sınıf"] == st.session_state.student_class], df_lb]):
        with t:
            if not d.empty:
                for _, r in d.sort_values(by="Puan", ascending=False).head(10).iterrows():
                    st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)