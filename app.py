# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURACIÓN DE SEGURIDAD
CLAVE_MILITANTE = "tresdefebrero2026"
CLAVE_ADMIN = "josefina3f_admin"

st.set_page_config(page_title="Lista 4 - Juan Debandi", page_icon="✌️", layout="centered")

# --- DISEÑO DE CONTRASTE EXTREMO Y VISIBILIDAD MÓVIL ---
st.markdown("""
    <style>
    .stApp {
        background-color: white;
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Escudo_del_Partido_Justicialista.svg/1200px-Escudo_del_Partido_Justicialista.svg.png");
        background-repeat: no-repeat;
        background-position: center;
        background-size: 400px;
        opacity: 0.8;
    }
    
    /* Reducir márgenes superiores para que el teclado no tape todo */
    .block-container {
        padding-top: 0.5rem !important;
        max-width: 500px;
    }

    /* ETIQUETAS NEGRAS Y GRUESAS PARA QUE SE VEAN AL SOL */
    label {
        color: black !important;
        font-weight: 900 !important;
        font-size: 18px !important;
        background: white;
        padding: 2px 5px;
        border-radius: 3px;
    }

    /* INPUTS CON BORDE NEGRO GRUESO */
    .stTextInput input {
        background-color: white !important;
        color: black !important;
        border: 3px solid black !important;
        height: 45px !important;
    }

    .bienvenida {
        text-align: center;
        color: white;
        background: #003366;
        padding: 10px;
        border: 3px solid black;
        font-weight: 900;
        font-size: 22px;
        margin-bottom: 15px;
    }

    .stButton>button {
        background-color: #00008B !important;
        color: white !important;
        font-weight: 900 !important;
        font-size: 22px !important;
        border: 3px solid #FFD700 !important;
        margin-top: 10px;
    }

    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGUEO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "es_admin" not in st.session_state:
    st.session_state["es_admin"] = False
if "log_ingresos" not in st.session_state:
    st.session_state["log_ingresos"] = []

if not st.session_state["autenticado"]:
    # Mostramos el logo nuevo (PDT) si existe
    if os.path.exists("Logo PDT - PJ.jpg.jpeg"):
        st.image("Logo PDT - PJ.jpg.jpeg", use_container_width=True)
    
    st.markdown('<div class="bienvenida">CONSULTA EL PADRÓN</div>', unsafe_allow_html=True)
    
    # Usamos labels claros y obligatorios
    nombre_militante = st.text_input("NOMBRE O REFERENTE:", placeholder="Tu nombre o UB")
    clave = st.text_input("CLAVE DE ACCESO:", type="password", placeholder="Contraseña")
    
    if st.button("ENTRAR AL SISTEMA"):
        if clave == CLAVE_ADMIN:
            st.session_state["autenticado"] = True
            st.session_state["es_admin"] = True
            st.rerun()
        elif clave == CLAVE_MILITANTE and nombre_militante != "":
            ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            st.session_state["log_ingresos"].append({"Fecha": ahora, "Usuario": nombre_militante})
            st.session_state["autenticado"] = True
            st.rerun()
        elif nombre_militante == "":
            st.error("DEBÉS PONER TU NOMBRE PARA EL REGISTRO")
        else:
            st.error("CLAVE INCORRECTA")

else:
    # --- PANEL ADMIN ---
    if st.session_state["es_admin"]:
        with st.expander("🛡️ CONTROL DE INGRESOS"):
            if st.session_state["log_ingresos"]:
                st.table(pd.DataFrame(st.session_state["log_ingresos"]))
            else:
                st.write("Sin registros.")
            if st.button("SALIR ADMIN"):
                st.session_state["autenticado"] = False
                st.rerun()

    # --- PANTALLA PRINCIPAL ---
    st.markdown('<div class="bienvenida">CONSULTA EL PADRÓN</div>', unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align:center; color:black;'>BienvenidX CompañerX</h4>", unsafe_allow_html=True)
    
    @st.cache_data
    def cargar_datos():
        try:
            df = pd.read_csv("datos.csv", sep=None, engine='python', encoding="utf-8", on_bad_lines='skip')
            if 'Matricula' in df.columns:
                df['Matricula'] = df['Matricula'].astype(str).str.replace('.0', '', regex=False)
            return df
        except: return None

    df = cargar_datos()
    if df is not None:
        busqueda = st.text_input("Buscá por DNI, Apellido o Calle:")
        if busqueda:
            termino = busqueda.upper()
            resultado = df[df.apply(lambda row: row.astype(str).str.upper().contains(termino).any(), axis=1)]
            if not resultado.empty:
                st.dataframe(resultado, use_container_width=True)
            else:
                st.error("NO ENCONTRADO")
        
        if st.button("CERRAR SESIÓN"):
            st.session_state["autenticado"] = False
            st.rerun()
