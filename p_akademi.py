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

st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem;}
    
    /* Pito Konuşma Balonu */
    .pito-bubble {
        position: relative; background: #f0f2f6; border: 2px solid #3a7bd5;
        border-radius: 15px; padding: 20px; margin-bottom: 20px; color: #1e1e1e;
        font-weight: 500; font-size: 1.1rem; box-shadow: 4px 4px 15px rgba(0,0,0,0.1);
    }
    .pito-bubble:after {
        content: ''; position: absolute; bottom: -20px; left: 40px;
        border-width: 20px 20px 0; border-style: solid; border-color: #3a7bd5 transparent;
    }

    /* Çözüm Rehberi Kutusu (İnceleme Modu) */
    .solution-guide {
        background-color: #f8fafc !important;
        border: 2px solid #3a7bd5 !important;
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
        color: #1e1e1e !important;
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

# --- 2. VERİ TABANI YÖNETİMİ ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db(use_cache=True):
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=60 if use_cache else 0)
        if df is None or df.empty:
            return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        df["Okul No"] = df["Okul No"].astype(str).str.split('.').str[0].str.strip()
        df = df[df["Okul No"].str.isdigit()] 
        df["Puan"] = pd.to_numeric(df["Puan"], errors='coerce').fillna(0).astype(int)
        return df.dropna(subset=["Okul No"])
    except:
        return pd.DataFrame()

def force_save():
    try:
        no = str(st.session_state.student_no).strip()
        df_all = get_db(use_cache=False)
        df_clean = df_all[df_all["Okul No"] != no]
        progress = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = RUTBELER[sum(st.session_state.completed_modules)]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, int(st.session_state.total_score), rank, progress, st.session_state.db_module, st.session_state.db_exercise, datetime.now().strftime("%H:%M:%S")]], 
                               columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

