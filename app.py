import streamlit as st
import pandas as pd
import re
import io
import os
# Try import cryptography, handle if missing for demo purposes
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
    
    /* Títulos */
    .section-title { color: #1F4E79; font-size: 1.8rem; font-weight: 700; margin-top: 2.5rem; border-bottom: 4px solid #DAE9F7; padding-bottom: 5px; }

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

    /* Profile Card */
    .profile-card { background-color: #f8f9fa; border-left: 5px solid #1F4E79; padding: 15px; border-radius: 8px; margin-top: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .profile-name { font-weight: 800; color: #1F4E79; font-size: 1.1rem; }
    .profile-role { font-size: 0.9rem; color: #666; font-style: italic; margin-bottom: 5px; }
    .profile-company { font-weight: 600; color: #333; font-size: 0.9rem; border-top: 1px solid #ddd; padding-top: 5px; }

    /* Tablas */
    .custom-table { width: 100%; border-collapse: separate; border-spacing: 0; min-width: 500px; border-radius: 8px; overflow: hidden; border: 1px solid #eee; }
    .custom-table th { background-color: #1F4E79; color: white; padding: 12px; text-align: center; font-weight: 600; }
    .custom-table td { border-bottom: 1px solid #f0f0f0; padding: 12px; text-align: center; color: #333; }
    .table-container { overflow-x: auto; box-shadow: 0 2px 5px rgba(0,0,0,0.03); border-radius: 8px; margin-bottom: 20px; }

    /* Layouts */
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
    .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px; }
    @media (max-width: 768px) { .grid-2, .grid-3 { grid-template-columns: 1fr; } }
    
    .box-header { color: #1F4E79; font-weight: 700; font-size: 1.2rem; margin-bottom: 10px; border-bottom: 2px solid #DAE9F7; display: block; }
    .content-box { background-color: white; border: 1px solid #dcdcdc; border-radius: 12px; padding: 20px; height: 100%; }
    
    /* Home & Search */
    .hero-title { color: #1F4E79; font-size: 4rem; font-weight: 900; text-align: center; margin-bottom: 5px; letter-spacing: -1px; }
    .hero-subtitle { color: #555; font-size: 1.5rem; text-align: center; margin-bottom: 50px; font-weight: 300; }
    .feature-card { background-color: white; border-radius: 12px; padding: 25px; text-align: center; border: 1px solid #eee; box-shadow: 0 4px 12px rgba(0,0,0,0.05); transition: transform 0.3s ease; height: 100%; }
    .feature-card:hover { transform: translateY(-5px); border-color: #DAE9F7; }
    .feature-icon { font-size: 3rem; margin-bottom: 15px; display: block; }
    .feature-title { color: #1F4E79; font-weight: 700; font-size: 1.2rem; margin-bottom: 10px; }
    .feature-desc { color: #666; font-size: 1rem; line-height: 1.5; }
    
    .search-alert { background-color: #e3f2fd; border-left: 4px solid #1F4E79; padding: 10px; border-radius: 4px; color: #0d47a1; font-size: 0.9rem; margin-bottom: 10px; }
    .search-count { font-weight: 700; }
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
    st.markdown(f'<div class="table-container">{df.to_html(index=False, border=0, classes="custom-table")}</div>', unsafe_allow_html=True)

# --- 3. GENERADOR DE DATOS MOCK (PARA DEMO) ---
def generate_mock_data():
    """Genera datos falsos si no existen los archivos reales"""
    # Mock Empresas
    data_emp = {
        'Nombre': ['Tech Solutions SL', 'Industrias Norte SA', 'Innovación Global', 'Caf'],
        'provincia': ['Gipuzkoa', 'Bizkaia', 'Araba', 'Gipuzkoa'],
        'veredicto_final': ['TOP TIER', 'STANDARD', 'GROWTH', 'TOP TIER'],
        'conclusion_sueldo_80k': ['Es VIABLE pagar >80k', 'DIFICIL pagar >80k', 'Es VIABLE', 'VIABLE'],
        'ventas_estimado': [5000000, 12000000, 2500000, 450000000],
        'numero_empleados': [45, 120, 25, 3000],
        'ano_constitucion': [2010, 1995, 2018, 1950],
        'web_oficial': ['www.techsol.com', 'www.norte.com', 'www.innoglo.com', 'www.caf.net'],
        'actividad_resumen': ['Desarrollo de software SaaS', 'Manufactura pesada', 'Consultoría IA', 'Trenes'],
        'propiedad_accionistas': ['Fundadores (80%)', 'Familia (100%)', 'VC Fund', 'Publica'],
        'private_equity_firmas': ['-', '-', 'Sequoia', '-'],
        'cto_actual': ['Jon Doe', 'Mikel Smith', 'Ana García', 'Txomin Perez'],
        'tamano_ing': ['15 engineers', '5 engineers', '10 engineers', '200+ engineers'],
        'usa_inteligencia_artificial': ['Sí, Generativa', 'No', 'Sí, Core', 'Sí, Predictiva'],
        'plataforma_cloud': ['AWS', 'On-premise', 'Azure', 'Hybrid'],
        'perfil_txt': ['Python, React, Kubernetes', 'Java, Oracle', 'Python, PyTorch', 'C++, Embedded']
    }
    
    # Mock Alumni
    data_alum = {
        'Nombre': ['Iker Dorronsoro', 'Amaia Lopez', 'Unai Etxebarria', 'Maria Sanz'],
        'Cargo': ['Senior Backend', 'CTO', 'Product Manager', 'Director de Ingeniería'],
        'nombre_matriz_einforma': ['Tech Solutions SL', 'Tech Solutions SL', 'Industrias Norte SA', 'Caf'],
        'jerarquía': ['Middle Management', 'Top Management', 'Middle Management', 'Top Management'],
        'funcion': ['Ingeniería', 'Tecnología', 'Producto', 'Ingeniería'],
        'url_linkedin': ['#', '#', '#', '#']
    }
    
    return pd.DataFrame(data_emp), pd.DataFrame(data_alum)

# --- 4. CARGA DE DATOS ---
@st.cache_data
def load_data():
    df_main = None
    df_alumni = pd.DataFrame()
    files_missing = False

    # 1. EMPRESAS
    file_empresas = 'euskadi_navarra_dollar.csv'
    if os.path.exists(file_empresas):
        try: df_main = pd.read_csv(file_empresas, sep=';', encoding='utf-8')
        except: 
            try: df_main = pd.read_csv(file_empresas, sep=';', encoding='latin-1')
            except: pass
    
    # 2. ALUMNI (Encriptado)
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
        except Exception as e:
            st.sidebar.error(f"Error desencriptando: {e}")
    
    # --- FALLBACK A MOCK DATA SI FALLA LA CARGA ---
    if df_main is None or df_main.empty:
        files_missing = True
        df_main, df_alumni_mock = generate_mock_data()
        # Solo usamos el mock de alumni si el real falló
        if df_alumni.empty:
            df_alumni = df_alumni_mock
    
    # Limpieza básica de Alumni
    if not df_alumni.empty:
        df_alumni.columns = [c.strip() for c in df_alumni.columns]
        # Normalizar columnas clave
        cols_map = {'funcion': 'función', 'jerarquia': 'jerarquía'}
        df_alumni.rename(columns=cols_map, inplace=True)
        
        cols_to_format = ['Nombre', 'Cargo', 'jerarquía', 'función']
        for col in cols_to_format:
            c = next((x for x in df_alumni.columns if x.lower() == col.lower()), None)
            if c: df_alumni[c] = df_alumni[c].astype(str).str.strip().str.title()
            
        c_matriz = next((x for x in df_alumni.columns if 'informa' in x.lower()), 'nombre_matriz_einforma')
        if c_matriz in df_alumni.columns: 
            df_alumni[c_matriz] = df_alumni[c_matriz].astype(str).str.strip()
    
    return df_main, df_alumni, files_missing

df_main, df_alumni, using_mock_data = load_data()

# --- 5. INTERFAZ: SIDEBAR ---
if using_mock_data:
    st.sidebar.warning("⚠️ **Modo Demo**: No se encontraron los archivos originales (`.csv/.enc`). Se están usando datos generados.")

st.sidebar.header("🔍 Buscador")
tab_empresa, tab_profesional = st.sidebar.tabs(["🏢 Empresa", "🧑‍💼 Profesional"])

# Gestión de Estado
if 'selected_empresa' not in st.session_state: st.session_state['selected_empresa'] = None

with tab_empresa:
    st.write("")
    
    # 1. Input del usuario (Búsqueda por texto)
    search_term_emp = st.text_input("Nombre Empresa", placeholder="Ej: Caf, Idom...")
    
    # 2. Filtro opcional de provincia (menos intrusivo)
    provincias = ["Todas"] + sorted(df_main['provincia'].dropna().unique().tolist())
    with st.expander("Filtrar por Provincia (Opcional)"):
        selected_provincia = st.selectbox("Selecciona:", provincias, label_visibility="collapsed")

    # 3. Lógica de Filtrado
    df_f = df_main.copy()
    
    # Aplicar filtro de provincia si no es todas
    if selected_provincia != "Todas": 
        df_f = df_f[df_f['provincia'] == selected_provincia]
    
    # Aplicar búsqueda por texto
    if search_term_emp: 
        df_f = df_f[df_f['Nombre'].astype(str).str.contains(search_term_emp, case=False, na=False)]

    # 4. Resultados Reactivos
    lista_res = sorted(df_f['Nombre'].unique().tolist())
    match_count_emp = len(lista_res)
    
    sel_emp = None

    if search_term_emp:
        if match_count_emp > 1:
            # Múltiples coincidencias
            st.markdown(f'<div class="search-alert">🔍 {match_count_emp} empresas encontradas.</div>', unsafe_allow_html=True)
            sel_emp = st.selectbox("Selecciona:", lista_res, index=None, placeholder="Elige empresa...")
            
            if sel_emp:
                if st.button("Ver Análisis", key="btn_emp_multi", use_container_width=True):
                    st.session_state['selected_empresa'] = sel_emp
                    st.rerun()

        elif match_count_emp == 1:
            # Coincidencia Única
            st.success("✅ Empresa encontrada")
            sel_emp = lista_res[0]
            # Mostramos input deshabilitado como confirmación visual
            st.text_input("Resultado:", value=sel_emp, disabled=True)
            
            if st.button("Ver Análisis", key="btn_emp_single", use_container_width=True):
                st.session_state['selected_empresa'] = sel_emp
                st.rerun()
        
        else:
            st.error("❌ No se encontraron empresas.")
    else:
        # Estado inicial (sin buscar nada)
        st.caption("Escribe para buscar...")

    st.write("")
    st.divider()
    if st.button("🏠 Volver al Inicio", type="secondary", use_container_width=True):
        st.session_state['selected_empresa'] = None
        st.rerun()

with tab_profesional:
    st.write("")
    if df_alumni.empty:
        st.warning("Base de datos de profesionales vacía.")
    else:
        col_nom = next((c for c in df_alumni.columns if c.lower() == 'nombre'), None)
        col_emp = next((c for c in df_alumni.columns if 'informa' in c.lower()), None)
        col_car = next((c for c in df_alumni.columns if c.lower() == 'cargo'), None)

        search_prof = st.text_input("Buscar Profesional:", placeholder="Ej: Dorronsoro")
        
        if search_prof and col_nom:
            mask = df_alumni[col_nom].astype(str).str.contains(search_prof, case=False, na=False)
            lista_prof = sorted(df_alumni[mask][col_nom].unique().tolist())
            match_count = len(lista_prof)

            sel_prof = None
            if match_count > 1:
                st.markdown(f'<div class="search-alert">🔍 {match_count} coincidencias.</div>', unsafe_allow_html=True)
                sel_prof = st.selectbox("Selecciona:", lista_prof, index=None)
            elif match_count == 1:
                st.success("✅ Contacto encontrado")
                sel_prof = lista_prof[0]
                st.text_input("Nombre", value=sel_prof, disabled=True)
            else:
                st.error("❌ No encontrado.")

            if sel_prof and col_emp:
                d = df_alumni[df_alumni[col_nom] == sel_prof].iloc[0]
                emp_p = d[col_emp]
                cargo_p = d[col_car] if col_car else "N/A"
                
                st.divider()
                st.markdown(f"""
                    <div class="profile-card">
                        <div class="profile-name">{sel_prof}</div>
                        <div class="profile-role">{cargo_p}</div>
                        <div class="profile-company">🏢 {emp_p}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Analizar {emp_p} ➔", key="go_prof", use_container_width=True):
                    st.session_state['selected_empresa'] = emp_p
                    st.rerun()

# --- 6. PANEL PRINCIPAL ---
selected_empresa = st.session_state['selected_empresa']

# Limpieza de selección nula
if str(selected_empresa).lower() in ['nan', 'none', '']: selected_empresa = None

if selected_empresa:
    # --- VISTA DETALLE EMPRESA ---
    
    # Buscar en Dataframe Principal
    row_data = df_main[df_main['Nombre'] == selected_empresa]
    if row_data.empty:
        # Intento fuzzy
        row_data = df_main[df_main['Nombre'].str.contains(re.escape(selected_empresa), case=False, na=False)]

    # CASO 1: EMPRESA ENCONTRADA EN DB FINANCIERA
    if not row_data.empty:
        r = row_data.iloc[0]
        st.title(f"🏢 {get_val(r, 'Nombre')}")
        
        # 1. RESUMEN
        st.markdown('<div class="section-title">Resumen</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="kpi-card"><div class="kpi-value">{capitalize_first_letter(get_val(r, "provincia"))}</div><div class="kpi-label">UBICACIÓN</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi-card"><div class="kpi-value">{get_val(r, "veredicto_final")}</div><div class="kpi-label">CLASIFICACIÓN</div></div>', unsafe_allow_html=True)
        
        v_raw = get_val(r, "conclusion_sueldo_80k")
        # Lógica simple para extraer color del veredicto
        v_color = "#2E7D32" if "VIABLE" in v_raw.upper() else "#C62828" if "DIFICIL" in v_raw.upper() else "#1F4E79"
        v_text = "VIABLE" if "VIABLE" in v_raw.upper() else "DIFÍCIL" if "DIFICIL" in v_raw.upper() else "NEUTRO"
        
        c3.markdown(f'<div class="kpi-card"><div class="kpi-value" style="color:{v_color}">{v_text}</div><div class="kpi-label">VIABILIDAD >80k</div></div>', unsafe_allow_html=True)
        
        st.write("")
        render_table(pd.DataFrame({
            "Ventas Est.": [clean_number_format(get_val(r, 'ventas_estimado'))],
            "Empleados": [clean_number_format(get_val(r, 'numero_empleados'))],
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

    else:
        # CASO 2: EMPRESA NO ESTÁ EN DB FINANCIERA
        st.title(f"🏢 {selected_empresa}")
        st.error("⚠️ Datos financieros no disponibles para esta entidad.")

    # 4. SECCIÓN ALUMNI (COMÚN PARA AMBOS CASOS)
    st.markdown('<div class="section-title">Networking (Alumni)</div>', unsafe_allow_html=True)
    
    col_matriz = next((c for c in df_alumni.columns if 'informa' in c.lower()), None)
    if col_matriz and not df_alumni.empty:
        # Filtrado flexible
        match = df_alumni[df_alumni[col_matriz].astype(str).str.strip() == str(selected_empresa).strip()]
        if match.empty:
             match = df_alumni[df_alumni[col_matriz].astype(str).str.contains(re.escape(str(selected_empresa).strip()), case=False, na=False)]
        
        if not match.empty:
            num = match['Nombre'].nunique()
            st.markdown(f"""
                <div style="background-color: #E8F5E9; border: 1px solid #2E7D32; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 20px;">
                    <div style="color: #2E7D32; font-size: 2rem; font-weight: 800;">{num}</div>
                    <div style="color: #1B5E20; font-weight: 700; text-transform: uppercase; font-size: 0.9rem;">Contactos Encontrados</div>
                </div>""", unsafe_allow_html=True)

            t1, t2 = st.tabs(["📊 Niveles", "📋 Lista Detallada"])
            
            with t1:
                if 'jerarquía' in match.columns:
                    cts = match['jerarquía'].value_counts().reset_index()
                    cts.columns = ['Nivel', 'Total']
                    render_table(cts)
            
            with t2:
                # Selección de columnas limpias para mostrar
                cols_view = ['Nombre', 'Cargo', 'jerarquía', 'función', 'url_linkedin']
                cols_exist = [c for c in cols_view if c in match.columns]
                render_table(match[cols_exist])
        else:
            st.info(f"No se han encontrado ex-alumnos trabajando actualmente en {selected_empresa}.")
    else:
        st.caption("Base de datos de alumni no conectada.")

else:
    # --- HOME / DASHBOARD (BINGO EDITION) ---
    st.markdown('<div style="padding-top: 40px;"></div>', unsafe_allow_html=True)
    
    # 1. TÍTULO Y SUBTÍTULO
    st.markdown('<div class="hero-title">BINGO</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Filtra, conecta, y bingo!</div>', unsafe_allow_html=True)

    # 2. KPIs (Sin cambios)
    m1, m2, m3, m4 = st.columns([1, 2, 2, 1])
    with m2:
        st.markdown(f'<div class="kpi-card" style="padding:15px;"><div class="kpi-value">{len(df_main)}</div><div class="kpi-label">EMPRESAS</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="kpi-card" style="padding:15px;"><div class="kpi-value">{df_alumni["Nombre"].nunique() if not df_alumni.empty else 0}</div><div class="kpi-label">CONTACTOS</div></div>', unsafe_allow_html=True)

    # 3. TARJETAS DE HERRAMIENTAS ACTUALIZADAS
    st.write("")
    st.write("")
    st.markdown("### 🚀 Herramientas")
    
    c1, c2, c3 = st.columns(3)
    
    # Tarjeta 1: Filtra Empresas
    with c1:
        st.markdown("""
            <div class="feature-card">
                <span class="feature-icon">🏢</span>
                <div class="feature-title">Filtra Empresas</div>
                <div class="feature-desc">Información sobre Negocio y Tecnología.</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Tarjeta 2: Conecta con Profesionales
    with c2:
        st.markdown("""
            <div class="feature-card">
                <span class="feature-icon">🤝</span>
                <div class="feature-title">Conecta con Profesionales</div>
                <div class="feature-desc">Información exclusiva desde top management a entry level.</div>
            </div>
        """, unsafe_allow_html=True)

    # Tarjeta 3: Canta Bingo
    with c3:
        st.markdown("""
            <div class="feature-card">
                <span class="feature-icon">🎯</span>
                <div class="feature-title">Canta Bingo</div>
                <div class="feature-desc">Identifica la oportunidad perfecta y cierra el trato.</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("👈 Utiliza el menú lateral para comenzar tu búsqueda.")