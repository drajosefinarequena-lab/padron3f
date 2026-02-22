# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# 1. CONFIGURACIÓN DE SEGURIDAD Y ACCESOS
USUARIOS_AUTORIZADOS = {
    "CASEROS": "L4_3f_CAS",
    "CIUDADELA": "L4_3f_CIU",
    "BARRIO_EJERCITO": "L4_3f_BEJ",
    "VILLA_BOSCH": "L4_3f_VBO",
    "MARTIN_CORONADO": "L4_3f_MCO",
    "CIUDAD_JARDIN": "L4_3f_CJA",
    "SANTOS_LUGARES": "L4_3f_SLU",
    "SAENZ_PEÑA": "L4_3f_SPE",
    "PODESTA": "L4_3f_POD",
    "CHURRUCA": "L4_3f_CHU",
    "EL_LIBERTADOR": "L4_3f_ELI",
    "LOMA_HERMOSA": "L4_3f_LHE"
}
CLAVE_ADMIN = "josefina3f_admin"

st.set_page_config(page_title="Lista 4 - Peronismo de Todos", page_icon="✌️", layout="centered")

# --- DISEÑO TÁCTICO (ALTO CONTRASTE) ---
st.markdown("""
    <style>
    .stApp { 
        background-color: white; 
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Escudo_del_Partido_Justicialista.svg/1200px-Escudo_del_Partido_Justicialista.svg.png"); 
        background-repeat: no-repeat; 
        background-position: center; 
        background-size: 400px; 
        opacity: 0.9; 
    }
    .block-container { padding-top: 1rem !important; max-width: 600px; }
    label, p, h3, h4 { color: black !important; font-weight: 900 !important; font-size: 18px !important; }
    .stTextInput input { background-color: white !important; color: black !important; border: 4px solid black !important; font-weight: bold !important; }
    .bienvenida { text-align: center; color: white; background: #003366; padding: 15px; border: 3px solid black; font-weight: 900; font-size: 20px; margin-bottom: 10px; }
    .stButton>button { background-color: #00008B !important; color: white !important; font-weight: 900 !important; border: 3px solid #FFD700 !important; width: 100%; height: 50px; }
    .aviso-seguridad { background-color: #ffeb3b; padding: 10px; border: 2px solid #f44336; color: black; font-weight: bold; text-align: center; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE LOG Y GEO ---
def registrar_evento(usuario, ubicacion, resultado):
    archivo_log = "log_accesos.csv"
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nuevo = pd.DataFrame([{"Fecha": ahora, "Usuario": usuario, "Ubicacion": ubicacion, "Resultado": resultado}])
    if not os.path.isfile(archivo_log):
        nuevo.to_csv(archivo_log, index
