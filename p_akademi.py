import streamlit as st
from streamlit_ace import st_ace
import sys
from io import StringIO

# Sayfa Yapılandırması
st.set_page_config(layout="wide", page_title="Pito Akademi: Python Uzmanlık Yolculuğu")

# --- SESSION STATE: İLERLEME TAKİBİ ---
if 'completed_modules' not in st.session_state:
    st.session_state.completed_modules = [False] * 8
if 'current_module' not in st.session_state:
    st.session_state.current_module = 0
if 'current_exercise' not in st.session_state:
    st.session_state.current_exercise = 0
if 'exercise_passed' not in st.session_state:
    st.session_state.exercise_passed = False

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
            {"msg": "Koşul doğru değilse ne çalışır?", "task": "n = 5\nif n > 10:\n    print('Büyük')\n___:\n    print('Küçük')", "check": lambda c, o: "Küçük" in o},
            {"msg": "85 ve üstü ise Pekiyi yazdır.", "task": "n = 90\nif n ___ 85:\n    print('Pekiyi')", "check": lambda c, o: ">=" in c and "Pekiyi" in o},
            {"msg": "Aynı anda iki koşulun doğruluğu için?", "task": "if 5 > 3 ___ 2 < 4:\n    print('Evet')", "check": lambda c, o: "and" in c and "Evet" in o},
            {"msg": "Değilse Eğer (elif) komutunu tamamla.", "task": "p = 60\nif p > 85: print('A')\n___ p > 50: print('B')", "check": lambda c, o: "elif" in c and "B" in o}
        ]
    },
    {
        "module_title": "4. Döngü Yapıları",
        "exercises": [
            {"msg": "3 kez dönen bir range fonksiyonu yaz.", "task": "for i in ___(3):\n    print('Pito')", "check": lambda c, o: o.count("Pito") == 3},
            {"msg": "Döngü içindeki sayacı yazdır.", "task": "for i in range(2):\n    print(___)", "check": lambda c, o: "1" in o},
            {"msg": "While döngüsünü başlatmak için gereken komut?", "task": "i = 0\n___ i < 2:\n    print(i)\n    i += 1", "check": lambda c, o: "while" in c and "1" in o},
            {"msg": "Döngüyü anında kırmak için hangi komut kullanılır?", "task": "for i in range(5):\n    if i == 2: ___\n    print(i)", "check": lambda c, o: "1" in o and "2" not in o},
            {"msg": "O adımı atlayıp devam etmek için?", "task": "for i in range(3):\n    if i == 1: ___\n    print(i)", "check": lambda c, o: "0" in o and "2" in o and "1" not in o}
        ]
    },
    {
        "module_title": "5. Listeler ve Fonksiyonlar",
        "exercises": [
            {"msg": "Liste oluştur: [10, 20] yaz ve yazdır.", "task": "liste = [___, 20]\nprint(liste)", "check": lambda c, o: "10" in o},
            {"msg": "Listenin ilk elemanına (indeks 0) eriş.", "task": "l = [50, 60]\nprint(l[___])", "check": lambda c, o: "50" in o},
            {"msg": "Listenin uzunluğunu bulan fonksiyon?", "task": "l = [1, 2, 3]\nprint(___(l))", "check": lambda c, o: "3" in o and "len" in c},
            {"msg": "Fonksiyon tanımlamak için hangi anahtar kelime kullanılır?", "task": "___ selam():\n    print('Merhaba')", "check": lambda c, o: "def" in c},
            {"msg": "Tanımladığın 'selam' fonksiyonunu çağır.", "task": "def selam(): print('Pito')\n___", "check": lambda c, o: "Pito" in o and "selam()" in c}
        ]
    },
    {
        "module_title": "6. İleri Veri Yapıları",
        "exercises": [
            {"msg": "Demet (tuple) oluştur: (1, 2) ve yazdır.", "task": "d = (___, 2)\nprint(d)", "check": lambda c, o: "(1, 2)" in o},
            {"msg": "Küme (set) tanımla: {1, 2}. Kümelerde tekrar eden öge olmaz.", "task": "k = {1, 2, ___}\nprint(k)", "check": lambda c, o: "1" in o},
            {"msg": "Sözlük (dict) oluştur. 'ad': 'Pito' eşleşmesini tamamla.", "task": "s = {'ad': '___'}\nprint(s['ad'])", "check": lambda c, o: "Pito" in o},
            {"msg": "Sözlüğe yeni bir anahtar ekle.", "task": "s = {'a': 1}\ns['___'] = 2\nprint(s)", "check": lambda c, o: "'b'" in c or '"b"' in c},
            {"msg": "Sözlükteki tüm anahtarları listele.", "task": "s = {'a': 1}\nprint(s.___())", "check": lambda c, o: "keys" in c}
        ]
    },
    {
        "module_title": "7. Nesne Yönelimli Programlama",
        "exercises": [
            {"msg": "Bir sınıf (class) tanımla.", "task": "___ Robot:\n    pass", "check": lambda c, o: "class" in c},
            {"msg": "Sınıftan bir nesne (object) oluştur.", "task": "class Robot: pass\npito = ___()", "check": lambda c, o: "Robot()" in c},
            {"msg": "Nesneye bir nitelik (attribute) ata.", "task": "class Robot: pass\npito = Robot()\npito.___ = 'Mavi'", "check": lambda c, o: "renk" in c},
            {"msg": "Sınıf içine bir metot (fonksiyon) ekle.", "task": "class Robot:\n    def ___(self):\n        print('Bip!')", "check": lambda c, o: "ses_cikar" in c},
            {"msg": "Metodu nesne üzerinden çağır.", "task": "class R: def s(self): print('X')\nr = R()\nr.___()", "check": lambda c, o: "s()" in c}
        ]
    },
    {
        "module_title": "8. Dosya İşlemleri",
        "exercises": [
            {"msg": "Dosya açmak için hangi fonksiyon kullanılır?", "task": "f = ___('notlar.txt', 'w')", "check": lambda c, o: "open" in c},
            {"msg": "Dosyaya yazı yazmak için metodu tamamla.", "task": "f = open('test.txt', 'w')\nf.___('Pito')\nf.close()", "check": lambda c, o: "write" in c},
            {"msg": "Dosyayı okuma modunda ('r') aç.", "task": "f = open('test.txt', '___')", "check": lambda c, o: "'r'" in c or '"r"' in c},
            {"msg": "Dosyanın tüm içeriğini oku.", "task": "f = open('test.txt', 'r')\nicerik = f.___()\nprint(icerik)", "check": lambda c, o: "read" in c},
            {"msg": "Dosyayı mutlaka kapatmalısın!", "task": "f = open('test.txt', 'r')\nf.___()", "check": lambda c, o: "close" in c}
        ]
    }
]

