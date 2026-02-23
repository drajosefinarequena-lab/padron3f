# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# 1. CONFIGURACIÓN DE SEGURIDAD (LOCALIDADES + 2026)
# El referente debe elegir su localidad y poner la clave correspondiente
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

# --- DISEÑO Y BANNER ---
st.markdown("""
    <style>
    .stApp { background-color: white; }
    .banner { 
        text-align: center; 
        background: linear-gradient(90deg, #003366 0%, #0055aa 100%); 
        color: white; 
        padding: 20px; 
        border-radius: 10px; 
        margin-bottom: 20px;
        border-bottom: 5px solid #FFD700;
    }
    .bienvenida { text-align: center; color: #003366; font-weight: 900; font-size: 24px; margin-bottom: 15px; }
    label { color: black !important; font-weight: bold !important; }
    .stButton>button { background-color: #003366 !important; color: white !important; width: 100%; border: 2px solid #FFD700 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE AUDITORÍA ---
def registrar_en_log(militante, localidad, accion, detalle):
    archivo_log = "auditoria_lista4.csv"
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    try:
        ip = requests.get('https://api.ipify.org', timeout=2).text
    except:
        ip = "No detectada"
        
    nuevo_evento = pd.DataFrame([{
        "Fecha": ahora, "Militante": militante, "Localidad": localidad, 
        "Accion": accion, "Detalle": detalle, "IP": ip
    }])
    
    if not os.path.isfile(archivo_log):
        nuevo_evento.to_csv(archivo_log, index=False, encoding='utf-8')
    else:
        nuevo_evento.to_csv(archivo_log, mode='a', header=False, index=False, encoding='utf-8')

# --- ESTADO DE SESIÓN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "es_admin" not in st.session_state: st.session_state.es_admin = False

# --- PANTALLA DE INGRESO ---
if not st.session_state.autenticado:
    st.markdown('<div class="banner"><h1>✌️ LISTA 4</h1><h3>PERONISMO DE TODOS - 3F</h3></div>', unsafe_allow_html=True)
    st.markdown('<div class="bienvenida">CONSULTA EL PADRÓN</div>', unsafe_allow_html=True)
    
    with st.container():
        acepta = st.checkbox("Acepto el registro de mi actividad para el control interno")
        nombre_militante = st.text_input("TU NOMBRE Y APELLIDO:", placeholder="Ej: Juan Pérez")
        localidad_sel = st.selectbox("LOCALIDAD A LA QUE PERTENECES:", ["---"] + list(LOCALIDADES_CLAVES.keys()))
        clave_ingresada = st.text_input("CLAVE DE ACCESO:", type="password")
        
        if st.button("ACCEDER AL SISTEMA", disabled=not acepta):
            if clave_ingresada == CLAVE_ADMIN:
                st.session_state.autenticado = True
                st.session_state.es_admin = True
                registrar_en_log(nombre_militante, "ADMIN", "INGRESO", "Acceso Administrador")
                st.rerun()
            elif localidad_sel in LOCALIDADES_CLAVES and clave_ingresada == LOCALIDADES_CLAVES[localidad_sel] and nombre_militante != "":
                st.session_state.autenticado = True
                st.session_state.usuario_nombre = nombre_militante
                st.session_state.usuario_loc = localidad_sel
                registrar_en_log(nombre_militante, localidad_sel, "INGRESO", "Sesión Iniciada")
                st.rerun()
            else:
                st.error("DATOS INCORRECTOS O NOMBRE VACÍO")

else:
    # --- PANEL DE ADMINISTRACIÓN ---
    if st.session_state.es_admin:
        with st.expander("🛡️ PANEL DE CONTROL DE INGRESOS (AUDITORÍA)"):
            if os.path.exists("auditoria_lista4.csv"):
                st.dataframe(pd.read_csv("auditoria_lista4.csv").sort_index(ascending=False), use_container_width=True)
            else:
                st.info("No hay registros todavía.")

    st.markdown(f"### BienvenidX CompañerX {st.session_state.get('usuario_nombre', 'ADMIN')}")
    
    # --- BUSCADOR ---
    @st.cache_data
    def cargar_datos():
        # Probamos encodings para evitar el error de las imágenes previas
        for enc in ['latin-1', 'utf-8', 'cp1252']:
            try:
                df = pd.read_csv("datos.csv", sep=None, engine='python', encoding=enc)
                # Filtro estricto: Solo DNI, Nombre, Apellido, Dirección
                visibles = [c for c in df.columns if any(x in c.upper() for x in ['DNI', 'MATRICULA', 'NOMBRE', 'APELLIDO', 'DIRECCION', 'CALLE'])]
                return df[visibles].fillna('')
            except: continue
        return None

    padron = cargar_datos()

    if padron is not None:
        busqueda = st.text_input("🔎 BUSCAR POR DNI, APELLIDO O CALLE:", key="input_main")
        if busqueda:
            user_ref = st.session_state.get('usuario_nombre', 'ADMIN')
            loc_ref = st.session_state.get('usuario_loc', 'ADMIN')
            registrar_en_log(user_ref, loc_ref, "BÚSQUEDA", busqueda)
            
            termino = busqueda.upper()
            mask = padron.astype(str).apply(lambda row: row.str.upper().str.contains(termino)).any(axis=1)
            res = padron[mask]
            
            if not res.empty:
                st.success(f"Resultados encontrados: {len(res)}")
                st.dataframe(res, use_container_width=True)
            else:
                st.warning("No se encontraron resultados.")
    else:
        st.error("Error crítico: No se pudo cargar el archivo datos.csv. Verifica el formato.")

    if st.button("CERRAR SESIÓN"):
        st.session_state.autenticado = False
        st.rerun()
