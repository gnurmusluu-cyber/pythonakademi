import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO

# Sayfa Yapılandırması
st.set_page_config(layout="wide", page_title="Pito Akademi: Puanlı Eğitim")

# --- SESSION STATE: İLERLEME VE PUANLAMA ---
if 'completed_modules' not in st.session_state:
    st.session_state.completed_modules = [False] * 8
if 'current_module' not in st.session_state:
    st.session_state.current_module = 0
if 'current_exercise' not in st.session_state:
    st.session_state.current_exercise = 0
if 'exercise_passed' not in st.session_state:
    st.session_state.exercise_passed = False
if 'total_score' not in st.session_state:
    st.session_state.total_score = 0
if 'scored_exercises' not in st.session_state:
    st.session_state.scored_exercises = set()
# YENİ: Mevcut egzersizden alınabilecek anlık puanı takip eder
if 'current_potential_score' not in st.session_state:
    st.session_state.current_potential_score = 20

# --- RÜTBE HESAPLAMA ---
def get_rank(score):
    if score < 100: return "🌱 Python Çırağı"
    if score < 300: return "💻 Kod Yazarı"
    if score < 600: return "🛠️ Yazılım Geliştirici"
    if score < 900: return "🚀 Algoritma Uzmanı"
    return "🏆 Python Ustası"

