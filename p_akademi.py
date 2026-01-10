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

# --- 2. HAFIZA BAŞLATMA ---
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
    .leaderboard-card { background: linear-gradient(135deg, #1e1e1e, #2d2d2d); border-radius: 12px; padding: 10px; margin-bottom: 8px; color: white; }
    .champion-card { background: linear-gradient(135deg, #FFD700, #FFA500); border-radius: 15px; padding: 15px; margin-top: 20px; color: #1e1e1e; text-align: center; font-weight: bold; }
    .stButton > button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important; color: white !important; font-weight: bold; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. VERİ TABANI YÖNETİMİ ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db(use_cache=True):
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=60 if use_cache else 0)
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
                        # KRİTİK VERİ YÜKLEME ADIMI
                        m_v = int(row['Mevcut Modül'])
                        e_v = int(row['Mevcut Egzersiz'])
                        st.session_state.update({
                            'student_no': in_no_raw, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"],
                            'total_score': int(row["Puan"]), 'db_module': m_v, 'db_exercise': e_v,
                            'current_module': min(m_v, 7), 'current_exercise': e_v,
                            'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")],
                            'is_logged_in': True, 'pito_emotion': "pito_dusunuyor"
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

# --- 6. MÜFREDAT VE ANA ARAYÜZ ---
training_data = [
    {"module_title": "1. Giriş ve Çıktı", "exercises": [
        {"msg": "Ekrana **'Merhaba Pito'** yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')"},
        {"msg": "Ekrana **100** sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o, "solution": "print(100)"},
        {"msg": "Virgül ile ayırarak **'Puan:'** ve **100** yazdır.", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o, "solution": "print('Puan:', 100)"},
        {"msg": "Diyez (#) ile **yorum satırı** oluştur.", "task": "___ Bu bir not", "check": lambda c, o: "#" in c, "solution": "# Not"},
        {"msg": "Alt satıra geçmek için **'\\n'** kullan.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o, "solution": "print('Üst\\nAlt')"}
    ]},
    {"module_title": "2. Değişkenler", "exercises": [
        {"msg": "**yas** değişkenine **15** ata ve yazdır.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o, "solution": "yas = 15"},
        {"msg": "**isim** değişkenine **'Pito'** değerini ata.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o, "solution": "isim = 'Pito'"},
        {"msg": "**input()** ile veri al.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c, "solution": "input"},
        {"msg": "**str()** kullanarak sayıyı metne çevir.", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c, "solution": "str"},
        {"msg": "Veriyi **int()** ile tam sayıya çevir.", "task": "n = ___(___('S: '))\nprint(n + 1)", "check": lambda c, o: "int" in c, "solution": "int"}
    ]},
    {"module_title": "3. Karar Yapıları", "exercises": [{"msg": "Eşitlik için '==' kullan.", "task": "if 10 ___ 10: print('X')", "check": lambda c, o: "==" in c, "solution": "=="}, {"msg": "else: bloğu kur.", "task": "if 5>10: pass\n___: print('Y')", "check": lambda c, o: "else" in c, "solution": "else"}, {"msg": "'>=' operatörü.", "task": "if 5 ___ 5: print('Z')", "check": lambda c, o: ">=" in c, "solution": ">="}, {"msg": "'and' ile iki koşul denetle.", "task": "if 1==1 ___ 2==2: print('OK')", "check": lambda c, o: "and" in c, "solution": "and"}, {"msg": "'elif' ile alternatif şart kur.", "task": "if 5>10: pass\n___ 5==5: print('A')", "check": lambda c, o: "elif" in c, "solution": "elif"}]},
    {"module_title": "4. Döngüler", "exercises": [{"msg": "3 kez 'X' yazdır.", "task": "for i in ___(3): print('X')", "check": lambda c, o: o.count("X")==3, "solution": "range"}, {"msg": "while döngüsü kur.", "task": "i=0\n___ i<1: print('Y'); i+=1", "check": lambda c, o: "while" in c, "solution": "while"}, {"msg": "break kullan.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "break" in c, "solution": "break"}, {"msg": "continue kullan.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "continue" in c, "solution": "continue"}, {"msg": "i sayacını yazdır.", "task": "for i in range(2): print(___)", "check": lambda c, o: "1" in o, "solution": "i"}]},
    {"module_title": "5. Listeler", "exercises": [{"msg": "Liste oluştur.", "task": "L = [___, 20]", "check": lambda c, o: "10" in c, "solution": "10"}, {"msg": "İlk elemana eriş.", "task": "L=[5,6]\nprint(L[___])", "check": lambda c, o: "5" in o, "solution": "0"}, {"msg": "len() ile boyut ölç.", "task": "L=[1,2]\nprint(___(L))", "check": lambda c, o: "2" in o, "solution": "len"}, {"msg": "append() ile 30 ekle.", "task": "L=[10]\nL.___(___)\nprint(L)", "check": lambda c, o: "30" in o, "solution": "append"}, {"msg": "pop() ile sil.", "task": "L=[1,2]\nL.___()\nprint(L)", "check": lambda c, o: "1" in o, "solution": "pop"}]},
    {"module_title": "6. Fonksiyonlar", "exercises": [{"msg": "def ile f tanımla.", "task": "___ f(): print('X')", "check": lambda c, o: "def" in c, "solution": "def"}, {"msg": "Tuple (1, 2) oluştur.", "task": "t = (___, 2)\nprint(t)", "check": lambda c, o: "1" in c, "solution": "1"}, {"msg": "Sözlük anahtarı.", "task": "d = {'ad': '___'}\nprint(d['ad'])", "check": lambda c, o: "Pito" in c, "solution": "Pito"}, {"msg": "keys() metodu.", "task": "d={'a':1}\nprint(d.___())", "check": lambda c, o: "keys" in c, "solution": "keys"}, {"msg": "Set (küme) oluştur.", "task": "s = {1, 2, ___}\nprint(s)", "check": lambda c, o: "1" in c, "solution": "1"}]},
    {"module_title": "7. OOP", "exercises": [{"msg": "class ile Robot kur.", "task": "___ Robot: pass", "check": lambda c, o: "class" in c, "solution": "class"}, {"msg": "R'den p üret.", "task": "class R: pass\np = ___()", "check": lambda c, o: "R()" in c, "solution": "R"}, {"msg": "renk niteliği ata.", "task": "class R: pass\np=R()\np.___ = 'Mavi'\nprint(p.renk)", "check": lambda c, o: "renk" in c, "solution": "renk"}, {"msg": "ses metodu (self).", "task": "class R:\n def ___(self):\n  print('Bip!')", "check": lambda c, o: "ses" in c, "solution": "ses"}, {"msg": "s() metodunu çağır.", "task": "class R:\n def s(self): print('X')\nr=R()\nr.___()", "check": lambda c, o: "s()" in c, "solution": "s"}]},
    {"module_title": "8. Dosyalar", "exercises": [{"msg": "open() ve 'w' kullan.", "task": "dosya = ___('n.txt', '___')", "check": lambda c, o: "open" in c, "solution": "w"}, {"msg": "write() ile yaz.", "task": "f = open('t.txt', 'w'); f.___('Pito'); f.close()", "check": lambda c, o: "write" in c, "solution": "write"}, {"msg": "'r' ile aç.", "task": "f = open('t.txt', '___')", "check": lambda c, o: "'r'" in c, "solution": "r"}, {"msg": "read() ile oku.", "task": "f = open('t.txt', 'r')\nprint(f.___())\nf.close()", "check": lambda c, o: "read" in c, "solution": "read"}, {"msg": "close() ile kapat.", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o: "close" in c, "solution": "close"}]}
]

col_main, col_side = st.columns([3, 1])
student_rank = RUTBELER[sum(st.session_state.completed_modules)]

with col_main:
    st.markdown(f"#### 👋 {student_rank} {st.session_state.student_name} | ⭐ Puan: {int(st.session_state.total_score)}")
    
    if st.session_state.db_module >= 8:
        if not st.session_state.celebrated:
            st.balloons(); st.session_state.celebrated = True
            st.session_state.pito_emotion = "pito_mezun"
        st.success("🎉 Eğitim Tamamlandı!"); st.stop()

    m_idx = st.session_state.current_module
    e_idx = st.session_state.current_exercise
    curr_ex = training_data[m_idx]["exercises"][e_idx]
    is_locked = (m_idx < st.session_state.db_module)

    c_pito, c_msg = st.columns([1, 4])
    with c_pito: st.markdown(get_pito_gif(st.session_state.pito_emotion, width=180), unsafe_allow_html=True)
    with c_msg: st.info(f"##### 🗣️ Pito:\n{curr_ex['msg']}"); st.caption(f"Adım: {e_idx + 1}/5 | Modül: {m_idx + 1}")

    code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=180, readonly=is_locked, key=f"ace_{m_idx}_{e_idx}", auto_update=True)

    def run_pito_code(c, user_input=""):
        old_stdout, new_stdout = sys.stdout, StringIO()
        sys.stdout = new_stdout
        if "input(" in c and not user_input: return "⚠️ Terminale veri gir!"
        try:
            exec(c.replace("___", "None"), {"input": lambda p: str(user_input), "print": print, "int": int, "str": str, "len": len, "open": open})
            return new_stdout.getvalue()
        except Exception as e: return f"Hata: {e}"

    u_in = st.text_input("👇 Terminal:", key=f"t_{m_idx}_{e_idx}") if "input(" in code and not is_locked else ""

    if not is_locked:
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
                        else: st.session_state.db_module += 1; st.session_state.db_exercise = 0; st.session_state.completed_modules[m_idx] = True
                        force_save()
                    st.success("Tebrikler! ✅")
                else: st.session_state.pito_emotion = "pito_hata"; st.warning("Hatalı!")
            st.rerun()

    if st.session_state.exercise_passed or is_locked:
        if st.button("➡️ Sonraki"):
            if e_idx < 4: st.session_state.current_exercise += 1
            else: st.session_state.current_module += 1; st.session_state.current_exercise = 0
            st.session_state.update({'exercise_passed': False, 'pito_emotion': "pito_dusunuyor"})
            st.rerun()

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