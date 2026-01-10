import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import os
import base64

# --- 1. SAYFA VE CIHAZ AYARLARI ---
st.set_page_config(layout="wide", page_title="Pito Python Akademi", initial_sidebar_state="collapsed")

# --- 2. BEYAZ ZEMİN VE WIDGET GÖRÜNÜRLÜK ZIRHI (CSS) ---
st.markdown("""
    <style>
    /* Uygulama Arka Planını Beyaz Yap */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"] {
        background-color: #FFFFFF !important;
    }
    header {visibility: hidden;}

    /* Global Metin Rengi (Koyu Lacivert) */
    html, body, [class*="st-"] { color: #1E293B !important; font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown { color: #1E293B !important; }

    /* INPUT VE SELECTBOX KESİN ÇÖZÜM (Siyah kutu hatasını giderir) */
    div[data-baseweb="input"] > div, div[data-baseweb="base-input"], div[data-baseweb="select"] > div {
        background-color: #F8FAFC !important;
        color: #1E293B !important;
        border: 2px solid #E2E8F0 !important;
    }
    input { color: #1E293B !important; background-color: transparent !important; }
    div[data-baseweb="popover"], div[data-baseweb="popover"] > div { background-color: #FFFFFF !important; }
    div[data-baseweb="popover"] li { color: #1E293B !important; background-color: #FFFFFF !important; }
    
    /* Çözüm Örneği Kutu Tasarımı */
    .solution-box {
        background-color: #F0FDF4 !important;
        border: 2px solid #BBF7D0 !important;
        padding: 20px;
        border-radius: 12px;
        color: #166534 !important;
        margin: 15px 0;
    }

    /* Pito Konuşma Balonu */
    .pito-bubble {
        position: relative; background: #F8FAFC; border: 2px solid #3a7bd5;
        border-radius: 20px; padding: 25px; margin: 0 auto 30px auto; 
        color: #1E293B !important; font-weight: 500; font-size: 1.15rem; 
        text-align: center; box-shadow: 0 10px 25px rgba(58, 123, 213, 0.08);
        max-width: 850px;
    }
    .pito-bubble:after {
        content: ''; position: absolute; bottom: -20px; left: 50%; transform: translateX(-50%);
        border-width: 20px 20px 0; border-style: solid; border-color: #3a7bd5 transparent;
    }

    /* Liderlik Tablosu Kartları */
    .leaderboard-card { 
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 15px; 
        padding: 15px; margin-bottom: 12px; color: #1E293B !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .rank-tag { display: inline-block; background: #3a7bd5; color: white !important; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; font-weight: bold; }
    
    .stButton > button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important; color: white !important; font-weight: 600; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HAFIZA VE GIF SİSTEMİ ---
initial_states = {
    'is_logged_in': False, 'student_name': "", 'student_no': "", 'student_class': "",
    'completed_modules': [False]*8, 'current_module': 0, 'current_exercise': 0,
    'exercise_passed': False, 'total_score': 0, 'scored_exercises': set(),
    'db_module': 0, 'db_exercise': 0, 'current_potential_score': 20,
    'celebrated': False, 'rejected_user': False, 'pito_emotion': "pito_merhaba",
    'feedback_type': None, 'feedback_msg': ""
}
for key, value in initial_states.items():
    if key not in st.session_state: st.session_state[key] = value

def get_pito_gif(gif_name, width=280):
    gif_path = f"assets/{gif_name}.gif"
    if os.path.exists(gif_path):
        with open(gif_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        return f'<div style="text-align: center;"><img src="data:image/gif;base64,{encoded}" width="{width}" style="max-width: 100%;"></div>'
    return f'<div style="text-align: center;"><img src="https://img.icons8.com/fluency/200/robot-viewer.png" width="{width}"></div>'

# --- 4. VERİ TABANI ---
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
        prog_str = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = RUTBELER[sum(st.session_state.completed_modules)]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, int(st.session_state.total_score), rank, prog_str, int(st.session_state.db_module), int(st.session_state.db_exercise), datetime.now().strftime("%H:%M:%S")]], columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])
        conn.update(spreadsheet=SHEET_URL, data=pd.concat([df_clean, new_row], ignore_index=True))
    except: pass

SINIFLAR = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B"]
RUTBELER = ["🥚 Yumurta", "🌱 Filiz", "🪵 Oduncu", "🧱 Mimar", "🌀 Usta", "📋 Uzman", "📦 Kaptan", "🤖 Robot", "🏆 Kahraman"]

# --- 5. GİRİŞ EKRANI ---
if not st.session_state.is_logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="pito-bubble">Merhaba! Ben <b>Pito</b>.<br>Python Dünyası macerasına hoş geldin!</div>', unsafe_allow_html=True)
        st.markdown(get_pito_gif("pito_merhaba", width=300), unsafe_allow_html=True)
        in_no = st.text_input("Okul Numaran:", key="login_field").strip()
        if in_no and in_no.isdigit():
            df = get_db()
            user_data = df[df["Okul No"] == in_no] if not df.empty else pd.DataFrame()
            if not user_data.empty:
                row = user_data.iloc[0]
                st.info(f"🔍 Hoş geldin **{row['Öğrencinin Adı']}**.")
                if st.button("✅ Maceraya Devam Et"):
                    mv, ev = int(row['Mevcut Modül']), int(row['Mevcut Egzersiz'])
                    st.session_state.update({'student_no': in_no, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': mv, 'db_exercise': ev, 'current_module': min(mv, 7), 'current_exercise': ev, 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True, 'pito_emotion': "pito_dusunuyor"})
                    st.rerun()
            else:
                in_name = st.text_input("Adın Soyadın:")
                in_class = st.selectbox("Sınıfın:", SINIFLAR)
                if st.button("Akademiye Kaydol! ✨") and in_name:
                    st.session_state.update({'student_no': in_no, 'student_name': in_name, 'student_class': in_class, 'is_logged_in': True})
                    force_save(); st.rerun()
    st.stop()

# --- 6. EĞİTİCİ MÜFREDAT (MEB KAYNAKLI) ---
training_data = [
    {"module_title": "1. Veri Çıkışı ve print()", "exercises": [
        {"msg": "Ekrana yazı yazdırmak için **print()** kullanılır. Metinler mutlaka **tırnak** içinde olmalıdır. \n\n**Görev:** Ekrana **'Merhaba Pito'** yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')"},
        {"msg": "Sayılar için tırnak gerekmez. Python sayıları matematiksel değer olarak tanır. \n\n**Görev:** Ekrana tırnak kullanmadan **100** sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o, "solution": "print(100)"},
        {"msg": "Verileri yan yana yazdırmak için **virgül (,)** kullanılır. Virgül araya boşluk ekler. \n\n**Görev:** **'Puan:'** metni ile **100** sayısını yan yana yazdır.", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o, "solution": "print('Puan:', 100)"},
        {"msg": "**# (Diyez)** işaretiyle yorum satırı oluşturulur. \n\n**Görev:** Satırın başına **#** koy ve yanına **Not** yaz.", "task": "___ Not", "check": lambda c, o: "#" in c, "solution": "# Not"},
        {"msg": "Metinleri farklı satırlara bölmek için **'\\n'** kullanılır. \n\n**Görev:** Tek print içinde **'Üst'** ve **'Alt'** kelimelerini alt alta yazdır.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o, "solution": "print('Üst\\nAlt')"}
    ]},
    {"module_title": "2. Değişkenler ve input()", "exercises": [
        {"msg": "Değişkenler verileri hafızada saklar. **(=)** ile atama yapılır. \n\n**Görev:** **yas** isimli bir değişken oluştur, içine **15** ata ve yazdır.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o, "solution": "yas = 15\nprint(yas)"},
        {"msg": "**input()** ile kullanıcıdan bilgi alırız. \n\n**Görev:** **'Adın: '** sorusuyla bir girdi al, bunu **ad** değişkenine ata.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c, "solution": "ad = input('Adın: ')\nprint(ad)"},
        {"msg": "Girdi her zaman metindir. Sayısal işlem için **int()** kullanılır. \n\n**Görev:** Girdi değerini **int**'e çevir ve üzerine 1 ekle.", "task": "n = ___(___('S: '))\nprint(n + 1)", "check": lambda c, o: "int" in c and "input" in c, "solution": "n = int(input('10'))\nprint(n+1)"}
    ]},
    {"module_title": "3. Karar Yapıları (if-else)", "exercises": [
        {"msg": "Eşitlik için **(==)** kullanılır. \n\n**Görev:** Eğer 10 sayısı **10'a eşitse** 'X' yazdır.", "task": "if 10 ___ 10: print('X')", "check": lambda c, o: "==" in c, "solution": "if 10 == 10: print('X')"},
        {"msg": "Şart yanlışsa **else:** bloğu çalışır. \n\n**Görev:** 5 sayısı 10'dan büyük değilse **'Y'** yazdıran bir else kur.", "task": "if 5>10: pass\n___: print('Y')", "check": lambda c, o: "else" in c, "solution": "else:\n    print('Y')"}
    ]},
    {"module_title": "4. Döngüler: for ve while", "exercises": [
        {"msg": "**for** ve **range()** fonksiyonu ile kod tekrarlanır. \n\n**Görev:** 3 kez ekrana 'X' yazdıran döngüyü kur.", "task": "for i in ___(3): print('X')", "check": lambda c, o: o.count("X")==3, "solution": "for i in range(3): print('X')"},
        {"msg": "**while** yanındaki şart doğruyken döner. \n\n**Görev:** **i < 1** doğruyken 'Y' yazdıran döngü kur.", "task": "i=0\n___ i<1: print('Y'); i+=1", "check": lambda c, o: "while" in c, "solution": "while i < 1:\n    print('Y')\n    i += 1"}
    ]}
]

# --- 7. ARA YÜZ VE GÜVENLİ İNDEX KONTROLÜ ---
# - INDEXERROR VE APIEXCEPTION KORUMASI
m_idx = min(st.session_state.current_module, len(training_data)-1)
max_ex = len(training_data[m_idx]["exercises"])
if st.session_state.current_exercise >= max_ex:
    st.session_state.current_exercise = max_ex - 1

col_main, col_side = st.columns([3, 1])
rank_idx = sum(st.session_state.completed_modules)
student_rank = RUTBELER[min(rank_idx, len(RUTBELER)-1)]

with col_main:
    st.markdown(f"#### 👋 {st.session_state.student_name} | ⭐ Puan: {int(st.session_state.total_score)}")
    st.markdown(f"<span class='rank-tag'>{student_rank}</span> <small>{st.session_state.student_class}</small>", unsafe_allow_html=True)
    
    prog_val = (rank_idx * 5 + st.session_state.current_exercise) / (len(training_data) * 5)
    st.progress(min(prog_val, 1.0), text=f"Akademi İlerlemesi: %{int(prog_val*100)}")

    if st.session_state.db_module >= len(training_data):
        st.success("🎉 Tüm eğitimi tamamladın Python Kahramanı!"); st.stop()

    mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} Modül {i+1}" for i in range(len(training_data))]
    sel_mod = st.selectbox("Ders Listesi:", mod_titles, index=m_idx, label_visibility="collapsed")
    new_m_idx = mod_titles.index(sel_mod)
    if new_m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': new_m_idx, 'current_exercise': 0, 'feedback_type': None}); st.rerun()

    st.divider()
    curr_ex = training_data[m_idx]["exercises"][st.session_state.current_exercise]
    is_locked = (m_idx < st.session_state.db_module)

    c1, c2 = st.columns([1, 4])
    with c1: st.markdown(get_pito_gif(st.session_state.pito_emotion, width=180), unsafe_allow_html=True)
    with c2:
        st.info(f"##### 🗣️ Pito:\n{curr_ex['msg']}")
        st.caption(f"Adım: {st.session_state.current_exercise + 1} | Modül: {m_idx+1}")

    code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=15, height=200, readonly=is_locked, key=f"ace_{m_idx}_{st.session_state.current_exercise}", auto_update=True)

    if is_locked:
        st.markdown('<div class="solution-box">✅ <b>Pito\'nun Çözümü:</b></div>', unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")

    if st.session_state.feedback_type:
        if st.session_state.feedback_type == "error": st.error(f"❌ {st.session_state.feedback_msg}")
        else: st.success(f"✅ {st.session_state.feedback_msg}")

    if not is_locked:
        u_in = st.text_input("👇 Terminal Girdisi (Gerekliyse):", key=f"t_{m_idx}") if "input(" in code else ""
        if st.button("🔍 Kodumu Kontrol Et"):
            old_stdout, new_stdout = sys.stdout, StringIO()
            sys.stdout = new_stdout
            try:
                exec(code.replace("___", "None"), {"input": lambda p: str(u_in or "10"), "print": print, "int": int, "str": str, "len": len, "open": open, "range": range})
                out = new_stdout.getvalue()
                if curr_ex['check'](code, out) and "___" not in code:
                    st.session_state.update({'exercise_passed': True, 'pito_emotion': "pito_basari", 'feedback_type': "success", 'feedback_msg': "Tebrikler! Doğru sonuç."})
                    if f"{m_idx}_{st.session_state.current_exercise}" not in st.session_state.scored_exercises:
                        st.session_state.total_score += st.session_state.current_potential_score
                        st.session_state.scored_exercises.add(f"{m_idx}_{st.session_state.current_exercise}")
                        if st.session_state.db_exercise < len(training_data[m_idx]["exercises"]) - 1: st.session_state.db_exercise += 1
                        else: st.session_state.db_module += 1; st.session_state.db_exercise = 0; st.session_state.completed_modules[m_idx] = True
                        force_save()
                else: st.session_state.update({'pito_emotion': "pito_hata", 'feedback_type': "error", 'feedback_msg': "Cevap hatalı veya eksik."})
            except Exception as e: st.session_state.update({'pito_emotion': "pito_hata", 'feedback_type': "error", 'feedback_msg': f"Hata: {e}"})
            st.rerun()

    nb1, nb2 = st.columns(2)
    with nb1:
        if is_locked and st.session_state.current_exercise > 0:
            if st.button("⬅️ Önceki Adım"):
                st.session_state.update({'current_exercise': st.session_state.current_exercise - 1, 'feedback_type': None}); st.rerun()
    with nb2:
        if st.session_state.exercise_passed or is_locked:
            if st.session_state.current_exercise < len(training_data[m_idx]["exercises"]) - 1:
                if st.button("➡️ Sonraki Adım"):
                    st.session_state.update({'current_exercise': st.session_state.current_exercise + 1, 'exercise_passed': False, 'pito_emotion': "pito_dusunuyor", 'feedback_type': None}); st.rerun()

with col_side:
    st.markdown("### 🏆 Sıralama")
    df = get_db()
    t1, t2 = st.tabs(["👥 Sınıf", "🏫 Okul"])
    with t1:
        if not df.empty:
            for _, r in df[df["Sınıf"] == st.session_state.student_class].sort_values("Puan", ascending=False).head(8).iterrows():
                st.markdown(f'''<div class="leaderboard-card"><b>{r["Öğrencinin Adı"]}</b><br><span class="rank-tag">{r["Rütbe"]}</span><br>⭐ {int(r["Puan"])} Puan</div>''', unsafe_allow_html=True)
    with t2:
        if not df.empty:
            for _, r in df.sort_values("Puan", ascending=False).head(8).iterrows():
                st.markdown(f'''<div class="leaderboard-card"><b>{r["Öğrencinin Adı"]}</b> <small>({r["Sınıf"]})</small><br><span class="rank-tag">{r["Rütbe"]}</span><br>⭐ {int(r["Puan"])} Puan</div>''', unsafe_allow_html=True)