# --- EĞİTİM VERİLERİ (8 Modül x 5 Egzersiz) ---
training_data = [
    {
        "module_title": "1. Giriş ve Çıktı",
        "exercises": [
            {"msg": "Ekrana yazı yazdırmak için hangi komutu kullanırız?", "task": "___('Merhaba Pito')", "check": lambda c, o: "Merhaba Pito" in o},
            {"msg": "Sayıları tırnak kullanmadan 100 olarak yazdır.", "task": "print(___)", "check": lambda c, o: "100" in o},
            {"msg": "Virgül kullanarak 'Puan:' ve 100 sayısını beraber yazdır.", "task": "print('Puan:', ___)", "check": lambda c, o: "Puan: 100" in o},
            {"msg": "Yorum satırları için satır başına hangi işareti koymalısın?", "task": "___ Bu bir açıklama satırıdır", "check": lambda c, o: "#" in c and "___" not in c},
            {"msg": "Alt satıra geçmek için hangi özel karakteri kullanırız?", "task": "print('Üst' + '___' + 'Alt')", "check": lambda c, o: "\n" in o}
        ]
    },
    {
        "module_title": "2. Değişkenler ve Giriş",
        "exercises": [
            {"msg": "yas = 15 tanımla ve yazdır.", "task": "yas = ___\nprint(yas)", "check": lambda c, o: "15" in o},
            {"msg": "Metinsel (string) bir veri ata.", "task": "isim = '___'\nprint(isim)", "check": lambda c, o: len(o.strip()) > 0 and "___" not in c},
            {"msg": "Kullanıcıdan veri almak için hangi komut kullanılır?", "task": "ad = ___('Adın nedir? ')\nprint(ad)", "check": lambda c, o: "input" in c},
            {"msg": "Sayıyı metne çevirmek için hangi fonksiyonu kullanırız?", "task": "s = 10\nprint(___(s))", "check": lambda c, o: "str" in c and "10" in o},
            {"msg": "Matematiksel işlem için input'u hangi türe çevirmelisin?", "task": "sayi = ___(___('Sayı: '))\nprint(sayi + 5)", "check": lambda c, o: "int" in c and "input" in c}
        ]
    },
    {
        "module_title": "3. Karar Yapıları",
        "exercises": [
            {"msg": "Eşitlik kontrolü için operatörü tamamla.", "task": "s = 10\nif s ___ 10:\n    print('On')", "check": lambda c, o: "On" in o},
            {"msg": "Koşul doğru değilse ne çalışır?", "task": "s = 5\nif s > 10: print('A')\n___: print('B')", "check": lambda c, o: "Küçük" in o or "B" in o},
            {"msg": "85 ve üstü ise Pekiyi yazdır.", "task": "n = 90\nif n ___ 85: print('Pekiyi')", "check": lambda c, o: ">=" in c},
            {"msg": "Aynı anda iki koşulun doğruluğu için?", "task": "if 5 > 3 ___ 2 < 4: print('Evet')", "check": lambda c, o: "and" in c},
            {"msg": "Değilse Eğer (elif) komutunu tamamla.", "task": "p = 60\nif p > 85: print('A')\n___ p > 50: print('B')", "check": lambda c, o: "elif" in c}
        ]
    },
    {
        "module_title": "4. Döngü Yapıları",
        "exercises": [
            {"msg": "3 kez dönen bir range fonksiyonu yaz.", "task": "for i in ___(3): print('Pito')", "check": lambda c, o: o.count("Pito") == 3},
            {"msg": "Döngü içindeki sayacı yazdır.", "task": "for i in range(2): print(___)", "check": lambda c, o: "1" in o},
            {"msg": "While döngüsünü başlatmak için gereken komut?", "task": "i = 0\n___ i < 2:\n    print(i)\n    i += 1", "check": lambda c, o: "while" in c},
            {"msg": "Döngüyü anında kırmak için hangi komut kullanılır?", "task": "for i in range(5):\n    if i == 2: ___\n    print(i)", "check": lambda c, o: "1" in o and "2" not in o},
            {"msg": "O adımı atlayıp devam etmek için?", "task": "for i in range(3):\n    if i == 1: ___\n    print(i)", "check": lambda c, o: "0" in o and "2" in o}
        ]
    },
    {
        "module_title": "5. Listeler ve Fonksiyonlar",
        "exercises": [
            {"msg": "Liste oluştur: [10, 20] yaz ve yazdır.", "task": "liste = [___, 20]\nprint(liste)", "check": lambda c, o: "10" in o},
            {"msg": "Listenin ilk elemanına (indeks 0) eriş.", "task": "l = [50, 60]\nprint(l[___])", "check": lambda c, o: "50" in o},
            {"msg": "Listenin uzunluğunu bulan fonksiyon?", "task": "l = [1, 2, 3]\nprint(___(l))", "check": lambda c, o: "3" in o and "len" in c},
            {"msg": "Fonksiyon tanımlamak için anahtar kelime?", "task": "___ selam(): print('X')", "check": lambda c, o: "def" in c},
            {"msg": "Tanımladığın 'selam' fonksiyonunu çağır.", "task": "def selam(): print('Pito')\n___", "check": lambda c, o: "Pito" in o and "selam()" in c}
        ]
    },
    {
        "module_title": "6. İleri Veri Yapıları",
        "exercises": [
            {"msg": "Demet (tuple) oluştur: (1, 2) yaz.", "task": "d = (___, 2)\nprint(d)", "check": lambda c, o: "(1, 2)" in o},
            {"msg": "Küme (set) tanımla: {1, 2}.", "task": "k = {1, 2, ___}\nprint(k)", "check": lambda c, o: "1" in o},
            {"msg": "Sözlük (dict) oluştur: 'ad': 'Pito'.", "task": "s = {'ad': '___'}\nprint(s['ad'])", "check": lambda c, o: "Pito" in o},
            {"msg": "Sözlüğe yeni bir anahtar ekle.", "task": "s = {'a': 1}\ns['___'] = 2", "check": lambda c, o: "'b'" in c or '"b"' in c},
            {"msg": "Sözlükteki tüm anahtarları listele.", "task": "s = {'a': 1}\nprint(s.___())", "check": lambda c, o: "keys" in c}
        ]
    },
    {
        "module_title": "7. Nesne Yönelimli Programlama",
        "exercises": [
            {"msg": "Bir sınıf (class) tanımla.", "task": "___ Robot: pass", "check": lambda c, o: "class" in c},
            {"msg": "Sınıftan bir nesne oluştur.", "task": "class Robot: pass\npito = ___()", "check": lambda c, o: "Robot()" in c},
            {"msg": "Nesneye bir nitelik ata.", "task": "class R: pass\np = R()\np.___ = 'Mavi'", "check": lambda c, o: "renk" in c},
            {"msg": "Sınıf içine bir metot (fonksiyon) ekle.", "task": "class R:\n    def ___(self): print('Bip')", "check": lambda c, o: "ses" in c},
            {"msg": "Metodu nesne üzerinden çağır.", "task": "class R: def s(self): print('X')\ r = R()\nr.___()", "check": lambda c, o: "s()" in c}
        ]
    },
    {
        "module_title": "8. Dosya İşlemleri",
        "exercises": [
            {"msg": "Dosya açmak için hangi fonksiyon kullanılır?", "task": "f = ___('notlar.txt', 'w')", "check": lambda c, o: "open" in c},
            {"msg": "Dosyaya yazı yazmak için metodu tamamla.", "task": "f = open('t.txt', 'w')\nf.___('Pito')\nf.close()", "check": lambda c, o: "write" in c},
            {"msg": "Dosyayı okuma modunda ('r') aç.", "task": "f = open('t.txt', '___')", "check": lambda c, o: "'r'" in c},
            {"msg": "Dosyanın tüm içeriğini oku.", "task": "f = open('t.txt', 'r')\ni = f.___()\nprint(i)", "check": lambda c, o: "read" in c},
            {"msg": "Dosyayı mutlaka kapatmalısın!", "task": "f = open('t.txt', 'r')\nf.___()", "check": lambda c, o: "close" in c}
        ]
    }
]

