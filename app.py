# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# 1. SEGURIDAD: LOCALIDADES
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

st.set_page_config(page_title="Lista 4 - Auditoría Total", page_icon="✌️", layout="centered")

# --- REGISTRO DE EVENTOS (LOG) ---
def registrar_evento(usuario, accion, detalle):
    archivo_log = "auditoria_completa.csv"
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Intentamos obtener la IP del usuario
    try:
        ip = requests.get('https://api.ipify.org', timeout=2).text
    except:
        ip = "No detectada"
        
    nuevo_log = pd.DataFrame([{
        "Fecha": ahora, 
        "Usuario": usuario, 
        "Accion": accion, 
        "Detalle": detalle, 
        "IP": ip
    }])
    
    if not os.path.isfile(archivo_log):
        nuevo_log.to_csv(archivo_log, index=False, encoding='utf-8')
    else:
        nuevo_log.to_csv(archivo_log, mode='a', header=False, index=False, encoding='utf-8')

# --- SESIÓN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "es_admin" not in st.session_state: st.session_state.es_admin = False

# --- PANTALLA DE ACCESO ---
if not st.session_state.autenticado:
    st.markdown("<h2 style='text-align:center;'>✌️ LISTA 4 - INGRESO</h2>", unsafe_allow_html=True)
    
    acepta = st.checkbox("Acepto el registro de mi actividad por seguridad")
    loc = st.selectbox("LOCALIDAD:", ["---"] + list(USUARIOS_AUTORIZADOS.keys()))
    pin = st.text_input("CLAVE:", type="password")
    
    if st.button("ACCEDER", disabled=not acepta):
        if pin == CLAVE_ADMIN:
            st.session_state.autenticado = True
            st.session_state.es_admin = True
            registrar_evento("ADMIN", "INGRESO", "Entró al Panel de Control")
            st.rerun()
        elif loc in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[loc] == pin:
            st.session_state.autenticado = True
            st.session_state.usuario_actual = loc
            registrar_evento(loc, "INGRESO", "Sesión iniciada")
            st.rerun()
        else:
            st.error("Datos incorrectos")

else:
    # --- PANEL DE ADMINISTRADOR ---
    if st.session_state.es_admin:
        st.markdown("### 🛡️ PANEL DE CONTROL DE INGRESOS Y CONSULTAS")
        if os.path.exists("auditoria_completa.csv"):
            log_data = pd.read_csv("auditoria_completa.csv")
            st.dataframe(log_data.sort_index(ascending=False), use_container_width=True)
            if st.button("Limpiar historial (Solo Admin)"):
                os.remove("auditoria_completa.csv")
                st.rerun()
        else:
            st.info("No hay ingresos registrados todavía.")

    # --- BUSCADOR ---
    st.markdown("---")
    st.markdown("### 🔎 CONSULTA DE PADRÓN")
    
    @st.cache_data
    def cargar_datos():
        try:
            df = pd.read_csv("datos.csv", sep=None, engine='python', encoding='latin-1')
            # Solo columnas básicas: DNI, Nombre, Apellido, Dirección
            visibles = [c for c in df.columns if any(x in c.upper() for x in ['DNI', 'MATRICULA', 'NOMBRE', 'APELLIDO', 'DIRECCION', 'CALLE'])]
            return df[visibles].fillna('')
        except: return None

    padron = cargar_datos()

    if padron is not None:
        busqueda = st.text_input("Buscá por Apellido, DNI o Calle:")
        if busqueda:
            # REGISTRAR LA BÚSQUEDA
            user_log = "ADMIN" if st.session_state.es_admin else st.session_state.usuario_actual
            registrar_evento(user_log, "BÚSQUEDA", busqueda)
            
            # FILTRAR
            termino = busqueda.upper()
            mask = padron.astype(str).apply(lambda row: row.str.upper().str.contains(termino)).any(axis=1)
            res = padron[mask]
            
            if not res.empty:
                st.success(f"Resultados: {len(res)}")
                st.dataframe(res, use_container_width=True)
            else:
                st.warning("No se encontraron resultados.")

    if st.button("SALIR"):
        st.session_state.autenticado = False
        st.rerun()
