# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import requests
import os

# 1. SEGURIDAD: LOCALIDADES Y CLAVES 2026
LOCALIDADES_CLAVES = {
    "CASEROS": "caseros2026",
    "CIUDADELA": "ciudadela2026",
    "BARRIO_EJERCITO": "barrioejercito2026",
    "VILLA_BOSCH": "villabosch2026",
    "MARTIN_CORONADO": "martincoronado2026",
    "CIUDAD_JARDIN": "ciudadjardin2026",
    "SANTOS_LUGARES": "santoslugares2026",
    "SAENZ_PEÑA": "saenzpeña2026",
    "PODESTA": "podesta2026",
    "CHURRUCA": "churruca2026",
    "EL_LIBERTADOR": "ellibertador2026",
    "LOMA_HERMOSA": "lomahermosa2026"
}
CLAVE_ADMIN = "josefina3f_admin"

st.set_page_config(page_title="Lista 4 - Peronismo de Todos", page_icon="✌️", layout="centered")

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def registrar_evento_google(nombre, localidad, accion, detalle):
    try:
        ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        ip = requests.get('https://api.ipify.org', timeout=2).text
        
        nueva_fila = pd.DataFrame([{
            "Fecha": ahora,
            "Usuario": nombre,
            "Célula/Localidad": localidad,
            "Acción": accion,
            "Término Buscado": detalle,
            "Ubicación (IP)": ip
        }])
        
        df_existente = conn.read(worksheet="resultados")
        df_actualizado = pd.concat([df_existente, nueva_fila], ignore_index=True)
        conn.update(worksheet="resultados", data=df_actualizado)
    except:
        pass 

# --- DISEÑO ---
st.markdown("""
    <style>
    .stApp { background-color: white; }
    .banner { text-align: center; background: #003366; color: white; padding: 15px; border-radius: 10px; border-bottom: 5px solid #FFD700; }
    label { color: black !important; font-weight: bold !important; }
    .stButton>button { background-color: #003366 !important; color: white !important; border: 2px solid #FFD700 !important; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIO DE SESIÓN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown('<div class="banner"><h1>✌️ LISTA 4</h1><h3>PERONISMO DE TODOS - 3F</h3></div>', unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;'>Consulta de Padrón</h4>", unsafe_allow_html=True)
    
    nombre_m = st.text_input("TU NOMBRE Y APELLIDO:")
    loc_sel = st.selectbox("LOCALIDAD:", ["---"] + list(LOCALIDADES_CLAVES.keys()))
    pin = st.text_input("CLAVE DE ACCESO:", type="password")
    
    if st.button("INGRESAR"):
        if pin == CLAVE_ADMIN:
            st.session_state.autenticado = True
            st.session_state.es_admin = True
            st.session_state.nombre = nombre_m if nombre_m else "ADMIN"
            st.session_state.localidad = "ADMIN"
            registrar_evento_google(st.session_state.nombre, "ADMIN", "INGRESO", "Panel Admin")
            st.rerun()
        elif loc_sel in LOCALIDADES_CLAVES and pin == LOCALIDADES_CLAVES[loc_sel] and nombre_m != "":
            st.session_state.autenticado = True
            st.session_state.nombre = nombre_m
            st.session_state.localidad = loc_sel
            st.session_state.es_admin = False
            registrar_evento_google(nombre_m, loc_sel, "INGRESO", "Inicio de sesión")
            st.rerun()
        else:
            st.error("Datos incorrectos o falta tu nombre.")

else:
    # --- BUSCADOR ---
    if st.session_state.es_admin:
        with st.expander("🛡️ AUDITORÍA DE CONSULTAS (GOOGLE SHEETS)"):
            st.dataframe(conn.read(worksheet="resultados").sort_index(ascending=False))

    @st.cache_data
    def cargar_padron():
        # Nombre exacto del nuevo archivo
        archivo = "Padron 2026  PJ BONAERENSE Completo Calles 1.csv"
        if not os.path.exists(archivo):
            st.error(f"No se encuentra el archivo: {archivo}")
            return None
            
        for enc in ['latin-1', 'cp1252', 'utf-8']:
            try:
                df = pd.read_csv(archivo, encoding=enc, sep=None, engine='python')
                # Filtro: Solo DNI, Nombre, Apellido, Dirección
                visibles = [c for c in df.columns if any(x in c.upper() for x in ['DNI', 'MATRICULA', 'NOMBRE', 'APELLIDO', 'DIRECCION', 'CALLE'])]
                return df[visibles].fillna('')
            except: continue
        return None

    df_padron = cargar_padron()

    if df_padron is not None:
        st.markdown(f"**Militante:** {st.session_state.nombre} | **Localidad:** {st.session_state.localidad}")
        busqueda = st.text_input("🔎 BUSCAR POR DNI, APELLIDO O CALLE:")
        
        if busqueda:
            termino = busqueda.upper()
            mask = df_padron.astype(str).apply(lambda row: row.str.upper().str.contains(termino)).any(axis=1)
            resultados = df_padron[mask]
            
            if not resultados.empty:
                registrar_evento_google(st.session_state.nombre, st.session_state.localidad, "BÚSQUEDA", busqueda)
                st.success(f"Encontrados: {len(resultados)}")
                st.dataframe(resultados, use_container_width=True)
            else:
                st.warning("No se encontraron resultados.")

    if st.button("CERRAR SESIÓN"):
        st.session_state.autenticado = False
        st.rerun()
