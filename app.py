# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# 1. CONFIGURACIÓN DE SEGURIDAD Y ACCESOS
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

# --- DISEÑO TÁCTICO ---
st.markdown("""
    <style>
    .stApp { 
        background-color: white; 
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Escudo_del_Partido_Justicialista.svg/1200px-Escudo_del_Partido_Justicialista.svg.png"); 
        background-repeat: no-repeat; 
        background-position: center; 
        background-size: 400px; 
        opacity: 0.9; 
    }
    .block-container { padding-top: 1rem !important; max-width: 600px; }
    label, p, h3, h4 { color: black !important; font-weight: 900 !important; font-size: 18px !important; }
    .stTextInput input { background-color: white !important; color: black !important; border: 4px solid black !important; font-weight: bold !important; }
    .bienvenida { text-align: center; color: white; background: #003366; padding: 15px; border: 3px solid black; font-weight: 900; font-size: 20px; margin-bottom: 10px; }
    .stButton>button { background-color: #00008B !important; color: white !important; font-weight: 900 !important; border: 3px solid #FFD700 !important; width: 100%; height: 50px; }
    .aviso-seguridad { background-color: #ffeb3b; padding: 10px; border: 2px solid #f44336; color: black; font-weight: bold; text-align: center; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE LOG Y API ---
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
    try:
        url = st.secrets["URL_SHEET_BEST"]
        response = requests.post(url, json=datos, timeout=5)
        return response.status_code == 200
    except:
        return False

# --- INICIALIZACIÓN DE SESIÓN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "es_admin" not in st.session_state: st.session_state.es_admin = False
if "usuario_actual" not in st.session_state: st.session_state.usuario_actual = None

# --- LÓGICA DE ACCESO ---
if not st.session_state.autenticado:
    st.markdown('<div class="bienvenida">INGRESO SEGURO - LISTA 4</div>', unsafe_allow_html=True)
    st.markdown('<div class="aviso-seguridad">⚠️ REGISTRO DE UBICACIÓN ACTIVO</div>', unsafe_allow_html=True)
    
    acepta_terminos = st.checkbox("ACEPTO EL REGISTRO GEOGRÁFICO")
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
            st.error("DATOS INCORRECTOS")

else:
    # --- PANTALLA PRINCIPAL ---
    user_label = st.session_state.get("usuario_actual", "Militante")
    st.markdown(f'<div class="bienvenida">PANEL: {user_label}</div>', unsafe_allow_html=True)
    
    if st.session_state.es_admin:
        with st.expander("🛡️ AUDITORÍA DE ACCESOS"):
            if os.path.exists("log_accesos.csv"):
                st.table(pd.read_csv("log_accesos.csv").tail(10))

    @st.cache_data
    def cargar_datos_padron():
        for enc in ['latin-1', 'utf-8', 'iso-8859-1']:
            try:
                df_c = pd.read_csv("datos.csv", encoding=enc, on_bad_lines='skip')
                df_c = df_c.fillna('')
                for col in df_c.columns:
                    if any(x in col.upper() for x in ['DNI', 'MATRICULA']):
                        df_c[col] = df_c[col].astype(str).str.replace('.0', '', regex=False)
                return df_c
            except: continue
        return None

    df = cargar_datos_padron()

    if df is not None:
        st.markdown("### 🔎 BÚSQUEDA DE AFILIADOS")
        busqueda = st.text_input("DNI o Apellido:").upper()
        
        if busqueda:
            mask = df.astype(str).apply(lambda row: row.str.upper().str.contains(busqueda)).any(axis=1)
            res = df[mask]
            
            if not res.empty:
                st.success(f"Encontrados: {len(res)}")
                st.dataframe(res, use_container_width=True)
                
                # --- SISTEMA DE CARGA TÁCTICA ---
                if len(res) < 15:
                    st.markdown("---")
                    st.markdown("### 🗳️ REGISTRAR COMPROMISO")
                    with st.form("registro_voto", clear_on_submit=True):
                        lista_personas = [f"{r.get('APELLIDO', '')}, {r.get('NOMBRE', '')} ({r.get('DNI', r.get('MATRICULA', ''))})" for i, r in res.iterrows()]
                        persona = st.selectbox("Seleccionar Afiliado:", lista_personas)
                        
                        voto = st.radio("Estado del Voto:", ["🟢 SEGURO LISTA 4", "🟡 INDECISO / VOLVER", "🔴 OTROS / NO VOTA"], horizontal=True)
                        obs = st.text_area("Notas (Ej: Pide boleta, no está, etc.)")
                        
                        if st.form_submit_button("GUARDAR EN GOOGLE SHEETS"):
                            datos_visita = {
                                "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                "Militante": user_label,
                                "DNI_Vecino": persona.split('(')[-1].replace(')', ''),
                                "Nombre_Vecino": persona.split('(')[0],
                                "Estado": voto,
                                "Observaciones": obs
                            }
                            if enviar_a_google_sheets(datos_visita):
                                st.balloons()
                                st.success("¡Voto registrado en la base central!")
                            else:
                                st.error("Error al guardar. Verificá la URL de Sheet.best en Secrets.")
            else:
                st.error("No se registran coincidencias.")

    if st.button("SALIR (CERRAR SESIÓN)"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
