import streamlit as st
import pandas as pd
import re
from cryptography.fernet import Fernet
import io

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Analizador de Empresas",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FORZAR VISIBILIDAD DEL SIDEBAR ---
# Esto hace que la barra lateral nunca esté vacía, así que siempre se mostrará
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063376.png", width=50)
st.sidebar.title("Menú Principal")
st.sidebar.write("---")

# --- CSS PREMIUM (ESTILO MEJORADO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    * { box-sizing: border-box; }
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        font-size: 16px;
        color: #2c3e50;
    }

    /* Títulos */
    .section-title {
        color: #1F4E79;
        font-size: clamp(1.4rem, 5vw, 2rem);
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        border-bottom: 4px solid #DAE9F7;
        padding-bottom: 10px;
    }

    /* KPIs */
    .kpi-card {
        background-color: #DAE9F7;
        border-radius: 12px;
        padding: clamp(12px, 4vw, 25px);
        text-align: center;
        border: 2px solid #1F4E79;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-2px); }
    
    .kpi-label {
        color: #1F4E79;
        font-size: clamp(0.75rem, 3vw, 1.1rem);
        text-transform: uppercase;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .kpi-value {
        color: #1F4E79;
        font-size: clamp(1.3rem, 5vw, 2.4rem);
        font-weight: 800;
        line-height: 1.2;
    }
    .kpi-value.viable { color: #2E7D32; }

    /* Cajas Contenido */
    .content-box {
        background-color: white;
        border: 1px solid #dcdcdc;
        border-radius: 12px;
        padding: clamp(15px, 4vw, 30px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.03);
        height: 100%;
    }
    .box-header {
        color: #1F4E79;
        font-weight: 700;
        font-size: clamp(1.1rem, 4vw, 1.5rem);
        margin-bottom: 15px;
        border-bottom: 2px solid #DAE9F7;
        padding-bottom: 10px;
        display: block;
    }
    .box-text {
        font-size: clamp(0.95rem, 3vw, 1.2rem);
        color: #34495e;
        line-height: 1.8;
    }

    /* Grid Layout */
    .grid-2-col {
        display: grid;
        grid-template-columns: 1fr;
        gap: clamp(10px, 4vw, 30px);
        margin-bottom: 30px;
    }
    @media (min-width: 768px) {
        .grid-2-col { grid-template-columns: 1fr 1fr; }
    }

    /* Tech Section */
    .tech-hero-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border: none;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(31, 78, 121, 0.15);
    }
    .tech-hero-table th {
        background-color: #1F4E79;
        color: white;
        padding: clamp(10px, 3vw, 20px);
        text-align: center;
        font-weight: 700;
        font-size: clamp(0.85rem, 3vw, 1.3rem);
        width: 50%;
    }
    .tech-hero-table td {
        background-color: white;
        padding: clamp(12px, 3vw, 25px);
        text-align: center;
        font-size: clamp(1rem, 3vw, 1.6rem);
        font-weight: 500;
        border-bottom: 4px solid #DAE9F7;
    }

    /* Tablas Generales */
    .table-container { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .custom-table { width: 100%; border-collapse: collapse; margin-top: 15px; min-width: 500px; }
    .custom-table th { background-color: #1F4E79; color: white; padding: 12px; text-align: center; }
    .custom-table td { background-color: white; border-bottom: 1px solid #eee; padding: 12px; text-align: center; color: #333; }
    
    /* Tarjeta Perfil Sidebar */
    .profile-card {
        background-color: #f0f4f8;
        border-left: 5px solid #1F4E79;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .profile-name { font-weight: 800; color: #1F4E79; font-size: 1.2rem; margin-bottom: 4px; }
    .profile-role { font-size: 0.95rem; color: #666; margin-bottom: 10px; font-style: italic; }
    .profile-company { font-weight: 600; color: #333; display: flex; align-items: center; gap: 6px; font-size: 0.95rem; border-top: 1px solid #ddd; padding-top: 8px;}

    /* Ajustes Sidebar */
    [data-testid="stSidebar"] h1 { font-size: clamp(1.3rem, 4vw, 1.8rem) !important; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE UTILIDAD ---
def clean_number_format(val):
    if pd.isna(val): return "-"
    try:
        val_str = str(val).strip()
        val_str = re.sub(r'\(.*?\)', '', val_str).strip()
        clean_digits = re.sub(r'[^\d]', '', val_str)
        if not clean_digits: return val_str
        return "{:,}".format(int(clean_digits))
    except:
        return str(val)

def get_val(row, col_name):
    if col_name in row:
        val = row[col_name]
        return str(val) if pd.notna(val) else "-"
    for c in row.index:
        if c.lower().replace('_', '') == col_name.lower().replace('_', ''):
            val = row[c]
            return str(val) if pd.notna(val) else "-"
    return "-"

def capitalize_first_letter(text):
    text = str(text).strip()
    if not text or text == "-": return "-"
    words = text.split()
    if words:
        words[0] = words[0].capitalize()
        return " ".join(words)
    return text

def render_table(df):
    if df.empty:
        st.write("Sin datos.")
        return
    html = df.to_html(index=False, border=0, classes="custom-table")
    st.markdown(f'<div class="table-container">{html}</div>', unsafe_allow_html=True)

# --- CARGA DE DATOS ROBUSTA ---
@st.cache_data
def load_data():
    # 1. Cargar Empresas
    try:
        df = pd.read_csv('guipuzcoa_dollar_final_ddbb.csv', sep=';', encoding='utf-8')
    except:
        try:
            df = pd.read_csv('guipuzcoa_dollar_final_ddbb.csv', sep=';', encoding='latin-1')
        except:
            return None, None

    # 2. Cargar Alumni (INTENTO DOBLE DE ENCODING + FORMATEO)
    df_alumni = pd.DataFrame()
    try:
        if "encryption_key" in st.secrets:
            key = st.secrets["encryption_key"]
            cipher_suite = Fernet(key)
            with open('alumni_seguro.enc', 'rb') as file:
                encrypted_data = file.read()
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            
            # Intento 1: UTF-8
            try:
                df_alumni = pd.read_csv(io.BytesIO(decrypted_data), sep=';', encoding='utf-8')
            except:
                # Intento 2: Latin-1 (Fallback)
                df_alumni = pd.read_csv(io.BytesIO(decrypted_data), sep=';', encoding='latin-1')
            
            # A) Normalizar nombres de columnas (quita espacios extra)
            df_alumni.columns = [c.strip() for c in df_alumni.columns]
            
            # B) Buscar columnas clave dinámicamente
            col_nombre = next((c for c in df_alumni.columns if c.lower() == 'nombre'), None)
            col_cargo = next((c for c in df_alumni.columns if c.lower() == 'cargo'), None)
            col_matriz = next((c for c in df_alumni.columns if 'informa' in c.lower()), 'nombre_matriz_einforma')

            # C) APLICAR FORMATO ELEGANTE (Capitalize/Title)
            if col_nombre:
                # Convierte "IGNACIO MUÑOZ" -> "Ignacio Muñoz"
                df_alumni[col_nombre] = df_alumni[col_nombre].astype(str).str.strip().str.title()
            
            if col_cargo:
                # Convierte "DIRECTOR DE MARKETING" -> "Director De Marketing"
                df_alumni[col_cargo] = df_alumni[col_cargo].astype(str).str.strip().str.title()

            if col_matriz in df_alumni.columns:
                df_alumni[col_matriz] = df_alumni[col_matriz].astype(str).str.strip()
            
            # D) Normalización de jerarquía
            if 'jerarquía' in df_alumni.columns:
                df_alumni['jerarquía'] = df_alumni['jerarquía'].astype(str).str.strip().str.title()
                
    except Exception as e:
        # Silencioso en producción
        pass
    
    return df, df_alumni

df_main, df_alumni = load_data()

# --- GESTIÓN DE ESTADO ---
if 'selected_empresa' not in st.session_state:
    st.session_state['selected_empresa'] = None

# --- SIDEBAR ---
if df_main is not None:
    st.sidebar.header("🔍 Panel de Búsqueda")
    
    tab_empresa, tab_profesional = st.sidebar.tabs(["🏢 Empresa", "🧑‍💼 Profesional"])
    
    # --- MODO 1: EMPRESA ---
    with tab_empresa:
        st.write("")
        provincias = ["Todas"] + sorted(df_main['provincia'].dropna().unique().tolist())
        selected_provincia = st.selectbox("Selecciona una provincia", provincias)
        search_term_emp = st.text_input("Busca una empresa", placeholder="Ej: Caf")

        df_filtered_emp = df_main.copy()
        if selected_provincia != "Todas":
            df_filtered_emp = df_filtered_emp[df_filtered_emp['provincia'] == selected_provincia]
        
        if search_term_emp:
            df_filtered_emp = df_filtered_emp[df_filtered_emp['Nombre'].astype(str).str.contains(search_term_emp, case=False, na=False)]

        empresa_list = sorted(df_filtered_emp['Nombre'].unique().tolist())

        if empresa_list:
            empresa_seleccionada_box = st.selectbox("Resultados empresas", empresa_list)
            if st.button("Ver Análisis Empresa", use_container_width=True):
                st.session_state['selected_empresa'] = empresa_seleccionada_box
                st.rerun()
        else:
            st.warning("No se encontraron empresas.")

    # --- MODO 2: PROFESIONAL (PERFECTO) ---
    with tab_profesional:
        st.write("")
        
        if df_alumni is None or df_alumni.empty:
            st.error("⚠️ No se cargaron datos. Verifica la clave.")
        else:
            # Detección inteligente de columnas
            col_nombre = next((c for c in df_alumni.columns if c.lower() == 'nombre'), None)
            col_empresa = next((c for c in df_alumni.columns if 'informa' in c.lower()), None)
            col_cargo = next((c for c in df_alumni.columns if c.lower() == 'cargo'), None)

            if col_nombre:
                search_term_prof = st.text_input("Filtrar por nombre", placeholder="Ej: Ignacio")
                
                # Filtrado robusto (case insensitive)
                if search_term_prof:
                    mask = df_alumni[col_nombre].astype(str).str.contains(search_term_prof, case=False, na=False)
                    prof_filtered = df_alumni[mask]
                    prof_list = sorted(prof_filtered[col_nombre].unique().tolist())
                else:
                    prof_list = sorted(df_alumni[col_nombre].head(50).unique().tolist())

                # Selector
                if prof_list:
                    prof_seleccionado = st.selectbox("Selecciona profesional:", prof_list, index=None, placeholder="Elige uno...")
                    
                    if prof_seleccionado and col_empresa:
                        # Obtener datos
                        datos_prof = df_alumni[df_alumni[col_nombre] == prof_seleccionado].iloc[0]
                        empresa_del_prof = datos_prof[col_empresa]
                        cargo_del_prof = datos_prof[col_cargo] if col_cargo else "Cargo no especificado"
                        
                        # --- TARJETA DE PERFIL (Diseño Limpio) ---
                        st.markdown(f"""
                        <div class="profile-card">
                            <div class="profile-name">{prof_seleccionado}</div>
                            <div class="profile-role">{cargo_del_prof}</div>
                            <div class="profile-company">🏢 {empresa_del_prof}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"Ir a Análisis ->", use_container_width=True):
                            st.session_state['selected_empresa'] = empresa_del_prof
                            st.rerun()
                elif search_term_prof:
                    st.warning("No hay coincidencias.")

    st.sidebar.markdown("---")

# --- PANEL CENTRAL ---
selected_empresa = st.session_state['selected_empresa']

if selected_empresa:
    # Búsqueda exacta primero, luego aproximada
    row_data = df_main[df_main['Nombre'] == selected_empresa]
    
    if row_data.empty:
        try:
            row_data = df_main[df_main['Nombre'].astype(str).str.contains(re.escape(selected_empresa), case=False, na=False)]
        except: pass

    if not row_data.empty:
        row = row_data.iloc[0]

        # TÍTULO
        st.title(f"🏢 {get_val(row, 'Nombre')}")
        
        # 1. RESUMEN
        st.markdown('<div class="section-title">Resumen Ejecutivo</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        ubicacion = capitalize_first_letter(get_val(row, 'provincia'))
        veredicto_raw = get_val(row, 'conclusion_sueldo_80k')
        parts = veredicto_raw.split()
        veredicto_clean = "".join(filter(str.isalnum, parts[1])) if len(parts) > 1 else "VIABLE"
        clase_viabilidad = "viable" if "VIABLE" in veredicto_clean.upper() else ""

        with col1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">📍 Ubicación</div><div class="kpi-value">{ubicacion}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">📊 Clasificación</div><div class="kpi-value">{get_val(row, "veredicto_final")}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">💰 Viabilidad >80k</div><div class="kpi-value {clase_viabilidad}">{veredicto_clean}</div></div>', unsafe_allow_html=True)

        st.write("") 
        datos_tabla_1 = {
            "Año Constitución": [get_val(row, 'ano_constitucion')],
            "Población": [get_val(row, 'poblacion')],
            "Ventas Estimadas": [clean_number_format(get_val(row, 'ventas_estimado'))],
            "Empleados": [clean_number_format(get_val(row, 'numero_empleados'))],
            "Web": [get_val(row, 'web_oficial')]
        }
        render_table(pd.DataFrame(datos_tabla_1))

        # 2. SECTOR
        st.markdown('<div class="section-title">Sector y Actividad</div>', unsafe_allow_html=True)
        html_sector = f"""
        <div class="grid-2-col">
            <div class="content-box">
                <span class="box-header">Sector</span>
                <span class="box-text">{get_val(row, 'SECTOR_NOMBRE')}</span>
            </div>
            <div class="content-box">
                <span class="box-header">Actividad Principal</span>
                <span class="box-text">{get_val(row, 'actividad_resumen')}</span>
            </div>
        </div>
        """
        st.markdown(html_sector, unsafe_allow_html=True)

        # 3. PROPIEDAD
        st.markdown('<div class="section-title">Propiedad y Solvencia</div>', unsafe_allow_html=True)
        html_propiedad = f"""
        <div class="grid-2-col">
            <div class="content-box">
                <span class="box-header">Estructura de Propiedad</span>
                <div class="box-text" style="margin-bottom: 12px;">
                    <b>Propiedad:</b> {get_val(row, 'propiedad_accionistas')}
                </div>
                <div class="box-text">
                    <b>Private Equity:</b> {get_val(row, 'private_equity_firmas')}
                </div>
            </div>
            <div class="content-box">
                <span class="box-header">Finanzas y Solvencia</span>
                <div class="box-text" style="margin-bottom: 12px;">
                    <b>Financiación Pública:</b> {get_val(row, 'financiacion_publica_detalle')}
                </div>
                <div class="box-text">
                    <b>Solvencia:</b> {get_val(row, 'solvencia_txt')}
                </div>
            </div>
        </div>
        """
        st.markdown(html_propiedad, unsafe_allow_html=True)

        # 4. MADUREZ TECNOLÓGICA
        st.markdown('<div class="section-title">Madurez Tecnológica</div>', unsafe_allow_html=True)
        
        cto_val = get_val(row, 'cto_actual')
        ing_val = get_val(row, 'tamano_ing')
        ia_val = get_val(row, 'usa_inteligencia_artificial')
        cloud_val = get_val(row, 'plataforma_cloud')
        perfil_val = get_val(row, 'perfil_txt')
        
        html_tech_top = f"""
        <table class="tech-hero-table">
            <tr>
                <th>CTO / RESPONSABLE TEC.</th>
                <th>EQUIPO INGENIERÍA</th>
            </tr>
            <tr>
                <td>{cto_val}</td>
                <td>{ing_val}</td>
            </tr>
        </table>
        """
        st.markdown(html_tech_top, unsafe_allow_html=True)
        
        html_tech_details = f"""
        <div style="margin-top: 20px;">
            <div class="tech-detail-card">
                <div class="tech-label">🧠 Uso Inteligencia Artificial</div>
                <div class="tech-value">{ia_val}</div>
            </div>
            <div class="grid-2-col" style="margin-bottom: 0;">
                <div class="tech-detail-card">
                    <div class="tech-label">☁️ Arquitectura Cloud</div>
                    <div class="tech-value">{cloud_val}</div>
                </div>
                <div class="tech-detail-card">
                    <div class="tech-label">💻 Perfil Tecnológico</div>
                    <div class="tech-value">{perfil_val}</div>
                </div>
            </div>
        </div>
        """
        st.markdown(html_tech_details, unsafe_allow_html=True)

        # 5. NETWORKING (MODIFICADO Y ROBUSTO)
        st.markdown('<div class="section-title">Networking (Alumni)</div>', unsafe_allow_html=True)
        
        # Filtro Inteligente (intenta nombre exacto y si no, contenido)
        nombre_limpio = str(selected_empresa).strip()
        
        # Primero busca la columna correcta de 'nombre matriz'
        col_matriz = next((c for c in df_alumni.columns if 'informa' in c.lower()), None)
        
        if col_matriz:
            matches = df_alumni[df_alumni[col_matriz] == nombre_limpio]
            if matches.empty:
                # Intento parcial
                matches = df_alumni[df_alumni[col_matriz].astype(str).str.contains(re.escape(nombre_limpio), case=False, na=False)]
        else:
            matches = pd.DataFrame()

        total_alumni = matches['Nombre'].nunique() if not matches.empty else 0

        if total_alumni > 0:
            st.success(f"✅ Se han encontrado **{total_alumni}** contactos en esta empresa.")
            tab1, tab2 = st.tabs(["Resumen por Categoría", "Detalle de Personas"])
            
            with tab1:
                if 'jerarquía' in matches.columns:
                    counts = matches['jerarquía'].value_counts().reset_index()
                    counts.columns = ['Categoría', 'Cantidad']
                    order_map = {'Top Management': 1, 'Middle Management': 2, 'Entry Level/Others': 3}
                    counts['sort_key'] = counts['Categoría'].apply(lambda x: order_map.get(x, 99))
                    counts = counts.sort_values('sort_key').drop('sort_key', axis=1)
                    render_table(counts)
                else:
                    st.warning("No hay datos de categoría disponibles.")
            
            with tab2:
                # Mostrar columnas disponibles dinámicamente
                cols_posibles = ['Nombre', 'Cargo', 'jerarquía', 'url_linkedin']
                cols_finales = [c for c in cols_posibles if c in matches.columns]
                df_show = matches[cols_finales].rename(columns={'jerarquía': 'Categoría'})
                render_table(df_show)
        else:
            st.info("No se han encontrado ex-alumnos en esta empresa.")

    else:
        st.error("Error al cargar los datos de la empresa seleccionada.")

# --- PANTALLA DE BIENVENIDA (LANDING PAGE) ---
else:
    st.markdown("""
    <div style="text-align: center; margin-top: 50px; margin-bottom: 30px;">
        <h1 style="color: #1F4E79; font-size: 3rem;">🔍 Analizador de Empresas</h1>
        <p style="font-size: 1.2rem; color: #555;">Explora datos financieros, tecnológicos y contactos de alumni en tiempo real.</p>
    </div>
    """, unsafe_allow_html=True)

    total_empresas = len(df_main) if df_main is not None else 0
    total_alumni = df_alumni['Nombre'].nunique() if df_alumni is not None and not df_alumni.empty else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">🏢 Empresas Rastradas</div><div class="kpi-value">{total_empresas}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">🎓 Profesionales Alumni</div><div class="kpi-value">{total_alumni}</div></div>', unsafe_allow_html=True)
    with col3:
        n_prov = len(df_main['provincia'].unique()) if df_main is not None else 0
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">🌍 Provincias</div><div class="kpi-value">{n_prov}</div></div>', unsafe_allow_html=True)

    st.write("")
    st.info("👈 **Para comenzar:** Abre el menú lateral (arriba a la izquierda) y busca una empresa o profesional.")
    
    if df_main is not None and not df_main.empty:
        st.markdown("### 🎲 O explora algunas empresas destacadas:")
        top_empresas = df_main.sample(3)['Nombre'].tolist()
        cols = st.columns(len(top_empresas))
        for i, emp in enumerate(top_empresas):
            with cols[i]:
                if st.button(f"🔎 {emp}", key=f"btn_{i}", use_container_width=True):
                    st.session_state['selected_empresa'] = emp
                    st.rerun()