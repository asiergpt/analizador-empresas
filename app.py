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
    page_title="BINGO - Market Intelligence",
    page_icon="🎱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- UTILIDAD: SCROLL TO TOP ---
def scroll_to_top():
    """Fuerza el scroll al inicio de la página usando JS"""
    js = '''<script>
        var body = window.parent.document.querySelector(".main");
        console.log("Scrolling to top");
        body.scrollTop = 0;
    </script>'''
    components.html(js, height=0)

# --- 1. GESTIÓN DE ESTILOS (CSS) ---
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; font-size: 16px; color: #2c3e50; }
    
    /* Títulos y Cabeceras */
    .main-header { color: #1F4E79; font-size: 2.2rem; font-weight: 800; margin-bottom: 0.5rem; }
    .sub-header { color: #666; font-size: 1.1rem; margin-bottom: 2rem; }
    .section-title { color: #1F4E79; font-size: 1.5rem; font-weight: 700; margin-top: 2rem; border-bottom: 3px solid #DAE9F7; padding-bottom: 5px; margin-bottom: 15px; }

    /* KPIs */
    .kpi-card { background-color: #ffffff; border-radius: 12px; padding: 15px; text-align: center; border: 2px solid #DAE9F7; box-shadow: 0 2px 4px rgba(0,0,0,0.03); height: 100%; display: flex; flex-direction: column; justify-content: center; transition:all 0.2s;}
    .kpi-card:hover { border-color: #1F4E79; box-shadow: 0 4px 8px rgba(0,0,0,0.08); }
    .kpi-value { color: #1F4E79; font-size: 1.8rem; font-weight: 800; line-height: 1.2; margin-bottom: 5px; }
    .kpi-label { font-size: 0.8rem; text-transform: uppercase; font-weight: 600; color: #666; letter-spacing: 0.5px; }
    .kpi-subtext { font-size: 0.9rem; font-weight: 700; margin-top: 5px; }

    /* Tablas */
    .custom-table { width: 100%; border-collapse: separate; border-spacing: 0; min-width: 500px; border-radius: 8px; overflow: hidden; border: 1px solid #eee; }
    .custom-table th { background-color: #1F4E79; color: white; padding: 12px; text-align: left; font-weight: 600; }
    .custom-table td { border-bottom: 1px solid #f0f0f0; padding: 12px; text-align: left; color: #333; vertical-align: middle; }
    .table-container { overflow-x: auto; box-shadow: 0 2px 5px rgba(0,0,0,0.03); border-radius: 8px; margin-bottom: 20px; background: white; }

    /* Grids y Layouts */
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
    .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 20px; }
    @media (max-width: 768px) { .grid-2, .grid-3 { grid-template-columns: 1fr; } }
    
    .content-box { background-color: white; border: 1px solid #eee; border-radius: 10px; padding: 15px; height: 100%; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .box-header { color: #1F4E79; font-weight: 700; font-size: 1.1rem; margin-bottom: 10px; display: block; }

    /* Elementos de la Home */
    .hero-title { color: #1F4E79; font-size: 4rem; font-weight: 900; text-align: center; margin-bottom: 5px; letter-spacing: -1px; }
    .hero-subtitle { color: #555; font-size: 1.5rem; text-align: center; margin-bottom: 40px; font-weight: 300; }
    .feature-card { background-color: white; border-radius: 12px; padding: 25px; text-align: center; border: 1px solid #eee; box-shadow: 0 4px 12px rgba(0,0,0,0.05); transition: transform 0.3s ease; height: 100%; display: flex; flex-direction: column; justify-content: space-between; }
    .feature-card:hover { transform: translateY(-5px); border-color: #DAE9F7; }
    .feature-icon { font-size: 3rem; margin-bottom: 15px; display: block; }
    .feature-title { color: #1F4E79; font-weight: 700; font-size: 1.2rem; margin-bottom: 10px; }
    .feature-desc { color: #666; font-size: 1rem; line-height: 1.5; margin-bottom: 20px; }

    /* Estilos Adicionales */
    .results-bar { background-color: #e3f2fd; color: #0d47a1; padding: 12px 20px; border-radius: 8px; font-weight: 500; margin-bottom: 20px; border-left: 5px solid #1F4E79; display: flex; justify-content: space-between; align-items: center; }
    /* Ajuste para expanders en móvil */
    [data-testid="stExpander"] { border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); background-color: white; }
    [data-testid="stExpander"] summary { font-weight: 600; color: #1F4E79; }
    /* Etiquetas de Alumni */
    .badge-top { background-color: #E3F2FD; color: #1565C0; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 700; }
    .badge-mid { background-color: #E8F5E9; color: #2E7D32; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 700; }
    .badge-entry { background-color: #FFF3E0; color: #EF6C00; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

inject_css()

# --- 2. UTILIDADES ---
def clean_number_format(val):
    if pd.isna(val): return "-"
    s = re.sub(r'[^\d]', '', str(val))
    return "{:,}".format(int(s)) if s else str(val)

def get_val(row, col, default="-"):
    if col in row and pd.notna(row[col]):
        val = str(row[col])
        return val if val.lower() != "nan" else default
    return default

def capitalize_first_letter(text):
    text = str(text).strip()
    if not text or text == "-" or text.lower() == "nan": return "-"
    return " ".join([word.capitalize() for word in text.split()])

def render_table(df):
    if df.empty: 
        st.caption("Sin datos para mostrar.")
        return
    st.markdown(f'<div class="table-container">{df.to_html(index=False, border=0, classes="custom-table", escape=False)}</div>', unsafe_allow_html=True)

# --- 3. DATOS MOCK Y CARGA ---
def generate_mock_data():
    data_emp = {
        'Nombre': ['Tech Solutions SL', 'Industrias Norte SA', 'Innovación Global', 'Caf', 'Idom', 'Gestamp', 'Solarpack'],
        'provincia': ['Gipuzkoa', 'Bizkaia', 'Araba', 'Gipuzkoa', 'Bizkaia', 'Bizkaia', 'Bizkaia'],
        'veredicto_final': ['TOP', 'STANDARD', 'GROWTH', 'TOP', 'TOP', 'TOP', 'GROWTH'],
        'conclusion_sueldo_80k': ['Es VIABLE', 'DIFICIL', 'Es VIABLE', 'VIABLE', 'VIABLE', 'VIABLE', 'VIABLE'],
        'ventas_estimado': [5000000, 12000000, 2500000, 450000000, 300000000, 8000000000, 150000000],
        'numero_empleados': [45, 120, 25, 3000, 4000, 40000, 600],
        'ano_constitucion': [2010, 1995, 2018, 1917, 1957, 1997, 2005],
        'web_oficial': ['www.techsol.com', 'www.norte.com', 'www.innoglo.com', 'www.caf.net', 'www.idom.com', 'www.gestamp.com', 'www.solarpack.com'],
        'actividad_resumen': ['SaaS', 'Manufactura', 'Consultoría IA', 'Ferrocarril', 'Ingeniería', 'Automoción', 'Energía'],
        'propiedad_accionistas': ['Fundadores', 'Familia', 'VC Fund', 'Publica', 'Empleados', 'Familia Ribera', 'EQT'],
        'private_equity_firmas': ['-', '-', 'Sequoia', '-', '-', '-', 'EQT Partners'],
        'cto_actual': ['Jon Doe', 'Mikel Smith', 'Ana García', 'Txomin Perez', 'Luis M.', 'Oscar G.', 'Maria T.'],
        'tamano_ing': ['15', '5', '10', '200+', '1000+', '500+', '40'],
        'usa_inteligencia_artificial': ['Sí', 'No', 'Sí', 'Sí', 'Sí', 'Sí', 'No'],
        'plataforma_cloud': ['AWS', 'On-prem', 'Azure', 'Hybrid', 'AWS', 'Azure', 'Google'],
        'perfil_txt': ['Python, React', 'Java', 'Python, PyTorch', 'C++', 'Java, .NET', 'SAP, IoT', 'Python'],
        'patentes': [2, 0, 5, 50, 10, 100, 15]
    }
    
    data_alum = {
        'Nombre': ['Iker D.', 'Amaia L.', 'Unai E.', 'Maria S.', 'Jon A.'],
        'Cargo': ['Dev', 'CTO', 'PM', 'Director', 'Ingeniero'],
        'nombre_matriz_einforma': ['Tech Solutions SL', 'Tech Solutions SL', 'Industrias Norte SA', 'Caf', 'Idom'],
        'jerarquía': ['Middle Management', 'Top Management', 'Middle Management', 'Top Management', 'Entry Level'],
        'funcion': ['Ingeniería', 'Tecnología', 'Producto', 'Ingeniería', 'Obras'],
        'url_linkedin': ['#', '#', '#', '#', '#']
    }
    return pd.DataFrame(data_emp), pd.DataFrame(data_alum)

@st.cache_data
def load_data():
    df_main = None
    df_alumni = pd.DataFrame()
    
    # 1. EMPRESAS
    files_to_try = ['guipuzcoa_dollar_final_ddbb.csv', 'euskadi_navarra_dollar.csv']
    for file_name in files_to_try:
        if os.path.exists(file_name):
            try: 
                df_main = pd.read_csv(file_name, sep=';', encoding='utf-8', dtype=str)
                break
            except: 
                try: df_main = pd.read_csv(file_name, sep=';', encoding='latin-1', dtype=str)
                except: 
                    try: df_main = pd.read_csv(file_name, sep=',', encoding='utf-8', dtype=str)
                    except: pass
    
    # 2. ALUMNI
    file_alumni = 'alumni_seguro.enc'
    if os.path.exists(file_alumni) and "encryption_key" in st.secrets and Fernet:
        try:
            key = st.secrets["encryption_key"]
            cipher_suite = Fernet(key)
            with open(file_alumni, 'rb') as file: 
                encrypted_data = file.read()
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            try: df_alumni = pd.read_csv(io.BytesIO(decrypted_data), sep=';', encoding='utf-8')
            except: df_alumni = pd.read_csv(io.BytesIO(decrypted_data), sep=';', encoding='latin-1')
        except Exception: pass

    if df_main is None or df_main.empty:
        df_main, df_alumni_mock = generate_mock_data()
        if df_alumni.empty: df_alumni = df_alumni_mock

    if not df_main.empty:
        # Reemplazo TIBURÓN -> TOP
        if 'veredicto_final' in df_main.columns:
             df_main['veredicto_final'] = df_main['veredicto_final'].str.replace('TIBURÓN', 'TOP', case=False, regex=False)

        if 'numero_empleados' in df_main.columns:
            def clean_to_int(x):
                s = re.sub(r'[^\d]', '', str(x))
                return int(s) if s else 0
            df_main['numero_empleados'] = df_main['numero_empleados'].apply(clean_to_int)
        else: df_main['numero_empleados'] = 0

        if 'patentes' in df_main.columns:
            df_main['patentes'] = pd.to_numeric(df_main['patentes'], errors='coerce').fillna(0).astype(int)
        else: df_main['patentes'] = 0

        if 'private_equity_firmas' not in df_main.columns: df_main['private_equity_firmas'] = "Ninguno"
        else: df_main['private_equity_firmas'] = df_main['private_equity_firmas'].fillna("Ninguno")

        if 'usa_inteligencia_artificial' not in df_main.columns: df_main['usa_inteligencia_artificial'] = "NO"
        else: df_main['usa_inteligencia_artificial'] = df_main['usa_inteligencia_artificial'].fillna("NO")
            
    if not df_alumni.empty:
        df_alumni.columns = [c.strip() for c in df_alumni.columns]
        cols_map = {'funcion': 'función', 'jerarquia': 'jerarquía'}
        df_alumni.rename(columns=cols_map, inplace=True)
        
        c_matriz = next((x for x in df_alumni.columns if 'informa' in x.lower()), 'nombre_matriz_einforma')
        if c_matriz in df_alumni.columns: 
            df_alumni[c_matriz] = df_alumni[c_matriz].astype(str).str.strip()
            
    return df_main, df_alumni

df_main, df_alumni = load_data()

# --- 4. GESTIÓN DE ESTADO Y NAVEGACIÓN ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'selected_empresa' not in st.session_state: st.session_state.selected_empresa = None
if 'current_page' not in st.session_state: st.session_state.current_page = 0
if 'scroll_needed' not in st.session_state: st.session_state.scroll_needed = False

ITEMS_PER_PAGE = 20

def navigate_to(page):
    st.session_state.page = page
    st.session_state.scroll_needed = True # Activar scroll al cambiar de página principal
    if page == 'explorer':
        st.session_state.selected_empresa = None
        st.session_state.current_page = 0

def select_company(empresa_nombre):
    st.session_state.selected_empresa = empresa_nombre
    st.session_state.page = 'detail'
    st.session_state.scroll_needed = True

def change_page(delta):
    st.session_state.current_page += delta
    st.session_state.scroll_needed = True # Activar scroll en paginación

# Aplicar Scroll si es necesario al inicio del renderizado
if st.session_state.scroll_needed:
    scroll_to_top()
    st.session_state.scroll_needed = False

# --- 5. LÓGICA DE LAS PÁGINAS ---

# === A. SIDEBAR ===
with st.sidebar:
    if st.session_state.page == 'home':
        st.info("👋 Bienvenido a BINGO. Usa las tarjetas principales para navegar.")
    
    elif st.session_state.page == 'explorer':
        st.header("🔍 Filtros de Búsqueda")
        if st.button("⬅️ Volver al Inicio", use_container_width=True):
            navigate_to('home')
            st.rerun()
        st.divider()
        f_nombre = st.text_input("Nombre Empresa")
        provs = sorted(df_main['provincia'].dropna().unique().tolist())
        f_provincia = st.multiselect("Provincia", provs)
        f_patentes = st.radio("¿Tiene Patentes?", ["Todos", "Sí", "No"], horizontal=True)
        f_pe = st.radio("¿Tiene Private Equity?", ["Todos", "Sí", "No"], horizontal=True)
        f_ia = st.radio("¿Usa Inteligencia Artificial?", ["Todos", "Sí", "No"], horizontal=True)

    elif st.session_state.page == 'detail':
        st.header("Navegación")
        if st.button("⬅️ Volver al Listado", use_container_width=True):
            navigate_to('explorer')
            st.rerun()
        if st.button("🏠 Inicio", use_container_width=True):
            navigate_to('home')
            st.rerun()

# === B. CONTENIDO PRINCIPAL ===

# ----------------- HOME (BINGO) -----------------
if st.session_state.page == 'home':
    st.markdown('<div style="padding-top: 40px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">BINGO</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Filtra, conecta, y bingo!</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns([1, 2, 2, 1])
    with m2:
        st.markdown(f'<div class="kpi-card" style="padding:15px;"><div class="kpi-value">{len(df_main)}</div><div class="kpi-label">EMPRESAS</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="kpi-card" style="padding:15px;"><div class="kpi-value">{df_alumni["Nombre"].nunique() if not df_alumni.empty else 0}</div><div class="kpi-label">CONTACTOS</div></div>', unsafe_allow_html=True)

    st.write("")
    st.write("")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""<div class="feature-card"><div><span class="feature-icon">🏢</span><div class="feature-title">Filtra Empresas</div><div class="feature-desc">Explora el mercado filtrando por tecnología, capital y tamaño.</div></div></div>""", unsafe_allow_html=True)
        if c1.button("Ir al Explorador ➔", key="btn_home_filter", use_container_width=True):
            navigate_to('explorer')
            st.rerun()
    with c2:
        st.markdown("""<div class="feature-card"><div><span class="feature-icon">🤝</span><div class="feature-title">Profesionales</div><div class="feature-desc">Busca directamente a personas clave en nuestra base de datos.</div></div></div>""", unsafe_allow_html=True)
        if c2.button("Buscar Personas ➔", key="btn_home_prof", use_container_width=True):
            st.info("En desarrollo.")
    with c3:
        st.markdown("""<div class="feature-card"><div><span class="feature-icon">🎯</span><div class="feature-title">Mis Bingos</div><div class="feature-desc">Gestiona tus oportunidades y tratos cerrados.</div></div></div>""", unsafe_allow_html=True)
        c3.button("Ver mis Oportunidades ➔", disabled=True, use_container_width=True)

# ----------------- EXPLORADOR (MOBILE FRIENDLY) -----------------
elif st.session_state.page == 'explorer':
    st.title("🚀 Explorador de Empresas")
    st.markdown("Usa los filtros del menú lateral para encontrar tu cliente ideal.")
    
    df_show = df_main.copy()
    
    # Aplicación de Filtros
    if f_nombre: df_show = df_show[df_show['Nombre'].astype(str).str.contains(f_nombre, case=False, na=False)]
    if f_provincia: df_show = df_show[df_show['provincia'].isin(f_provincia)]
    if f_patentes == "Sí": df_show = df_show[df_show['patentes'] > 0]
    elif f_patentes == "No": df_show = df_show[df_show['patentes'] == 0]

    pe_negatives = ['ninguno', 'no identificado', 'sin datos', 'n/a', 'nan', '']
    if f_pe != "Todos":
        has_pe = ~df_show['private_equity_firmas'].astype(str).str.lower().str.strip().isin(pe_negatives)
        has_pe = has_pe & ~df_show['private_equity_firmas'].astype(str).str.lower().str.contains('ninguno', na=False)
        if f_pe == "Sí": df_show = df_show[has_pe]
        else: df_show = df_show[~has_pe]
    
    if f_ia != "Todos":
        no_ai_mask = (
            df_show['usa_inteligencia_artificial'].astype(str).str.strip().str.upper().str.startswith('NO') |
            df_show['usa_inteligencia_artificial'].astype(str).str.contains('No hay evidencia', case=False, na=False) |
            df_show['usa_inteligencia_artificial'].astype(str).str.contains('Sin datos', case=False, na=False)
        )
        if f_ia == "Sí": df_show = df_show[~no_ai_mask]
        else: df_show = df_show[no_ai_mask]

    # --- LÓGICA DE PAGINACIÓN ---
    total_items = len(df_show)
    total_pages = math.ceil(total_items / ITEMS_PER_PAGE)
    if st.session_state.current_page >= total_pages: st.session_state.current_page = 0
    if st.session_state.current_page < 0: st.session_state.current_page = 0
        
    start_idx = st.session_state.current_page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    df_page = df_show.iloc[start_idx:end_idx]

    # Barra de resultados elegante
    st.markdown(f"""
        <div class="results-bar">
            <div>🎯 <b>{total_items}</b> empresas encontradas</div>
            <div style="font-size: 0.9rem;">Página {st.session_state.current_page + 1} de {max(1, total_pages)}</div>
        </div>
    """, unsafe_allow_html=True)
    
    if not df_page.empty:
        # --- LISTADO RESPONSIVE USANDO EXPANDERS ---
        for index, row in df_page.iterrows():
            nombre = row['Nombre']
            provincia = capitalize_first_letter(get_val(row, 'provincia'))
            with st.expander(f"🏢 **{nombre}** ({provincia})"):
                
                # Métricas clave en 3 columnas
                c1, c2, c3 = st.columns(3)
                c1.metric("Empleados", clean_number_format(row['numero_empleados']))
                c2.metric("Ventas Est.", clean_number_format(get_val(row, 'ventas_estimado')))
                pat = str(row.get('patentes', 0))
                c3.metric("Patentes", pat, delta="Innovador" if int(pat)>0 else None, delta_color="off")

                st.write("") # Espacio
                # Botón de acción full width
                if st.button("➕ Más detalles", key=f"btn_{index}", use_container_width=True):
                    select_company(row['Nombre'])
                    st.rerun()
            
        # --- CONTROLES DE PAGINACIÓN ---
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

# ----------------- DETALLE -----------------
elif st.session_state.page == 'detail':
    selected_empresa = st.session_state.selected_empresa
    row_data = df_main[df_main['Nombre'] == selected_empresa]
    
    if not row_data.empty:
        r = row_data.iloc[0]
        
        # Cabecera Limpia
        st.markdown(f'<div class="main-header">🏢 {get_val(r, "Nombre")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sub-header">{capitalize_first_letter(get_val(r, "provincia"))} | {get_val(r, "web_oficial")}</div>', unsafe_allow_html=True)
        
        # 1. KPIs Principales
        c1, c2, c3 = st.columns(3)
        
        v_raw = get_val(r, "conclusion_sueldo_80k")
        v_color = "#2E7D32" if "VIABLE" in v_raw.upper() else "#C62828" if "DIFICIL" in v_raw.upper() else "#1F4E79"
        v_text = "VIABLE" if "VIABLE" in v_raw.upper() else "DIFÍCIL" if "DIFICIL" in v_raw.upper() else "NEUTRO"
        
        # Usando st.markdown para tarjetas personalizadas
        c1.markdown(f"""<div class="kpi-card"><div class="kpi-value">{get_val(r, "veredicto_final")}</div><div class="kpi-label">CLASIFICACIÓN BINGO</div></div>""", unsafe_allow_html=True)
        c2.markdown(f"""<div class="kpi-card"><div class="kpi-value" style="color:{v_color}">{v_text}</div><div class="kpi-label">VIABILIDAD SALARIAL (>80k)</div></div>""", unsafe_allow_html=True)
        c3.markdown(f"""<div class="kpi-card"><div class="kpi-value">{clean_number_format(get_val(r, 'numero_empleados'))}</div><div class="kpi-label">EMPLEADOS</div></div>""", unsafe_allow_html=True)

        st.write("")
        
        # 2. DATOS CLAVE Y NEGOCIO
        st.markdown('<div class="section-title">Datos Clave & Negocio</div>', unsafe_allow_html=True)
        
        c_izq, c_der = st.columns([1, 2])
        with c_izq:
            # Tabla lateral pequeña
            render_table(pd.DataFrame({
                "Concepto": ["Ventas Estimadas", "Patentes", "Año Constitución"],
                "Valor": [clean_number_format(get_val(r, 'ventas_estimado')), str(r.get('patentes', 0)), get_val(r, 'ano_constitucion')]
            }))
        with c_der:
             st.markdown(f"""
                <div class="content-box" style="margin-bottom: 15px;"><span class="box-header">Actividad</span>{get_val(r, 'actividad_resumen')}</div>
                <div class="content-box"><span class="box-header">Propiedad y Fondos</span><b>Accionistas:</b> {get_val(r, 'propiedad_accionistas')}<br><br><b>Private Equity:</b> {get_val(r, 'private_equity_firmas')}</div>
            """, unsafe_allow_html=True)

        # 3. TECH STACK
        st.markdown('<div class="section-title">Tecnología</div>', unsafe_allow_html=True)
        c_tech1, c_tech2 = st.columns(2)
        c_tech1.markdown(f"""<div class="content-box"><span class="box-header">Equipo & Liderazgo</span><b>CTO/Responsable:</b> {get_val(r, 'cto_actual')}<br><b>Tamaño Equipo Ing.:</b> {get_val(r, 'tamano_ing')}</div>""", unsafe_allow_html=True)
        c_tech2.markdown(f"""<div class="content-box"><span class="box-header">Stack & Cloud</span><b>Perfil Técnico:</b> {get_val(r, 'perfil_txt')}<br><b>Cloud:</b> {get_val(r, 'plataforma_cloud')}</div>""", unsafe_allow_html=True)
        
        st.write("")
        ia_val = get_val(r, 'usa_inteligencia_artificial')
        ia_icon = "🧠" if "SÍ" in ia_val.upper() else "⚪"
        st.markdown(f"""<div class="content-box" style="background-color: #f8f9fa;"><span class="box-header">{ia_icon} Uso de Inteligencia Artificial</span>{ia_val}</div>""", unsafe_allow_html=True)

        
        # 4. ALUMNI (NETWORKING)
        st.markdown('<div class="section-title">Networking (Alumni)</div>', unsafe_allow_html=True)
        col_matriz = next((c for c in df_alumni.columns if 'informa' in c.lower()), None)
        
        if col_matriz and not df_alumni.empty:
            match = df_alumni[df_alumni[col_matriz].astype(str).str.strip() == str(selected_empresa).strip()]
            if match.empty:
                 match = df_alumni[df_alumni[col_matriz].astype(str).str.contains(re.escape(str(selected_empresa).strip()), case=False, na=False)]

            if not match.empty:
                st.success(f"✅ Se han encontrado {len(match)} contactos en esta empresa.")
                
                # Preparar datos para el resumen ordenado
                df_summary = match.copy()
                if 'jerarquía' in df_summary.columns:
                    # Definir orden específico
                    hierarchy_order = ['Top Management', 'Middle Management', 'Entry Level', 'Otros']
                    # Normalizar datos para que coincidan con las categorías
                    df_summary['jerarquía'] = df_summary['jerarquía'].fillna('Otros').astype(str)
                    # Crear columna categórica ordenada
                    df_summary['jerarquía_cat'] = pd.Categorical(
                        df_summary['jerarquía'], 
                        categories=hierarchy_order, 
                        ordered=True
                    )
                
                t1, t2 = st.tabs(["📊 Resumen por Nivel", "📋 Lista Detallada"])
                
                with t1:
                    if 'jerarquía_cat' in df_summary.columns:
                        # Contar y ordenar por el índice categórico
                        summary_counts = df_summary['jerarquía_cat'].value_counts().sort_index()
                        
                        # Crear HTML personalizado para la tabla resumen con badges
                        html_summary = '<table class="custom-table" style="width:100%"><thead><tr><th>Categoría</th><th>Total</th></tr></thead><tbody>'
                        for cat, count in summary_counts.items():
                            if count > 0:
                                badge_class = "badge-top" if "Top" in cat else "badge-mid" if "Middle" in cat else "badge-entry"
                                html_summary += f'<tr><td><span class="{badge_class}">{cat}</span></td><td style="font-weight:bold;">{count}</td></tr>'
                        html_summary += '</tbody></table>'
                        st.markdown(html_summary, unsafe_allow_html=True)
                    else:
                        st.info("Datos de jerarquía no disponibles para resumen.")
                
                with t2:
                    # Mostrar tabla detallada, ordenando primero por la jerarquía
                    if 'jerarquía_cat' in df_summary.columns:
                         df_summary = df_summary.sort_values('jerarquía_cat')

                    cols_view = ['Nombre', 'Cargo', 'jerarquía', 'función', 'url_linkedin']
                    cols_exist = [c for c in cols_view if c in df_summary.columns]
                    # Usar el dataframe original 'match' si no se pudo crear la categoría, o el ordenado 'df_summary'
                    render_table(df_summary[cols_exist] if 'jerarquía_cat' in df_summary.columns else match[cols_exist])
            else:
                st.info("No hay contactos alumni registrados en esta empresa.")
        else:
            st.info("No hay datos de alumni cargados.")
    else:
        st.error("Error al cargar los datos de la empresa.")