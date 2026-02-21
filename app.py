# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURACIÓN DE SEGURIDAD
CLAVE_MILITANTE = "interna123pj2026"
CLAVE_ADMIN = "josefina3f_admin"

st.set_page_config(page_title="Lista 4 - Juan Debandi", page_icon="✌️", layout="centered")

# --- DISEÑO DE ALTO CONTRASTE ---
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
    .block-container { padding-top: 1rem !important; max-width: 600px; }
    label, p, h3, h4 { color: black !important; font-weight: 900 !important; font-size: 18px !important; }
    .stTextInput input { background-color: white !important; color: black !important; border: 4px solid black !important; font-weight: bold !important; font-size: 18px !important; }
    .bienvenida { text-align: center; color: white; background: #003366; padding: 10px; border: 3px solid black; font-weight: 900; font-size: 22px; margin-bottom: 10px; }
    .stButton>button { background-color: #00008B !important; color: white !important; font-weight: 900 !important; font-size: 20px !important; border: 3px solid #FFD700 !important; }
    [data-testid="stDataFrame"] { background-color: white !important; border: 3px solid black !important; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN CRÍTICA DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "es_admin" not in st.session_state:
    st.session_state.es_admin = False
if "log_ingresos" not in st.session_state:
    st.session_state.log_ingresos = []

# --- CARGA DE DATOS (FUERA DEL BUCLE DE LOGIN) ---
@st.cache_data
def cargar_datos():
    for enc in ['latin-1', 'iso-8859-1', 'cp1252', 'utf-8']:
        try:
            df = pd.read_csv("datos.csv", sep=None, engine='python', encoding=enc, on_bad_lines='skip')
            df = df.fillna('')
            if 'Matricula' in df.columns:
                df['Matricula'] = df['Matricula'].astype(str).str.replace('.0', '', regex=False)
            return df
        except:
            continue
    return None

# --- LÓGICA DE PANTALLAS ---
if not st.session_state.autenticado:
    # PANTALLA DE LOGIN
    if os.path.exists("Logo PDT - PJ.jpg.jpeg"):
        st.image("Logo PDT - PJ.jpg.jpeg", use_container_width=True)
    st.markdown('<div class="bienvenida">INGRESO MILITANTE - LISTA 4</div>', unsafe_allow_html=True)
    
    nombre_ingresado = st.text_input("NOMBRE O REFERENTE:", key="nom_login")
    clave_ingresada = st.text_input("CLAVE DE ACCESO:", type="password", key="pwd_login")
    
    if st.button("ACCEDER AL PADRÓN"):
        if clave_ingresada == CLAVE_ADMIN:
            st.session_state.autenticado = True
            st.session_state.es_admin = True
            st.rerun()
        elif clave_ingresada == CLAVE_MILITANTE and nombre_ingresado != "":
            ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            st.session_state.log_ingresos.append({"Fecha": ahora, "Usuario": nombre_ingresado})
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("DATOS INCORRECTOS")

else:
    # PANTALLA DE BÚSQUEDA (SOLO SE VE SI st.session_state.autenticado == True)
    if os.path.exists("Logo PDT - PJ.jpg.jpeg"):
        st.image("Logo PDT - PJ.jpg.jpeg", width=150)
    
    st.markdown('<div class="bienvenida">CONSULTA EL PADRÓN</div>', unsafe_allow_html=True)
    
    if st.session_state.es_admin:
        with st.expander("🛡️ PANEL DE CONTROL (ADMIN)"):
            if st.session_state.log_ingresos:
                st.table(pd.DataFrame(st.session_state.log_ingresos))
    
    df = cargar_datos()
    
    if df is not None:
        st.markdown("### 🔎 BUSCAR")
        # El buscador está fuera de cualquier formulario para que responda al instante
        busqueda = st.text_input("Ingresá DNI o Apellido:", key="campo_busqueda")
        
        if busqueda:
            termino = busqueda.upper()
            mask = df.astype(str).apply(lambda row: row.str.upper().str.contains(termino)).any(axis=1)
            resultado = df[mask]
            
            if not resultado.empty:
                st.success(f"Encontrados: {len(resultado)}")
                st.dataframe(resultado, use_container_width=True)
            else:
                st.warning("NO SE ENCONTRARON RESULTADOS")
    
    st.write("---")
    if st.button("CERRAR SESIÓN"):
        st.session_state.autenticado = False
        st.session_state.es_admin = False
        st.rerun()