# --- ÜST PANEL: NAVİGASYON ---
st.title("🚀 Pito Akademi: Tam Müfredat Programlama Atölyesi")
cols = st.columns(len(training_data))
for i, mod in enumerate(training_data):
    is_locked = i > 0 and not st.session_state.completed_modules[i - 1]
    status = "✅" if st.session_state.completed_modules[i] else "🔒" if is_locked else "📖"
    if cols[i].button(f"{status} {mod['module_title']}", disabled=is_locked, key=f"nav_{i}"):
        st.session_state.current_module = i
        st.session_state.current_exercise = 0
        st.session_state.exercise_passed = False
        st.rerun()

st.divider()

# --- İÇERİK ---
m_idx = st.session_state.current_module
e_idx = st.session_state.current_exercise
curr_mod = training_data[m_idx]
curr_ex = curr_mod["exercises"][e_idx]

st.write(f"**{curr_mod['module_title']}** - Egzersiz: {e_idx + 1} / 5")
st.progress((e_idx) / 5)

col1, col2 = st.columns([1, 2])
with col1:
    st.image("https://img.icons8.com/fluency/96/robot-viewer.png", width=80)
    st.info(f"**Pito:** {curr_ex['msg']}")
    st.markdown("🔍 Boşlukları (`___`) doldurarak algoritmayı tamamla.")

with col2:
    code = st_ace(value=curr_ex['task'], language="python", theme="dracula", font_size=16, key=f"ace_{m_idx}_{e_idx}")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔍 Görevi Kontrol Et", use_container_width=True):
            old_stdout = sys.stdout
            redirected_output = sys.stdout = StringIO()
            
            def mock_input(prompt=""):
                print(prompt, end="")
                return "10" 
            
            try:
                # Boşluklar dolmadan kodun hata vermemesi için None ataması
                exec_code = code.replace("___", "None")
                exec(exec_code, {"input": mock_input})
                sys.stdout = old_stdout
                output = redirected_output.getvalue()
                
                st.subheader("📟 Terminal Çıktısı")
                if output:
                    st.code(output)
                else:
                    st.code("Pito: 'Kod çalıştı (Bazı kodlar terminal çıktısı üretmez).'")
                
                if curr_ex['check'](code, output) and "___" not in code:
                    st.session_state.exercise_passed = True
                    st.success("Harika! Pito bu çözümü onayladı. ✅")
                else:
                    st.warning("Pito: 'Henüz doğru sonuca ulaşamadık. Boşlukları kontrol et.'")
                    st.session_state.exercise_passed = False
            except Exception as e:
                sys.stdout = old_stdout
                st.error(f"Hata: {e}")

    # İLERLEME BUTONLARI (Sadece başarılıysa görünür)
    if st.session_state.exercise_passed:
        with col_btn2:
            if e_idx < 4:
                if st.button("➡️ Sıradaki Egzersize İlerle", use_container_width=True):
                    st.session_state.current_exercise += 1
                    st.session_state.exercise_passed = False
                    st.rerun()
            else:
                btn_text = "🏆 Modülü Bitir ve Sonrakine Geç" if m_idx < 7 else "🎓 Mezuniyet: Eğitimi Tamamla!"
                if st.button(btn_text, use_container_width=True):
                    st.session_state.completed_modules[m_idx] = True
                    if m_idx < len(training_data) - 1:
                        st.session_state.current_module += 1
                        st.session_state.current_exercise = 0
                    st.session_state.exercise_passed = False
                    st.rerun()