# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# 1. CONFIGURACIÓN DE SEGURIDAD
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

# --- REGISTRO PERSISTENTE (ÉXITOS Y ERRORES) ---
def registrar_evento(usuario, ubicacion, resultado):
    archivo_log = "log_accesos.csv"
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nuevo_registro = pd.DataFrame([{"Fecha": ahora, "Usuario_Intentado": usuario, "Ubicacion": ubicacion, "Resultado": resultado}])
    
    if not os.path.isfile(archivo_log):
        nuevo_registro.to_csv(archivo_log, index=False, encoding='utf-8')
    else:
        nuevo_registro.to_csv(archivo_log, mode='a', header=False, index=False, encoding='utf-8')

def obtener_datos_ip():
    try:
        r = requests.get('https://ipapi.co/json/', timeout=3)
        data = r.json()
        return f"{data.get('city')}, {data.get('region')} (IP: {data.get('ip')})"
    except: return "IP No rastreable"

# --- DISEÑO ---
st.markdown("""
    <style>
    .stApp { background-color: white; background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Escudo_del_Partido_Justicialista.svg/1200px-Escudo_del_Partido_Justicialista.svg.png"); background-repeat: no-repeat; background-position: center; background-size: 400px; opacity: 0.9; }
    .bienvenida { text-align: center; color: white; background: #003366; padding: 15px; border: 3px solid black; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "es_admin" not in st.session_state: st.session_state.es_admin = False

# --- ACCESO ---
if not st.session_state.autenticado:
    if os.path.exists("Logo PDT - PJ.jpg.jpeg"):
        st.image("Logo PDT - PJ.jpg.jpeg", use_container_width=True)
    st.markdown('<div class="bienvenida">INGRESO SEGURO - LISTA 4</div>', unsafe_allow_html=True)
    
    acepta = st.checkbox("ACEPTO EL REGISTRO DE MI UBICACIÓN")
    user_ing = st.selectbox("LOCALIDAD:", ["---"] + list(USUARIOS_AUTORIZADOS.keys()))
    pass_ing = st.text_input("CLAVE:", type="password")
    
    if st.button("ENTRAR", disabled=not acepta):
        ubi_actual = obtener_datos_ip()
        if pass_ing == CLAVE_ADMIN:
            st.session_state.autenticado = True
            st.session_state.es_admin = True
            registrar_evento("ADMIN", ubi_actual, "EXITO_ADMIN")
            st.rerun()
        elif user_ing in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[user_ing] == pass_ing:
            registrar_evento(user_ing, ubi_actual, "EXITO")
            st.session_state.autenticado = True
            st.session_state.usuario_actual = user_ing
            st.rerun()
        else:
            # REGISTRAMOS EL ERROR
            registrar_evento(user_ing if user_ing != "---" else "DESCONOCIDO", ubi_actual, "ERROR_LOGIN")
            st.error("CLAVE INCORRECTA. Intento registrado por seguridad.")
else:
    # --- BUSCADOR ---
    if st.session_state.es_admin:
        with st.expander("🛡️ AUDITORÍA DE SEGURIDAD (ÉXITOS Y ERRORES)"):
            if os.path.exists("log_accesos.csv"):
                log_df = pd.read_csv("log_accesos.csv")
                # Resaltamos los errores en rojo para tu vista
                st.dataframe(log_df.style.apply(lambda x: ['background: #ffcccc' if v == 'ERROR_LOGIN' else '' for v in x], axis=1), use_container_width=True)
    
    # ... (Carga de datos y buscador DNI/Nombre/Apellido/Dirección que ya configuramos)
