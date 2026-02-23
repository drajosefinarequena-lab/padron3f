# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection # Necesitás agregar esto a requirements.txt
from datetime import datetime
import requests
import os

# 1. CONFIGURACIÓN DE SEGURIDAD (CON TU NUEVA NOMENCLATURA)
LOCALIDADES_CLAVES = {
    "CASEROS": "caseros2026",
    "CIUDADELA": "ciudadela2026",
    "BARRIO_EJERCITO": "barrioejercito2026",
    "VILLA_BOSCH": "villabosch2026",
    "MARTIN_CORONADO": "martincoronado2026",
    "CIUDAD_JARDIN": "ciudadjardin2026",
    "SANTOS_LUGARES": "santoslugares2026",
    "SAENZ_PEÑA": "saenzpeña2026",
    "PODESTA": "podesta2026",
    "CHURRUCA": "churruca2026",
    "EL_LIBERTADOR": "ellibertador2026",
    "LOMA_HERMOSA": "lomahermosa2026"
}
CLAVE_ADMIN = "josefina3f_admin"

st.set_page_config(page_title="Lista 4 - Gestión Territorial", page_icon="✌️")

# --- CONEXIÓN A GOOGLE SHEETS ---
# Usamos el nombre del archivo que ya tenés: Base_Campaña_Lista4_3F
conn = st.connection("gsheets", type=GSheetsConnection)

def registrar_consulta_google(nombre, localidad, busqueda):
    try:
        ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        ip = requests.get('https://api.ipify.org', timeout=2).text
        
        # Estructura según tu hoja "resultados"
        nueva_fila = pd.DataFrame([{
            "Fecha": ahora,
            "Usuario": nombre,
            "Célula/Localidad": localidad,
            "Término Buscado": busqueda,
            "Ubicación (IP)": ip
        }])
        
        # Leemos los datos actuales y sumamos el nuevo registro
        df_existente = conn.read(worksheet="resultados")
        df_actualizado = pd.concat([df_existente, nueva_fila], ignore_index=True)
        
        # Guardamos en la nube
        conn.update(worksheet="resultados", data=df_actualizado)
    except Exception as e:
        st.error(f"Error al registrar en Google Sheets: {e}")

# --- DISEÑO Y LOGUEO ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("### ✌️ LISTA 4 - INGRESO MILITANTE")
    nombre_m = st.text_input("NOMBRE Y APELLIDO:")
    loc_sel = st.selectbox("LOCALIDAD:", ["---"] + list(LOCALIDADES_CLAVES.keys()))
    pin = st.text_input("CLAVE:", type="password")
    
    if st.button("ENTRAR"):
        if pin == CLAVE_ADMIN:
            st.session_state.autenticado = True
            st.session_state.es_admin = True
            st.rerun()
        elif loc_sel in LOCALIDADES_CLAVES and pin == LOCALIDADES_CLAVES[loc_sel] and nombre_m != "":
            st.session_state.autenticado = True
            st.session_state.nombre = nombre_m
            st.session_state.localidad = loc_sel
            st.rerun()
        else:
            st.error("Datos incorrectos")

else:
    # --- BUSCADOR ---
    st.markdown(f"### Hola, {st.session_state.get('nombre', 'Admin')}")
    
    # Carga de padrón (datos.csv local)
    @st.cache_data
    def cargar_padron():
        try:
            return pd.read_csv("datos.csv", encoding='latin-1', sep=None, engine='python')
        except: return None

    df_padron = cargar_padron()

    if df_padron is not None:
        busqueda = st.text_input("🔎 BUSCAR POR DNI, APELLIDO O CALLE:")
        if busqueda:
            # Filtramos solo columnas visibles (DNI, Nombre, Apellido, Direccion)
            visibles = [c for c in df_padron.columns if any(x in c.upper() for x in ['DNI', 'MATRICULA', 'NOMBRE', 'APELLIDO', 'DIRECCION', 'CALLE'])]
            termino = busqueda.upper()
            mask = df_padron[visibles].astype(str).apply(lambda row: row.str.upper().str.contains(termino)).any(axis=1)
            resultados = df_padron[visibles][mask]
            
            if not resultados.empty:
                # REGISTRAMOS LA CONSULTA EN GOOGLE SHEETS
                registrar_consulta_google(
                    st.session_state.get('nombre', 'ADMIN'),
                    st.session_state.get('localidad', 'ADMIN'),
                    busqueda
                )
                st.success(f"Encontrados: {len(resultados)}")
                st.dataframe(resultados)
            else:
                st.warning("No se encontraron resultados.")

    if st.button("CERRAR SESIÓN"):
        st.session_state.autenticado = False
        st.rerun()
