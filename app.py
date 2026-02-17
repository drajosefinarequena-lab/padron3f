# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
CLAVE_MILITANTE = "tresdefebrero2026"

st.set_page_config(page_title="Lista 4 - Juan Debandi", page_icon="✌️")

# --- DISEÑO DE ALTO IMPACTO ---
st.markdown("""
    <style>
    /* Escudo con mucha más presencia (Marca de agua) */
    .stApp {
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Escudo_del_Partido_Justicialista.svg/1200px-Escudo_del_Partido_Justicialista.svg.png");
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        background-size: 550px; 
        opacity: 0.6; /* NIVEL ALTO: Ahora se va a ver bien marcado */
    }
    
    /* Banner Superior Sólido y Fuerte */
    .banner {
        background-color: #003366; /* Azul Noche Intenso */
        padding: 30px;
        border-radius: 0px 0px 20px 20px; /* Bordes redondeados solo abajo */
        margin: -50px -50px 30px -50px; /* Extiende el banner a los bordes */
        text-align: center;
        color: white;
        border-bottom: 5px solid #FFD700; /* Línea dorada de distinción */
    }

    .banner h1 { 
        font-size: 40px; 
        font-weight: 900; 
        text-shadow: 3px 3px 5px #000000;
        margin: 0;
    }
    .banner h3 { 
        font-size: 24px; 
        font-weight: bold; 
        margin-top: 10px;
        color: #FFD700; /* Texto dorado para el cargo */
    }

    /* Caja de búsqueda y tablas con fondo sólido para que se lean bien */
    .stTextInput, .stTable, .stDataFrame {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 10px;
        padding: 10px;
    }

    /* Botón Peronista */
    .stButton>button {
        width: 100%;
        background-color: #003366;
        color: white;
        font-weight: bold;
        font-size: 20px;
        height: 60px;
        border: 2px solid #FFD700;
        border-radius: 10px;
    }
    </style>
    
    <div class="banner">
        <h1>PERONISMO DE TODOS</h1>
        <h3>LISTA 4 - JUAN DEBANDI PRESIDENTE</h3>
    </div>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGUEO ---
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
            st.error("Clave incorrecta. Consultá con tu responsable de unidad básica.")
else:
    # --- BUSCADOR PRINCIPAL ---
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Escudo_del_Partido_Justicialista.svg/1200px-Escudo_del_Partido_Justicialista.svg.png", width=100)
    st.sidebar.title("CONDUCCIÓN")
    st.sidebar.subheader("JUAN DEBANDI")
    
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
        st.error("❌ No se encontró el archivo 'datos.csv'.")
    else:
        st.success(f"✅ PADRÓN CARGADO: {len(df)} AFILIADOS")
        
        busqueda = st.text_input("Buscá por DNI, APELLIDO o DIRECCIÓN:")

        if busqueda:
            termino = busqueda.upper()
            resultado = df[
                df['Matricula'].str.contains(termino, na=False) | 
                df['Apellido'].str.upper().str.contains(termino, na=False) |
                df['DIRECCION'].str.upper().str.contains(termino, na=False)
            ]
            
            if not resultado.empty:
                st.write(f"### Resultados encontrados:")
                columnas = ['Apellido', 'Nombre', 'Matricula', 'DIRECCION', 'CIRCUITO', 'EDAD']
                reales = [c for c in columnas if c in df.columns]
                st.dataframe(resultado[reales], use_container_width=True)
            else:
                st.warning("No se encontraron registros con esos datos.")
