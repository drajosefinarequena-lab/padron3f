# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import requests
import os

# 1. CLAVES 2026 POR LOCALIDAD
LOCALIDADES_CLAVES = {
    "CASEROS": "caseros2026", "CIUDADELA": "ciudadela2026", "BARRIO_EJERCITO": "barrioejercito2026",
    "VILLA_BOSCH": "villabosch2026", "MARTIN_CORONADO": "martincoronado2026", "CIUDAD_JARDIN": "ciudadjardin2026",
    "SANTOS_LUGARES": "santoslugares2026", "SAENZ_PEÑA": "saenzpeña2026", "PODESTA": "podesta2026",
    "CHURRUCA": "churruca2026", "EL_LIBERTADOR": "ellibertador2026", "LOMA_HERMOSA": "lomahermosa2026"
}
CLAVE_ADMIN = "josefina3f_admin"

st.set_page_config(page_title="Lista 4 - Ingreso", page_icon="✌️", layout="centered")

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def registrar_auditoria(nombre, localidad, accion, detalle):
    try:
        ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        ip = requests.get('https://api.ipify.org', timeout=2).text
        nueva_fila = pd.DataFrame([{"Fecha": ahora, "Usuario": nombre, "Célula/Localidad": localidad, "Acción": accion, "Término Buscado": detalle, "Ubicación (IP)": ip}])
        df_existente = conn.read(worksheet="resultados")
        df_actualizado = pd.concat([df_existente, nueva_fila], ignore_index=True)
        conn.update(worksheet="resultados", data=df_actualizado)
    except: pass 

# --- INTERFAZ DE LA IMAGEN ---
st.markdown("<h1 style='text-align:center;'>✌️ LISTA 4 - INGRESO</h1>", unsafe_allow_html=True)

if "autenticado" not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    acepta = st.checkbox("Acepto el registro de mi actividad por seguridad")
    nombre_m = st.text_input("NOMBRE Y APELLIDO:")
    loc_sel = st.selectbox("LOCALIDAD:", ["---"] + list(LOCALIDADES_CLAVES.keys()))
    pin = st.text_input("CLAVE:", type="password")
    
    if st.button("ACCEDER", disabled=not acepta):
        if pin == CLAVE_ADMIN:
            st.session_state.autenticado, st.session_state.es_admin, st.session_state.nombre, st.session_state.localidad = True, True, (nombre_m if nombre_m else "ADMIN"), "ADMIN"
            registrar_auditoria(st.session_state.nombre, "ADMIN", "INGRESO", "Panel Admin")
            st.rerun()
        elif loc_sel in LOCALIDADES_CLAVES and pin == LOCALIDADES_CLAVES[loc_sel] and nombre_m != "":
            st.session_state.autenticado, st.session_state.nombre, st.session_state.localidad, st.session_state.es_admin = True, nombre_m, loc_sel, False
            registrar_auditoria(nombre_m, loc_sel, "INGRESO", "Inicio sesión")
            st.rerun()
        else:
            st.error("Datos incorrectos o falta completar el nombre")

else:
    # --- BUSCADOR UNIVERSAL (APELLIDO, DNI Y CALLES) ---
    st.write(f"Compañerx: **{st.session_state.nombre}** | Localidad: **{st.session_state.localidad}**")
    
    @st.cache_data
    def cargar_datos():
        archivo = "Padron 2026  PJ BONAERENSE Completo Calles 1.csv"
        for enc in ['latin-1', 'cp1252', 'utf-8']:
            try:
                df = pd.read_csv(archivo, encoding=enc, sep=None, engine='python')
                visibles = [c for c in df.columns if any(x in c.upper() for x in ['DNI', 'MATRICULA', 'NOMBRE', 'APELLIDO', 'DIRECCION', 'CALLE'])]
                return df[visibles].fillna('')
            except: continue
        return None

    padron = cargar_datos()
    if padron is not None:
        busqueda = st.text_input("🔎 BUSCAR POR CALLE, APELLIDO O DNI:")
        if busqueda:
            t = busqueda.upper()
            mask = padron.astype(str).apply(lambda row: row.str.upper().str.contains(t)).any(axis=1)
            res = padron[mask]
            if not res.empty:
                registrar_auditoria(st.session_state.nombre, st.session_state.localidad, "BÚSQUEDA", busqueda)
                st.dataframe(res, use_container_width=True)
            else: st.warning("No se encontraron resultados.")

    if st.button("SALIR"):
        st.session_state.autenticado = False
        st.rerun()
