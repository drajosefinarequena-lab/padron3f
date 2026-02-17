# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE SEGURIDAD
CLAVE_MILITANTE = "tresdefebrero2026"

st.set_page_config(page_title="Padrón 2026 - 3F", page_icon="✌️")

# Estilo visual peronista
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; background-color: #0056b3; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGUEO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.title("✌️ Ingreso Militante")
    st.subheader("Sistema de Consultas - Padrón 2026")
    
    clave = st.text_input("Introducí la clave de acceso:", type="password")
    if st.button("Entrar al Sistema"):
        if clave == CLAVE_MILITANTE:
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Clave incorrecta. Consultá con tu referente.")
else:
    # --- BUSCADOR PRINCIPAL ---
    st.title("🔎 Buscador Padrón 2026")
    st.sidebar.header("Opciones")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()

    # Función para cargar los datos con corrección de errores automática
    @st.cache_data
    def cargar_datos():
        try:
            # Usamos motor Python y on_bad_lines para saltear filas rotas
            # Probamos primero con la codificación más común
            try:
                df = pd.read_csv("datos.csv", sep=None, engine='python', encoding="utf-8", on_bad_lines='skip')
            except:
                df = pd.read_csv("datos.csv", sep=None, engine='python', encoding="latin-1", on_bad_lines='skip')
            
            # Limpiamos los datos
            if 'Matricula' in df.columns:
                df['Matricula'] = df['Matricula'].astype(str).str.replace('.0', '', regex=False)
            return df
        except Exception as e:
            return None

    df = cargar_datos()

    if df is None:
        st.error("❌ ERROR: No se encuentra el archivo 'datos.csv' o el formato es inválido.")
        st.info("Asegurate de que el archivo se llame 'datos.csv' y esté en la misma carpeta que este programa.")
    else:
        st.success(f"✅ Padrón cargado. Total de registros: {len(df)}")
        
        st.markdown("### Consultar Compañero")
        busqueda = st.text_input("Buscá por DNI (Matrícula), Apellido o Dirección:")

        if busqueda:
            termino = busqueda.upper()
            
            # Buscamos en las columnas que tiene tu archivo PADRON2026
            # Usamos 'na=False' para evitar errores si hay celdas vacías
            resultado = df[
                df['Matricula'].str.contains(termino, na=False) | 
                df['Apellido'].str.upper().str.contains(termino, na=False) |
                df['DIRECCION'].str.upper().str.contains(termino, na=False)
            ]
            
            if not resultado.empty:
                st.write(f"Se encontraron **{len(resultado)}** resultados:")
                
                # Definimos qué columnas mostrar para que no se vea desordenado
                columnas_interes = ['Apellido', 'Nombre', 'Matricula', 'DIRECCION', 'CIRCUITO', 'EDAD']
                columnas_reales = [c for c in columnas_interes if c in df.columns]
                
                st.dataframe(resultado[columnas_reales], use_container_width=True)
            else:
                st.warning("No se encontraron resultados para esa búsqueda.")