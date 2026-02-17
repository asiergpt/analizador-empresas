import streamlit as st
import pandas as pd
import re
import io
import os

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

# --- 1. GESTIÓN DE ESTILOS (CSS) ---
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; font-size: 16px; color: #2c3e50; }
    
    .section-title { color: #1F4E79; font-size: 1.8rem; font-weight: 700; margin-top: 2.5rem; border-bottom: 4px solid #DAE9F7; padding-bottom: 5px; }
    .kpi-card { background-color: #DAE9F7; border-radius: 12px; padding: 20px; text-align: center; border: 2px solid #1F4E79; box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: 100%; display: flex; flex-direction: column; justify-content: center; }
    .kpi-value { color: #1F4E79; font-size: 2rem; font-weight: 800; line-height: 1.2; }
    .kpi-label { font-size: 0.85rem; text-transform: uppercase; font-weight: 700; color: #1F4E79; margin-top: 5px; letter-spacing: 1px; }

    .tech-hero { background-color: #1F4E79; color: white; border-radius: 10px; padding: 20px; text-align: center; box-shadow: 0 4px 10px rgba(31, 78, 121, 0.2); }
    .tech-hero-label { font-size: 0.85rem; text-transform: uppercase; opacity: 0.9; font-weight: 600; margin-bottom: 5px; }
    .tech-hero-val { font-size: 1.3rem; font-weight: 700; }

    .tech-card { background-color: white; border: 1px solid #e0e0e0; border-top: 4px solid #1F4E79; border-radius: 10px; padding: 20px; height: 100%; box-shadow: 0 2px 8px rgba(0,0,0,0.05); transition: transform 0.2s; }
    .tech-card:hover { transform: translateY(-3px); }
    .tech-icon { font-size: 1.8rem; margin-bottom: 10px; display: block; }
    .tech-title { color: #1F4E79; font-weight: 700; font-size: 0.95rem; margin-bottom: 8px; text-transform: uppercase; }
    .tech-text { font-size: 1rem; color: #444; line-height: 1.4; }

    .custom-table { width: 100%; border-collapse: separate; border-spacing: 0; min-width: 500px; border-radius: 8px; overflow: hidden; border: 1px solid #eee; }
    .custom-table th { background-color: #1F4E79; color: white; padding: 12px; text-align: center; font-weight: 600; }
    .custom-table td { border-bottom: 1px solid #f0f0f0; padding: 12px; text-align: center; color: #333; }
    .table-container { overflow-x: auto; box-shadow: 0 2px 5px rgba(0,0,0,0.03); border-radius: 8px; margin-bottom: 20px; }

    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
    .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px; }
    @media (max-width: 768px) { .grid-2, .grid-3 { grid-template-columns: 1fr; } }
    
    .box-header { color: #1F4E79; font-weight: 700; font-size: 1.2rem; margin-bottom: 10px; border-bottom: 2px solid #DAE9F7; display: block; }
    .content-box { background-color: white; border: 1px solid #dcdcdc; border-radius: 12px; padding: 20px; height: 100%; }
    
    .hero-title { color: #1F4E79; font-size: 4rem; font-weight: 900; text-align: center; margin-bottom: 5px; letter-spacing: -1px; }
    .hero-subtitle { color: #555; font-size: 1.5rem; text-align: center; margin-bottom: 50px; font-weight: 300; }
    
    .feature-card { background-color: white; border-radius: 12px; padding: 25px; text-align: center; border: 1px solid #eee; box-shadow: 0 4px 12px rgba(0,0,0,0.05); transition: transform 0.3s ease; height: 100%; display: flex; flex-direction: column; justify-content: space-between; }
    .feature-card:hover { transform: translateY(-5px); border-color: #DAE9F7; }
    .feature-icon { font-size: 3rem; margin-bottom: 15px; display: block; }
    .feature-title { color: #1F4E79; font-weight: 700; font-size: 1.2rem; margin-bottom: 10px; }
    .feature-desc { color: #666; font-size: 1rem; line-height: 1.5; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

inject_css()

# --- 2. UTILIDADES ---
def clean_number_format(val):
    if pd.isna(val): return "-"
    # Limpiamos todo excepto dígitos para visualización
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
    st.markdown(f'<div class="table-container">{df.to_html(index=False, border=0, classes="custom-table")}</div>', unsafe_allow_html=True)

# --- 3. DATOS MOCK Y CARGA ---
def generate_mock_data():
    data_emp = {
        'Nombre': ['Tech Solutions SL', 'Industrias Norte SA', 'Innovación Global', 'Caf', 'Idom', 'Gestamp', 'Solarpack'],
        'provincia': ['Gipuzkoa', 'Bizkaia', 'Araba', 'Gipuzkoa', 'Bizkaia', 'Bizkaia', 'Bizkaia'],
        'veredicto_final': ['TOP TIER', 'STANDARD', 'GROWTH', 'TOP TIER', 'TOP TIER', 'TOP TIER', 'GROWTH'],
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
        'jerarquía': ['Middle', 'Top', 'Middle', 'Top', 'Entry'],
        'funcion': ['Ingeniería', 'Tecnología', 'Producto', 'Ingeniería', 'Obras'],
        'url_linkedin': ['#', '#', '#', '#', '#']
    }
    return pd.DataFrame(data_emp), pd.DataFrame(data_alum)

@st.cache_data
def load_data():
    df_main = None
    df_alumni = pd.DataFrame()
    
    # 1. EMPRESAS
    # Intentamos cargar con varios nombres posibles por si acaso
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
        except Exception:
            pass

    # Fallback a Mock
    if df_main is None or df_main.empty:
        df_main, df_alumni_mock = generate_mock_data()
        if df_alumni.empty: df_alumni = df_alumni_mock

    # --- LIMPIEZA Y PREPARACIÓN DE DATOS ---
    if not df_main.empty:
        # Limpieza Empleados
        if 'numero_empleados' in df_main.columns:
            def clean_to_int(x):
                s = re.sub(r'[^\d]', '', str(x))
                return int(s) if s else 0
            df_main['numero_empleados'] = df_main['numero_empleados'].apply(clean_to_int)
        else:
            df_main['numero_empleados'] = 0

        # Limpieza Patentes (asegurar numérico)
        if 'patentes' in df_main.columns:
            df_main['patentes'] = pd.to_numeric(df_main['patentes'], errors='coerce').fillna(0).astype(int)
        else:
            df_main['patentes'] = 0

        # Limpieza Campos de Texto Clave
        if 'private_equity_firmas' not in df_main.columns:
            df_main['private_equity_firmas'] = "Ninguno"
        else:
            df_main['private_equity_firmas'] = df_main['private_equity_firmas'].fillna("Ninguno")

        if 'usa_inteligencia_artificial' not in df_main.columns:
            df_main['usa_inteligencia_artificial'] = "NO"
        else:
            df_main['usa_inteligencia_artificial'] = df_main['usa_inteligencia_artificial'].fillna("NO")
            
    # Limpieza Alumni
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

def navigate_to(page):
    st.session_state.page = page
    if page == 'explorer':
        st.session_state.selected_empresa = None

def select_company(empresa_nombre):
    st.session_state.selected_empresa = empresa_nombre
    st.session_state.page = 'detail'

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
        
        # 1. Nombre
        f_nombre = st.text_input("Nombre Empresa")
        
        # 2. Provincia
        provs = sorted(df_main['provincia'].dropna().unique().tolist())
        f_provincia = st.multiselect("Provincia", provs)
        
        # 3. Patentes (Sí/No)
        f_patentes = st.radio("¿Tiene Patentes?", ["Todos", "Sí", "No"], horizontal=True)

        # 4. Private Equity (Sí/No)
        f_pe = st.radio("¿Tiene Private Equity?", ["Todos", "Sí", "No"], horizontal=True)
        
        # 5. Inteligencia Artificial (Sí/No)
        f_ia = st.radio("¿Usa Inteligencia Artificial?", ["Todos", "Sí", "No"], horizontal=True)

    elif st.session_state.page == 'detail':
        st.header("Empresa Seleccionada")
        st.success(f"🏢 {st.session_state.selected_empresa}")
        
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

    # KPIs
    m1, m2, m3, m4 = st.columns([1, 2, 2, 1])
    with m2:
        st.markdown(f'<div class="kpi-card" style="padding:15px;"><div class="kpi-value">{len(df_main)}</div><div class="kpi-label">EMPRESAS</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="kpi-card" style="padding:15px;"><div class="kpi-value">{df_alumni["Nombre"].nunique() if not df_alumni.empty else 0}</div><div class="kpi-label">CONTACTOS</div></div>', unsafe_allow_html=True)

    st.write("")
    st.write("")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
            <div class="feature-card">
                <div>
                    <span class="feature-icon">🏢</span>
                    <div class="feature-title">Filtra Empresas</div>
                    <div class="feature-desc">Explora el mercado filtrando por tecnología, capital y tamaño.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if c1.button("Ir al Explorador ➔", key="btn_home_filter", use_container_width=True):
            navigate_to('explorer')
            st.rerun()

    with c2:
        st.markdown("""
            <div class="feature-card">
                <div>
                    <span class="feature-icon">🤝</span>
                    <div class="feature-title">Profesionales</div>
                    <div class="feature-desc">Busca directamente a personas clave en nuestra base de datos.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if c2.button("Buscar Personas ➔", key="btn_home_prof", use_container_width=True):
            st.info("Funcionalidad en desarrollo. Usa el Explorador de Empresas por ahora.")

    with c3:
        st.markdown("""
            <div class="feature-card">
                <div>
                    <span class="feature-icon">🎯</span>
                    <div class="feature-title">Mis Bingos</div>
                    <div class="feature-desc">Gestiona tus oportunidades y tratos cerrados.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        c3.button("Ver mis Oportunidades ➔", disabled=True, use_container_width=True)

# ----------------- EXPLORADOR -----------------
elif st.session_state.page == 'explorer':
    st.title("🚀 Explorador de Empresas")
    st.markdown("Usa los filtros del menú lateral para encontrar tu cliente ideal.")
    
    df_show = df_main.copy()
    
    # 1. Filtro Nombre
    if f_nombre:
        df_show = df_show[df_show['Nombre'].astype(str).str.contains(f_nombre, case=False, na=False)]
    
    # 2. Filtro Provincia
    if f_provincia:
        df_show = df_show[df_show['provincia'].isin(f_provincia)]
    
    # 3. Filtro Patentes
    if f_patentes == "Sí":
        df_show = df_show[df_show['patentes'] > 0]
    elif f_patentes == "No":
        df_show = df_show[df_show['patentes'] == 0]

    # 4. Filtro Private Equity
    # Definimos qué consideramos "NO tener PE" (valores vacíos, nulos, o explícitamente negativos)
    pe_negatives = ['ninguno', 'no identificado', 'sin datos', 'n/a', 'nan', '']
    if f_pe != "Todos":
        # Creamos una máscara booleana temporal
        has_pe = ~df_show['private_equity_firmas'].astype(str).str.lower().str.strip().isin(pe_negatives)
        # Filtramos también aquellos que contienen "ninguno" en frases largas
        has_pe = has_pe & ~df_show['private_equity_firmas'].astype(str).str.lower().str.contains('ninguno', na=False)
        
        if f_pe == "Sí":
            df_show = df_show[has_pe]
        else:
            df_show = df_show[~has_pe]
    
    # 5. Filtro IA
    if f_ia != "Todos":
        # Definimos qué es "NO usar IA" (empieza por NO o contiene frases negativas comunes)
        no_ai_mask = (
            df_show['usa_inteligencia_artificial'].astype(str).str.strip().str.upper().str.startswith('NO') |
            df_show['usa_inteligencia_artificial'].astype(str).str.contains('No hay evidencia', case=False, na=False) |
            df_show['usa_inteligencia_artificial'].astype(str).str.contains('Sin datos', case=False, na=False)
        )
        
        if f_ia == "Sí":
            df_show = df_show[~no_ai_mask]
        else:
            df_show = df_show[no_ai_mask]

    st.write(f"**Resultados:** {len(df_show)} empresas encontradas.")
    
    if not df_show.empty:
        # Cabecera simulada
        cols = st.columns([3, 1, 1, 1, 1, 1.5])
        cols[0].markdown("**Empresa**")
        cols[1].markdown("**Provincia**")
        cols[2].markdown("**Empleados**")
        cols[3].markdown("**Patentes**")
        cols[4].markdown("**Ventas Est.**")
        cols[5].markdown("**Acción**")
        st.divider()
        
        # Paginación simple si hay muchos resultados
        max_rows = 50
        if len(df_show) > max_rows:
            st.warning(f"Mostrando los primeros {max_rows} resultados de {len(df_show)}. Refina tu búsqueda.")
            df_show = df_show.head(max_rows)

        for index, row in df_show.iterrows():
            c = st.columns([3, 1, 1, 1, 1, 1.5])
            c[0].write(f"**{row['Nombre']}**")
            c[1].write(get_val(row, 'provincia'))
            c[2].write(clean_number_format(row['numero_empleados']))
            c[3].write(str(row.get('patentes', 0)))
            c[4].write(clean_number_format(get_val(row, 'ventas_estimado')))
            
            if c[5].button("🔍 Ver 360°", key=f"btn_{index}"):
                select_company(row['Nombre'])
                st.rerun()
            st.markdown("<hr style='margin: 5px 0; opacity: 0.2;'>", unsafe_allow_html=True)
    else:
        st.warning("No hay empresas que coincidan con estos filtros.")

# ----------------- DETALLE -----------------
elif st.session_state.page == 'detail':
    selected_empresa = st.session_state.selected_empresa
    row_data = df_main[df_main['Nombre'] == selected_empresa]
    
    if not row_data.empty:
        r = row_data.iloc[0]
        
        c_title, c_btn = st.columns([4,1])
        c_title.title(f"🏢 {get_val(r, 'Nombre')}")
        
        # 1. RESUMEN
        st.markdown('<div class="section-title">Resumen</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="kpi-card"><div class="kpi-value">{capitalize_first_letter(get_val(r, "provincia"))}</div><div class="kpi-label">UBICACIÓN</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi-card"><div class="kpi-value">{get_val(r, "veredicto_final")}</div><div class="kpi-label">CLASIFICACIÓN</div></div>', unsafe_allow_html=True)
        
        v_raw = get_val(r, "conclusion_sueldo_80k")
        v_color = "#2E7D32" if "VIABLE" in v_raw.upper() else "#C62828" if "DIFICIL" in v_raw.upper() else "#1F4E79"
        v_text = "VIABLE" if "VIABLE" in v_raw.upper() else "DIFÍCIL" if "DIFICIL" in v_raw.upper() else "NEUTRO"
        
        c3.markdown(f'<div class="kpi-card"><div class="kpi-value" style="color:{v_color}">{v_text}</div><div class="kpi-label">VIABILIDAD >80k</div></div>', unsafe_allow_html=True)
        
        st.write("")
        render_table(pd.DataFrame({
            "Ventas Est.": [clean_number_format(get_val(r, 'ventas_estimado'))],
            "Empleados": [clean_number_format(get_val(r, 'numero_empleados'))],
            "Patentes": [str(r.get('patentes', 0))],
            "Año Const.": [get_val(r, 'ano_constitucion')],
            "Web": [get_val(r, 'web_oficial')]
        }))

        # 2. NEGOCIO
        st.markdown('<div class="section-title">Negocio</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="grid-2">
            <div class="content-box"><span class="box-header">Actividad</span><span class="box-text">{get_val(r, 'actividad_resumen')}</span></div>
            <div class="content-box"><span class="box-header">Propiedad</span><span class="box-text"><b>Accionistas:</b> {get_val(r, 'propiedad_accionistas')}<br><br><b>PE:</b> {get_val(r, 'private_equity_firmas')}</span></div>
        </div>""", unsafe_allow_html=True)

        # 3. TECH
        st.markdown('<div class="section-title">Tecnología</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="grid-2">
            <div class="tech-hero"><div class="tech-hero-label">CTO / Responsable</div><div class="tech-hero-val">{get_val(r, 'cto_actual')}</div></div>
            <div class="tech-hero"><div class="tech-hero-label">Equipo Ingeniería</div><div class="tech-hero-val">{get_val(r, 'tamano_ing')}</div></div>
        </div>
        <div class="grid-3">
            <div class="tech-card"><span class="tech-icon">🧠</span><div class="tech-title">IA & Automatización</div><div class="tech-text">{get_val(r, 'usa_inteligencia_artificial')}</div></div>
            <div class="tech-card"><span class="tech-icon">☁️</span><div class="tech-title">Infraestructura</div><div class="tech-text">{get_val(r, 'plataforma_cloud')}</div></div>
            <div class="tech-card"><span class="tech-icon">💻</span><div class="tech-title">Stack Técnico</div><div class="tech-text">{get_val(r, 'perfil_txt')}</div></div>
        </div>""", unsafe_allow_html=True)
        
        # 4. ALUMNI
        st.markdown('<div class="section-title">Networking (Alumni)</div>', unsafe_allow_html=True)
        col_matriz = next((c for c in df_alumni.columns if 'informa' in c.lower()), None)
        
        if col_matriz and not df_alumni.empty:
            match = df_alumni[df_alumni[col_matriz].astype(str).str.strip() == str(selected_empresa).strip()]
            if match.empty:
                 match = df_alumni[df_alumni[col_matriz].astype(str).str.contains(re.escape(str(selected_empresa).strip()), case=False, na=False)]

            if not match.empty:
                st.success(f"✅ Se han encontrado {len(match)} contactos en esta empresa.")
                cols_view = ['Nombre', 'Cargo', 'jerarquía', 'función', 'url_linkedin']
                cols_exist = [c for c in cols_view if c in match.columns]
                render_table(match[cols_exist])
            else:
                st.info("No hay contactos alumni registrados en esta empresa.")
        else:
            st.info("No hay datos de alumni cargados.")
    else:
        st.error("Error al cargar los datos de la empresa.")