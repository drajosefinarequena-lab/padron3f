# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# 1. CONFIGURACIÓN DE SEGURIDAD
USUARIOS_AUTORIZADOS = {
    "CASEROS": "L4_3f_CAS",
    "CIUDADELA": "L4_3f_CIU",
    "BARRIO_EJERCITO": "L4_3f_BEJ",
    "VILLA_BOSCH": "L4_3f_VBO",
    "MARTIN_CORONADO": "L4_3f_MCO",
    "CIUDAD_JARDIN": "L4_3f_CJA",
    "SANTOS_LUGARES": "L4_3f_SLU",
    "SAENZ_PEÑA": "L4_3f_SPE",
    "PODESTA": "L4_3f_POD",
    "CHURRUCA": "L4_3f_CHU",
    "EL_LIBERTADOR": "L4_3f_ELI",
    "LOMA_HERMOSA": "L4_3f_LHE"
}
CLAVE_ADMIN = "josefina3f_admin"

st.set_page_config(page_title="Lista 4 - Peronismo de Todos", page_icon="✌️", layout="centered")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .stApp { background-color: white; background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Escudo_del_Partido_Justicialista.svg/1200px-Escudo_del_Partido_Justicialista.svg.png"); background-repeat: no-repeat; background-position: center; background-size: 400px; opacity: 0.9; }
    .block-container { padding-top: 1rem !important; max-width: 600px; }
    label, p, h3, h4 { color: black !important; font-weight: 900 !important; }
    .bienvenida { text-align: center; color: white; background: #003366; padding: 15px; border: 3px solid black; font-weight: 900; font-size: 20px; margin-bottom: 10px; }
    .stButton>button { background-color: #00008B !important; color: white !important; font-weight: 900 !important; border: 3px solid #FFD700 !important; width: 100%; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE APOYO ---
def registrar_evento(usuario, ubicacion, resultado):
    archivo_log = "log_accesos.csv"
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nuevo = pd.DataFrame([{"Fecha": ahora, "Usuario": usuario, "Ubicacion": ubicacion, "Resultado": resultado}])
    if not os.path.isfile(archivo_log):
        nuevo.to_csv(archivo_log, index=False, encoding='utf-8')
    else:
        nuevo.to_csv(archivo_log, mode='a', header=False, index=False, encoding='utf-8')

def obtener_datos_ip():
    try:
        r = requests.get('https://ipapi.co/json/', timeout=3)
        data = r.json()
        return f"{data.get('city')}, {data.get('region')} (IP: {data.get('ip')})"
    except: return "IP No rastreable"

def enviar_a_google_sheets(datos):
    """Envía los datos a través de la API de Sheet.best"""
    try:
        url = st.secrets["URL_SHEET_BEST"]
        response = requests.post(url, json=datos)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return False

# --- GESTIÓN DE SESIÓN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "es_admin" not in st.session_state: st.session_state.es_admin = False

# --- PANTALLA DE ACCESO ---
if not st.session_state.autenticado:
    st.markdown('<div class="bienvenida">INGRESO SEGURO - LISTA 4</div>', unsafe_allow_html=True)
    acepta_terminos = st.checkbox("ACEPTO EL REGISTRO DE MI UBICACIÓN PARA INGRESAR")
    usuario_ing = st.selectbox("LOCALIDAD:", ["---"] + list(USUARIOS_AUTORIZADOS.keys()))
    clave_ing = st.text_input("CLAVE:", type="password")
    
    if st.button("ENTRAR", disabled=not acepta_terminos):
        ubi_actual = obtener_datos_ip()
        if clave_ing == CLAVE_ADMIN:
            st.session_state.autenticado, st.session_state.es_admin = True, True
            st.session_state.usuario_actual = "ADMIN"
            registrar_evento("ADMIN", ubi_actual, "EXITO_ADMIN")
            st.rerun()
        elif usuario_ing in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[usuario_ing] == clave_ing:
            st.session_state.autenticado = True
            st.session_state.usuario_actual = usuario_ing
            registrar_evento(usuario_ing, ubi_actual, "EXITO")
            st.rerun()
        else:
            st.error("DATOS INCORRECTOS.")

else:
    # --- PANTALLA PRINCIPAL ---
    st.markdown(f'<div class="bienvenida">PANEL: {st.session_state.usuario_actual}</div>', unsafe_allow_html=True)
    
    @st.cache_data
    def cargar_datos_padron():
        try:
            df_c = pd.read_csv("datos.csv", encoding='latin-1', on_bad_lines='skip')
            df_c = df_c.fillna('')
            # Limpieza básica de columnas DNI
            for col in df_c.columns:
                if any(x in col.upper() for x in ['DNI', 'MATRICULA']):
                    df_c[col] = df_c[col].astype(str).str.replace('.0', '', regex=False)
            return df_c
        except: return None

    df = cargar_datos_padron()

    if df is not None:
        st.markdown("### 🔎 BÚSQUEDA DE AFILIADOS")
        busqueda = st.text_input("Ingresá DNI o Apellido:").upper()
        
        if busqueda:
            mask = df.astype(str).apply(lambda row: row.str.upper().str.contains(busqueda)).any(axis=1)
            res = df[mask]
            
            if not res.empty:
                st.success(f"Resultados: {len(res)}")
                st.dataframe(res, use_container_width=True)
                
                # --- FORMULARIO DE ACCIÓN TERRITORIAL ---
                if len(res) < 10: # Evitar formularios masivos si la búsqueda es muy amplia
                    st.markdown("---")
                    st.markdown("### 🗳️ REGISTRAR VISITA")
                    with st.form("registro_voto", clear_on_submit=True):
                        # Selección de vecino si hay más de uno en el resultado
                        opciones_vecinos = [f"{row.get('APELLIDO', '')}, {row.get('NOMBRE', '')} ({row.get('DNI', row.get('MATRICULA', ''))})" for i, row in res.iterrows()]
                        vecino_sel = st.selectbox("Confirmar Vecino:", opciones_vecinos)
                        
                        voto_estado = st.radio("Intención de Voto:", ["🟢 SEGURO LISTA 4", "🟡 INDECISO / VOLVER", "🔴 OTROS / NO VOTA"], horizontal=True)
                        comentario = st.text_area("Observaciones (Ej: Necesita transporte, No estaba):")
                        
                        if st.form_submit_button("GUARDAR EN TERRITORIO"):
                            datos_finales = {
                                "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                "Militante": st.session_state.usuario_actual,
                                "DNI_Vecino": vecino_sel.split('(')[-1].replace(')', ''),
                                "Nombre_Vecino": vecino_sel.split('(')[0],
                                "Estado": voto_estado,
                                "Observaciones": comentario
                            }
                            if enviar_a_google_sheets(datos_finales):
                                st.balloons()
                                st.success("¡Voto registrado correctamente!")
                            else:
                                st.error("Error al guardar. Verificá la conexión.")
            else:
                st.error("No se encontraron resultados.")

    if st.button("SALIR DEL SISTEMA"):
        st.session_state.autenticado = False
        st.rerun()
