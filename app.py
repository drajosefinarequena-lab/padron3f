# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURACIÓN DE SEGURIDAD
CLAVE_MILITANTE = "tresdefebrero2026"
CLAVE_ADMIN = "josefina3f_admin" # CAMBIÁ ESTA CLAVE POR UNA QUE SOLO VOS SEPAS

st.set_page_config(page_title="Lista 4 - Juan Debandi", page_icon="✌️", layout="centered")

# --- INICIALIZAR REGISTRO DE INGRESOS ---
if "log_ingresos" not in st.session_state:
    st.session_state["log_ingresos"] = []

# --- DISEÑO DE ALTO CONTRASTE ---
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Escudo_del_Partido_Justicialista.svg/1200px-Escudo_del_Partido_Justicialista.svg.png");
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        background-size: 500px; 
        background-color: white;
    }
    .stTextInput input { background-color: white !important; color: black !important; font-weight: bold !important; border: 3px solid #000000 !important; }
    [data-testid="stDataFrame"] { background-color: white !important; border: 2px solid black !important; }
    .bienvenida { text-align: center; color: black; background: white; padding: 15px; border: 4px solid #003366; border-radius: 10px; font-weight: 900; font-size: 30px; }
    .stButton>button { width: 100%; background-color: #00008B !important; color: white !important; font-weight: 900 !important; border: 4px solid #FFD700 !important; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGUEO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "es_admin" not in st.session_state:
    st.session_state["es_admin"] = False

if not st.session_state["autenticado"]:
    if os.path.exists("banner.jpg"):
        st.image("banner.jpg", use_container_width=True)
    
    st.markdown('<div class="bienvenida">CONSULTA EL PADRÓN</div>', unsafe_allow_html=True)
    
    nombre_militante = st.text_input("NOMBRE O REFERENTE:", placeholder="Para el registro interno")
    clave = st.text_input("CLAVE DE ACCESO:", type="password")
    
    if st.button("ENTRAR"):
        if clave == CLAVE_ADMIN:
            st.session_state["autenticado"] = True
            st.session_state["es_admin"] = True
            st.rerun()
        elif clave == CLAVE_MILITANTE and nombre_militante != "":
            # Registro el ingreso
            ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            st.session_state["log_ingresos"].append({"Fecha": ahora, "Usuario": nombre_militante})
            st.session_state["autenticado"] = True
            st.rerun()
        elif nombre_militante == "":
            st.warning("Por seguridad, debés ingresar tu nombre o referente.")
        else:
            st.error("CLAVE INCORRECTA")

else:
    # --- PESTAÑA DE ADMINISTRACIÓN (SOLO VISIBLE PARA VOS) ---
    if st.session_state["es_admin"]:
        with st.expander("🛡️ PANEL DE CONTROL SEGURO (SOLO ADMIN)"):
            st.write("### Registro de ingresos de militantes")
            if st.session_state["log_ingresos"]:
                df_logs = pd.DataFrame(st.session_state["log_ingresos"])
                st.table(df_logs)
            else:
                st.write("No hay ingresos registrados en esta sesión.")
            
            if st.button("CERRAR PANEL ADMIN"):
                st.session_state["autenticado"] = False
                st.session_state["es_admin"] = False
                st.rerun()
        st.markdown("---")

    # --- BUSCADOR NORMAL ---
    if os.path.exists("banner.jpg"):
        st.image("banner.jpg", use_container_width=True)
    st.markdown('<div class="bienvenida">CONSULTA EL PADRÓN</div>', unsafe_allow_html=True)
    
    @st.cache_data
    def cargar_datos():
        try:
            try:
                df = pd.read_csv("datos.csv", sep=None, engine='python', encoding="utf-8", on_bad_lines='skip')
            except:
                df = pd.read_csv("datos.csv", sep=None, engine='python', encoding="latin-1", on_bad_lines='skip')
            return df
        except: return None

    df = cargar_datos()
    if df is not None:
        busqueda = st.text_input("Buscá por DNI, Apellido o Calle:")
        if busqueda:
            termino = busqueda.upper()
            resultado = df[df.apply(lambda row: row.astype(str).str.contains(termino).any(), axis=1)]
            if not resultado.empty:
                st.dataframe(resultado, use_container_width=True)
            else:
                st.error("NO ENCONTRADO")
        
        if st.button("SALIR"):
            st.session_state["autenticado"] = False
            st.session_state["es_admin"] = False
            st.rerun()
