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

# --- 2. TÜM HAFIZA DEĞİŞKENLERİNİ BAŞLAT (HATA ÖNLEYİCİ) ---
#
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

# --- 3. GIF OYNATICI (BASE64 İLE AKICI HAREKET) ---
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
        font-weight: 500; font-size: 1.2rem; text-align: center; max-width: 700px;
        box-shadow: 4px 4px 15px rgba(0,0,0,0.1);
    }
    .pito-bubble:after {
        content: ''; position: absolute; bottom: -20px; left: 50%; transform: translateX(-50%);
        border-width: 20px 20px 0; border-style: solid; border-color: #3a7bd5 transparent;
    }
    .leaderboard-card { background: linear-gradient(135deg, #1e1e1e, #2d2d2d); border-radius: 12px; padding: 10px; margin-bottom: 8px; color: white; border: 1px solid #444; }
    .champion-card { background: linear-gradient(135deg, #FFD700, #FFA500); border-radius: 15px; padding: 15px; margin-top: 20px; color: #1e1e1e; text-align: center; font-weight: bold; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3); }
    .stButton > button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important; color: white !important; font-weight: bold; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. VERİ TABANI YÖNETİMİ ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db(use_cache=True):
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=0 if not use_cache else 60)
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
                        m_v, e_v = int(row['Mevcut Modül']), int(row['Mevcut Egzersiz'])
                        st.session_state.update({'student_no': in_no_raw, 'student_name': row["Öğrencinin Adı"], 'student_class': row["Sınıf"], 'total_score': int(row["Puan"]), 'db_module': m_v, 'db_exercise': e_v, 'current_module': min(m_v, 7), 'current_exercise': e_v if m_v < 8 else 0, 'completed_modules': [True if x == "1" else False for x in str(row["Tamamlanan Modüller"]).split(",")], 'is_logged_in': True, 'pito_emotion': "pito_dusunuyor" if m_v < 8 else "pito_mezun"})
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

# --- 6. MÜFREDAT VE EGZERSİZLER ---
training_data = [
    {"module_title": "1. Giriş ve Çıktı", "exercises": [
        {"msg": "Python'da ekrana yazı yazdırmak için **print()** kullanılır. Metinler mutlaka **tırnak** içinde olmalıdır. Hadi dene: Ekrana **'Merhaba Pito'** yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o, "solution": "print('Merhaba Pito')"},
        {"msg": "Sayıları yazdırırken **tırnak kullanılmaz.** Şimdi ekrana **100** sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o, "solution": "print(100)"},
        {"msg": "Metin ve sayıyı birleştirmek için **virgül (,)** kullanılır. Hadi dene: **'Puan:'** metni ile **100** sayısını yan yana yazdır.", "task": "print('Puan:', ___)", "check": lambda c, o: "100" in o, "solution": "print('Puan:', 100)"},
        {"msg": "**# (Diyez)** işareti Python tarafından okunmaz. Bir yorum satırı ekle.", "task": "___ Bu bir not", "check": lambda c, o: "#" in c, "solution": "# Notum"},
        {"msg": "Alt satıra geçmek için **'\\n'** kullanılır. Tek print içinde **'Üst'** ve **'Alt'** kelimelerini farklı satırlarda yazdır.", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o, "solution": "print('Üst' + '\\n' + 'Alt')"}
    ]},
    {"module_title": "2. Değişkenler", "exercises": [
        {"msg": "Değişkenler bilgi saklar. **yas** değişkenine **15** ata ve yazdır.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o, "solution": "yas = 15\nprint(yas)"},
        {"msg": "**isim** değişkenine **'Pito'** değerini ata ve yazdır.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o, "solution": "isim = 'Pito'\nprint(isim)"},
        {"msg": "**input()** ile dışarıdan bilgi alırız. **'Adın: '** sorusuyla bir input al ve yazdır.", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c, "solution": "ad = input('Adın: ')\nprint(ad)"},
        {"msg": "**str()** fonksiyonu sayıyı metne çevirir. **s = 10** değişkenini metne çevirip yazdır.", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c, "solution": "s = 10\nprint(str(s))"},
        {"msg": "Input verisini sayıya çevirmek için **int()** kullanılır. Gelen inputu **int**'e çevir.", "task": "n = ___(___('Sayı: '))\nprint(n + 1)", "check": lambda c, o: "int" in c and "input" in c, "solution": "n = int(input('10'))\nprint(n+1)"}
    ]},
    {"module_title": "3. Karar Yapıları", "exercises": [{"msg": "Eşitlik için '==' kullanılır. 10 **10'a eşitse** 'X' yazdır.", "task": "if 10 ___ 10: print('X')", "check": lambda c, o: "==" in c, "solution": "if 10 == 10: print('X')"}, {"msg": "Şart yanlışsa **else:** çalışır. Bir else bloğu kur.", "task": "if 5>10: pass\n___: print('Y')", "check": lambda c, o: "else" in c, "solution": "if 5>10: pass\nelse: print('Y')"}, {"msg": "**'>='** büyük veya eşiti kontrol eder. Kullan ve 'Z' yazdır.", "task": "if 5 ___ 5: print('Z')", "check": lambda c, o: ">=" in c, "solution": "if 5 >= 5: print('Z')"}, {"msg": "**'and'** iki şartı da bekler. Kullan ve 'OK' yazdır.", "task": "if 1==1 ___ 2==2: print('OK')", "check": lambda c, o: "and" in c, "solution": "if 1==1 and 2==2: print('OK')"}, {"msg": "**'elif'** alternatif şarttır. Kullan ve 'A' yazdır.", "task": "if 5>10: pass\n___ 5==5: print('A')", "check": lambda c, o: "elif" in c, "solution": "if 5>10: pass\nelif 5==5: print('A')"}]},
    {"module_title": "4. Döngüler", "exercises": [{"msg": "3 kez 'X' yazdır.", "task": "for i in ___(3): print('X')", "check": lambda c, o: o.count("X")==3, "solution": "for i in range(3): print('X')"}, {"msg": "while döngüsü kur.", "task": "i=0\n___ i<1: print('Y'); i+=1", "check": lambda c, o: "while" in c, "solution": "i=0\nwhile i<1:\n    print('Y')\n    i+=1"}, {"msg": "**'break'** döngüyü bitirir. Kullan.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "break" in c, "solution": "for i in range(3):\n    if i==1: break\n    print(i)"}, {"msg": "**'continue'** adımı atlar. Kullan.", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "continue" in c, "solution": "for i in range(3):\n    if i==1: continue\n    print(i)"}, {"msg": "i sayacını yazdır.", "task": "for i in range(2): print(___)", "check": lambda c, o: "1" in o, "solution": "for i in range(2): print(i)"}]},
    {"module_title": "5. Listeler", "exercises": [{"msg": "Liste oluştur.", "task": "L = [___, 20]", "check": lambda c, o: "10" in c, "solution": "L = [10, 20]\nprint(L)"}, {"msg": "İlk elemana (0) eriş.", "task": "L=[5,6]\nprint(L[___])", "check": lambda c, o: "5" in o, "solution": "L=[5,6]\nprint(L[0])"}, {"msg": "**len()** boyutu ölçer. Yazdır.", "task": "L=[1,2]\nprint(___(L))", "check": lambda c, o: "2" in o, "solution": "L=[1,2]\nprint(len(L))"}, {"msg": "**append()** veri ekler. 30 ekle.", "task": "L=[10]\nL.___(___)\nprint(L)", "check": lambda c, o: "30" in o, "solution": "L=[10]\nL.append(30)\nprint(L)"}, {"msg": "**pop()** veri siler. Sonuncuyu sil.", "task": "L=[1,2]\nL.___()\nprint(L)", "check": lambda c, o: "1" in o, "solution": "L=[1,2]\nL.pop()\nprint(L)"}]},
    {"module_title": "6. Fonksiyonlar", "exercises": [{"msg": "**def** ile fonksiyon tanımla.", "task": "___ f(): print('X')", "check": lambda c, o: "def" in c, "solution": "def f(): print('X')\nf()"}, {"msg": "**Tuple** `()` ile oluşturulur. Bir tane kur.", "task": "t = (___, 2)\nprint(t)", "check": lambda c, o: "1" in c, "solution": "t = (1, 2)\nprint(t)"}, {"msg": "Sözlükte 'ad' anahtarına 'Pito' ata.", "task": "d = {'ad': '___'}\nprint(d['ad'])", "check": lambda c, o: "Pito" in c, "solution": "d = {'ad': 'Pito'}\nprint(d['ad'])"}, {"msg": "**keys()** anahtarları getirir. Yazdır.", "task": "d={'a':1}\nprint(d.___())", "check": lambda c, o: "keys" in c, "solution": "d={'a':1}\nprint(d.keys())"}, {"msg": "**Set** benzersiz veri tutar. Kur.", "task": "s = {1, 2, ___}\nprint(s)", "check": lambda c, o: "1" in c, "solution": "s = {1, 2, 1}\nprint(s)"}]},
    {"module_title": "7. OOP", "exercises": [{"msg": "**class** ile Robot sınıfı kur.", "task": "___ Robot: pass", "check": lambda c, o: "class" in c, "solution": "class Robot: pass"}, {"msg": "Sınıftan nesne (p) üret.", "task": "class R: pass\np = ___()", "check": lambda c, o: "R()" in c, "solution": "class R: pass\np = R()"}, {"msg": "Özellik (renk) ata.", "task": "class R: pass\np=R()\np.___ = 'Mavi'\nprint(p.renk)", "check": lambda c, o: "renk" in c, "solution": "class R: pass\np=R()\np.renk = 'Mavi'\nprint(p.renk)"}, {"msg": "Metotlara **self** eklenir. **ses** metodunu kur.", "task": "class R:\n def ___(self):\n  print('Bip!')", "check": lambda c, o: "ses" in c, "solution": "class R:\n    def ses(self): print('Bip!')\nr = R()\nr.ses()"}, {"msg": "Metodu (s) çağır.", "task": "class R:\n def s(self): print('X')\nr=R()\nr.___()", "check": lambda c, o: "s()" in c, "solution": "class R:\n    def s(self): print('X')\nr=R()\nr.s()"}]},
    {"module_title": "8. Dosyalar", "exercises": [{"msg": "open() ve 'w' ile aç.", "task": "dosya = ___('n.txt', '___')", "check": lambda c, o: "open" in c, "solution": "f = open('n.txt', 'w')\nf.write('X')\nf.close()"}, {"msg": "write() ile 'Pito' yaz.", "task": "f = open('t.txt', 'w'); f.___('Pito'); f.close()", "check": lambda c, o: "write" in c, "solution": "f = open('t.txt', 'w'); f.write('Pito'); f.close()"}, {"msg": "'r' ile okuma modunda aç.", "task": "f = open('t.txt', '___')", "check": lambda c, o: "'r'" in c, "solution": "f = open('t.txt', 'r'); f.close()"}, {"msg": "read() ile oku ve yazdır.", "task": "f = open('t.txt', 'r')\nprint(f.___())\nf.close()", "check": lambda c, o: "read" in c, "solution": "f = open('t.txt', 'w'); f.write('X'); f.close(); f = open('t.txt', 'r'); print(f.read()); f.close()"}, {"msg": "close() ile dosyayı kapat.", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o: "close" in c, "solution": "f = open('t.txt', 'r'); f.close()"}]}
]

# --- 7. KOD ÇALIŞTIRICI ---
def run_pito_code(c, user_input="10"):
    old_stdout, new_stdout = sys.stdout, StringIO()
    sys.stdout = new_stdout
    if "input(" in c and not user_input: return "⚠️ Terminale veri gir!"
    try:
        # Placeholder'ları temizle
        safe_code = c.replace("___", "None")
        exec(safe_code, {"input": lambda p: str(user_input), "print": print, "int": int, "str": str, "len": len, "open": open, "range": range})
        sys.stdout = old_stdout
        return new_stdout.getvalue()
    except Exception as e: 
        sys.stdout = old_stdout
        return f"Hata: {e}"

# --- 8. ARA YÜZ DÜZENİ ---
col_main, col_side = st.columns([3, 1])
student_rank = RUTBELER[sum(st.session_state.completed_modules)]

with col_main:
    st.markdown(f"#### 👋 {student_rank} {st.session_state.student_name} | ⭐ Puan: {int(st.session_state.total_score)}")
    
    if st.session_state.db_module >= 8:
        if not st.session_state.celebrated:
            st.balloons(); st.session_state.celebrated = True
            st.session_state.pito_emotion = "pito_mezun"
        st.success("### 🎉 Tebrikler! Eğitimi Başarıyla Tamamladın.")
        st.markdown('<div class="pito-bubble">Python yolculuğunu bitirdin! Puanın kaydedildi. Aşağıdan içerikleri inceleyebilir veya sıfırdan başlayabilirsin.</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Eğitimi Tekrar Al (Puan Sıfırlanır)"):
                st.session_state.update({'db_module': 0, 'db_exercise': 0, 'total_score': 0, 'current_module': 0, 'current_exercise': 0, 'completed_modules': [False]*8, 'scored_exercises': set(), 'celebrated': False, 'pito_emotion': "pito_dusunuyor"})
                force_save(); st.rerun()
        with c2:
            if st.button("🏆 Liderlik Listesinde Kal"): st.info("Puanın korunacak!")

    mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} Modül {i+1}" for i in range(8)]
    sel_mod = st.selectbox("Ders Seç (İnceleme Modu):", mod_titles, index=st.session_state.current_module)
    m_idx = mod_titles.index(sel_mod)
    if m_idx != st.session_state.current_module:
        st.session_state.update({'current_module': m_idx, 'current_exercise': 0})
        st.rerun()

    st.divider()
    e_idx = st.session_state.current_exercise
    curr_ex = training_data[m_idx]["exercises"][e_idx]
    is_locked = (m_idx < st.session_state.db_module)

    cp1, cp2 = st.columns([1, 4])
    with cp1: st.markdown(get_pito_gif(st.session_state.pito_emotion, width=180), unsafe_allow_html=True)
    with cp2:
        st.info(f"##### 🗣️ Pito:\n{curr_ex['msg']}")
        st.caption(f"Adım: {e_idx + 1}/5 | " + ("🔒 İnceleme Modu" if is_locked else f"🎁 Puan: {st.session_state.current_potential_score}"))

    code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=180, readonly=is_locked, key=f"ace_{m_idx}_{e_idx}", auto_update=True)

    if is_locked:
        st.success(f"**✅ Pito'nun Çözümü:**")
        st.code(curr_ex['solution'], language="python")
        sol_out = run_pito_code(curr_ex['solution'], "10") 
        st.markdown(f"**📟 Beklenen Çıktı:**")
        st.code(sol_out if sol_out else "Kod çalıştı!")
    else:
        u_in = st.text_input("👇 Terminal:", key=f"t_{m_idx}_{e_idx}") if "input(" in code else ""
        if st.button("🔍 Kontrol Et"):
            out = run_pito_code(code, u_in)
            # DÜZELTME: Net geri bildirim mekanizması
            if "⚠️" in out or "Hata" in out:
                st.error(f"**❌ Hata Oluştu!**\n{out}")
                st.session_state.pito_emotion = "pito_hata"
            elif curr_ex['check'](code, out) and "___" not in code:
                st.subheader("📟 Çıktı")
                st.code(out)
                st.session_state.update({'exercise_passed': True, 'pito_emotion': "pito_basari"})
                if f"{m_idx}_{e_idx}" not in st.session_state.scored_exercises:
                    st.session_state.total_score += st.session_state.current_potential_score
                    st.session_state.scored_exercises.add(f"{m_idx}_{e_idx}")
                    if st.session_state.db_exercise < 4: st.session_state.db_exercise += 1
                    else:
                        st.session_state.db_module += 1; st.session_state.db_exercise = 0; st.session_state.completed_modules[m_idx] = True
                    force_save()
                st.success("Tebrikler! ✅")
            else:
                st.session_state.pito_emotion = "pito_hata"
                st.error("**❌ Yanlış veya eksik çözüm!** Pito'nun ne dediğini tekrar oku ve kodu düzelt.")
            st.rerun()

    if st.session_state.exercise_passed or is_locked:
        c_back, c_next = st.columns(2)
        with c_back:
            if e_idx > 0:
                if st.button("⬅️ Önceki"): st.session_state.current_exercise -= 1; st.rerun()
        with c_next:
            if e_idx < 4:
                if st.button("➡️ Sonraki"): st.session_state.update({'current_exercise': e_idx + 1, 'exercise_passed': False, 'pito_emotion': "pito_dusunuyor"}); st.rerun()
            elif m_idx < 7:
                if st.button("🏆 Modülü Bitir"): st.session_state.update({'current_module': m_idx + 1, 'current_exercise': 0, 'pito_emotion': "pito_dusunuyor"}); st.rerun()

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
