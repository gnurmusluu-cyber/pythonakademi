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

RUTBELER = [
    "🥚 Yeni Başlayan", "🌱 Python Çırağı", "🪵 Kod Oduncusu", "🧱 Mantık Mimarı", 
    "🌀 Döngü Ustası", "📋 Liste Uzmanı", "📦 Fonksiyon Kaptanı", "🤖 OOP Robotu", "🏆 Python Kahramanı"
]

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
    .solution-header { color: #3a7bd5; font-weight: bold; font-size: 1.1rem; margin-bottom: 8px; }

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
    .restart-btn > button { background: linear-gradient(45deg, #e53935, #e35d5b) !important; }
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
        return pd.DataFrame(columns=["Okul No", "Öğrencinin Adı", "Sınıf", "Puan", "Rütbe", "Tamamlanan Modüller", "Mevcut Modül", "Mevcut Egzersiz", "Tarih"])

def force_save():
    try:
        no = str(st.session_state.student_no).strip()
        score = int(st.session_state.total_score)
        df_all = get_db(use_cache=False)
        if df_all.empty and st.session_state.db_module > 0: return 
        df_clean = df_all[df_all["Okul No"] != no]
        progress = ",".join(["1" if m else "0" for m in st.session_state.completed_modules])
        rank = RUTBELER[sum(st.session_state.completed_modules)]
        new_row = pd.DataFrame([[no, st.session_state.student_name, st.session_state.student_class, score, rank, progress, st.session_state.db_module, st.session_state.db_exercise, datetime.now().strftime("%H:%M:%S")]], 
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
        
        if in_no_raw and not in_no_raw.isdigit():
            st.error("⚠️ Hata: Okul numarası sadece rakamlardan oluşmalıdır!")
        elif in_no_raw:
            if st.session_state.rejected_user:
                st.session_state.rejected_user = False
                
            df = get_db(use_cache=False)
            user_data = df[df["Okul No"] == in_no_raw]
            
            if not user_data.empty:
                row = user_data.iloc[0]
                st.info(f"🔍 Bu numara **{row['Öğrencinin Adı']}** adına kayıtlı.")
                st.markdown("### Sen bu kişi misin? 🤔")
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Evet, Benim"):
                        m_v, e_v = int(row['Mevcut Modül']), int(row['Mevcut Egzersiz'])
                        st.session_state.update({'student_no': str(row["Okul No"]), 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': m_v, 'db_exercise': e_v, 'current_module': min(m_v, 7), 'current_exercise': e_v, 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True})
                        st.rerun()
                with c2:
                    if st.button("❌ Hayır, Ben Değilim"):
                        st.session_state.rejected_user = True
                        if "login_field" in st.session_state:
                            del st.session_state["login_field"]
                        st.rerun()
            else:
                st.info("Yeni bir maceracı! Bilgilerini tamamla:")
                in_name = st.text_input("Adın Soyadın:", key="new_name")
                in_class = st.selectbox("Sınıfın:", SINIFLAR, key="new_class")
                if st.button("Maceraya Başla! ✨"):
                    if in_name.strip():
                        st.session_state.update({'student_no': in_no_raw, 'student_name': in_name.strip(), 'student_class': in_class, 'is_logged_in': True})
                        force_save(); st.rerun()
    st.stop()

# --- 5. MÜFREDAT ---
training_data = [
    {"module_title": "1. Giriş ve Çıktı", "exercises": [
        {"msg": "Programımızın dış dünyayla iletişim kurmasının en temel yolu **print()** fonksiyonudur. Metinsel ifadeleri mutlaka **tırnak** içinde yazmalısın. Hadi dene: Ekrana **'Merhaba Pito'** yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')"},
        {"msg": "Python'da matematiksel değer olan sayıları ekrana yazdırırken **tırnak işareti kullanmayız.** Şimdi ekrana **100** sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o, "solution": "print(100)"},
        {"msg": "print() içinde farklı verileri ayırmak için **virgül (,)** kullanırız. Hadi dene: **'Puan:'** metni ile **100** sayısını yan yana yazdır.", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o, "solution": "print('Puan:', 100)"},
        {"msg": "**# (Diyez)** işaretiyle başlayan satırlar Python tarafından okunmaz. Hadi dene: Bir **yorum satırı** oluştur.", "task": "___ Bu bir yorumdur", "check": lambda c, o: "#" in c, "solution": "# Kodlarımı buraya yazıyorum"},
        {"msg": "Alt satıra geçmek için **'\\n'** karakteri kullanılır. Hadi dene: **'Üst'** ve **'Alt'** kelimelerini tek print içinde farklı satırlarda yazdır.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o, "solution": "print('Üst\\nAlt')"}
    ]},
    {"module_title": "2. Değişkenler", "exercises": [
        {"msg": "Değişkenler bilgileri hafızada saklamaya yarar. yas = 15 yazarak bir tam sayı değişkeni oluştur ve yazdır.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o, "solution": "yas = 15\nprint(yas)"},
        {"msg": "Hadi dene: **isim** adında bir değişken oluştur, içine **'Pito'** değerini ata ve ekrana yazdır.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o, "solution": "isim = 'Pito'\nprint(isim)"},
        {"msg": "**input()** ile kullanıcıdan bilgi alırız. Hadi dene: **'Adın: '** sorusuyla kullanıcıdan isim al ve yazdır.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c, "solution": "ad = input('Adın: ')\nprint(ad)"},
        {"msg": "**str()** fonksiyonu sayısal veriyi metne dönüştürür. Hadi dene: **s = 10** değişkenini metne çevirip yazdır.", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c, "solution": "s = 10\nprint(str(s))"},
        {"msg": "Matematiksel işlem için veriyi **int()** ile tam sayıya çevirmelisin. Hadi dene: n değişkenine bir **input** al ve bunu **int**'e çevir.", "task": "n = ___(___('S: '))\nprint(n + 1)", "check": lambda c, o: "int" in c and "input" in c, "solution": "n = int(input('10'))\nprint(n + 1)"}
    ]}
    # Not: Diğer modüller (3-8) aynı baseline yapısında devam etmektedir.
]

# --- 6. ARA YÜZ DÜZENİ ---
col_main, col_side = st.columns([3, 1])

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
        if st.button("🔄 Sıfırla"):
            st.session_state.update({'db_module':0, 'db_exercise':0, 'total_score':0, 'current_module':0, 'current_exercise':0, 'completed_modules':[False]*8, 'scored_exercises':set(), 'celebrated':False})
            force_save(); st.rerun()

    sel_mod = st.selectbox("Modül Seç:", [f"{'✅' if st.session_state.completed_modules[i] else '📖'} Modül {i+1}" for i in range(len(training_data))], index=m_idx)
    if training_data.index(training_data[m_idx]) != st.session_state.current_module:
        st.session_state.current_module, st.session_state.current_exercise = training_data.index(training_data[m_idx]), 0
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

    def run_pito_code(c, user_input="Pito"):
        old_stdout, new_stdout = sys.stdout, StringIO()
        sys.stdout = new_stdout
        try:
            # Mock Input: int bekleyen yere 10, metin bekleyen yere Pito gönderir
            mock_val = "10" if "int(" in c else str(user_input)
            exec(c.replace("___", "None"), {"input": lambda p: mock_val, "print": print, "int": int, "str": str, "len": len, "open": open, "range": range})
            sys.stdout = old_stdout
            return new_stdout.getvalue()
        except Exception as e:
            sys.stdout = old_stdout
            return f"Hata: {e}"

    if is_locked:
        st.markdown(f"""<div class="solution-guide"><div class="solution-header">✅ Pito'nun Çözüm Rehberi</div><b>Yönerge:</b> {curr_ex['msg']}</div>""", unsafe_allow_html=True)
        st.code(curr_ex['solution'], language="python")
        sol_out = run_pito_code(curr_ex['solution'], "Pito") 
        st.markdown("<b>Muhtemel Çıktı:</b>", unsafe_allow_html=True)
        st.code(sol_out if sol_out else "11" if "int(" in curr_ex['solution'] else "Kod çalıştı.")
    else:
        u_in = st.text_input("Giriş yap:", key=f"term_{m_idx}_{e_idx}") if "input(" in code else ""
        if st.button("🔍 Kontrol Et", use_container_width=True):
            out = run_pito_code(code, u_in or "10")
            if "Hata:" in out: 
                st.error(out)
                st.session_state.current_potential_score = max(5, st.session_state.current_potential_score - 5)
            else:
                # --- KRİTİK GÜNCELLEME: GERİ BİLDİRİM MANTIĞI ---
                is_task_correct = curr_ex['check'](code, out) and "___" not in code
                if is_task_correct:
                    st.success("Tebrikler! Görevi başarıyla tamamladın. ✅")
                    st.subheader("📟 Çıktı")
                    st.code(out if out else "[Çıktı Yok]")
                    st.session_state.exercise_passed = True
                    if f"{m_idx}_{e_idx}" not in st.session_state.scored_exercises:
                        st.session_state.total_score += st.session_state.current_potential_score
                        st.session_state.scored_exercises.add(f"{m_idx}_{e_idx}")
                        if st.session_state.db_exercise < len(training_data[m_idx]["exercises"]) - 1: st.session_state.db_exercise += 1
                        else: 
                            st.session_state.db_module += 1; st.session_state.db_exercise = 0
                            st.session_state.completed_modules[m_idx] = True
                        force_save()
                else:
                    st.warning("⚠️ Kodun teknik olarak çalıştı ama Pito'nun istediği görevi henüz tam yapamadın. Lütfen yönergeyi tekrar oku!")
                    st.subheader("📟 Senin Kodunun Çıktısı")
                    st.code(out if out else "[Çıktı Yok]")
                    st.session_state.current_potential_score = max(5, st.session_state.current_potential_score - 5)

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
    st.markdown(f"### 🏆 Liderlik Tablosu")
    df_lb = get_db()
    tab_class, tab_school = st.tabs(["👥 Sınıfım", "🏫 Okul"])
    with tab_class:
        df_c = df_lb[df_lb["Sınıf"] == st.session_state.student_class].sort_values(by="Puan", ascending=False).head(10)
        if not df_c.empty:
            for i, (_, r) in enumerate(df_c.iterrows()):
                st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]}</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)
    with tab_school:
        if not df_lb.empty:
            for i, (_, r) in enumerate(df_lb.sort_values(by="Puan", ascending=False).head(10).iterrows()):
                st.markdown(f'<div class="leaderboard-card"><b>{r["Rütbe"]} {r["Öğrencinin Adı"]} ({r["Sınıf"]})</b><br>{int(r["Puan"])} Puan</div>', unsafe_allow_html=True)