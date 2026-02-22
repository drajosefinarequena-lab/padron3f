# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# 1. SEGURIDAD Y LOCALIDADES
USUARIOS_AUTORIZADOS = {
    "CASEROS": "L4_3f_CAS", "CIUDADELA": "L4_3f_CIU", "BARRIO_EJERCITO": "L4_3f_BEJ",
    "VILLA_BOSCH": "L4_3f_VBO", "MARTIN_CORONADO": "L4_3f_MCO", "CIUDAD_JARDIN": "L4_3f_CJA",
    "SANTOS_LUGARES": "L4_3f_SLU", "SAENZ_PEÑA": "L4_3f_SPE", "PODESTA": "L4_3f_POD",
    "CHURRUCA": "L4_3f_CHU", "EL_LIBERTADOR": "L4_3f_ELI", "LOMA_HERMOSA": "L4_3f_LHE"
}
CLAVE_ADMIN = "josefina3f_admin"

st.set_page_config(page_title="Lista 4 - Peronismo de Todos", page_icon="✌️", layout="centered")

# --- DISEÑO Y BANNER ---
st.markdown("""
    <style>
    .stApp { background-color: white; }
    .bienvenida { text-align: center; color: white; background: #003366; padding: 20px; border: 3px solid black; font-weight: 900; font-size: 22px; margin-bottom: 20px; }
    .stButton>button { background-color: #00008B !important; color: white !important; font-weight: 900 !important; border: 3px solid #FFD700 !important; width: 100%; height: 55px; }
    label, p, h3 { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# Intentamos cargar el banner con prioridad a banner.jpg
if os.path.exists("banner.jpg"):
    st.image("banner.jpg", use_container_width=True)
elif os.path.exists("banner.jpeg"):
    st.image("banner.jpeg", use_container_width=True)

# --- FUNCIONES DE COMUNICACIÓN ---
def enviar_a_google_sheets(datos):
    try:
        url = st.secrets["URL_SHEET_BEST"]
        res = requests.post(url, json=datos, timeout=10)
        return res.status_code == 200
    except:
        return False

# --- GESTIÓN DE SESIÓN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "usuario_actual" not in st.session_state: st.session_state.usuario_actual = "Militante"

# --- PANTALLA DE LOGUEO ---
if not st.session_state.autenticado:
    st.markdown('<div class="bienvenida">INGRESO SEGURO - LISTA 4</div>', unsafe_allow_html=True)
    usuario_ing = st.selectbox("LOCALIDAD / EQUIPO:", ["---"] + list(USUARIOS_AUTORIZADOS.keys()))
    clave_ing = st.text_input("CONTRASEÑA TÁCTICA:", type="password")
    
    if st.button("ACCEDER AL PADRÓN"):
        if clave_ing == CLAVE_ADMIN:
            st.session_state.autenticado, st.session_state.es_admin = True, True
            st.session_state.usuario_actual = "ADMIN"
            st.rerun()
        elif usuario_ing in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[usuario_ing] == clave_ing:
            st.session_state.autenticado = True
            st.session_state.usuario_actual = usuario_ing
            st.rerun
