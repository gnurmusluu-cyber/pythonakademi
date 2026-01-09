import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import os
import re

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
    .rank-1 { border: 2px solid #FFD700; box-shadow: 0 0 10px #FFD700; }
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

# --- 3. SESSION STATE ---
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
        # Karşılama mesajı tam istediğiniz formatta güncellendi
        st.markdown('<div class="pito-bubble">Merhaba ben <b>Pito</b>! Haydi birlikte Python\'ın eğlenceli dünyasına dalalım.</div>', unsafe_allow_html=True)
        st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/180/robot-viewer.png", width=180)
        in_no_raw = st.text_input("Okul Numaran:", key="login_field").strip()
        if in_no_raw:
            df = get_db()
            user_data = df[df["Okul No"] == in_no_raw]
            if not user_data.empty:
                row = user_data.iloc[0]
                st.markdown(f"### Hoş geldin, **{row['Öğrencinin Adı']}**! 👋")
                st.success(f"Puanın: {row['Puan']} | Kaldığın Yer: Modül {int(row['Mevcut Modül'])+1}, Adım {int(row['Mevcut Egzersiz'])+1}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🚀 Devam Et"):
                        st.session_state.student_no, st.session_state.student_name, st.session_state.student_class = str(row["Okul No"]), row["Öğrencinin Adı"], row["Sınıf"]
                        st.session_state.total_score, st.session_state.db_module, st.session_state.db_exercise = int(row["Puan"]), int(row["Mevcut Modül"]), int(row["Mevcut Egzersiz"])
                        st.session_state.current_module, st.session_state.current_exercise = st.session_state.db_module, st.session_state.db_exercise
                        st.session_state.completed_modules = [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")]
                        st.session_state.is_logged_in = True
                        st.rerun()
                with c2:
                    if st.button("📚 İncele"):
                        st.session_state.student_no, st.session_state.student_name, st.session_state.student_class = str(row["Okul No"]), row["Öğrencinin Adı"], row["Sınıf"]
                        st.session_state.total_score, st.session_state.db_module, st.session_state.db_exercise = int(row["Puan"]), int(row["Mevcut Modül"]), int(row["Mevcut Egzersiz"])
                        st.session_state.current_module, st.session_state.current_exercise = 0, 0
                        st.session_state.completed_modules = [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")]
                        st.session_state.is_logged_in = True
                        st.rerun()
            else:
                st.info("Seni tanımıyorum. Bilgilerini tamamla:")
                in_name = st.text_input("Adın Soyadın:", key="new_name")
                in_class = st.selectbox("Sınıfın:", SINIFLAR, key="new_class")
                if st.button("Maceraya Başla! ✨"):
                    if in_name.strip():
                        st.session_state.student_no, st.session_state.student_name, st.session_state.student_class = in_no_raw, in_name.strip(), in_class
                        st.session_state.is_logged_in = True
                        force_save(); st.rerun()
    st.stop()

# --- 5. MÜFREDAT ---
training_data = [
    {"module_title": "1. Giriş ve Çıktı", "exercises": [
        {"msg": "print() fonksiyonu ekrana istediğimiz çıktıyı yazdırmamızı sağlar. Hadi dene: Ekrana 'Merhaba Pito' yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o},
        {"msg": "sayıları ekrana yazdırmak için tırnak işareti kullanmamıza gerek yoktur. Şimdi 100 sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o},
        {"msg": "print() fonksiyonu içerisinde aralarına virgül koyarak birden fazla veriyi sıralayıp ekrana yazdırabiliriz. 'Puan:' metni ile 100 sayısını virgül kullanarak yan yana yazdır.", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o},
        {"msg": "Kodlarımıza açıklama eklemek için # (diyez) işaretini kullanırız. Bu satırlar Python tarafından çalıştırılmaz. Bir yorum satırı ekle.", "task": "___ Bu bir yorumdur", "check": lambda c, o: "#" in c},
        {"msg": "Metin içerisinde bir alt satıra geçmek için \\n karakterini kullanırız. Üst ve Alt kelimelerini farklı satırlarda yazdır.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o}
    ]},
    {"module_title": "2. Değişkenler", "exercises": [
        {"msg": "Değişkenler bilgi saklamamıza yarar. yas = 15 yazarak bir tam sayı değişkeni oluştur ve yazdır.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o},
        {"msg": "Metinsel verileri (string) saklamak için tırnak kullanmalıyız. isim = 'Pito' tanımla ve yazdır.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o},
        {"msg": "input() fonksiyonu kullanıcıdan bilgi alır. 'Adın: ' sorusuyla bir isim al.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c},
        {"msg": "str() fonksiyonu sayıları metne dönüştürür. 10 sayısını metne çevir.", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c},
        {"msg": "Kullanıcıdan gelen veriler metindir. int() ile tam sayıya çevirmelisin.", "task": "n = ___(___('S: '))\nprint(n + 1)", "check": lambda c, o: "int" in c}
    ]}
]

# --- 6. ARA YÜZ DÜZENİ ---
col_main, col_side = st.columns([3, 1])

with col_main:
    st.markdown(f"#### 👋 {st.session_state.student_name} | ⭐ Puan: {st.session_state.total_score}")
    mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} {m['module_title']}" for i, m in enumerate(training_data)]
    sel_mod = st.selectbox("Modül Seç:", mod_titles, index=st.session_state.current_module, key=f"sel_{st.session_state.student_no}")
    m_idx = mod_titles.index(sel_mod)
    
    if m_idx != st.session_state.current_module:
        st.session_state.current_module = m_idx
        st.session_state.current_exercise = st.session_state.db_exercise if m_idx == st.session_state.db_module else 0
        st.session_state.current_potential_score = 20; st.rerun()

    # GÜNCEL GÖREVİME DÖN (Geliştirildi)
    if st.session_state.current_module != st.session_state.db_module or st.session_state.current_exercise != st.session_state.db_exercise:
        if st.button(f"🔙 Güncel Görevime Dön (Modül {st.session_state.db_module + 1}, Adım {st.session_state.db_exercise + 1})", use_container_width=True):
            st.session_state.current_module, st.session_state.current_exercise = st.session_state.db_module, st.session_state.db_exercise
            st.rerun()

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

    # GÜVENLİ ÇIKTI FONKSİYONU (ZIRHLANDI)
    def run_pito_code(c, user_input="", for_review=False):
        # Inceleme modunda ___ hatasini onle (SyntaxError engelleme)
        if for_review:
            # Boşlukları (___) görev tipine göre temizle
            if "#" in curr_ex['task'] or "yorum" in curr_ex['msg']:
                c = c.replace("___", "#")
            else:
                c = c.replace("___", "''")
        
        old_stdout, new_stdout = sys.stdout, StringIO()
        sys.stdout = new_stdout
        try:
            exec(c, {"input": lambda p: user_input if user_input else "Pito"})
            sys.stdout = old_stdout
            return new_stdout.getvalue()
        except Exception as e:
            sys.stdout = old_stdout
            return f"Eksik bilgi var: {e}"

    # PİTO TERMİNALİ
    u_in = ""
    if "input(" in code and not is_locked:
        u_in = st.text_input("👇 Pito Terminali: Bir isim veya değer yaz ve Kontrol Et'e bas:", placeholder="İsim, sayı vb...")

    if is_locked:
        st.subheader("📟 Sonuç (İnceleme Modu)")
        st.code(run_pito_code(code, for_review=True) if code else "Çıktı hazır.")
    else:
        if st.button("🔍 Kontrol Et", use_container_width=True):
            out = run_pito_code(code, u_in)
            st.subheader("📟 Çıktı")
            st.code(out if out else "Başarıyla çalıştı!")
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
                st.success("Tebrikler! Bir sonraki görev veri tabanına kaydedildi. ✅")
            else:
                st.session_state.current_potential_score = max(5, st.session_state.current_potential_score - 5)
                st.warning(f"Hatalı! Puanın {st.session_state.current_potential_score}'ye düştü.")

    if st.session_state.exercise_passed or is_locked:
        if e_idx < 4:
            if st.button("➡️ Sonraki Adıma Geç"):
                st.session_state.current_exercise += 1; st.session_state.exercise_passed = False; st.session_state.current_potential_score = 20; st.rerun()
        else:
            if st.button("🏆 Modülü Bitir"):
                st.session_state.current_module += 1; st.session_state.current_exercise = 0; st.session_state.current_potential_score = 20; st.balloons(); st.rerun()

with col_side:
    st.markdown(f"### 🏆 Sınıf Liderleri")
    df_lb = get_db()
    df_class = df_lb[df_lb["Sınıf"] == st.session_state.student_class]
    if not df_class.empty:
        df_sort = df_class.sort_values(by="Puan", ascending=False).drop_duplicates(subset=["Okul No"]).head(10)
        for i, (_, r) in enumerate(df_sort.iterrows()):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "⭐"
            st.markdown(f'<div class="leaderboard-card"><b>{medal} {r["Öğrencinin Adı"]}</b><br>{r["Puan"]} Puan</div>', unsafe_allow_html=True)