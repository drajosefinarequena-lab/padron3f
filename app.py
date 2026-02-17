# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os

# 1. CONFIGURACIÓN
CLAVE_MILITANTE = "tresdefebrero2026"

st.set_page_config(page_title="Lista 4 - Juan Debandi", page_icon="✌️", layout="centered")

# --- DISEÑO COMPACTO Y ALTO IMPACTO ---
st.markdown("""
    <style>
    /* Escudo de fondo con fuerza */
    .stApp {
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Escudo_del_Partido_Justicialista.svg/1200px-Escudo_del_Partido_Justicialista.svg.png");
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        background-size: 500px; 
        opacity: 0.5;
    }
    
    /* Achicamos el espacio superior de Streamlit */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        max-width: 500px; /* Centra y achica el ancho para móviles */
    }

    /* Caja blanca compacta para el ingreso */
    .login-box {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
        border: 1px solid #ddd;
    }

    /* Botón Peronista Sólido */
    .stButton>button {
        width: 100%;
        background-color: #003366;
        color: white;
        font-weight: bold;
        height: 45px;
        border-radius: 8px;
        border: 2px solid #FFD700;
        margin-top: 10px;
    }
    
    /* Ocultar barra lateral y menús innecesarios */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGUEO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    # Mostramos el banner arriba de todo
    if os.path.exists("banner.jpg"):
        st.image("banner.jpg", use_container_width=True)
    elif os.path.exists("banner.png"):
        st.image("banner.png", use_container_width=True)
    else:
        st.markdown("<h2 style='text-align:center; color:#003366; background:white; border-radius:10px;'>LISTA 4 - JUAN DEBANDI</h2>", unsafe_allow_html=True)

    # Caja de login compacta
    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center; margin-top:0; color:#003366;'>✌️ INGRESO</h3>", unsafe_allow_html=True)
        clave = st.text_input("Clave:", type="password", label_visibility="collapsed", placeholder="Introducí la clave aquí")
        if st.button("ENTRAR"):
            if clave == CLAVE_MILITANTE:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Clave incorrecta.")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- BUSCADOR (YA LOGUEADO) ---
    if os.path.exists("banner.jpg"):
        st.image("banner.jpg", width=250) # Banner más chico una vez adentro
    
    st.markdown("### 🔎 Consulta de Padrón")
    
    @st.cache_data
    def cargar_datos():
        try:
            try:
                df = pd.read_csv("datos.csv", sep=None, engine='python', encoding="utf-8", on_bad_lines='skip')
            except:
                df = pd.read_csv("datos.csv", sep=None, engine='python', encoding="latin-1", on_bad_lines='skip')
            if 'Matricula' in df.columns:
                df['Matricula'] = df['Matricula'].astype(str).str.replace('.0', '', regex=False)
            return df
        except:
            return None

    df = cargar_datos()

    if df is not None:
        busqueda = st.text_input("DNI, Apellido o Dirección:", placeholder="Ej: 30123456")
        if busqueda:
            termino = busqueda.upper()
            resultado = df[
                df['Matricula'].str.contains(termino, na=False) | 
                df['Apellido'].str.upper().str.contains(termino, na=False) |
                df['DIRECCION'].str.upper().str.contains(termino, na=False)
            ]
            if not resultado.empty:
                columnas = ['Apellido', 'Nombre', 'Matricula', 'DIRECCION', 'CIRCUITO', 'EDAD']
                reales = [c for c in columnas if c in df.columns]
                st.dataframe(resultado[reales], use_container_width=True)
            else:
                st.warning("No encontrado.")
        
        # Botón de salir discreto abajo
        if st.button("Cerrar Sesión"):
            st.session_state["autenticado"] = False
            st.rerun()
