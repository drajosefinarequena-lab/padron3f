# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os

# 1. CONFIGURACIÓN
CLAVE_MILITANTE = "tresdefebrero2026"

st.set_page_config(page_title="Lista 4 - Juan Debandi", page_icon="✌️")

# --- DISEÑO: ESCUDO PJ Y MARCA DE AGUA ---
st.markdown("""
    <style>
    /* Escudo de fondo - MÁXIMA POTENCIA */
    .stApp {
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Escudo_del_Partido_Justicialista.svg/1200px-Escudo_del_Partido_Justicialista.svg.png");
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        background-size: 500px; 
        opacity: 0.5; /* Opacidad alta para que se vea bien el escudo */
    }
    
    /* Contenedor de datos con fondo blanco para lectura clara */
    .block-container {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 20px;
        margin-top: 10px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
    }

    /* Botón Peronista Estilizado */
    .stButton>button {
        width: 100%;
        background-color: #003366;
        color: white;
        font-weight: bold;
        height: 50px;
        border-radius: 10px;
        border: 2px solid #FFD700;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DEL BANNER JPG ---
# Buscamos el archivo banner.jpg en la carpeta
if os.path.exists("banner.jpg"):
    st.image("banner.jpg", use_container_width=True)
elif os.path.exists("banner.png"):
    st.image("banner.png", use_container_width=True)
else:
    # Si no hay imagen, un título fuerte por defecto
    st.markdown("<h1 style='text-align:center; color:#003366;'>PERONISMO DE TODOS - LISTA 4</h1>", unsafe_allow_html=True)

# --- SISTEMA DE ACCESO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h2 style='text-align:center;'>✌️ INGRESO MILITANTE</h2>", unsafe_allow_html=True)
    clave = st.text_input("Introducí la clave de acceso:", type="password")
    if st.button("INGRESAR"):
        if clave == CLAVE_MILITANTE:
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Clave incorrecta.")
else:
    # --- BUSCADOR ---
    st.sidebar.markdown("### Conducción")
    st.sidebar.subheader("JUAN DEBANDI")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()

    @st.cache_data
    def cargar_datos():
        try:
            # Detección automática de formato CSV
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
        st.success(f"✅ Padrón cargado con éxito.")
        busqueda = st.text_input("Buscá por DNI, Apellido o Dirección:")

        if busqueda:
            termino = busqueda.upper()
            resultado = df[
                df['Matricula'].str.contains(termino, na=False) | 
                df['Apellido'].str.upper().str.contains(termino, na=False) |
                df['DIRECCION'].str.upper().str.contains(termino, na=False)
            ]
            
            if not resultado.empty:
                st.write(f"Resultados de la **Lista 4**:")
                columnas = ['Apellido', 'Nombre', 'Matricula', 'DIRECCION', 'CIRCUITO', 'EDAD']
                reales = [c for c in columnas if c in df.columns]
                st.dataframe(resultado[reales], use_container_width=True)
            else:
                st.warning("No se encontraron registros.")
