import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. SAYFA VE GÖRSEL AYARLAR ---
st.set_page_config(
    layout="wide", 
    page_title="Pito Akademi: Python Atölyesi",
    initial_sidebar_state="collapsed"
)

# Mobil uyumluluk için özel CSS
st.markdown("""
    <style>
    .stButton > button { width: 100%; border-radius: 8px; height: 3.5em; margin-bottom: 5px; font-weight: bold; }
    .ace_editor { border-radius: 10px; border: 1px solid #333; }
    div[data-testid="stExpander"] { border-radius: 10px; background-color: #1e1e1e; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GOOGLE SHEETS BAĞLANTISI ---
# ÖNEMLİ: Kendi Google Sheets linkinizi buraya yapıştırın
SHEET_URL = "https://docs.google.com/spreadsheets/d/BURAYA_KENDI_LINKINIZI_EKLEYIN/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

def get_leaderboard():
    try:
        df = conn.read(spreadsheet=SHEET_URL, usecols=[0,1,2,3])
        df = df.dropna(subset=["Öğrenci Adı"])
        return df.sort_values(by="Puan", ascending=False).drop_duplicates(subset=["Öğrenci Adı"])
    except:
        return pd.DataFrame(columns=["Öğrenci Adı", "Puan", "Rütbe", "Tarih"])

def save_score(name, score, rank):
    try:
        df = get_leaderboard()
        new_row = pd.DataFrame([[name, score, rank, datetime.now().strftime("%d/%m/%Y %H:%M")]], 
                               columns=["Öğrenci Adı", "Puan", "Rütbe", "Tarih"])
        updated_df = pd.concat([df, new_row], ignore_index=True)
        conn.update(spreadsheet=SHEET_URL, data=updated_df)
        st.toast("Skorun buluta kaydedildi! ☁️", icon="✅")
    except Exception as e:
        st.error(f"Kayıt Hatası: {e}. Lütfen Sheets linkini ve izinlerini kontrol edin.")

# --- 3. SESSION STATE (DURUM TAKİBİ) ---
if 'completed_modules' not in st.session_state: st.session_state.completed_modules = [False] * 8
if 'current_module' not in st.session_state: st.session_state.current_module = 0
if 'current_exercise' not in st.session_state: st.session_state.current_exercise = 0
if 'exercise_passed' not in st.session_state: st.session_state.exercise_passed = False
if 'total_score' not in st.session_state: st.session_state.total_score = 0
if 'scored_exercises' not in st.session_state: st.session_state.scored_exercises = set()
if 'current_potential_score' not in st.session_state: st.session_state.current_potential_score = 20

def get_rank(score):
    if score < 200: return "🌱 Python Çırağı"
    if score < 500: return "💻 Kod Yazarı"
    if score < 850: return "🛠️ Yazılım Geliştirici"
    return "🏆 Python Ustası"

# --- 4. ORİJİNAL 8 MODÜL İÇERİĞİ ---
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
        {"msg": "Değilse Eğer (elif).", "task": "x = 60\nif x > 80: pass\n___ x > 50: print('B')", "check": lambda c, o: "elif" in c}
    ]},
    {"module_title": "4. Döngü Yapıları", "exercises": [
        {"msg": "3 kez dönen for döngüsü.", "task": "for i in ___(3): print('X')", "check": lambda c, o: o.count("X") == 3},
        {"msg": "Döngü sayacını yazdır.", "task": "for i in range(2): print(___)", "check": lambda c, o: "1" in o},
        {"msg": "While döngüsü başlat.", "task": "i=0\n___ i<1: print('Y'); i+=1", "check": lambda c, o: "while" in c},
        {"msg": "Döngüyü anında kır (break).", "task": "for i in range(5):\n if i==2: ___\n print(i)", "check": lambda c, o: "2" not in o},
        {"msg": "Adımı atla (continue).", "task": "for i in range(3):\n if i==1: ___\n print(i)", "check": lambda c, o: "1" not in o}
    ]},
    {"module_title": "5. Listeler & Fonksiyonlar", "exercises": [
        {"msg": "Liste oluştur [10, 20].", "task": "L = [___, 20]\nprint(L)", "check": lambda c, o: "10" in o},
        {"msg": "İlk elemana eriş (indeks 0).", "task": "L = [5, 6]\nprint(L[___])", "check": lambda c, o: "5" in o},
        {"msg": "Listenin uzunluğunu bul (len).", "task": "L = [1, 2]\nprint(___(L))", "check": lambda c, o: "2" in o},
        {"msg": "Fonksiyon tanımla (def).", "task": "___ selam(): print('X')", "check": lambda c, o: "def" in c},
        {"msg": "Fonksiyonu çağır.", "task": "def selam(): print('Pito')\n___", "check": lambda c, o: "Pito" in o}
    ]},
    {"module_title": "6. İleri Veri Yapıları", "exercises": [
        {"msg": "Tuple oluştur (1, 2).", "task": "t = (___, 2)\nprint(t)", "check": lambda c, o: "1" in o},
        {"msg": "Set (küme) tanımla {1, 2}.", "task": "s = {1, 2, ___}\nprint(s)", "check": lambda c, o: "1" in o},
        {"msg": "Sözlük oluştur 'ad': 'Pito'.", "task": "d = {'ad': '___'}\nprint(d['ad'])", "check": lambda c, o: "Pito" in o},
        {"msg": "Sözlüğe anahtar ekle.", "task": "d = {'a': 1}\nd['___'] = 2", "check": lambda c, o: "'b'" in c or '"b"' in c},
        {"msg": "Tüm anahtarları listele.", "task": "d = {'a': 1}\nprint(d.___())", "check": lambda c, o: "keys" in c}
    ]},
    {"module_title": "7. OOP (Nesne Yönelimli)", "exercises": [
        {"msg": "Sınıf tanımla (class).", "task": "___ Robot: pass", "check": lambda c, o: "class" in c},
        {"msg": "Sınıftan nesne oluştur.", "task": "class R: pass\np = ___()", "check": lambda c, o: "R()" in c},
        {"msg": "Nesneye nitelik ata.", "task": "class R: pass\np = R()\np.___ = 'Mavi'", "check": lambda c, o: "renk" in c},
        {"msg": "Metot (fonksiyon) ekle.", "task": "class R:\n def ___(self): print('Bip')", "check": lambda c, o: "ses" in c},
        {"msg": "Metodu çağır.", "task": "class R: def s(self): print('X')\nr = R()\nr.___()", "check": lambda c, o: "s()" in c}
    ]},
    {"module_title": "8. Dosya İşlemleri", "exercises": [
        {"msg": "Dosya aç (open).", "task": "f = ___('not.txt', 'w')", "check": lambda c, o: "open" in c},
        {"msg": "Dosyaya yaz (write).", "task": "f = open('t.txt', 'w')\nf.___('Pito')\nf.close()", "check": lambda c, o: "write" in c},
        {"msg": "Okuma modu ('r') kullan.", "task": "f = open('t.txt', '___')", "check": lambda c, o: "'r'" in c},
        {"msg": "İçeriği oku (read).", "task": "f = open('t.txt', 'r')\ni = f.___()\nprint(i)", "check": lambda c, o: "read" in c},
        {"msg": "Dosyayı kapat (close).", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o: "close" in c}
    ]}
]

# --- 5. ÜST PANEL (DURUM VE NAVİGASYON) ---
st.markdown(f"### {get_rank(st.session_state.total_score)} | ⭐ Puan: {st.session_state.total_score}")
st.progress(min(st.session_state.total_score / 1000, 1.0))

mod_titles = [f"{'✅' if st.session_state.completed_modules[i] else '📖'} {m['module_title']}" for i, m in enumerate(training_data)]
selected_mod = st.selectbox("Gitmek istediğin Modül:", mod_titles, index=st.session_state.current_module)
new_mod_idx = mod_titles.index(selected_mod)

if new_mod_idx != st.session_state.current_module:
    st.session_state.current_module = new_mod_idx
    st.session_state.current_exercise = 0
    st.session_state.exercise_passed = False
    st.session_state.current_potential_score = 20
    st.rerun()

st.divider()

# --- 6. ANA İÇERİK ---
m_idx = st.session_state.current_module
e_idx = st.session_state.current_exercise
curr_ex = training_data[m_idx]["exercises"][e_idx]

# Pito ve Görev Bilgisi
col_pito, col_info = st.columns([1, 4])
with col_pito:
    try: st.image("assets/pito.png", width=80)
    except: st.image("https://img.icons8.com/fluency/96/robot-viewer.png", width=80)
with col_info:
    st.info(f"**Pito:** {curr_ex['msg']}")
    st.caption(f"🎁 Bu görevden kazanılacak: {st.session_state.current_potential_score} Puan | Adım: {e_idx + 1}/5")

# Kod Editörü
code = st_ace(
    value=curr_ex['task'], 
    language="python", 
    theme="dracula", 
    font_size=14, 
    height=180, 
    wrap=True, 
    key=f"ace_{m_idx}_{e_idx}"
)

# Kontrol ve İlerleme Butonları
if st.button("🔍 Görevi Kontrol Et", use_container_width=True):
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    def mock_input(p=""): return "10"
    
    try:
        exec(code.replace("___", "None"), {"input": mock_input})
        sys.stdout = old_stdout
        output = redirected_output.getvalue()
        
        st.subheader("📟 Terminal Çıktısı")
        st.code(output if output else "Pito: Kodun başarıyla çalıştı!")
        
        if curr_ex['check'](code, output) and "___" not in code:
            st.session_state.exercise_passed = True
            ex_key = f"{m_idx}_{e_idx}"
            if ex_key not in st.session_state.scored_exercises:
                st.session_state.total_score += st.session_state.current_potential_score
                st.session_state.scored_exercises.add(ex_key)
                st.toast(f"+{st.session_state.current_potential_score} Puan!", icon="💰")
            st.success("Harika! Doğru cevap. ✅")
        else:
            if not st.session_state.exercise_passed:
                st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
            st.warning(f"Hatalı! Alabileceğin puan {st.session_state.current_potential_score}'ye düştü.")
    except Exception as e:
        sys.stdout = old_stdout
        if not st.session_state.exercise_passed:
            st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
        st.error(f"Hata! Puanın azaldı. {e}")

if st.session_state.exercise_passed:
    if e_idx < 4:
        if st.button("➡️ Sonraki Adıma Geç", use_container_width=True):
            st.session_state.current_exercise += 1
            st.session_state.exercise_passed = False
            st.session_state.current_potential_score = 20
            st.rerun()
    else:
        if st.button("🏆 Modülü Tamamla", use_container_width=True):
            st.session_state.completed_modules[m_idx] = True
            st.session_state.exercise_passed = False
            st.session_state.current_potential_score = 20
            if m_idx < 7:
                st.session_state.current_module += 1
                st.session_state.current_exercise = 0
            st.balloons(); st.rerun()

# --- 7. LİDERLİK TABLOSU ---
st.divider()
with st.expander("🏆 Liderlik Tablosu & Skor Kaydı"):
    stu_name = st.text_input("Adın Soyadın:", placeholder="Örn: Ahmet Yılmaz")
    if st.button("Skorumu Kaydet"):
        if stu_name:
            save_score(stu_name, st.session_state.total_score, get_rank(st.session_state.total_score))
            st.success("Skorun kaydedildi! Tabloyu güncellemek için sayfayı yenileyebilirsin.")
    
    st.subheader("En İyi 10 Öğrenci")
    df_lead = get_leaderboard()
    if not df_lead.empty:
        st.dataframe(df_lead.head(10), use_container_width=True)
    else:
        st.write("Henüz kayıt bulunamadı.")