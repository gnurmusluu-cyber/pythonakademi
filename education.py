import streamlit as st
import random
import os
import base64

def egitim_ekrani(u, mufredat, msgs, emotions_module, ranks_module, ilerleme_fonksiyonu, normalize_fonksiyonu, supabase):
    # --- 0. SİBER-HUD VE STABİLİZASYON CSS ---
    st.markdown('''
        <style>
        .stApp { background-color: #0e1117; }
        
        /* SIDEBAR STABİLİZASYONU */
        [data-testid="stSidebar"] {
            min-width: 300px !important; /* Genişliği sabitle */
            max-width: 300px !important;
            background-color: #161b22 !important;
            border-right: 1px solid #00E5FF;
            transition: none !important; /* Geçişlerde sıçramayı önlemek için */
        }

        /* Sidebar İçeriğini HUD Altından Kurtar ve Sabitle */
        [data-testid="stSidebarUserContent"] {
            padding-top: 5rem !important;
            overflow-x: hidden !important; /* Yatay kaymayı engelle */
        }

        /* HUD BAR (STIKY) */
        .cyber-hud {
            position: fixed; top: 0; left: 0; width: 100%;
            background: rgba(14, 17, 23, 0.98);
            border-bottom: 2px solid #00E5FF;
            z-index: 999999; padding: 10px 25px;
            display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 4px 20px rgba(0, 229, 255, 0.3);
            backdrop-filter: blur(15px);
        }

        .hud-pito-gif img {
            width: 65px; height: 65px; border-radius: 50%;
            border: 3px solid #00E5FF; object-fit: cover;
            background: #000; margin-right: 15px;
        }

        /* Sayfa İçeriği Sıçramasını Önleme */
        .main-container { 
            margin-top: 95px; 
            padding: 10px;
            animation: fadeIn 0.3s ease-in; /* Geçişleri yumuşat */
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @media (max-width: 768px) {
            [data-testid="stSidebar"] { min-width: 100% !important; }
            .main-container { margin-top: 135px; }
        }
        </style>
    ''', unsafe_allow_html=True)

    # --- HUD VE İÇERİK MANTIĞI AYNI KALACAK ---
    # (Önceki başarılı HUD kodlarını buraya ekleyebilirsin)
