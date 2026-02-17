# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os

# 1. CONFIGURACIÓN
CLAVE_MILITANTE = "tresdefebrero2026"

st.set_page_config(page_title="Lista 4 - Juan Debandi", page_icon="✌️", layout="centered")

# --- DISEÑO DE CONTRASTE EXTREMO PARA SOL ---
st.markdown("""
    <style>
    /* Fondo con Escudo al 100% de color (Sin transparencia para que se vea bajo el sol) */
    .stApp {
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Escudo_del_Partido_Justicialista.svg/1200px-Escudo_del_Partido_Justicialista.svg.png");
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        background-size: 500px; 
        background-color: white; /* Fondo blanco sólido */
    }
    
    /* CAJAS TOTALMENTE BLANCAS Y LETRAS NEGRAS PURAS */
    .stTextInput input {
        background-color: white !important;
        color: black !important;
        font-weight: bold !important;
        border: 3px solid #000000 !important;
        font-size: 20px !important;
    }

    /* Tablas con máximo contraste */
    [data-testid="stDataFrame"] {
        background-color: white !important;
        border: 2px solid black !important;
    }
    
    /* Forzar texto de tabla en Negro Absoluto */
    [data-testid="stTable"] td, [data-testid="stDataFrame"] td, th {
        color: black !important;
        font-weight: 800 !important;
        font-size: 16px !important;
    }

    .block-container {
        padding-top: 1rem !important;
        max-width: 600px;
    }

    /* Botón Azul Intenso con Letra Blanca Gruesa */
    .stButton>button {
        width: 100%;
        background-color: #00008B !important; /* Azul Rey muy oscuro */
        color: white !important;
        font-weight: 900 !important;
        font-size: 24px !important;
        height: 60px;
        border-radius: 5px;
        border: 4px solid #FFD700 !important; /* Borde dorado fuerte */
        text-transform: uppercase;
    }
    
    /* Mensajes de Bienvenida */
    .bienvenida {
        text-align: center;
        color: black;
        background: white;
        padding: 15px;
        border: 4px solid #003366;
        border-radius: 10px;
        font-weight: 900;
        font-size: 30px !important;
    }

    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGUEO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    if os.path.exists("banner.jpg"):
        st.image("banner.jpg", use_container_width=True)
    
    st.markdown('<div class="bienvenida">CONSULTA EL PADRÓN</div>', unsafe_allow_html=True)
    
    clave = st.text_input("CLAVE:", type="password", placeholder="Escribí la contraseña")
    if st.button("ENTRAR"):
        if clave == CLAVE_MILITANTE:
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("CLAVE INCORRECTA")

else:
    # --- PANTALLA DE CONSULTA ---
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
            if 'Matricula' in df.columns:
                df['Matricula'] = df['Matricula'].astype(str).str.replace('.0', '', regex=False)
            return df
        except:
            return None

    df = cargar_datos()

    if df is not None:
        st.markdown("<b style='color:black; font-size:20px;'>Buscá por DNI, Apellido o Calle:</b>", unsafe_allow_html=True)
        busqueda = st.text_input("Buscador", label_visibility="collapsed")
        
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
                # Estilo de tabla de alto contraste
                st.dataframe(resultado[reales], use_container_width=True)
            else:
                st.error("NO ENCONTRADO")
        
        st.write("")
        if st.button("SALIR"):
            st.session_state["autenticado"] = False
            st.rerun()
