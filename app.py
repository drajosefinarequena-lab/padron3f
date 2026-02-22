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
    .aviso-seguridad { background-color: #ffeb3b; padding: 10px; border: 2px solid #f44336; color: black; font-weight: bold; text-align: center; margin-bottom: 15px; }
    label, p, h3 { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# Banner
if os.path.exists("banner.jpg"):
    st.image("banner.jpg", use_container_width=True)
elif os.path.exists("banner.jpeg"):
    st.image("banner.jpeg", use_container_width=True)

# --- FUNCIÓN DE ENVÍO ---
def enviar_a_google_sheets(datos):
    try:
        url = st.secrets["URL_SHEET_BEST"]
        res = requests.post(url, json=datos, timeout=10)
        return res.status_code == 200
    except:
        return False

# --- SESIÓN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "usuario_actual" not in st.session_state: st.session_state.usuario_actual = "Militante"
if "nombre_referente" not in st.session_state: st.session_state.nombre_referente = ""

# --- PANTALLA DE ACCESO ---
if not st.session_state.autenticado:
    st.markdown('<div class="bienvenida">INGRESO SEGURO - LISTA 4</div>', unsafe_allow_html=True)
    st.markdown('<div class="aviso-seguridad">⚠️ REGISTRO DE UBICACIÓN ACTIVO PARA SEGURIDAD</div>', unsafe_allow_html=True)
    
    acepta_geo = st.checkbox("ACEPTO EL REGISTRO DE MI UBICACIÓN E IP")
    
    # Campo obligatorio de Referente
    ref_ing = st.text_input("NOMBRE DEL REFERENTE / RESPONSABLE:", placeholder="Ej: JUAN PEREZ").upper()
    
    usuario_ing = st.selectbox("LOCALIDAD / EQUIPO:", ["---"] + list(USUARIOS_AUTORIZADOS.keys()))
    clave_ing = st.text_input("CONTRASEÑA TÁCTICA:", type="password")
    
    if st.button("ACCEDER AL PADRÓN", disabled=not acepta_geo or not ref_ing):
        if clave_ing == CLAVE_ADMIN or (usuario_ing in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[usuario_ing] == clave_ing):
            st.session_state.autenticado = True
            st.session_state.usuario_actual = usuario_ing if clave_ing != CLAVE_ADMIN else "ADMIN"
            st.session_state.nombre_referente = ref_ing
            st.rerun()
        else:
            st.error("CREDENCIALES INCORRECTAS")
    if acepta_geo and not ref_ing:
        st.info("Por favor, ingresá el nombre del Referente para continuar.")

# --- PANTALLA OPERATIVA ---
else:
    st.markdown(f'<div class="bienvenida">OPERATIVO: {st.session_state.usuario_actual} | REF: {st.session_state.nombre_referente}</div>', unsafe_allow_html=True)

    @st.cache_data
    def cargar_padron():
        try:
            df = pd.read_csv("datos.csv", encoding='latin-1', on_bad_lines='skip', sep=None, engine='python').fillna('')
            df.columns = [c.upper().strip() for c in df.columns]
            return df
        except:
            return None

    padron = cargar_padron()

    if padron is not None:
        st.markdown("### 🔎 LOCALIZAR AFILIADO")
        busqueda = st.text_input("Ingresá Apellido o DNI:").upper()
        
        if busqueda:
            resultado = padron[padron.astype(str).apply(lambda x: x.str.upper().str.contains(busqueda)).any(axis=1)]
            
            if not resultado.empty:
                st.success(f"Se encontraron {len(resultado)} coincidencias")
                st.dataframe(resultado.head(20), use_container_width=True)
                
                st.markdown("---")
                st.markdown("### 🗳️ REGISTRAR COMPROMISO")
                
                cols = resultado.columns
                c_dni = [c for c in cols if any(x in c for x in ['DNI', 'MATRI', 'DOC'])][0]
                c_ape = [c for c in cols if 'APE' in c]
                c_nom = [c for c in cols if 'NOM' in c]
                
                opciones_vecinos = {}
                for idx, row in resultado.iterrows():
                    label = f"{row[c_ape[0]] if c_ape else ''}, {row[c_nom[0]] if c_nom else ''} | DNI: {row[c_dni]}"
                    opciones_vecinos[label] = row
                
                seleccionado = st.selectbox("Seleccionar Vecino específico:", list(opciones_vecinos.keys()))
                
                with st.form(key=f"form_{seleccionado}"):
                    voto = st.radio("Intención de Voto:", ["🟢 SEGURO LISTA 4", "🟡 INDECISO / VOLVER", "🔴 OTROS"], horizontal=True)
                    nota = st.text_input("Notas de la visita:")
                    
                    if st.form_submit_button("GUARDAR EN GOOGLE SHEETS"):
                        vecino_datos = opciones_vecinos[seleccionado]
                        nombre_full = f"{vecino_datos[c_ape[0]]}, {vecino_datos[c_nom[0]]}" if c_ape and c_nom else seleccionado.split('|')[0].strip()

                        # ENVIAMOS LOS DATOS CON AMBAS VERSIONES PARA QUE NO FALLE
                        datos_api = {
                            "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Referente": st.session_state.nombre_referente,
                            "REFERENTE": st.session_state.nombre_referente, # AGREGADO PARA TU EXCEL EN MAYÚSCULAS
                            "Militante": st.session_state.usuario_actual,
                            "DNI_Vecino": str(vecino_datos[c_dni]),
                            "Nombre_Vecino": nombre_full,
                            "Estado": voto,
                            "Observaciones": nota
                        }
                        
                        if enviar_a_google_sheets(datos_api):
                            st.balloons()
                            st.success(f"¡Registrado! Vecino: {nombre_full}")
                        else:
                            st.error("Error al guardar. Revisa la base de datos.")
            else:
                st.warning("Sin coincidencias.")

    if st.button("CERRAR SESIÓN"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
