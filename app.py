# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURACIÓN DE SEGURIDAD
CLAVE_MILITANTE = "tresdefebrero2026"
CLAVE_ADMIN = "josefina3f_admin"

st.set_page_config(page_title="Lista 4 - Juan Debandi", page_icon="✌️", layout="centered")

# --- DISEÑO DE CONTRASTE EXTREMO Y VISIBILIDAD TOTAL ---
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
    
    .block-container {
        padding-top: 1rem !important;
        max-width: 600px;
    }

    /* ETIQUETAS Y TEXTOS EN NEGRO PURO */
    label, p, h3, h4 {
        color: black !important;
        font-weight: 900 !important;
        font-size: 18px !important;
    }

    /* INPUTS CON BORDE NEGRO MUY MARCADO */
    .stTextInput input {
        background-color: white !important;
        color: black !important;
        border: 4px solid black !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }

    .bienvenida {
        text-align: center;
        color: white;
        background: #003366;
        padding: 10px;
        border: 3px solid black;
        font-weight: 900;
        font-size: 22px;
        margin-bottom: 10px;
    }

    .stButton>button {
        background-color: #00008B !important;
        color: white !important;
        font-weight: 900 !important;
        font-size: 20px !important;
        border: 3px solid #FFD700 !important;
    }

    /* Forzar que las tablas sean legibles */
    [data-testid="stDataFrame"] {
        background-color: white !important;
        border: 3px solid black !important;
    }

    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "es_admin" not in st.session_state:
    st.session_state["es_admin"] = False
if "log_ingresos" not in st.session_state:
    st.session_state["log_ingresos"] = []

# --- LÓGICA DE ACCESO ---
if not st.session_state["autenticado"]:
    # Mostramos el logo Peronismo de Todos
    if os.path.exists("Logo PDT - PJ.jpg.jpeg"):
        st.image("Logo PDT - PJ.jpg.jpeg", use_container_width=True)
    
    st.markdown('<div class="bienvenida">CONSULTA EL PADRÓN</div>', unsafe_allow_html=True)
    
    nombre_militante = st.text_input("NOMBRE O REFERENTE:", placeholder="Tu nombre")
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
            st.error("POR SEGURIDAD, ESCRIBÍ TU NOMBRE")
        else:
            st.error("CLAVE INCORRECTA")

else:
    # --- PANTALLA DE CONSULTA (YA LOGUEADO) ---
    # Achicamos el logo para que el buscador suba
    if os.path.exists("Logo PDT - PJ.jpg.jpeg"):
        st.image("Logo PDT - PJ.jpg.jpeg", width=200)

    st.markdown('<div class="bienvenida">CONSULTA EL PADRÓN</div>', unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;'>BienvenidX CompañerX</h4>", unsafe_allow_html=True)

    # --- PANEL ADMIN SEGURO ---
    if st.session_state["es_admin"]:
        with st.expander("🛡️ CONTROL DE INGRESOS"):
            if st.session_state["log_ingresos"]:
                st.table(pd.DataFrame(st.session_state["log_ingresos"]))
            else:
                st.write("No hay registros en esta sesión.")
    
    # --- CARGA DE DATOS ---
    @st.cache_data
    def cargar_datos():
        try:
            # Intentamos leer el archivo datos.csv
            df = pd.read_csv("datos.csv", sep=None, engine='python', encoding="utf-8", on_bad_lines='skip')
            # Limpiamos el DNI
            if 'Matricula' in df.columns:
                df['Matricula'] = df['Matricula'].astype(str).str.replace('.0', '', regex=False)
            return df
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
            return None

    df = cargar_datos()

    if df is not None:
        # EL BUSCADOR: Ahora bien visible y con instrucciones claras
        st.markdown("### 🔎 BUSCAR AFILIADO")
        busqueda = st.text_input("Ingresá DNI, Apellido o Calle:", placeholder="Ej: 30123456")

        if busqueda:
            termino = busqueda.upper()
            # Buscamos en todas las columnas para que sea fácil para el militante
            resultado = df[df.apply(lambda row: row.astype(str).str.upper().contains(termino).any(), axis=1)]
            
            if not resultado.empty:
                st.success(f"Se encontraron {len(resultado)} resultados:")
                # Mostramos la tabla (dataframe)
                st.dataframe(resultado, use_container_width=True)
            else:
                st.error("NO SE ENCONTRÓ NINGÚN RESULTADO")
    
    # Botón para salir
    st.write("")
    if st.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.session_state["es_admin"] = False
        st.rerun()
