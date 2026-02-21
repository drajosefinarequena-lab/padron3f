# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# 1. SEGURIDAD: CLAVES POR LOCALIDAD Y ADMIN
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

# --- DISEÑO DE ALTO CONTRASTE ---
st.markdown("""
    <style>
    .stApp { background-color: white; background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Escudo_del_Partido_Justicialista.svg/1200px-Escudo_del_Partido_Justicialista.svg.png"); background-repeat: no-repeat; background-position: center; background-size: 400px; opacity: 0.9; }
    .block-container { padding-top: 1rem !important; max-width: 600px; }
    label, p, h3, h4 { color: black !important; font-weight: 900 !important; font-size: 18px !important; }
    .stTextInput input { background-color: white !important; color: black !important; border: 4px solid black !important; font-weight: bold !important; font-size: 18px !important; }
    .bienvenida { text-align: center; color: white; background: #003366; padding: 15px; border: 3px solid black; font-weight: 900; font-size: 20px; margin-bottom: 10px; }
    .stButton>button { background-color: #00008B !important; color: white !important; font-weight: 900 !important; border: 3px solid #FFD700 !important; width: 100%; height: 50px; font-size: 20px !important; }
    .aviso-seguridad { background-color: #ffeb3b; padding: 15px; border: 2px solid #f44336; border-radius: 5px; color: black; font-weight: bold; margin-bottom: 20px; text-align: center; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE REGISTRO PERSISTENTE ---
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

# --- INICIALIZACIÓN DE SESIÓN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "es_admin" not in st.session_state: st.session_state.es_admin = False

# --- PANTALLA DE ACCESO ---
if not st.session_state.autenticado:
    if os.path.exists("Logo PDT - PJ.jpg.jpeg"):
        st.image("Logo PDT - PJ.jpg.jpeg", use_container_width=True)
    st.markdown('<div class="bienvenida">INGRESO SEGURO - LISTA 4</div>', unsafe_allow_html=True)
    st.markdown('<div class="aviso-seguridad">⚠️ AVISO: Se registra ubicación geográfica para evitar filtraciones.</div>', unsafe_allow_html=True)
    
    acepta_terminos = st.checkbox("ACEPTO EL REGISTRO DE MI UBICACIÓN PARA INGRESAR")
    usuario_ing = st.selectbox("LOCALIDAD:", ["---"] + list(USUARIOS_AUTORIZADOS.keys()))
    clave_ing = st.text_input("CLAVE:", type="password")
    
    if st.button("ENTRAR", disabled=not acepta_terminos):
        ubi_actual = obtener_datos_ip()
        if clave_ing == CLAVE_ADMIN:
            st.session_state.autenticado = True
            st.session_state.es_admin = True
            registrar_evento("ADMIN", ubi_actual, "EXITO_ADMIN")
            st.rerun()
        elif usuario_ing in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[usuario_ing] == clave_ing:
            registrar_evento(usuario_ing, ubi_actual, "EXITO")
            st.session_state.autenticado = True
            st.session_state.usuario_actual = usuario_ing
            st.rerun()
        else:
            registrar_evento(usuario_ing if usuario_ing != "---" else "DESCONOCIDO", ubi_actual, "ERROR_LOGIN")
            st.error("DATOS INCORRECTOS. Intento registrado por seguridad.")

else:
    # --- PANTALLA DE CONSULTA ---
    st.markdown('<div class="bienvenida">CONSULTA EL PADRÓN</div>', unsafe_allow_html=True)
    
    if st.session_state.es_admin:
        with st.expander("🛡️ AUDITORÍA DE SEGURIDAD (HISTORIAL COMPLETO)"):
            if os.path.exists("log_accesos.csv"):
                st.table(pd.read_csv("log_accesos.csv"))

    @st.cache_data
    def cargar_datos():
        for enc in ['latin-1', 'iso-8859-1', 'cp1252', 'utf-8']:
            try:
                df_c = pd.read_csv("datos.csv", sep=None, engine='python', encoding=enc, on_bad_lines='skip')
                df_c = df_c.fillna('')
                
                # FILTRO ESTRICTO: Solo DNI, Nombre, Apellido y Dirección
                columnas_visibles = []
                for col in df_c.columns:
                    c_up = col.upper()
                    if any(x in c_up for x in ['MATRICULA', 'DNI', 'NOMBRE', 'APELLIDO', 'DIRECCION', 'DOMICILIO', 'CALLE']):
                        columnas_visibles.append(col)
                
                df_c = df_c[columnas_visibles]
                
                # Limpiar DNI si existe
                for col in df_c.columns:
                    if any(x in col.upper() for x in ['MATRICULA', 'DNI']):
                        df_c[col] = df_c[col].astype(str).str.replace('.0', '', regex=False)
                
                return df_c
            except: continue
        return None

    df = cargar_datos()

    if df is not None:
        st.markdown("### 🔎 BUSCAR AFILIADO")
        with st.form("buscador_form", clear_on_submit=False):
            busqueda = st.text_input("Ingresá DNI o Apellido:")
            if st.form_submit_button("BUSCAR"):
                if busqueda:
                    mask = df.astype(str).apply(lambda row: row.str.upper().str.contains(busqueda.upper())).any(axis=1)
                    res = df[mask]
                    if not res.empty:
                        st.success(f"Encontrados: {len(res)}")
                        st.dataframe(res, use_container_width=True)
                    else: st.error("NO ENCONTRADO")

    if st.button("CERRAR SESIÓN"):
        st.session_state.autenticado = False
        st.rerun()