# --- 3. SESSION STATE ---
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
        
        if st.session_state.rejected_user:
            st.warning("⚠️ O halde kendi okul numaranı gir!")

        in_no_raw = st.text_input("Okul Numaran (Sadece Rakam):", key="login_field").strip()
        
        if in_no_raw and in_no_raw.isdigit():
            df = get_db(use_cache=False)
            user_data = df[df["Okul No"] == in_no_raw] if not df.empty else pd.DataFrame()
            
            if not user_data.empty:
                row = user_data.iloc[0]
                st.info(f"🔍 Bu numara **{row['Öğrencinin Adı']}** adına kayıtlı.")
                st.markdown("### Sen bu kişi misin? 🤔")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Evet"):
                        mv, ev = int(row['Mevcut Modül']), int(row['Mevcut Egzersiz'])
                        st.session_state.update({'student_no': in_no_raw, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': mv, 'db_exercise': ev, 'current_module': min(mv, 7), 'current_exercise': ev, 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True})
                        st.rerun()
                with c2:
                    if st.button("❌ Hayır"):
                        st.session_state.rejected_user = True
                        if "login_field" in st.session_state: del st.session_state["login_field"]
                        st.rerun()
            else:
                in_name = st.text_input("Adın Soyadın:")
                in_class = st.selectbox("Sınıfın:", SINIFLAR)
                if st.button("Maceraya Başla! ✨") and in_name:
                    st.session_state.update({'student_no': in_no_raw, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True})
                    force_save(); st.rerun()
    st.stop()

# --- 5. EKSİKSİZ EĞİTİCİ MÜFREDAT ---
training_data = [
    {"module_title": "1. Giriş ve Çıktı", "exercises": [
        {"msg": "Ekrana yazı yazdırmak için **print()** kullanılır. Metinleri mutlaka **tırnak** içinde yazmalısın. Hadi dene: Ekrana **'Merhaba Pito'** yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')"},
        {"msg": "Sayıları ekrana yazdırırken **tırnak işareti kullanılmaz.** Şimdi ekrana **100** sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o, "solution": "print(100)"},
        {"msg": "print() içinde verileri ayırmak için **virgül (,)** kullanılır. Hadi dene: **'Puan:'** metni ile **100** sayısını yan yana yazdır.", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o, "solution": "print('Puan:', 100)"},
        {"msg": "**# (Diyez)** işaretiyle yorum satırı oluşturulur. Hadi dene: Bir **yorum satırı** oluştur.", "task": "___ Not", "check": lambda c, o: "#" in c, "solution": "# Not"},
        {"msg": "Alt satıra geçmek için **'\\n'** kullanılır. Hadi dene: **'Üst'** ve **'Alt'** kelimelerini alt alta yazdır.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o, "solution": "print('Üst\\nAlt')"}
    ]},
    {"module_title": "2. Değişkenler", "exercises": [
        {"msg": "Değişkenler bilgi saklar. **yas = 15** yazarak bir tam sayı değişkeni oluştur ve yazdır.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o, "solution": "yas = 15\nprint(yas)"},
        {"msg": "**isim** değişkenine **'Pito'** değerini ata ve yazdır.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o, "solution": "isim = 'Pito'\nprint(isim)"},
        {"msg": "**input()** ile bilgi alırız. Hadi dene: **'Adın: '** sorusuyla isim al ve yazdır.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c, "solution": "ad = input('Adın: ')\nprint(ad)"}
    ]},
    {"module_title": "3. Karar Yapıları", "exercises": [
        {"msg": "Eşitlik için **'=='** kullanılır. Hadi dene: Eğer 10 sayısı **10'a eşitse** ekrana 'X' yazdır.", "task": "if 10 ___ 10: print('X')", "check": lambda c, o: "==" in c, "solution": "if 10 == 10: print('X')"},
        {"msg": "Şart yanlışsa **'else:'** bloğu çalışır. Hadi dene: 5 sayısı 10'dan büyük değilse ekrana **'Y'** yazdır.", "task": "if 5>10: pass\n___: print('Y')", "check": lambda c, o: "else" in c, "solution": "else:\n    print('Y')"}
    ]},
    {"module_title": "4. Döngüler", "exercises": [
        {"msg": "**'for'** döngüsü ve **range(3)** ile 3 kez tekrar yap. Hadi dene: 3 kez 'X' yazdır.", "task": "for i in ___(3): print('X')", "check": lambda c, o: o.count("X")==3, "solution": "for i in range(3): print('X')"},
        {"msg": "**'while'**, şart doğruyken çalışır. Hadi dene: **i<1** doğruyken ekrana 'Y' yazdır.", "task": "i=0\n___ i<1: print('Y'); i+=1", "check": lambda c, o: "while" in c, "solution": "i=0\nwhile i < 1:\n    print('Y')\n    i += 1"}
    ]}
]

# --- 6. ARA YÜZ DÜZENİ ---
col_main, col_side = st.columns([3, 1])

completed_count = sum(st.session_state.completed_modules)
student_rank = RUTBELER[completed_count]

with col_main:
    st.markdown(f"#### 👋 {student_rank} {st.session_state.student_name} | ⭐ Puan: {int(st.session_state.total_score)}")
    
    if st.session_state.db_module >= 8:
        if not st.session_state.celebrated: st.balloons(); st.session_state.celebrated = True
        st.success("### 🎉 Tebrikler! Eğitimi Tamamladın.")
        if st.button("🔄 Sıfırla"):
            st.session_state.update({'db_module':0, 'db_exercise':0, 'total_score':0, 'current_module':0, 'current_exercise':0, 'completed_modules':[False]*8, 'scored_exercises':set(), 'celebrated':False})
            force_save(); st.rerun()

    mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} Modül {i+1}" for i in range(len(training_data))]
    sel_mod = st.selectbox("Modül Seç:", mod_titles, index=min(st.session_state.current_module, len(training_data)-1))
    m_idx = mod_titles.index(sel_mod)
    if m_idx != st.session_state.current_module:
        st.session_state.current_module, st.session_state.current_exercise = m_idx, 0
        st.rerun()

    st.divider()
    e_idx = st.session_state.current_exercise
    curr_ex = training_data[m_idx]["exercises"][e_idx]
    is_locked = (m_idx < st.session_state.db_module) or (st.session_state.db_module >= 8)

    c_img, c_msg = st.columns([1, 4])
    with c_img: st.image(PITO_IMG if os.path.exists(PITO_IMG) else "https://img.icons8.com/fluency/200/robot-viewer.png", width=140)
    with c_msg:
        st.info(f"##### 🗣️ Pito:\n{curr_ex['msg']}")
        st.caption(f"Adım: {e_idx + 1}/{len(training_data[m_idx]['exercises'])} " + ("🔒 İnceleme Modu" if is_locked else f"🎁 Puan: {st.session_state.current_potential_score}"))

    code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=200, readonly=is_locked, key=f"ace_{m_idx}_{e_idx}", auto_update=True)

    def run_pito_code(c, user_input=""):
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

    # --- KRİTİK GÜNCELLEME: İNCELEME MODU ÇÖZÜM GÖSTERİMİ ---
    if is_locked:
        st.markdown(f"""
        <div class="solution-guide">
            <div class="solution-header">✅ Pito'nun Çözüm Rehberi</div>
            <b>Nasıl Yapılır?</b><br>{curr_ex['msg']}
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**Doğru Kod:**")
        st.code(curr_ex['solution'], language="python")
        sol_out = run_pito_code(curr_ex['solution'], "10")
        st.markdown("**Muhtemel Çıktı:**")
        st.code(sol_out if sol_out else "Kod çalıştırıldı.")
    else:
        u_in = st.text_input("Giriş yap:", key=f"term_{m_idx}_{e_idx}") if "input(" in code else ""
        if st.button("🔍 Kontrol Et", use_container_width=True):
            out = run_pito_code(code, u_in)
            if "Hata:" in out: st.error(out)
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
                if st.button("➡️ Sonraki Adım"): st.session_state.current_exercise += 1; st.session_state.exercise_passed = False; st.rerun()
            elif m_idx < len(training_data) - 1:
                if st.button("🏆 Modülü Bitir"): st.session_state.current_module += 1; st.session_state.current_exercise = 0; st.rerun()

with col_side:
    st.markdown("### 🏆 Liderlik Tablosu")
    df_lb = get_db()
    t1, t2 = st.tabs(["👥 Sınıfım", "🏫 Okul"])
    with t1:
        if not df_lb.empty:
            df_c = df_lb[df_lb["Sınıf"] == st.session_state.student_class].sort_values(by="Puan", ascending=False).head(10)
            for i, (_, r) in enumerate(df_c.iterrows()):
                st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)
    with t2:
        if not df_lb.empty:
            df_s = df_lb.sort_values(by="Puan", ascending=False).head(10)
            for i, (_, r) in enumerate(df_s.iterrows()):
                st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]} ({r["Sınıf"]})</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)
