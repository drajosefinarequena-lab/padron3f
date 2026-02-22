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

# --- DISEÑO ---
st.markdown("""
    <style>
    .stApp { background-color: white; }
    .bienvenida { text-align: center; color: white; background: #003366; padding: 20px; border: 3px solid black; font-weight: 900; font-size: 22px; margin-bottom: 20px; }
    .stButton>button { background-color: #00008B !important; color: white !important; font-weight: 900 !important; border: 3px solid #FFD700 !important; width: 100%; height: 55px; }
    label, p, h3 { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# Cargamos el banner (imagen de Peronismo de Todos)
if os.path.exists("banner.jpg"):
    st.image("banner.jpg", use_container_width=True)
elif os.path.exists("banner.jpeg"):
    st.image("banner.jpeg", use_container_width=True)

# --- FUNCIÓN DE ENVÍO A GOOGLE ---
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
            st.rerun()
        else:
            st.error("CREDENCIALES INCORRECTAS")

# --- PANTALLA OPERATIVA ---
else:
    st.markdown(f'<div class="bienvenida">OPERATIVO: {st.session_state.usuario_actual}</div>', unsafe_allow_html=True)

    @st.cache_data
    def cargar_padron():
        try:
            df = pd.read_csv("datos.csv", encoding='latin-1').fillna('')
            df.columns = [c.upper().strip() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"Error al leer datos.csv: {e}")
            return None

    padron = cargar_padron()

    if padron is not None:
        st.markdown("### 🔎 LOCALIZAR AFILIADO")
        busqueda = st.text_input("Ingresá Apellido o DNI:").upper()
        
        if busqueda:
            resultado = padron[padron.astype(str).apply(lambda x: x.str.upper().str.contains(busqueda)).any(axis=1)]
            
            if not resultado.empty:
                st.success(f"Se encontraron {len(resultado)} coincidencias")
                st.dataframe(resultado.head(15), use_container_width=True)
                
                st.markdown("---")
                st.markdown("### 🗳️ REGISTRAR COMPROMISO")
                with st.form("form_relevamiento", clear_on_submit=True):
                    # Buscamos columnas de forma inteligente
                    cols = resultado.columns
                    c_dni = [c for c in cols if any(x in c for x in ['DNI', 'MATRI', 'DOC'])][0]
                    c_nom = [c for c in cols if any(x in c for x in ['NOM', 'APE'])][0]
                    
                    opciones_vecinos = {}
                    for idx, row in resultado.head(10).iterrows():
                        nombre_etiqueta = f"{row[c_nom]} | DNI: {row[c_dni]}"
                        opciones_vecinos[nombre_etiqueta] = row
                    
                    seleccionado = st.selectbox("Confirmar Identidad del Vecino:", list(opciones_vecinos.keys()))
                    voto = st.radio("Intención de Voto:", ["🟢 SEGURO LISTA 4", "🟡 INDECISO / VOLVER", "🔴 OTROS"], horizontal=True)
                    nota = st.text_input("Notas de la visita:")
                    
                    if st.form_submit_button("GUARDAR EN GOOGLE SHEETS"):
                        vecino_datos = opciones_vecinos[seleccionado]
                        datos_api = {
                            "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Militante": st.session_state.usuario_actual,
                            "DNI_Vecino": str(vecino_datos[c_dni]),
                            "Nombre_Vecino": str(vecino_datos[c_nom]),
                            "Estado": voto,
                            "Observaciones": nota
                        }
                        if enviar_a_google_sheets(datos_api):
                            st.balloons()
                            st.success(f"¡Registrado con éxito: {vecino_datos[c_nom]}!")
                        else:
                            st.error("Error al conectar con la base de datos.")
            else:
                st.warning("No se encontraron resultados.")

    if st.button("CERRAR SESIÓN"):
        st.session_state.autenticado = False
        st.rerun()
