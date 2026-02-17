import streamlit as st
import pandas as pd
import re
from cryptography.fernet import Fernet
import io

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Analizador de Empresas",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS "ULTRA-VISIBLE" PARA EL MENÚ MÓVIL Y ESTILOS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }

    /* --- TRANSFORMAR EL BOTÓN DE STREAMLIT EN UN BURGER MENU --- */
    /* Este código busca el botón de menú oficial y lo hace GRANDE y AZUL */
    
    /* 1. Asegurar que el botón sea visible en el encabezado */
    button[data-testid="stSidebarCollapse"] {
        background-color: #1F4E79 !important;
        color: white !important;
        width: 55px !important;
        height: 55px !important;
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 9999999 !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
        border: 2px solid white !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    /* 2. Forzar que el icono (flecha/hamburguesa) sea blanco y grande */
    button[data-testid="stSidebarCollapse"] svg {
        fill: white !important;
        width: 30px !important;
        height: 30px !important;
    }

    /* 3. Evitar que el header de Streamlit tape nuestro botón */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* --- DISEÑO DE LA PÁGINA --- */
    .hero-title { color: #1F4E79; font-size: 2.8rem; font-weight: 800; text-align: center; margin-top: 40px; }
    .hero-subtitle { color: #555; font-size: 1.1rem; text-align: center; margin-bottom: 30px; }
    
    .section-title { color: #1F4E79; font-size: 1.6rem; font-weight: 700; border-bottom: 3px solid #DAE9F7; margin-top: 20px; }
    
    .kpi-card { background-color: #DAE9F7; border-radius: 12px; padding: 20px; text-align: center; border: 1.5px solid #1F4E79; height: 100%; }
    .kpi-value { color: #1F4E79; font-size: 2rem; font-weight: 800; }
    
    .feature-card { 
        background-color: white; border-radius: 12px; padding: 20px; text-align: center; 
        border: 1px solid #eee; box-shadow: 0 4px 10px rgba(0,0,0,0.05); height: 100%;
    }

    .custom-table { width: 100%; border-collapse: collapse; border-radius: 8px; overflow: hidden; }
    .custom-table th { background-color: #1F4E79; color: white; padding: 10px; }
    .custom-table td { border-bottom: 1px solid #eee; padding: 10px; text-align: center; }

    /* Ajuste de margen para móviles por el botón */
    @media (max-width: 768px) {
        .hero-title { margin-top: 60px !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. UTILIDADES ---
def clean_number_format(val):
    if pd.isna(val) or val == "-": return "-"
    s = re.sub(r'[^\d]', '', str(val))
    return "{:,}".format(int(s)) if s else str(val)

def get_val(row, col):
    val = str(row[col]) if col in row and pd.notna(row[col]) else "-"
    return val if val.lower() != "nan" else "-"

def render_table(df):
    if df.empty: st.write("Sin datos."); return
    st.markdown(f'<div style="overflow-x: auto;">{df.to_html(index=False, border=0, classes="custom-table")}</div>', unsafe_allow_html=True)

# --- 4. CARGA DE DATOS ---
@st.cache_data
def load_data():
    df, df_alumni = None, pd.DataFrame()
    archivo_empresas = 'euskadi_navarra_dollar.csv'
    try:
        df = pd.read_csv(archivo_empresas, sep=';', encoding='utf-8')
    except:
        try: df = pd.read_csv(archivo_empresas, sep=';', encoding='latin-1')
        except: return None, pd.DataFrame()
    
    try:
        if "encryption_key" in st.secrets:
            key = st.secrets["encryption_key"]
            cipher_suite = Fernet(key)
            with open('alumni_seguro.enc', 'rb') as file: encrypted_data = file.read()
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            df_alumni = pd.read_csv(io.BytesIO(decrypted_data), sep=';', encoding='utf-8')
            df_alumni.columns = [c.strip() for c in df_alumni.columns]
    except: pass
    return df, df_alumni

df_main, df_alumni = load_data()

# --- 5. SIDEBAR (BUSCADOR) ---
if df_main is not None:
    st.sidebar.header("🔍 Buscador")
    tab_emp, tab_prof = st.sidebar.tabs(["🏢 Empresa", "🧑‍💼 Profesional"])
    
    with tab_emp:
        prov = st.selectbox("Provincia", ["Todas"] + sorted(df_main['provincia'].dropna().unique().tolist()))
        search_emp = st.text_input("Nombre Empresa", placeholder="Ej: Caf")
        df_f = df_main.copy()
        if prov != "Todas": df_f = df_f[df_f['provincia'] == prov]
        if search_emp: df_f = df_f[df_f['Nombre'].astype(str).str.contains(search_emp, case=False, na=False)]
        lista_e = sorted(df_f['Nombre'].unique().tolist())
        if lista_e:
            sel_e = st.selectbox("Resultados:", lista_e)
            if st.button("Ver Análisis", use_container_width=True):
                st.session_state['selected_empresa'] = sel_e
                st.rerun()

    with tab_prof:
        if not df_alumni.empty:
            col_nom = next((c for c in df_alumni.columns if 'nombre' in c.lower()), 'Nombre')
            col_emp = next((c for c in df_alumni.columns if 'informa' in c.lower()), 'Empresa')
            search_p = st.text_input("Filtrar Nombre:", placeholder="Ej: Asier")
            
            if search_p:
                mask = df_alumni[col_nom].astype(str).str.contains(search_p, case=False, na=False)
                res = sorted(df_alumni[mask][col_nom].unique().tolist())
                if len(res) > 1:
                    st.info(f"🔍 {len(res)} entradas encontradas. Selecciona una:")
                    sel_p = st.selectbox("Selecciona:", res, index=None)
                elif len(res) == 1:
                    st.success("✅ Contacto encontrado")
                    sel_p = res[0]
                    st.selectbox("Selecciona:", res, index=0, disabled=True)
                else:
                    st.error("No hay resultados")
                    sel_p = None
                
                if sel_p:
                    d = df_alumni[df_alumni[col_nom] == sel_p].iloc[0]
                    st.markdown(f"**{sel_p}**<br>🏢 {d[col_emp]}", unsafe_allow_html=True)
                    if st.button("Ir a Empresa ➔", use_container_width=True):
                        st.session_state['selected_empresa'] = d[col_emp]
                        st.rerun()

# --- 6. PANEL CENTRAL ---
sel_emp = st.session_state.get('selected_empresa')

if sel_emp:
    row = df_main[df_main['Nombre'] == sel_emp]
    if row.empty:
        row = df_main[df_main['Nombre'].str.contains(re.escape(str(sel_emp)), case=False, na=False)]
    
    if not row.empty:
        # Caso 1: Datos completos
        r = row.iloc[0]
        st.title(f"🏢 {get_val(r, 'Nombre')}")
        st.markdown('<div class="section-title">Resumen Financiero</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="kpi-card"><div class="kpi-value">{get_val(r, "provincia")}</div>UBICACIÓN</div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi-card"><div class="kpi-value">{get_val(r, "veredicto_final")}</div>CLASIFICACIÓN</div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="kpi-card"><div class="kpi-value">{get_val(r, "ventas_estimado")}</div>VENTAS</div>', unsafe_allow_html=True)
    else:
        # Caso 2: Solo DBA
        st.title(f"🏢 {sel_emp}")
        st.error("❌ No hay datos financieros para esta empresa en la base de datos principal.")
        if not df_alumni.empty:
            col_emp = next((c for c in df_alumni.columns if 'informa' in c.lower()), 'Empresa')
            match = df_alumni[df_alumni[col_emp].astype(str).str.strip() == str(sel_emp).strip()]
            if not match.empty:
                st.markdown("### 📋 Información del Fichero Alumni (DBA)")
                render_table(match[['Nombre', 'Cargo', col_emp]].rename(columns={col_emp: 'Empresa DBA'}))
else:
    # --- HOME ---
    st.markdown('<div class="hero-title">Analizador de Empresas 360°</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Buscador avanzado de mercado y red de contactos.</div>', unsafe_allow_html=True)
    st.write("")
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="feature-card"><b>🏢 Mercado</b><br>Datos financieros y estructurales.</div>', unsafe_allow_html=True)
    c2.markdown('<div class="feature-card"><b>🧑‍💼 Networking</b><br>Encuentra contactos en empresas clave.</div>', unsafe_allow_html=True)
    c3.markdown('<div class="feature-card"><b>📊 Viabilidad</b><br>Análisis de salarios y crecimiento.</div>', unsafe_allow_html=True)
    st.write("---")
    st.info("👈 **Móvil:** Haz clic en el botón azul de arriba a la izquierda para abrir el buscador.")