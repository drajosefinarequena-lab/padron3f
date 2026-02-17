# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
CLAVE_MILITANTE = "tresdefebrero2026"

st.set_page_config(page_title="Lista 4 - Juan Debandi", page_icon="✌️")

# --- BANNER Y MARCA DE AGUA (ESCUDO PJ) ---
st.markdown("""
    <style>
    /* Marca de agua de fondo */
    .stApp {
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Escudo_del_Partido_Justicialista.svg/1200px-Escudo_del_Partido_Justicialista.svg.png");
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        background-size: 600px; /* Tamaño del escudo */
        opacity: 0.1; /* Transparencia: 0.1 es muy suave */
    }
    
    /* Contenedor del Banner Azul */
    .banner {
        background-color: #0056b3;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 25px;
        text-align: center;
        color: white;
    }

    /* Botón de ingreso */
    .stButton>button {
        width: 100%;
        background-color: #0056b3;
        color: white;
        font-weight: bold;
    }
    </style>
    
    <div class="banner">
        <h1 style="margin:0;">PERONISMO DE TODOS</h1>
        <h3 style="margin:0;">LISTA 4 - JUAN DEBANDI PRESIDENTE</h3>
    </div>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGUEO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.title("✌️ Ingreso Militante")
    clave = st.text_input("Introducí la clave de acceso:", type="password")
    if st.button("Entrar al Sistema"):
        if clave == CLAVE_MILITANTE:
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Clave incorrecta.")
else:
    # --- BUSCADOR PRINCIPAL ---
    st.sidebar.header("Conducción Juan Debandi")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()

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

    if df is None:
        st.error("❌ No se encuentra el archivo 'datos.csv'")
    else:
        st.success(f"✅ Padrón activo. {len(df)} afiliados cargados.")
        
        busqueda = st.text_input("Buscá por DNI, Apellido o Dirección:")

        if busqueda:
            termino = busqueda.upper()
            resultado = df[
                df['Matricula'].str.contains(termino, na=False) | 
                df['Apellido'].str.upper().str.contains(termino, na=False) |
                df['DIRECCION'].str.upper().str.contains(termino, na=False)
            ]
            
            if not resultado.empty:
                st.write(f"Resultados para la **Lista 4**:")
                columnas = ['Apellido', 'Nombre', 'Matricula', 'DIRECCION', 'CIRCUITO', 'EDAD']
                reales = [c for c in columnas if c in df.columns]
                st.dataframe(resultado[reales], use_container_width=True)
            else:
                st.warning("No se encontraron resultados.")
