import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import os

# --- 1. SAYFA YAPILANDIRMASI ---
st.set_page_config(layout="wide", page_title="Pito Akademi", initial_sidebar_state="collapsed")

# Giriş ve Uygulama Tasarımı İçin CSS
st.markdown("""
    <style>
    .stButton > button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; background-color: #3a7bd5; color: white; }
    .ace_editor { border: 1px solid #444; border-radius: 12px; }
    .main-login-box { text-align: center; padding: 2rem; border-radius: 20px; background-color: #1e1e1e; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GOOGLE SHEETS BAĞLANTISI ---
# Sizin paylaştığınız tablo linki:
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lat8rO2qm9QnzEUYlzC_fypG3cRkGlJfSfTtwNvs318/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

def get_leaderboard():
    try:
        # ttl=0 ile verinin her zaman güncel gelmesini sağlıyoruz
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=["Öğrencinin Adı", "Puan", "Rütbe", "Tarih"])
        df = df.dropna(subset=["Öğrencinin Adı"])
        return df.sort_values(by="Puan", ascending=False).drop_duplicates(subset=["Öğrencinin Adı"])
    except Exception:
        return pd.DataFrame(columns=["Öğrencinin Adı", "Puan", "Rütbe", "Tarih"])

def auto_save_score():
    """Doğru cevap verildiğinde skoru otomatik kaydeder."""
    try:
        name = st.session_state.student_name
        score = st.session_state.total_score
        if score < 200: rank = "🌱 Python Çırağı"
        elif score < 500: rank = "💻 Kod Yazarı"
        elif score < 850: rank = "🛠️ Yazılım Geliştirici"
        else: rank = "🏆 Python Ustası"
        
        df_current = get_leaderboard()
        new_row = pd.DataFrame([[name, score, rank, datetime.now().strftime("%H:%M:%S")]], 
                               columns=["Öğrencinin Adı", "Puan", "Rütbe", "Tarih"])
        
        updated_df = pd.concat([df_current, new_row], ignore_index=True)
        updated_df = updated_df.sort_values(by="Puan", ascending=False).drop_duplicates(subset=["Öğrencinin Adı"])
        
        # Google Sheets'e güncel tabloyu gönder
        conn.update(spreadsheet=SHEET_URL, data=updated_df)
        st.toast(f"Skor buluta kaydedildi: {score}", icon="☁️")
    except Exception as e:
        st.error(f"Kayıt Hatası (Service Account ayarlarınızı kontrol edin): {e}")

# --- 3. SESSION STATE ---
if 'student_name' not in st.session_state: st.session_state.student_name = ""
if 'completed_modules' not in st.session_state: st.session_state.completed_modules = [False] * 8
if 'current_module' not in st.session_state: st.session_state.current_module = 0
if 'current_exercise' not in st.session_state: st.session_state.current_exercise = 0
if 'exercise_passed' not in st.session_state: st.session_state.exercise_passed = False
if 'total_score' not in st.session_state: st.session_state.total_score = 0
if 'scored_exercises' not in st.session_state: st.session_state.scored_exercises = set()
if 'current_potential_score' not in st.session_state: st.session_state.current_potential_score = 20

# --- 4. GÖRSELLEŞTİRİLMİŞ GİRİŞ EKRANI ---
if st.session_state.student_name == "":
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown("<div class='main-login-box'>", unsafe_allow_html=True)
        
        # Pito Resmi (En güvenli yükleme yöntemi)
        if os.path.exists("assets/pito.png"):
            st.image("assets/pito.png", width=180)
        else:
            # Yedek görsel (Eğer assets/pito.png bulunamazsa uygulama kırılmaz)
            st.image("https://img.icons8.com/fluency/150/robot-viewer.png", width=150)
            
        st.markdown("<h1 style='color:#00d2ff;'>Pito Akademi</h1>", unsafe_allow_html=True)
        st.write("Python macerana başlamak için ismini gir!")
        
        input_name = st.text_input("Adın Soyadın:", placeholder="Örn: Gamzenur Muslu", label_visibility="collapsed")
        if st.button("Atölyeye Giriş Yap 🚀"):
            if input_name.strip():
                st.session_state.student_name = input_name.strip()
                st.rerun()
            else:
                st.warning("Devam etmek için bir isim girmelisin!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 5. EĞİTİM İÇERİĞİ (8 MODÜL DEĞİŞTİRİLMEDİ) ---
def get_rank(score):
    if score < 200: return "🌱 Python Çırağı"
    if score < 500: return "💻 Kod Yazarı"
    if score < 850: return "🛠️ Yazılım Geliştirici"
    return "🏆 Python Ustası"

training_data = [
    {"module_title": "1. Giriş ve Çıktı", "exercises": [
        {"msg": "Ekrana 'Merhaba Pito' yazdır.", "task": "print('___')", "check": lambda c, o: "Merhaba Pito" in o},
        {"msg": "100 sayısını yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o},
        {"msg": "Puan: 100 yazdır (virgül kullan).", "task": "print('Puan:', ___)", "check": lambda c, o: "Puan: 100" in o},
        {"msg": "Yorum satırı ekle (#).", "task": "___ Bu bir yorumdur", "check": lambda c, o: "#" in c},
        {"msg": "Alt satır karakteri (\\n) kullan.", "task": "print('Üst' + '\\n' + 'Alt')", "check": lambda c, o: "\n" in o}
    ]},
    {"module_title": "2. Değişkenler ve Giriş", "exercises": [
        {"msg": "yas = 15 tanımla ve yazdır.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o},
        {"msg": "İsim ata (isim = 'Pito').", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: "Pito" in o},
        {"msg": "Kullanıcıdan veri al (input).", "task": "ad = ___('Adın: ')\nprint(ad)", "check": lambda c, o: "input" in c},
        {"msg": "Sayıyı metne çevir (str).", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c},
        {"msg": "Girişi tam sayıya çevir (int).", "task": "sayi = ___(___('S: '))\nprint(sayi + 5)", "check": lambda c, o: "int" in c}
    ]},
    {"module_title": "3. Karar Yapıları", "exercises": [
        {"msg": "Eşitlik kontrolü (==).", "task": "if 10 ___ 10: print('On')", "check": lambda c, o: "==" in c},
        {"msg": "Değilse durumu (else).", "task": "if 5 > 10: print('A')\n___: print('B')", "check": lambda c, o: "else" in c},
        {"msg": "85 ve üstü (>=).", "task": "if 90 ___ 85: print('Pekiyi')", "check": lambda c, o: ">=" in c},
        {"msg": "İki koşul (and).", "task": "if 1==1 ___ 2==2: print('Ok')", "check": lambda c, o: "and" in c},
        {"msg": "Değilse if (elif).", "task": "x = 60\nif x > 80: pass\n___ x > 50: print('B')", "check": lambda c, o: "elif" in c}
    ]},
    {"module_title": "4. Döngü Yapıları", "exercises": [
        {"msg": "3 kez dönen for döngüsü.", "task": "for i in ___(3): print('X')", "check": lambda c, o: o.count("X") == 3},
        {"msg": "Döngü sayacını yazdır.", "task": "for i in range(2): print(___)", "check": lambda c, o: "1" in o},
        {"msg": "While döngüsü başlat.", "task": "i=0\n___ i<1: print('Y'); i+=1", "check": lambda c, o: "while" in c},
        {"msg": "Döngüyü kır (break).", "task": "for i in range(5): if i==1: ___\n print(i)", "check": lambda c, o: "break" in c},
        {"msg": "Adımı atla (continue).", "task": "for i in range(3): if i==1: ___\n print(i)", "check": lambda c, o: "continue" in c}
    ]},
    {"module_title": "5. Listeler & Fonksiyonlar", "exercises": [
        {"msg": "Liste oluştur [10, 20].", "task": "L = [___, 20]\nprint(L)", "check": lambda c, o: "10" in o},
        {"msg": "İndeks 0'a eriş.", "task": "L = [5, 6]\nprint(L[___])", "check": lambda c, o: "5" in o},
        {"msg": "Uzunluk bul (len).", "task": "L = [1, 2]\nprint(___(L))", "check": lambda c, o: "2" in o},
        {"msg": "Fonksiyon tanımla (def).", "task": "___ f(): print('X')", "check": lambda c, o: "def" in c},
        {"msg": "Fonksiyonu çağır.", "task": "def f(): print('X')\n___", "check": lambda c, o: "f()" in c}
    ]},
    {"module_title": "6. İleri Veri Yapıları", "exercises": [
        {"msg": "Tuple oluştur (1, 2).", "task": "t = (___, 2)\nprint(t)", "check": lambda c, o: "1" in o},
        {"msg": "Set tanımla {1, 2}.", "task": "s = {1, 2, ___}\nprint(s)", "check": lambda c, o: "1" in o},
        {"msg": "Sözlük 'ad': 'Pito'.", "task": "d = {'ad': '___'}\nprint(d['ad'])", "check": lambda c, o: "Pito" in o},
        {"msg": "Anahtar ekle.", "task": "d = {'a': 1}\nd['___'] = 2", "check": lambda c, o: "'b'" in c or '"b"' in c},
        {"msg": "Anahtarları listele.", "task": "d = {'a': 1}\nprint(d.___())", "check": lambda c, o: "keys" in c}
    ]},
    {"module_title": "7. OOP (Nesne Yönelimli)", "exercises": [
        {"msg": "Sınıf tanımla (class).", "task": "___ Robot: pass", "check": lambda c, o: "class" in c},
        {"msg": "Nesne oluştur.", "task": "class R: pass\np = ___()", "check": lambda c, o: "R()" in c},
        {"msg": "Nitelik ata.", "task": "class R: pass\np = R()\np.___ = 'Mavi'", "check": lambda c, o: "renk" in c},
        {"msg": "Metot ekle.", "task": "class R: def ___(self): print('Bip')", "check": lambda c, o: "ses" in c},
        {"msg": "Metot çağır.", "task": "class R: def s(self): print('X')\nr = R()\nr.___()", "check": lambda c, o: "s()" in c}
    ]},
    {"module_title": "8. Dosya İşlemleri", "exercises": [
        {"msg": "Dosya aç (open).", "task": "f = ___('not.txt', 'w')", "check": lambda c, o: "open" in c},
        {"msg": "Dosyaya yaz (write).", "task": "f = open('t.txt', 'w')\nf.___('X')\nf.close()", "check": lambda c, o: "write" in c},
        {"msg": "Okuma modu ('r').", "task": "f = open('t.txt', '___')", "check": lambda c, o: "'r'" in c},
        {"msg": "İçeriği oku (read).", "task": "f = open('t.txt', 'r')\ni = f.___()\nprint(i)", "check": lambda c, o: "read" in c},
        {"msg": "Dosyayı kapat (close).", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o: "close" in c}
    ]}
]

# --- 6. ARA YÜZ VE EDİTÖR ---
st.markdown(f"#### 👋 Hoş geldin, {st.session_state.student_name} | **{get_rank(st.session_state.total_score)}** | ⭐ Puan: {st.session_state.total_score}")
st.progress(min(st.session_state.total_score / 1000, 1.0))

mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} {m['module_title']}" for i, m in enumerate(training_data)]
selected_mod = st.selectbox("Modül Seçiniz:", mod_titles, index=st.session_state.current_module)
new_idx = mod_titles.index(selected_mod)

if new_idx != st.session_state.current_module:
    st.session_state.current_module, st.session_state.current_exercise, st.session_state.exercise_passed, st.session_state.current_potential_score = new_idx, 0, False, 20
    st.rerun()

st.divider()

m_idx, e_idx = st.session_state.current_module, st.session_state.current_exercise
curr_ex = training_data[m_idx]["exercises"][e_idx]

st.info(f"**Pito:** {curr_ex['msg']}")
st.caption(f"🎁 Görev Puanı: {st.session_state.current_potential_score} | Adım: {e_idx + 1}/5")

code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=14, height=180, wrap=True, key=f"ace_{m_idx}_{e_idx}")

# --- VALUEERROR ÇÖZÜLEN KRİTİK ALAN ---
if st.button("🔍 Görevi Kontrol Et", use_container_width=True):
    old_stdout = sys.stdout 
    redirected_output = StringIO()
    sys.stdout = redirected_output # Yönlendirme güvenli yapıldı
    def mock_input(p=""): return "10"
    
    try:
        exec(code.replace("___", "None"), {"input": mock_input})
        sys.stdout = old_stdout 
        output = redirected_output.getvalue()
        
        st.subheader("📟 Çıktı")
        st.code(output if output else "Pito: Başarıyla çalıştı!")
        
        if curr_ex['check'](code, output) and "___" not in code:
            st.session_state.exercise_passed = True
            ex_key = f"{m_idx}_{e_idx}"
            if ex_key not in st.session_state.scored_exercises:
                st.session_state.total_score += st.session_state.current_potential_score
                st.session_state.scored_exercises.add(ex_key)
                auto_save_score() # Otomatik kayıt
            st.success("Tebrikler! ✅")
        else:
            if not st.session_state.exercise_passed:
                st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
            st.warning(f"Hatalı! Puanın {st.session_state.current_potential_score}'ye düştü.")
    except Exception as e:
        sys.stdout = old_stdout
        if not st.session_state.exercise_passed: st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
        st.error(f"Kod hatası! {e}")

if st.session_state.exercise_passed:
    if e_idx < 4:
        if st.button("➡️ Sonraki Adıma Geç", use_container_width=True):
            st.session_state.current_exercise, st.session_state.exercise_passed, st.session_state.current_potential_score = e_idx + 1, False, 20
            st.rerun()
    else:
        if st.button("🏆 Modülü Bitir", use_container_width=True):
            st.session_state.completed_modules[m_idx], st.session_state.exercise_passed, st.session_state.current_potential_score = True, False, 20
            if m_idx < 7: st.session_state.current_module, st.session_state.current_exercise = m_idx + 1, 0
            st.balloons(); st.rerun()

st.divider()
with st.expander("🏆 Liderlik Tablosu (Canlı)"):
    lb_df = get_leaderboard()
    if not lb_df.empty:
        st.dataframe(lb_df.head(10), use_container_width=True)
    else:
        st.write("Henüz kayıt bulunamadı.")