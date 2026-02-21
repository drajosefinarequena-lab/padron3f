# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# 1. CONFIGURACIÓN DE SEGURIDAD Y CLAVES
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

# --- ESTILOS DE ALTO CONTRASTE ---
st.markdown("""
    <style>
    .stApp { background-color: white; background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Escudo_del_Partido_Justicialista.svg/1200px-Escudo_del_Partido_Justicialista.svg.png"); background-repeat: no-repeat; background-position: center; background-size: 400px; opacity: 0.9; }
    label, p, h3, h4 { color: black !important; font-weight: 900 !important; }
    .stTextInput input { background-color: white !important; color: black !important; border: 4px solid black !important; }
    .bienvenida { text-align: center; color: white; background: #003366; padding: 15px; border: 3px solid black; font-weight: 900; font-size: 20px; }
    .stButton>button { background-color: #00008B !important; color: white !important; font-weight: 900 !important; border: 3px solid #FFD700 !important; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE REGISTRO PERSISTENTE (ARCHIVO LOG) ---
def registrar_ingreso(usuario, ubicacion):
    archivo_log = "log_accesos.csv"
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nuevo_registro = pd.DataFrame([{"Fecha": ahora, "Usuario": usuario, "Ubicacion": ubicacion}])
    
    if not os.path.isfile(archivo_log):
        nuevo_registro.to_csv(archivo_log, index=False, encoding='utf-8')
    else:
        nuevo_registro.to_csv(archivo_log, mode='a', header=False, index=False, encoding='utf-8')

# --- SESIÓN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "es_admin" not in st.session_state: st.session_state.es_admin = False

def obtener_datos_ip():
    try:
        r = requests.get('https://ipapi.co/json/', timeout=3)
        data = r.json()
        return f"{data.get('city')}, {data.get('region')} (IP: {data.get('ip')})"
    except: return "IP No rastreable"

# --- ACCESO ---
if not st.session_state.autenticado:
    if os.path.exists("Logo PDT - PJ.jpg.jpeg"):
        st.image("Logo PDT - PJ.jpg.jpeg", use_container_width=True)
    st.markdown('<div class="bienvenida">INGRESO SEGURO - LISTA 4</div>', unsafe_allow_html=True)
    acepta_terminos = st.checkbox("ACEPTO EL REGISTRO PERMANENTE DE MI UBICACIÓN")
    usuario_ing = st.selectbox("LOCALIDAD:", ["---"] + list(USUARIOS_AUTORIZADOS.keys()))
    clave_ing = st.text_input("CLAVE:", type="password")
    
    if st.button("ENTRAR", disabled=not acepta_terminos):
        if clave_ing == CLAVE_ADMIN:
            st.session_state.autenticado = True
            st.session_state.es_admin = True
            st.rerun()
        elif usuario_ing in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[usuario_ing] == clave_ing:
            ubi = obtener_datos_ip()
            registrar_ingreso(usuario_ing, ubi)
            st.session_state.autenticado = True
            st.session_state.usuario_actual = usuario_ing
            st.rerun()
        else:
            st.error("DATOS INCORRECTOS")
else:
    # --- BUSCADOR ---
    st.markdown('<div class="bienvenida">CONSULTA EL PADRÓN</div>', unsafe_allow_html=True)
    
    if st.session_state.es_admin:
        with st.expander("🛡️ AUDITORÍA HISTÓRICA DE INGRESOS"):
            if os.path.exists("log_accesos.csv"):
                st.table(pd.read_csv("log_accesos.csv"))
            else:
                st.write("No hay registros aún.")

    @st.cache_data
    def cargar_datos():
        for enc in ['latin-1', 'iso-8859-1', 'cp1252', 'utf-8']:
            try:
                df_c = pd.read_csv("datos.csv", sep=None, engine='python', encoding=enc, on_bad_lines='skip')
                df_c = df_c.fillna('')
                
                # NORMALIZAR COLUMNAS PARA VISIBILIDAD ESTRICTA
                # Aquí definimos exactamente qué columnas queremos mostrar
                columnas_visibles = []
                for col in df_c.columns:
                    c_up = col.upper()
                    if 'MATRICULA' in c_up or 'DNI' in c_up: columnas_visibles.append(col)
                    if 'NOMBRE' in c_up: columnas_visibles.append(col)
                    if 'APELLIDO' in c_up: columnas_visibles.append(col)
                    if 'DIRECCION' in c_up or 'DOMICILIO' in c_up or 'CALLE' in c_up: columnas_visibles.append(col)
                
                # Filtramos el DataFrame
                df_c = df_c[columnas_visibles]
                
                if any('MATRICULA' in c.upper() or 'DNI' in c.upper() for c in df_c.columns):
                    col_dni = [c for c in df_c.columns if 'MATRICULA' in c.upper() or 'DNI' in c.upper()][0]
                    df_c[col_dni] = df_c[col_dni].astype(str).str.replace('.0', '', regex=False)
                
                return df_c
            except: continue
        return None

    df = cargar_datos()

    if df is not None:
        with st.form("buscador_form"):
            busqueda = st.text_input("Ingresá DNI o Apellido:")
            if st.form_submit_button("BUSCAR"):
                if busqueda:
                    mask = df.astype(str).apply(lambda row: row.str.upper().str.contains(busqueda.upper())).any(axis=1)
                    res = df[mask]
                    if not res.empty:
                        st.success(f"Encontrados: {len(res)}")
                        st.dataframe(res, use_container_width=True)
                    else: st.error("NO ENCONTRADO")

    if st.button("CERRAR SESIÓN"):
        st.session_state.autenticado = False
        st.rerun()