# --- YAN PANEL: PİTO VE SKOR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/robot-viewer.png", width=100)
    st.title("Pito Akademi")
    st.divider()
    st.metric("📊 Toplam Puanın", st.session_state.total_score)
    st.subheader(f"🎖️ Rütbe: \n {get_rank(st.session_state.total_score)}")
    
    # Mevcut egzersiz puan durumu
    st.write(f"🎁 **Bu Egzersizden Alabileceğin:** {st.session_state.current_potential_score} Puan")
    if st.session_state.current_potential_score < 10:
        st.warning("Dikkat! Hataların arttığı için puanın düşüyor.")
    
    st.progress(min(st.session_state.total_score / 1000, 1.0))
    st.divider()
    st.info("Pito: 'Her hata yaptığında bu görevden alacağın puan 5 azalır. Dikkatli ol!'")

# --- ÜST PANEL: NAVİGASYON ---
st.title("🚀 Python Uzmanlık Yolculuğu")
cols = st.columns(len(training_data))
for i, mod in enumerate(training_data):
    is_locked = i > 0 and not st.session_state.completed_modules[i - 1]
    status = "✅" if st.session_state.completed_modules[i] else "🔒" if is_locked else "📖"
    if cols[i].button(f"{status} {mod['module_title']}", disabled=is_locked, key=f"nav_{i}"):
        st.session_state.current_module = i
        st.session_state.current_exercise = 0
        st.session_state.exercise_passed = False
        st.session_state.current_potential_score = 20
        st.rerun()

st.divider()

# --- İÇERİK ---
m_idx = st.session_state.current_module
e_idx = st.session_state.current_exercise
curr_mod = training_data[m_idx]
curr_ex = curr_mod["exercises"][e_idx]

st.write(f"**{curr_mod['module_title']}** - Adım: {e_idx + 1} / 5")
st.progress((e_idx) / 5)

col_info, col_edit = st.columns([1, 2])
with col_info:
    st.info(f"**Pito:** {curr_ex['msg']}")
    st.markdown("🔍 Boşlukları (`___`) doldur ve 'Görevi Kontrol Et' butonuna bas.")

with col_edit:
    code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=16, key=f"ace_{m_idx}_{e_idx}")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🔍 Görevi Kontrol Et", use_container_width=True):
            old_stdout = sys.stdout
            redirected_output = sys.stdout = StringIO()
            
            def mock_input(prompt=""):
                print(prompt, end="")
                return "10" 
            
            try:
                exec_code = code.replace("___", "None")
                exec(exec_code, {"input": mock_input})
                sys.stdout = old_stdout
                output = redirected_output.getvalue()
                
                st.subheader("📟 Terminal")
                st.code(output if output else "Pito: 'Kod çalıştı (Bazı kodlar çıktı üretmez).'")
                
                if curr_ex['check'](code, output) and "___" not in code:
                    st.session_state.exercise_passed = True
                    # PUANLAMA MANTIĞI
                    ex_key = f"{m_idx}_{e_idx}"
                    if ex_key not in st.session_state.scored_exercises:
                        st.session_state.total_score += st.session_state.current_potential_score
                        st.session_state.scored_exercises.add(ex_key)
                        st.toast(f"+{st.session_state.current_potential_score} Puan!", icon="💰")
                    st.success("Tebrikler! Pito bu çözümü onayladı. ✅")
                else:
                    if not st.session_state.exercise_passed:
                        st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                    st.warning(f"Pito: 'Henüz doğru olmadı. Alabileceğin puan {st.session_state.current_potential_score}'ye düştü!'")
                    st.session_state.exercise_passed = False
            except Exception as e:
                sys.stdout = old_stdout
                if not st.session_state.exercise_passed:
                    st.session_state.current_potential_score = max(0, st.session_state.current_potential_score - 5)
                st.error(f"Hata: {e}. Puanın {st.session_state.current_potential_score}'ye düştü.")

    if st.session_state.exercise_passed:
        with col_b2:
            if e_idx < 4:
                if st.button("➡️ Sıradaki Egzersize İlerle", use_container_width=True):
                    st.session_state.current_exercise += 1
                    st.session_state.exercise_passed = False
                    st.session_state.current_potential_score = 20 
                    st.rerun()
            else:
                btn_txt = "🏆 Modülü Bitir ve Sonrakine Geç" if m_idx < 7 else "🎓 Eğitimi Tamamla!"
                if st.button(btn_txt, use_container_width=True):
                    st.session_state.completed_modules[m_idx] = True
                    st.session_state.exercise_passed = False
                    st.session_state.current_potential_score = 20
                    if m_idx < 7:
                        st.session_state.current_module += 1
                        st.session_state.current_exercise = 0
                    st.balloons()
                    st.rerun()