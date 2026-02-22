# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# 1. SEGURIDAD Y ACCESOS
USUARIOS_AUTORIZADOS = {
    "CASEROS": "L4_3f_CAS", "CIUDADELA": "L4_3f_CIU", "BARRIO_EJERCITO": "L4_3f_BEJ",
    "VILLA_BOSCH": "L4_3f_VBO", "MARTIN_CORONADO": "L4_3f_MCO", "CIUDAD_JARDIN": "L4_3f_CJA",
    "SANTOS_LUGARES": "L4_3f_SLU", "SAENZ_PEÑA": "L4_3f_SPE", "PODESTA": "L4_3f_POD",
    "CHURRUCA": "L4_3f_CHU", "EL_LIBERTADOR": "L4_3f_ELI", "LOMA_HERMOSA": "L4_3f_LHE"
}
CLAVE_ADMIN = "josefina3f_admin"

st.set_page_config(page_title="Lista 4 - Peronismo de Todos", page_icon="✌️", layout="centered")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: white; background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Escudo_del_Partido_Justicialista.svg/1200px-Escudo_del_Partido_Justicialista.svg.png"); background-repeat: no-repeat; background-position: center; background-size: 400px; opacity: 0.9; }
    .bienvenida { text-align: center; color: white; background: #003366; padding: 15px; border: 3px solid black; font-weight: 900; font-size: 20px; }
    .stButton>button { background-color: #00008B !important; color: white !important; font-weight: 900 !important; border: 3px solid #FFD700 !important; width: 100%; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES CORE ---
def obtener_datos_ip():
    try: return requests.get('https://ipapi.co/json/', timeout=3).json().get('ip', 'IP Oculta')
    except: return "IP No rastreable"

def enviar_a_google_sheets(datos):
    try:
        url = st.secrets["URL_SHEET_BEST"]
        # CORRECCIÓN DE PARÉNTESIS AQUÍ
        res = requests.post(url, json=datos, timeout=10)
        return res.status_code == 200
    except: return False

# --- SESIÓN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "usuario_actual" not in st.session_state: st.session_state.usuario_actual = "Militante"

if not st.session_state.autenticado:
    st.markdown('<div class="bienvenida">INGRESO SEGURO - LISTA 4</div>', unsafe_allow_html=True)
    usuario_ing = st.selectbox("LOCALIDAD:", ["---"] + list(USUARIOS_AUTORIZADOS.keys()))
    clave_ing = st.text_input("CLAVE:", type="password")
    if st.button("ENTRAR"):
        if clave_ing == CLAVE_ADMIN or (usuario_ing in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[usuario_ing] == clave_ing):
            st.session_state.autenticado = True
            st.session_state.usuario_actual = usuario_ing if clave_ing != CLAVE_ADMIN else "ADMIN"
            st.rerun()
        else: st.error("DATOS INCORRECTOS")
else:
    st.markdown(f'<div class="bienvenida">PANEL: {st.session_state.usuario_actual}</div>', unsafe_allow_html=True)

    @st.cache_data
    def cargar_datos():
        try:
            df_c = pd.read_csv("datos.csv", encoding='latin-1').fillna('')
            df_c.columns = [c.upper() for c in df_c.columns]
            return df_c
        except: return None

    df = cargar_datos()
    if df is not None:
        busqueda = st.text_input("BUSCAR DNI O APELLIDO:").upper()
        if busqueda:
            res = df[df.astype(str).apply(lambda x: x.str.upper().str.contains(busqueda)).any(axis=1)]
            if not res.empty:
                st.dataframe(res.head(10), use_container_width=True)
                
                # --- FORMULARIO DE CARGA ---
                st.markdown("### 🗳️ REGISTRAR CONTACTO")
                with st.form("form_voto", clear_on_submit=True):
                    # Identificamos columnas dinámicamente
                    col_dni = [c for c in res.columns if 'DNI' in c or 'MATRICULA' in c][0]
                    col_nom = [c for c in res.columns if 'NOMBRE' in c or 'APELLIDO' in c][0]
                    
                    opciones = {f"{row[col_nom]} | DNI: {row[col_dni]}": row for i, row in res.head(10).iterrows()}
                    seleccion = st.selectbox("Confirmar Afiliado:", list(opciones.keys()))
                    
                    voto = st.radio("Intención:", ["🟢 SEGURO LISTA 4", "🟡 INDECISO", "🔴 OTROS"], horizontal=True)
                    obs = st.text_input("Notas:")
                    
                    if st.form_submit_button("GUARDAR EN GOOGLE SHEETS"):
                        elegido = opciones[seleccion]
                        datos_finales = {
                            "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Militante": st.session_state.usuario_actual,
                            "DNI_Vecino": str(elegido[col_dni]),
                            "Nombre_Vecino": str(elegido[col_nom]),
                            "Estado": voto,
                            "Observaciones": obs
                        }
                        if enviar_a_google_sheets(datos_finales):
                            st.balloons()
                            st.success("¡Registrado!")
                        else: st.error("Error al guardar.")

    if st.button("SALIR"):
        st.session_state.autenticado = False
        st.rerun()
