import streamlit as st
import pandas as pd
import re
import io
import os
import math
import streamlit.components.v1 as components

# Intento de importar librería de encriptación
try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="BINGO - by Asier Dorronsoro",
    page_icon="🎱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- UTILIDAD: SCROLL TO TOP (Optimizado) ---
def scroll_to_top():
    """Solo ejecuta scroll cuando realmente es necesario"""
    if st.session_state.get('scroll_needed', False):
        js = '''<script>
            var body = window.parent.document.querySelector(".main");
            body.scrollTop = 0;
        </script>'''
        components.html(js, height=0)

# --- 1. GESTIÓN DE ESTILOS (CSS CORPORATE CLEAN) ---
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; font-size: 16px; color: #2c3e50; }
    
    /* Títulos */
    .section-title { color: #1F4E79; font-size: 1.8rem; font-weight: 700; margin-top: 2.5rem; border-bottom: 4px solid #DAE9F7; padding-bottom: 5px; margin-bottom: 20px;}

    /* KPIs */
    .kpi-card { background-color: #DAE9F7; border-radius: 12px; padding: 20px; text-align: center; border: 2px solid #1F4E79; box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: 100%; display: flex; flex-direction: column; justify-content: center; }
    .kpi-value { color: #1F4E79; font-size: 2rem; font-weight: 800; line-height: 1.2; }
    .kpi-label { font-size: 0.85rem; text-transform: uppercase; font-weight: 700; color: #1F4E79; margin-top: 5px; letter-spacing: 1px; }

    /* Tarjetas Tech */
    .tech-hero { background-color: #1F4E79; color: white; border-radius: 10px; padding: 20px; text-align: center; box-shadow: 0 4px 10px rgba(31, 78, 121, 0.2); }
    .tech-hero-label { font-size: 0.85rem; text-transform: uppercase; opacity: 0.9; font-weight: 600; margin-bottom: 5px; }
    .tech-hero-val { font-size: 1.3rem; font-weight: 700; }

    .tech-card { background-color: white; border: 1px solid #e0e0e0; border-top: 4px solid #1F4E79; border-radius: 10px; padding: 20px; height: 100%; box-shadow: 0 2px 8px rgba(0,0,0,0.05); transition: transform 0.2s; }
    .tech-card:hover { transform: translateY(-3px); }
    .tech-icon { font-size: 1.8rem; margin-bottom: 10px; display: block; }
    .tech-title { color: #1F4E79; font-weight: 700; font-size: 0.95rem; margin-bottom: 8px; text-transform: uppercase; }
    .tech-text { font-size: 1rem; color: #444; line-height: 1.4; }

    /* Tablas */
    .custom-table { width: 100%; border-collapse: separate; border-spacing: 0; min-width: 500px; border-radius: 8px; overflow: hidden; border: 1px solid #eee; }
    .custom-table th { background-color: #1F4E79; color: white; padding: 12px; text-align: center; font-weight: 600; }
    .custom-table td { border-bottom: 1px solid #f0f0f0; padding: 12px; text-align: center; color: #333; }
    .table-container { overflow-x: auto; box-shadow: 0 2px 5px rgba(0,0,0,0.03); border-radius: 8px; margin-bottom: 20px; }

    /* Layouts Grid Puro */
    .responsive-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-bottom: 20px;
        align-items: stretch;
    }
    
    @media (max-width: 768px) {
        .responsive-grid { grid-template-columns: 1fr; }
        .grid-2, .grid-3 { display: grid; grid-template-columns: 1fr; gap: 15px;}
    }
    
    @media (min-width: 769px) {
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px; }
    }

    .box-header { color: #1F4E79; font-weight: 700; font-size: 1.2rem; margin-bottom: 10px; border-bottom: 2px solid #DAE9F7; display: block; }
    
    .content-box { 
        background-color: white; 
        border: 1px solid #dcdcdc; 
        border-radius: 12px; 
        padding: 20px; 
        height: 100%; 
        display: flex;
        flex-direction: column;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Home */
    .hero-title { color: #1F4E79; font-size: 4rem; font-weight: 900; text-align: center; margin-bottom: 5px; letter-spacing: -1px; }
    .hero-subtitle { color: #555; font-size: 1.5rem; text-align: center; margin-bottom: 50px; font-weight: 300; }
    .feature-card { background-color: white; border-radius: 12px; padding: 25px; text-align: center; border: 1px solid #eee; box-shadow: 0 4px 12px rgba(0,0,0,0.05); transition: transform 0.3s ease; height: 100%; display: flex; flex-direction: column; justify-content: space-between; }
    .feature-card:hover { transform: translateY(-5px); border-color: #DAE9F7; }
    .feature-icon { font-size: 3rem; margin-bottom: 15px; display: block; }
    .feature-title { color: #1F4E79; font-weight: 700; font-size: 1.2rem; margin-bottom: 10px; }
    .feature-desc { color: #666; font-size: 1rem; line-height: 1.5; margin-bottom: 20px; }
    
    .results-bar { background-color: #e3f2fd; color: #0d47a1; padding: 12px 20px; border-radius: 8px; font-weight: 500; margin-bottom: 20px; border-left: 5px solid #1F4E79; display: flex; justify-content: space-between; align-items: center; }
    
    /* --- BADGES PROFESIONALES (Diseño Limpio Corporate) --- */
    .badge-top { 
        background-color: #1F4E79;
        color: white; 
        padding: 5px 10px; 
        border-radius: 4px; 
        font-size: 0.85rem; 
        font-weight: 500;
        display: inline-block;
        min-width: 140px;
        text-align: center;
        text-decoration: none !important;
    }
    .badge-mid { 
        background-color: #E3F2FD;
        color: #1565C0; 
        padding: 5px 10px; 
        border-radius: 4px; 
        font-size: 0.85rem; 
        font-weight: 500; 
        display: inline-block;
        min-width: 140px;
        text-align: center;
        text-decoration: none !important;
    }
    .badge-entry { 
        background-color: #F5F5F5;
        color: #616161; 
        padding: 5px 10px; 
        border-radius: 4px; 
        font-size: 0.85rem; 
        font-weight: 500; 
        display: inline-block;
        min-width: 140px;
        text-align: center;
        text-decoration: none !important;
    }
    
    /* Export buttons */
    .export-button-container { margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

inject_css()

# --- 2. UTILIDADES ---
def clean_number_format(val):
    """Formatea números con separadores de miles"""
    if pd.isna(val): return "-"
    s = re.sub(r'[^\d]', '', str(val))
    return "{:,}".format(int(s)) if s else str(val)

def safe_get_val(row, col, default="-"):
    """Obtiene valor con manejo seguro de columnas faltantes"""
    try:
        if col in row.index and pd.notna(row[col]):
            val = str(row[col]).strip()
            return val if val.lower() != "nan" else default
        return default
    except Exception:
        return default

def capitalize_first_letter(text):
    """Capitaliza la primera letra de cada palabra"""
    text = str(text).strip()
    if not text or text == "-" or text.lower() == "nan": 
        return "-"
    return " ".join([word.capitalize() for word in text.split()])

def render_table(df):
    """Renderiza tabla HTML personalizada"""
    if df.empty: 
        st.caption("Sin datos para mostrar.")
        return
    st.markdown(f'<div class="table-container">{df.to_html(index=False, border=0, classes="custom-table", escape=False)}</div>', unsafe_allow_html=True)

def has_private_equity(value):
    """Determina si tiene Private Equity"""
    if pd.isna(value): 
        return False
    negatives = {'ninguno', 'no identificado', 'sin datos', 'n/a', 'nan', '', '-'}
    return str(value).strip().lower() not in negatives

def uses_ai(value):
    """Determina si usa Inteligencia Artificial"""
    if pd.isna(value): 
        return False
    yes_values = {'sí', 'yes', 'si'}
    return str(value).strip().lower() in yes_values

def get_hierarchy_order(hierarchy_value):
    """Retorna orden numérico para jerarquía"""
    if pd.isna(hierarchy_value):
        return 5
    hierarchy_value = str(hierarchy_value).strip().lower()
    order_map = {
        'top management': 1,
        'middle management': 2,
        'entry level/others': 3,
    }
    return order_map.get(hierarchy_value, 5)

# --- 3. DATOS Y CARGA ---
def generate_mock_data():
    """Genera datos de ejemplo si no hay archivos"""
    data_emp = {
        'Nombre': ['Tech Solutions SL', 'Industrias Norte SA', 'Innovación Global', 'Caf', 'Idom'],
        'provincia': ['Gipuzkoa', 'Bizkaia', 'Araba', 'Gipuzkoa', 'Bizkaia'],
        'veredicto_final': ['TOP', 'STANDARD', 'GROWTH', 'TOP', 'TOP'],
        'conclusion_sueldo_80k': ['Es VIABLE', 'DIFICIL', 'Es VIABLE', 'VIABLE', 'VIABLE'],
        'ventas_estimado': [5000000, 12000000, 2500000, 450000000, 300000000],
        'numero_empleados': [45, 120, 25, 3000, 4000],
        'ano_constitucion': [2010, 1995, 2018, 1917, 1957],
        'web_oficial': ['www.techsol.com', 'www.norte.com', 'www.innoglo.com', 'www.caf.net', 'www.idom.com'],
        'actividad_resumen': ['SaaS', 'Manufactura', 'Consultoría IA', 'Ferrocarril', 'Ingeniería'],
        'propiedad_accionistas': ['Fundadores', 'Familia', 'VC Fund', 'Publica', 'Empleados'],
        'private_equity_firmas': ['-', '-', 'Sequoia', '-', '-'],
        'cto_actual': ['Jon Doe', 'Mikel Smith', 'Ana García', 'Txomin Perez', 'Luis M.'],
        'tamano_ing': ['15', '5', '10', '200+', '1000+'],
        'usa_inteligencia_artificial': ['Sí', 'No', 'Sí', 'Sí', 'Sí'],
        'plataforma_cloud': ['AWS', 'On-prem', 'Azure', 'Hybrid', 'AWS'],
        'perfil_txt': ['Python, React', 'Java', 'Python, PyTorch', 'C++', 'Java, .NET'],
        'patentes': [2, 0, 5, 50, 10],
        'SECTOR_NOMBRE': ['Tecnología', 'Industria', 'Consultoría', 'Transporte', 'Ingeniería'],
        'financiacion_publica_detalle': ['Hazitek', 'No', 'CDTI', 'Europea', 'No'],
        'solvencia_txt': ['Alta', 'Media', 'Alta', 'Muy Alta', 'Alta']
    }
    return pd.DataFrame(data_emp)

def validate_and_clean_data(df):
    """Valida y limpia datos cargados"""
    if df.empty:
        return df
    
    if 'patentes' in df.columns:
        df['patentes'] = pd.to_numeric(df['patentes'], errors='coerce').fillna(0).astype(int)
    else:
        df['patentes'] = 0
    
    if 'numero_empleados' in df.columns:
        def clean_to_int(x):
            s = re.sub(r'[^\d]', '', str(x))
            return int(s) if s else 0
        df['numero_empleados'] = df['numero_empleados'].apply(clean_to_int)
    else:
        df['numero_empleados'] = 0
    
    required_cols = {
        'private_equity_firmas': 'Ninguno',
        'usa_inteligencia_artificial': 'NO'
    }
    for col, default in required_cols.items():
        if col not in df.columns:
            df[col] = default
        else:
            df[col] = df[col].fillna(default)
    
    if 'veredicto_final' in df.columns:
        df['veredicto_final'] = df['veredicto_final'].str.replace('TIBURÓN', 'TOP', case=False, regex=False)
    
    df = df.drop_duplicates(subset=['Nombre'], keep='first')
    
    return df

@st.cache_data(ttl=3600)
def load_data():
    """Carga datos desde archivos o genera mock data"""
    df_main = None
    df_alumni = pd.DataFrame()
    
    files_to_try = ['guipuzcoa_dollar_final_ddbb.csv', 'euskadi_navarra_dollar.csv']
    for file_name in files_to_try:
        if os.path.exists(file_name):
            try: 
                df_main = pd.read_csv(file_name, sep=';', encoding='utf-8', dtype=str)
                break
            except: 
                try: 
                    df_main = pd.read_csv(file_name, sep=';', encoding='latin-1', dtype=str)
                    break
                except: 
                    try: 
                        df_main = pd.read_csv(file_name, sep=',', encoding='utf-8', dtype=str)
                        break
                    except: 
                        pass
    
    file_alumni = 'alumni_seguro.enc'
    if os.path.exists(file_alumni) and "encryption_key" in st.secrets and Fernet:
        try:
            key = st.secrets["encryption_key"]
            cipher_suite = Fernet(key)
            with open(file_alumni, 'rb') as file: 
                encrypted_data = file.read()
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            try: 
                df_alumni = pd.read_csv(io.BytesIO(decrypted_data), sep=';', encoding='utf-8')
            except: 
                df_alumni = pd.read_csv(io.BytesIO(decrypted_data), sep=';', encoding='latin-1')
        except Exception as e:
            st.warning(f"⚠️ No se pudieron cargar datos de contactos encriptados")

    if df_main is None or df_main.empty:
        df_main = generate_mock_data()

    df_main = validate_and_clean_data(df_main)
    
    if not df_alumni.empty:
        df_alumni.columns = [c.strip() for c in df_alumni.columns]
        cols_map = {'funcion': 'función', 'jerarquia': 'jerarquía'}
        df_alumni.rename(columns=cols_map, inplace=True)
        
        c_matriz = next((x for x in df_alumni.columns if 'informa' in x.lower()), 'nombre_matriz_einforma')
        if c_matriz in df_alumni.columns: 
            df_alumni[c_matriz] = df_alumni[c_matriz].astype(str).str.strip()
            
    return df_main, df_alumni

df_main, df_alumni = load_data()

# --- 4. INICIALIZACIÓN DE ESTADO ---
if 'page' not in st.session_state: 
    st.session_state.page = 'home'
if 'selected_empresa' not in st.session_state: 
    st.session_state.selected_empresa = None
if 'current_page' not in st.session_state: 
    st.session_state.current_page = 0
if 'scroll_needed' not in st.session_state: 
    st.session_state.scroll_needed = False

if 'f_nombre' not in st.session_state: 
    st.session_state.f_nombre = ""
if 'f_provincia' not in st.session_state: 
    st.session_state.f_provincia = []
if 'f_patentes' not in st.session_state: 
    st.session_state.f_patentes = "Todos"
if 'f_pe' not in st.session_state: 
    st.session_state.f_pe = "Todos"
if 'f_ia' not in st.session_state: 
    st.session_state.f_ia = "Todos"
if 'f_deusto' not in st.session_state: 
    st.session_state.f_deusto = "Todos"

# --- INICIALIZACIÓN PARA BUSCAR PERSONAS ---
if 'f_personas_nombre' not in st.session_state:
    st.session_state.f_personas_nombre = ""
if 'f_personas_empresa' not in st.session_state:
    st.session_state.f_personas_empresa = ""
if 'f_personas_provincia' not in st.session_state:
    st.session_state.f_personas_provincia = []
if 'f_personas_jerarquia' not in st.session_state:
    st.session_state.f_personas_jerarquia = []
if 'f_personas_funcion' not in st.session_state:
    st.session_state.f_personas_funcion = ""
if 'current_page_personas' not in st.session_state:
    st.session_state.current_page_personas = 0


ITEMS_PER_PAGE = 20

def navigate_to(page):
    """Navega a una página específica"""
    st.session_state.page = page
    st.session_state.scroll_needed = True
    if page == 'explorer':
        st.session_state.selected_empresa = None
        st.session_state.current_page = 0

def select_company(empresa_nombre):
    """Selecciona una empresa para ver detalle"""
    st.session_state.selected_empresa = empresa_nombre
    st.session_state.page = 'detail'
    st.session_state.scroll_needed = True

def change_page(delta):
    """Cambia la página de resultados"""
    st.session_state.current_page += delta
    st.session_state.scroll_needed = True

scroll_to_top()

# --- OPTIMIZACIÓN: Pre-calcular empresas con contactos (UNA SOLA VEZ con caché) ---
@st.cache_data(ttl=3600)
def get_empresas_con_contactos():
    """Retorna set de empresas que tienen contactos en df_alumni"""
    if df_alumni.empty:
        return set()
    
    empresas_set = set(
        df_alumni['nombre_matriz_einforma'].astype(str).str.strip().unique()
    )
    return empresas_set

# --- FUNCIÓN AUXILIAR: Obtener nombre empresa (con fallback a nombre_dba) ---
def get_empresa_name(row):
    """Retorna nombre_matriz_einforma o nombre_dba si no existe"""
    matriz = safe_get_val(row, 'nombre_matriz_einforma', default=None)
    if matriz and matriz != "-":
        return matriz
    return safe_get_val(row, 'nombre_dba', default="-")



# --- 6. PÁGINA: HOME ---
# --- 6. PÁGINA: HOME ---
if st.session_state.page == 'home':
    # CSS personalizado para mayor elegancia
    st.markdown("""
    <style>
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 60px 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .hero-section h1 {
        font-size: 3.5em;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        letter-spacing: -1px;
    }
    
    .card-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .card {
        background: white;
        border-radius: 15px;
        padding: 40px 30px;
        text-align: center;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        border-top: 5px solid;
        cursor: pointer;
    }
    
    .card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    }
    
    .card-empresas {
        border-top-color: #667eea;
    }
    
    .card-profesionales {
        border-top-color: #f093fb;
    }
    
    .card-icon {
        font-size: 4em;
        margin-bottom: 15px;
    }
    
    .card h3 {
        font-size: 1.5em;
        margin: 15px 0 10px 0;
        color: #333;
        font-weight: 700;
    }
    
    .card p {
        font-size: 0.95em;
        color: #666;
        margin: 10px 0 0 0;
        line-height: 1.5;
    }
    
    .note-section {
        background: #f8f9fa;
        border-left: 5px solid #667eea;
        padding: 20px 25px;
        border-radius: 10px;
        margin-top: 10px;
    }
    
    .note-section p {
        margin: 0;
        color: #555;
        font-size: 0.95em;
        line-height: 1.6;
    }
    
    @media (max-width: 1024px) {
        .card-container {
            grid-template-columns: 1fr;
        }
        
        .hero-section h1 {
            font-size: 2.5em;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # --- HERO SECTION ---
    st.markdown("""
    <div class="hero-section">
        <h1>🎯 BINGO</h1>
        <p style="font-size: 1.3em; margin: 15px 0 0 0; opacity: 0.95; font-weight: 300;">Filtra empresas, conecta con profesionales y ¡canta bingo!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- CARDS SECTION (CLICKEABLES) ---
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(
            "",
            key="btn_home_empresas_card",
            use_container_width=True,
            help="Filtra empresas"
        ):
            navigate_to('explorer')
            st.rerun()
        
        st.markdown("""
        <div class="card card-empresas" style="margin-top: -65px;">
            <div class="card-icon">🏢</div>
            <h3>Filtra Empresas</h3>
            <p>Busca y descubre empresas de Gipuzkoa, Bizkaia, Araba y Navarra</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button(
            "",
            key="btn_home_personas_card",
            use_container_width=True,
            help="Conecta con profesionales"
        ):
            navigate_to('personas')
            st.rerun()
        
        st.markdown("""
        <div class="card card-profesionales" style="margin-top: -65px;">
            <div class="card-icon">👥</div>
            <h3>Conecta con Profesionales</h3>
            <p>Busca y conecta con personas de Deusto Alumni</p>
        </div>
        """, unsafe_allow_html=True)
    
    # --- NOTA ---
    st.markdown("""
    <div class="note-section">
        <p><strong>📌 Nota:</strong> Los datos provienen de inteligencia artificial e información pública (prensa, rankings, webs corporativas). Aunque procuramos precisión, algunos datos pueden ser incompletos o inexactos. Verifica información crítica directamente con las empresas.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 7. PÁGINA: EXPLORADOR ---
elif st.session_state.page == 'explorer':
    st.title("🚀 Explorador de Empresas")
    st.markdown("Usa los filtros del menú lateral para encontrar tu cliente ideal.")
    
    with st.sidebar:
        st.header("🔍 Filtros de Búsqueda")
        if st.button("⬅️ Volver al Inicio", use_container_width=True):
            navigate_to('home')
            st.rerun()
        st.divider()
        
        st.session_state.f_nombre = st.text_input("Nombre Empresa", value=st.session_state.f_nombre)
        
        provs = sorted(df_main['provincia'].dropna().unique().tolist())
        st.session_state.f_provincia = st.multiselect("Provincia", provs, default=st.session_state.f_provincia)
        
        st.session_state.f_patentes = st.radio("¿Tiene Patentes?", ["Todos", "Sí", "No"], 
                                               index=["Todos", "Sí", "No"].index(st.session_state.f_patentes),
                                               horizontal=True)
        
        st.session_state.f_pe = st.radio("¿Tiene Private Equity?", ["Todos", "Sí", "No"], 
                                         index=["Todos", "Sí", "No"].index(st.session_state.f_pe),
                                         horizontal=True)
        
        st.session_state.f_ia = st.radio("¿Usa Inteligencia Artificial?", ["Todos", "Sí", "No"], 
                                         index=["Todos", "Sí", "No"].index(st.session_state.f_ia),
                                         horizontal=True)
        
        st.session_state.f_deusto = st.radio("¿Deusto Alumni?", ["Todos", "Sí", "No"], 
                                             index=["Todos", "Sí", "No"].index(st.session_state.f_deusto),
                                             horizontal=True)

    # --- APLICAR FILTROS (FUERA DEL SIDEBAR) ---
    empresas_alumni = get_empresas_con_contactos()
    
    df_show = df_main.copy()

    if st.session_state.f_nombre:
        df_show = df_show[df_show['Nombre'].astype(str).str.contains(
            st.session_state.f_nombre, case=False, na=False)]

    if st.session_state.f_provincia:
        df_show = df_show[df_show['provincia'].isin(st.session_state.f_provincia)]

    if st.session_state.f_patentes == "Sí":
        df_show = df_show[df_show['patentes'] > 0]
    elif st.session_state.f_patentes == "No":
        df_show = df_show[df_show['patentes'] == 0]

    if st.session_state.f_pe == "Sí":
        df_show = df_show[df_show['private_equity_firmas'].apply(has_private_equity)]
    elif st.session_state.f_pe == "No":
        df_show = df_show[~df_show['private_equity_firmas'].apply(has_private_equity)]

    if st.session_state.f_ia == "Sí":
        df_show = df_show[df_show['usa_inteligencia_artificial'].apply(uses_ai)]
    elif st.session_state.f_ia == "No":
        df_show = df_show[~df_show['usa_inteligencia_artificial'].apply(uses_ai)]

    # NUEVO: Filtro Deusto Alumni (OPTIMIZADO - Usa caché)
    if st.session_state.f_deusto == "Sí":
        df_show = df_show[df_show['Nombre'].isin(empresas_alumni)]
    elif st.session_state.f_deusto == "No":
        df_show = df_show[~df_show['Nombre'].isin(empresas_alumni)]

    # --- PAGINACIÓN ---
    total_items = len(df_show)
    total_pages = math.ceil(total_items / ITEMS_PER_PAGE) if total_items > 0 else 1
    if st.session_state.current_page >= total_pages: 
        st.session_state.current_page = 0
    if st.session_state.current_page < 0: 
        st.session_state.current_page = 0
        
    start_idx = st.session_state.current_page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    df_page = df_show.iloc[start_idx:end_idx]

    st.markdown(f"""<div class="results-bar"><div>🎯 <b>{total_items}</b> empresas encontradas</div><div style="font-size: 0.9rem;">Página {st.session_state.current_page + 1} de {max(1, total_pages)}</div></div>""", unsafe_allow_html=True)
    
    # --- RENDERIZAR EMPRESAS ---
    if not df_page.empty:
        for index, row in df_page.iterrows():
            nombre = row['Nombre']
            provincia = capitalize_first_letter(safe_get_val(row, 'provincia'))
            
            # Contar contactos en df_alumni
            num_contactos = 0
            if not df_alumni.empty:
                match = df_alumni[df_alumni['nombre_matriz_einforma'].astype(str).str.strip() == str(nombre).strip()]
                if match.empty:
                    match = df_alumni[df_alumni['nombre_matriz_einforma'].astype(str).str.contains(re.escape(str(nombre).strip()), case=False, na=False)]
                num_contactos = len(match)
            
            with st.expander(f"🏢 **{nombre}** ({provincia})"):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Empleados", clean_number_format(row['numero_empleados']))
                c2.metric("Ventas Est.", clean_number_format(safe_get_val(row, 'ventas_estimado')))
                pat = str(row.get('patentes', 0))
                c3.metric("Patentes", pat, delta="Innovador" if int(pat) > 0 else None, delta_color="off")
                c4.metric("Contactos", num_contactos, delta="Alumni" if num_contactos > 0 else None, delta_color="off")
                st.write("")
                if st.button("➕ Más detalles", key=f"btn_{index}", use_container_width=True):
                    select_company(row['Nombre'])
                    st.rerun()
        
        st.write("")
        col_prev, col_info, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.session_state.current_page > 0:
                if st.button("⬅️ Anterior", use_container_width=True):
                    change_page(-1)
                    st.rerun()
        with col_next:
            if st.session_state.current_page < total_pages - 1:
                if st.button("Siguiente ➡️", use_container_width=True):
                    change_page(1)
                    st.rerun()
    else: 
        st.warning("No hay empresas que coincidan con estos filtros.")


# --- 8. PÁGINA: DETALLE ---
elif st.session_state.page == 'detail':
    selected_empresa = st.session_state.selected_empresa
    row_data = df_main[df_main['Nombre'] == selected_empresa]
    
    if not row_data.empty:
        r = row_data.iloc[0]
        
        # BOTONES DE NAVEGACIÓN (ARRIBA)
        col_nav1, col_nav2, col_nav3 = st.columns([1, 3, 1])
        with col_nav1:
            if st.button("⬅️ Explorador", use_container_width=True):
                navigate_to('explorer')
                st.rerun()
        with col_nav3:
            if st.button("🏠 Inicio", use_container_width=True):
                navigate_to('home')
                st.rerun()
        
        st.divider()
        
        st.title(f"🏢 {safe_get_val(r, 'Nombre')}")
        
        # 1. RESUMEN
        st.markdown('<div class="section-title">Resumen</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="kpi-card"><div class="kpi-value">{capitalize_first_letter(safe_get_val(r, "provincia"))}</div><div class="kpi-label">UBICACIÓN</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi-card"><div class="kpi-value">{safe_get_val(r, "veredicto_final")}</div><div class="kpi-label">CLASIFICACIÓN BINGO</div></div>', unsafe_allow_html=True)
        v_raw = safe_get_val(r, "conclusion_sueldo_80k")
        v_color = "#2E7D32" if "VIABLE" in v_raw.upper() else "#C62828" if "DIFICIL" in v_raw.upper() else "#1F4E79"
        v_text = "VIABLE" if "VIABLE" in v_raw.upper() else "DIFÍCIL" if "DIFICIL" in v_raw.upper() else "NEUTRO"
        c3.markdown(f'<div class="kpi-card"><div class="kpi-value" style="color:{v_color}">{v_text}</div><div class="kpi-label">VIABILIDAD SALARIAL</div></div>', unsafe_allow_html=True)
        
        st.write("")
        render_table(pd.DataFrame({
            "Ventas Est.": [clean_number_format(safe_get_val(r, 'ventas_estimado'))],
            "Empleados": [clean_number_format(safe_get_val(r, 'numero_empleados'))],
            "Patentes": [str(r.get('patentes', 0))],
            "Año Const.": [safe_get_val(r, 'ano_constitucion')],
            "Web": [safe_get_val(r, 'web_oficial')]
        }))

        # 2. SECTOR Y ACTIVIDAD (GRID)
        st.markdown('<div class="section-title">Sector y Actividad</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="responsive-grid">
            <div class="content-box">
                <span class="box-header">Sector</span>
                {safe_get_val(r, 'SECTOR_NOMBRE')}
            </div>
            <div class="content-box">
                <span class="box-header">Actividad Principal</span>
                {safe_get_val(r, 'actividad_resumen')}
            </div>
        </div>""", unsafe_allow_html=True)

        # 3. PROPIEDAD Y SOLVENCIA (GRID)
        st.markdown('<div class="section-title">Propiedad y Solvencia</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="responsive-grid">
            <div class="content-box">
                <span class="box-header">Estructura de la Propiedad</span>
                <b>Accionistas:</b> {safe_get_val(r, 'propiedad_accionistas')}<br><br>
                <b>Private Equity:</b> {safe_get_val(r, 'private_equity_firmas')}
            </div>
            <div class="content-box">
                <span class="box-header">Finanzas y Solvencia</span>
                <b>Financiación Pública:</b> {safe_get_val(r, 'financiacion_publica_detalle')}<br><br>
                <b>Solvencia:</b> {safe_get_val(r, 'solvencia_txt')}
            </div>
        </div>""", unsafe_allow_html=True)

        # 4. MADUREZ TECNOLÓGICA
        st.markdown('<div class="section-title">Madurez Tecnológica</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="grid-2">
            <div class="tech-hero"><div class="tech-hero-label">CTO / Responsable</div><div class="tech-hero-val">{safe_get_val(r, 'cto_actual')}</div></div>
            <div class="tech-hero"><div class="tech-hero-label">Equipo Ingeniería</div><div class="tech-hero-val">{safe_get_val(r, 'tamano_ing')}</div></div>
        </div>
        <div class="grid-3">
            <div class="tech-card"><span class="tech-icon">🧠</span><div class="tech-title">IA & Automatización</div><div class="tech-text">{safe_get_val(r, 'usa_inteligencia_artificial')}</div></div>
            <div class="tech-card"><span class="tech-icon">☁️</span><div class="tech-title">Infraestructura</div><div class="tech-text">{safe_get_val(r, 'plataforma_cloud')}</div></div>
            <div class="tech-card"><span class="tech-icon">💻</span><div class="tech-title">Stack Técnico</div><div class="tech-text">{safe_get_val(r, 'perfil_txt')}</div></div>
        </div>""", unsafe_allow_html=True)
        
        # 5. NETWORKING (ALUMNI) - ORDENADO POR JERARQUÍA
        st.markdown('<div class="section-title">Networking (Alumni)</div>', unsafe_allow_html=True)
        
        match = pd.DataFrame()
        if not df_alumni.empty:
            match = df_alumni[df_alumni['nombre_matriz_einforma'].astype(str).str.strip() == str(selected_empresa).strip()]
            if match.empty:
                match = df_alumni[df_alumni['nombre_matriz_einforma'].astype(str).str.contains(re.escape(str(selected_empresa).strip()), case=False, na=False)]

        if not match.empty:
            st.success(f"✅ Se han encontrado {len(match)} contactos en esta empresa.")
            
            # ORDENAR POR JERARQUÍA
            if 'jerarquía' in match.columns:
                match['sort_order'] = match['jerarquía'].apply(get_hierarchy_order)
                df_sorted = match.sort_values(by=['sort_order', 'Nombre']).drop('sort_order', axis=1)
            else:
                df_sorted = match.copy()
            
            t1, t2 = st.tabs(["📊 Resumen", "📋 Lista Detallada"])
            
            with t1:
                if 'jerarquía' in df_sorted.columns:
                    summary_data = []
                    for hierarchy in ['top management', 'middle management', 'entry level/others']:
                        count = len(df_sorted[df_sorted['jerarquía'].astype(str).str.lower().str.strip() == hierarchy])
                        if count > 0:
                            display_name = hierarchy.title() if hierarchy != 'entry level/others' else 'Entry Level/Others'
                            summary_data.append({
                                'Nivel': display_name,
                                'Total': count,
                                'key': hierarchy
                            })
                    
                    if summary_data:
                        df_summary = pd.DataFrame(summary_data)
                        
                        html_sum = '<table class="custom-table" style="width:100%"><thead><tr><th>Nivel Jerárquico</th><th>Cantidad</th></tr></thead><tbody>'
                        for _, row_c in df_summary.iterrows():
                            key = row_c['key']
                            if "top" in key:
                                badge = "badge-top"
                            elif "middle" in key:
                                badge = "badge-mid"
                            else:
                                badge = "badge-entry"
                            html_sum += f'<tr><td><span class="{badge}">{row_c["Nivel"]}</span></td><td style="text-align: center;"><b>{row_c["Total"]}</b></td></tr>'
                        html_sum += '</tbody></table>'
                        st.markdown(html_sum, unsafe_allow_html=True)
                    else:
                        st.info("No hay datos de jerarquía disponibles")
                else:
                    st.info("Datos de jerarquía no disponibles.")
            
            # TAB 2: LISTA DETALLADA
            with t2:
                cols_view = ['Nombre', 'Cargo', 'jerarquía', 'función', 'url_linkedin']
                cols_exist = [c for c in cols_view if c in df_sorted.columns]
                
                df_display = df_sorted[cols_exist].copy()
                
                if 'Nombre' in df_display.columns:
                    df_display['Nombre'] = df_display['Nombre'].apply(
                        lambda x: ' '.join([word.capitalize() for word in str(x).split()]) if pd.notna(x) else '-'
                    )
                
                if 'jerarquía' in df_display.columns:
                    def get_badge(hierarchy):
                        if pd.isna(hierarchy):
                            return '-'
                        hierarchy = str(hierarchy).strip().lower()
                        if "top" in hierarchy:
                            return f'<span class="badge-top">{hierarchy.title()}</span>'
                        elif "middle" in hierarchy:
                            return f'<span class="badge-mid">{hierarchy.title()}</span>'
                        else:
                            return f'<span class="badge-entry">{hierarchy.upper()}</span>'
                    
                    df_display['jerarquía'] = df_display['jerarquía'].apply(get_badge)
                
                render_table(df_display)

        else:
            st.info("ℹ️ No hay contactos alumni registrados actualmente en esta empresa.")
        
        # BOTONES DE NAVEGACIÓN (ABAJO)
        st.divider()
        col_nav1, col_nav2, col_nav3 = st.columns([1, 3, 1])
        with col_nav1:
            if st.button("⬅️ Explorador", key="btn_back_explorer", use_container_width=True):
                navigate_to('explorer')
                st.rerun()
        with col_nav3:
            if st.button("🏠 Inicio", key="btn_back_home", use_container_width=True):
                navigate_to('home')
                st.rerun()

    else:
        st.error("Error al cargar los datos de la empresa.")

# --- 9. PÁGINA: BUSCAR PROFESIONALES ---
elif st.session_state.page == 'personas':
    st.title("🤝 Buscar Profesionales")
    st.markdown("Encuentra a los profesionales clave en tu base de datos de contactos.")
    
    with st.sidebar:
        st.header("🔍 Filtros de Búsqueda")
        if st.button("⬅️ Volver al Inicio", use_container_width=True):
            navigate_to('home')
            st.rerun()
        st.divider()
        
        # Filtro: Nombre de Persona
        st.session_state.f_personas_nombre = st.text_input(
            "Nombre Persona",
            value=st.session_state.f_personas_nombre,
            placeholder="Escribe un nombre..."
        )
        
        # Filtro: Nombre de Empresa (BÚSQUEDA DINÁMICA CON PRIORIDAD)
        if not df_alumni.empty:
            # Obtiene empresas de AMBAS columnas (pero con prioridad a einforma)
            df_temp = df_alumni.copy()
            df_temp['empresa_a_mostrar'] = df_temp.apply(
                lambda row: (
                    row['nombre_matriz_einforma'] 
                    if pd.notna(row['nombre_matriz_einforma']) and str(row['nombre_matriz_einforma']).strip() not in ['', 'nan', '-']
                    else row['nombre_dba']
                ),
                axis=1
            )
            
            todas_las_empresas = sorted(
                set(df_temp['empresa_a_mostrar'].fillna('').astype(str).str.strip().unique()) - {'', 'nan', '-'}
            )
            
            # Input de búsqueda de empresa
            empresa_input = st.text_input(
                "Empresa",
                value=st.session_state.f_personas_empresa,
                placeholder="Escribe para buscar..."
            )
            
            # Filtrar empresas según lo que escribe el usuario
            if empresa_input:
                empresas_filtradas = [e for e in todas_las_empresas if empresa_input.lower() in e.lower()]
            else:
                empresas_filtradas = []
            
            # Mostrar sugerencias (max 10)
            if empresas_filtradas:
                st.session_state.f_personas_empresa = st.selectbox(
                    "Selecciona empresa",
                    empresas_filtradas,
                    index=0,
                    key="empresa_select",
                    label_visibility="collapsed"
                )
            else:
                st.session_state.f_personas_empresa = empresa_input if empresa_input else ""
        
        # Filtro: Provincia de Empresa
        if not df_main.empty:
            provs_empresas = sorted(df_main['provincia'].dropna().unique().tolist())
            st.session_state.f_personas_provincia = st.multiselect(
                "Provincia Empresa", 
                provs_empresas, 
                default=st.session_state.f_personas_provincia
            )
        
        # Filtro: Jerarquía
        if not df_alumni.empty:
            jerarquias = sorted(
                df_alumni['jerarquía'].dropna().astype(str).str.strip().unique().tolist()
            )
            jerarquias = [j for j in jerarquias if j.lower() not in ['nan', '-', '']]
            st.session_state.f_personas_jerarquia = st.multiselect(
                "Nivel Jerárquico", 
                jerarquias, 
                default=st.session_state.f_personas_jerarquia
            )
        
        # Filtro: Función (multiselect)
        if not df_alumni.empty:
            funciones = sorted(
                df_alumni['función'].dropna().astype(str).str.strip().unique().tolist()
            )
            funciones = [f for f in funciones if f.lower() not in ['nan', '-', '']]
            st.session_state.f_personas_funcion = st.multiselect(
                "Función", 
                funciones, 
                default=st.session_state.f_personas_funcion if isinstance(st.session_state.f_personas_funcion, list) else []
            )
        
        # Botón para limpiar filtros
        st.divider()
        if st.button("🔄 Limpiar Filtros", use_container_width=True):
            st.session_state.f_personas_nombre = ""
            st.session_state.f_personas_empresa = ""
            st.session_state.f_personas_provincia = []
            st.session_state.f_personas_jerarquia = []
            st.session_state.f_personas_funcion = []
            st.session_state.current_page_personas = 0
            st.rerun()

    # --- APLICAR FILTROS ---
    df_personas = df_alumni.copy() if not df_alumni.empty else pd.DataFrame()
    
    if df_personas.empty:
        st.warning("❌ No hay datos de contactos disponibles.")
    else:
        # Crear columna de empresa con prioridad (einforma > dba)
        df_personas['empresa_filtro'] = df_personas.apply(
            lambda row: (
                row['nombre_matriz_einforma'] 
                if pd.notna(row['nombre_matriz_einforma']) and str(row['nombre_matriz_einforma']).strip() not in ['', 'nan', '-']
                else row['nombre_dba']
            ),
            axis=1
        )
        
        # Filtro por nombre de persona
        if st.session_state.f_personas_nombre:
            df_personas = df_personas[df_personas['Nombre'].astype(str).str.contains(
                st.session_state.f_personas_nombre, case=False, na=False)]
        
        # Filtro por empresa (SOLO UNA, con prioridad einforma)
        if st.session_state.f_personas_empresa:
            df_personas = df_personas[
                df_personas['empresa_filtro'].astype(str).str.contains(
                    st.session_state.f_personas_empresa, case=False, na=False)
            ]
        
        # Filtro por provincia (cruzar con df_main)
        if st.session_state.f_personas_provincia:
            empresas_provincia = df_main[
                df_main['provincia'].isin(st.session_state.f_personas_provincia)
            ]['Nombre'].tolist()
            df_personas = df_personas[
                df_personas['empresa_filtro'].isin(empresas_provincia)
            ]
        
        # Filtro por jerarquía
        if st.session_state.f_personas_jerarquia:
            df_personas = df_personas[
                df_personas['jerarquía'].astype(str).str.strip().isin(st.session_state.f_personas_jerarquia)
            ]
        
        # Filtro por función
        if st.session_state.f_personas_funcion:
            df_personas = df_personas[
                df_personas['función'].astype(str).str.strip().isin(st.session_state.f_personas_funcion)
            ]
        
        # --- PAGINACIÓN ---
        total_items = len(df_personas)
        total_pages = math.ceil(total_items / ITEMS_PER_PAGE) if total_items > 0 else 1
        
        if st.session_state.current_page_personas >= total_pages:
            st.session_state.current_page_personas = 0
        if st.session_state.current_page_personas < 0:
            st.session_state.current_page_personas = 0
        
        start_idx = st.session_state.current_page_personas * ITEMS_PER_PAGE
        end_idx = start_idx + ITEMS_PER_PAGE
        df_page = df_personas.iloc[start_idx:end_idx]
        
        st.markdown(f"""<div class="results-bar"><div>🎯 <b>{total_items}</b> profesionales encontrados</div><div style="font-size: 0.9rem;">Página {st.session_state.current_page_personas + 1} de {max(1, total_pages)}</div></div>""", unsafe_allow_html=True)
        
        # --- RENDERIZAR PROFESIONALES ---
        if not df_page.empty:
            for index, row in df_page.iterrows():
                nombre = capitalize_first_letter(safe_get_val(row, 'Nombre'))
                empresa = get_empresa_name(row)
                provincia = "-"
                jerarquia = safe_get_val(row, 'jerarquía')
                funcion = capitalize_first_letter(safe_get_val(row, 'función'))
                
                # Obtener provincia desde df_main
                if empresa != "-":
                    empresa_data = df_main[df_main['Nombre'] == empresa]
                    if not empresa_data.empty:
                        provincia = capitalize_first_letter(safe_get_val(empresa_data.iloc[0], 'provincia'))
                
                # Expander con info de la persona
                with st.expander(f"👤 **{nombre}** - {funcion}"):
                    # Tabla con detalles completos
                    df_detalle = pd.DataFrame({
                        "Nombre": [nombre],
                        "Empresa": [empresa],
                        "Provincia": [provincia],
                        "Función": [funcion],
                        "Jerarquía": [jerarquia]
                    })
                    render_table(df_detalle)
                    
                    st.write("")
                    
                    # Botón para ver la empresa
                    if empresa != "-" and empresa in df_main['Nombre'].values:
                        if st.button(f"👁️ Ver perfil de {empresa}", key=f"btn_persona_empresa_{index}", use_container_width=True):
                            select_company(empresa)
                            st.rerun()
                    else:
                        st.caption("❌ Empresa no disponible en la base de datos")
            
            # --- PAGINACIÓN (BOTONES) ---
            st.write("")
            col_prev, col_info, col_next = st.columns([1, 2, 1])
            with col_prev:
                if st.session_state.current_page_personas > 0:
                    if st.button("⬅️ Anterior", use_container_width=True):
                        st.session_state.current_page_personas -= 1
                        st.rerun()
            with col_next:
                if st.session_state.current_page_personas < total_pages - 1:
                    if st.button("Siguiente ➡️", use_container_width=True):
                        st.session_state.current_page_personas += 1
                        st.rerun()
        else:
            st.warning("⚠️ No hay profesionales que coincidan con estos filtros.")
