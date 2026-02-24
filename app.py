# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import requests
import os

# 1. SEGURIDAD: LOCALIDADES Y CLAVES 2026
LOCALIDADES_CLAVES = {
    "CASEROS": "caseros2026", "CIUDADELA": "ciudadela2026", "BARRIO_EJERCITO": "barrioejercito2026",
    "VILLA_BOSCH": "villabosch2026", "MARTIN_CORONADO": "martincoronado2026", "CIUDAD_JARDIN": "ciudadjardin2026",
    "SANTOS_LUGARES": "santoslugares2026", "SAENZ_PEÑA": "saenzpeña2026", "PODESTA": "podesta2026",
    "CHURRUCA": "churruca2026", "EL_LIBERTADOR": "ellibertador2026", "LOMA_HERMOSA": "lomahermosa2026"
}
CLAVE_ADMIN = "josefina3f_admin"

st.set_page_config(page_title="Lista 4 - Padrón 3F", page_icon="✌️", layout="centered")

# --- CONEXIÓN A GOOGLE SHEETS PARA AUDITORÍA ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    st.error("Error de conexión a la planilla. Verifica los Secrets.")

def registrar_evento(nombre, localidad, accion, detalle):
    try:
        ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        ip = requests.get('https://api.ipify.org', timeout=2).text
        nueva_fila = pd.DataFrame([{"Fecha": ahora, "Usuario": nombre, "Célula/Localidad": localidad, "Acción": accion, "Término Buscado": detalle, "Ubicación (IP)": ip}])
        df_existente = conn.read(worksheet="resultados")
        df_actualizado = pd.concat([df_existente, nueva_fila], ignore_index=True)
        conn.update(worksheet="resultados", data=df_actualizado)
    except: pass 

# --- PANTALLA DE ACCESO ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align:center;'>✌️ LISTA 4 - INGRESO</h1>", unsafe_allow_html=True)
    nombre_m = st.text_input("TU NOMBRE Y APELLIDO:")
    loc_sel = st.selectbox("LOCALIDAD:", ["---"] + list(LOCALIDADES_CLAVES.keys()))
    pin = st.text_input("CLAVE:", type="password")
    
    if st.button("ACCEDER"):
        if pin == CLAVE_ADMIN:
            st.session_state.autenticado, st.session_state.es_admin, st.session_state.nombre, st.session_state.localidad = True, True, (nombre_m if nombre_m else "ADMIN"), "ADMIN"
            registrar_evento(st.session_state.nombre, "ADMIN", "INGRESO", "Panel Admin")
            st.rerun()
        elif loc_sel in LOCALIDADES_CLAVES and pin == LOCALIDADES_CLAVES[loc_sel] and nombre_m != "":
            st.session_state.autenticado, st.session_state.nombre, st.session_state.localidad, st.session_state.es_admin = True, nombre_m, loc_sel, False
            registrar_evento(nombre_m, loc_sel, "INGRESO", "Inicio sesión")
            st.rerun()
        else: st.error("DAT
