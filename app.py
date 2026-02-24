# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. SEGURIDAD Y CLAVES 2026
LOCALIDADES_CLAVES = {
    "CASEROS": "caseros2026", "CIUDADELA": "ciudadela2026", "BARRIO_EJERCITO": "barrioejercito2026",
    "VILLA_BOSCH": "villabosch2026", "MARTIN_CORONADO": "martincoronado2026", "CIUDAD_JARDIN": "ciudadjardin2026",
    "SANTOS_LUGARES": "santoslugares2026", "SAENZ_PEÑA": "saenzpeña2026", "PODESTA": "podesta2026",
    "CHURRUCA": "churruca2026", "EL_LIBERTADOR": "ellibertador2026", "LOMA_HERMOSA": "lomahermosa2026"
}
CLAVE_ADMIN = "josefina3f_admin"
ARCHIVO_LOG = "registro_actividad_lista4.csv"

st.set_page_config(page_title="Lista 4 - Gestión", page_icon="✌️", layout="wide")

# --- FUNCIÓN PARA GUARDAR DATOS PERMANENTES ---
def registrar_en_archivo(usuario, localidad, accion, detalle):
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nueva_linea = pd.DataFrame([[ahora, usuario, localidad, accion, detalle]], 
                                columns=["Fecha", "Usuario", "Localidad", "Accion", "Busqueda"])
    
    # Si el archivo no existe, lo crea con cabecera. Si existe, agrega al final.
    if not os.path.isfile(ARCHIVO_LOG):
        nueva_linea.to_csv(ARCHIVO_LOG, index=False)
    else:
        nueva_linea.to_csv(ARCHIVO_LOG, mode='a', header=False, index=False)

# --- DISEÑO ---
st.markdown("<style>.stApp { background-color: white; } .banner { text-align: center; background: #003366; color: white; padding: 15px; border-radius: 10px; border-bottom: 5px solid #FFD700; margin-bottom: 20px; }</style>", unsafe_allow_html=True)

if "autenticado" not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown('<div class="banner"><h1>✌️ LISTA 4</h1><h3>PERONISMO DE TODOS - 3F</h3></div>', unsafe_allow_html=True)
    nombre_m = st.text_input("TU NOMBRE Y APELLIDO:")
    loc_sel = st.selectbox("LOCALIDAD:", ["---"] + list(LOCALIDADES_CLAVES.keys()))
    pin = st.text_input("CLAVE DE ACCESO:", type="password")
    
    if st.button("INGRESAR"):
        if pin == CLAVE_ADMIN or (loc_sel in LOCALIDADES_CLAVES and pin == LOCALIDADES_CLAVES[loc_sel] and nombre_m != ""):
            st.session_state.autenticado = True
            st.session_state.es_admin = (pin == CLAVE_ADMIN)
            st.session_state.nombre = nombre_m if nombre_m else "ADMIN"
            st.session_state.localidad = loc_sel if pin != CLAVE_ADMIN else "ADMIN"
            registrar_en_archivo(st.session_state.nombre, st.session_state.localidad, "INGRESO", "Sesión iniciada")
            st.rerun()
        else: st.error("DATOS INCORRECTOS")
else:
    # --- PANEL ADMIN: DESCARGA DE DATOS ---
    if st.session_state.get('es_admin', False):
        st.markdown("### 📊 AUDITORÍA ACUMULADA")
        if os.path.isfile(ARCHIVO_LOG):
            df_historial = pd.read_csv(ARCHIVO_LOG)
            st.dataframe(df_historial.iloc[::-1], use_container_width=True)
            
            # Botón para que vos descargues el reporte diario
            csv_data = df_historial.to_csv(index=False).encode('utf-8')
            st.download_button("📥 DESCARGAR REPORTE DIARIO (CSV)", data=csv_data, file_name=f"reporte_lista4_{datetime.now().strftime('%d_%m')}.csv")
        else:
            st.info("Todavía no hay actividad registrada hoy.")
        st.divider()

    # --- BUSCADOR ---
    st.markdown('<div class="banner"><h3>CONSULTA DE AFILIADOS - LISTA 4</h3></div>', unsafe_allow_html=True)
    busqueda = st.text_input("🔎 BUSCAR POR CALLE, APELLIDO O DNI:")
    
    if busqueda:
        # Lógica de carga del padrón (igual a la anterior)
        archivos = [f for f in os.listdir('.') if f.startswith('Padron 2026') and f.endswith('.csv')]
        if archivos:
            df = pd.read_csv(archivos[0], encoding='latin-1', sep=None, engine='python')
            res = df[df.astype(str).apply(lambda row: row.str.upper().str.contains(busqueda.upper())).any(axis=1)]
            if not res.empty:
                registrar_en_archivo(st.session_state.nombre, st.session_state.localidad, "CONSULTA", busqueda)
                st.dataframe(res, use_container_width=True)
