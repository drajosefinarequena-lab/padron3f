# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
CLAVE_MILITANTE = "tresdefebrero2026"

st.set_page_config(page_title="Lista 4 - Juan Debandi", page_icon="✌️")

# --- DISEÑO MEJORADO: COLORES Y ESCUDO ---
st.markdown("""
    <style>
    /* Marca de agua con más presencia */
    .stApp {
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Escudo_del_Partido_Justicialista.svg/1200px-Escudo_del_Partido_Justicialista.svg.png");
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        background-size: 500px; 
        opacity: 0.25; /* Subimos de 0.1 a 0.25 para que se vea más fuerte */
    }
    
    /* Banner con degradado peronista */
    .banner {
        background: linear-gradient(90deg, #003366 0%, #0056b3 50%, #003366 100%);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 30px;
        text-align: center;
        color: white;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        border: 2px solid #ffffff;
    }

    /* Títulos del Banner */
    .banner h1 { font-size: 32px; font-weight: bold; text-shadow: 2px 2px 4px #000000; }
    .banner h3 { font-size: 20px; font-weight: normal; margin-top: 5px; }

    /* Botones más vibrantes */
    .stButton>button {
        width: 100%;
        background-color: #003366;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 50px;
        border: 1px solid white;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        border: 2px solid white;
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
    if st.button("ENTRAR AL SISTEMA"):
        if clave == CLAVE_MILITANTE:
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Clave incorrecta.")
else:
    # --- BUSCADOR PRINCIPAL ---
    st.sidebar.markdown("### Conducción")
    st.sidebar.title("JUAN DEBANDI")
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
        st.error("❌ Archivo 'datos.csv' no encontrado.")
    else:
        st.success(f"✅ Padrón Cargado: {len(df)} afiliados.")
        
        busqueda = st.text_input("Buscá por DNI, Apellido o Dirección:")

        if busqueda:
            termino = busqueda.upper()
            resultado = df[
                df['Matricula'].str.contains(termino, na=False) | 
                df['Apellido'].str.upper().str.contains(termino, na=False) |
                df['DIRECCION'].str.upper().str.contains(termino, na=False)
            ]
            
            if not resultado.empty:
                st.write(f"Resultados encontrados:")
                columnas = ['Apellido', 'Nombre', 'Matricula', 'DIRECCION', 'CIRCUITO', 'EDAD']
                reales = [c for c in columnas if c in df.columns]
                st.dataframe(resultado[reales], use_container_width=True)
            else:
                st.warning("No se encontraron registros.")
