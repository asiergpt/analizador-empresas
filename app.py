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

# --- CSS PERSONALIZADO (OPTIMIZADO MÓVIL + PC) ---
st.markdown("""
    <style>
    /* Importar fuente Roboto */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    * {
        box-sizing: border-box;
    }
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        font-size: 16px;
        color: #2c3e50;
    }

    /* Títulos de sección */
    .section-title {
        color: #1F4E79;
        font-size: clamp(1.4rem, 5vw, 2rem);
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        border-bottom: 4px solid #DAE9F7;
        padding-bottom: 10px;
    }

    /* --- 1. KPIs SUPERIORES --- */
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
    .kpi-card:hover { 
        transform: translateY(-2px); 
    }
    
    .kpi-label {
        color: #1F4E79;
        font-size: clamp(0.75rem, 3vw, 1.1rem);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
        margin-bottom: 10px;
        word-break: break-word;
    }
    .kpi-value {
        color: #1F4E79;
        font-size: clamp(1.3rem, 5vw, 2.4rem);
        font-weight: 800;
        line-height: 1.2;
        word-break: break-word;
    }
    .kpi-value.viable { 
        color: #2E7D32; 
    }

    /* --- 2. CAJAS DE CONTENIDO --- */
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
        word-break: break-word;
    }
    .box-text {
        font-size: clamp(0.95rem, 3vw, 1.2rem);
        color: #34495e;
        line-height: 1.8;
        word-break: break-word;
    }
    .box-text b { 
        color: #1F4E79; 
        font-weight: 700; 
    }

    /* --- 3. GRID LAYOUT RESPONSIVO --- */
    .grid-2-col {
        display: grid;
        grid-template-columns: 1fr;
        gap: clamp(10px, 4vw, 30px);
        margin-bottom: 30px;
    }
    
    @media (min-width: 768px) {
        .grid-2-col {
            grid-template-columns: 1fr 1fr;
        }
    }

    /* --- 4. SECCIÓN TECH --- */
    .tech-hero-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border: none;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(31, 78, 121, 0.15);
        font-size: clamp(0.85rem, 3vw, 1rem);
    }
    .tech-hero-table th {
        background-color: #1F4E79;
        color: white;
        padding: clamp(10px, 3vw, 20px);
        text-align: center;
        font-weight: 700;
        font-size: clamp(0.85rem, 3vw, 1.3rem);
        letter-spacing: 1px;
        width: 50%;
        text-transform: uppercase;
        word-break: break-word;
    }
    .tech-hero-table td {
        background-color: white;
        padding: clamp(12px, 3vw, 25px);
        text-align: center;
        font-size: clamp(1rem, 3vw, 1.6rem);
        color: #2c3e50;
        font-weight: 500;
        border-bottom: 4px solid #DAE9F7;
        word-break: break-word;
        overflow-wrap: break-word;
    }
    .tech-hero-table td:first-child {
        border-right: 1px solid #eee;
    }

    /* B) Tarjetas de Detalle */
    .tech-detail-card {
        background-color: #fcfcfc;
        border: 1px solid #e0e0e0;
        border-left: 8px solid #1F4E79;
        border-radius: 8px;
        padding: clamp(12px, 3vw, 25px);
        margin-bottom: 15px;
        display: flex;
        flex-direction: column;
        transition: background-color 0.3s;
    }
    .tech-detail-card:hover {
        background-color: #f4f8fb;
    }
    
    .tech-label {
        color: #1F4E79;
        font-size: clamp(0.9rem, 3vw, 1.2rem);
        font-weight: 800;
        margin-bottom: 8px;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
        word-break: break-word;
    }
    
    .tech-value {
        color: #4a4a4a;
        font-size: clamp(0.95rem, 3vw, 1.3rem);
        line-height: 1.6;
        word-break: break-word;
        overflow-wrap: break-word;
    }

    /* Tablas Generales */
    .custom-table { 
        width: 100%; 
        border-collapse: collapse; 
        margin-top: 15px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        font-size: clamp(0.85rem, 2.5vw, 1.1rem);
    }
    .custom-table th { 
        background-color: #1F4E79; 
        color: white; 
        padding: clamp(10px, 2vw, 15px); 
        text-align: center; 
        font-size: clamp(0.8rem, 2.5vw, 1.1rem);
        word-break: break-word;
    }
    .custom-table td { 
        background-color: white; 
        border-bottom: 1px solid #eee; 
        padding: clamp(10px, 2vw, 15px); 
        text-align: center; 
        font-size: clamp(0.8rem, 2.5vw, 1.1rem);
        color: #333;
        word-break: break-word;
    }

    /* Contenedor de tablas con scroll */
    .table-container {
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] h1 { 
        font-size: clamp(1.3rem, 4vw, 1.8rem) !important; 
    }
    [data-testid="stSidebar"] p { 
        font-size: clamp(0.9rem, 3vw, 1.1rem) !important; 
    }
    [data-testid="stSidebar"] label { 
        font-size: clamp(0.95rem, 3vw, 1.2rem) !important; 
        font-weight: 600; 
    }

    /* Título principal */
    h1 {
        font-size: clamp(1.8rem, 6vw, 3rem) !important;
        word-break: break-word;
    }

    /* Media query adicional para pantallas muy pequeñas */
    @media (max-width: 480px) {
        html, body, [class*="css"] {
            font-size: 14px;
        }
        .section-title {
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }
        .grid-2-col {
            gap: 10px;
        }
        .kpi-card {
            padding: 12px;
        }
        .content-box {
            padding: 12px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE UTILIDAD ---
def clean_number_format(val):
    if pd.isna(val): 
        return "-"
    try:
        val_str = str(val).strip()
        val_str = re.sub(r'\(.*?\)', '', val_str).strip()
        clean_digits = re.sub(r'[^\d]', '', val_str)
        if not clean_digits: 
            return val_str
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
    if not text or text == "-": 
        return "-"
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

# --- CARGA DE DATOS SEGURA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('guipuzcoa_dollar_final_ddbb.csv', sep=';', encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv('guipuzcoa_dollar_final_ddbb.csv', sep=';', encoding='latin-1')
    except FileNotFoundError:
        return None, None

    try:
        key = st.secrets["encryption_key"]
        cipher_suite = Fernet(key)
        
        with open('alumni_seguro.enc', 'rb') as file:
            encrypted_data = file.read()
            
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        df_alumni = pd.read_csv(io.BytesIO(decrypted_data), sep=';', encoding='utf-8')
        
        if 'nombre_matriz_einforma' in df_alumni.columns:
            df_alumni['nombre_matriz_einforma'] = df_alumni['nombre_matriz_einforma'].astype(str).str.strip()
            
    except Exception as e:
        df_alumni = pd.DataFrame(columns=['Nombre', 'nombre_matriz_einforma', 'jerarquía'])
    
    return df, df_alumni

df_main, df_alumni = load_data()

# --- INTERFAZ PRINCIPAL ---
if df_main is None:
    st.error("❌ No se encontró el archivo 'guipuzcoa_dollar_final_ddbb.csv'.")
else:
    # --- SIDEBAR ---
    st.sidebar.header("🔍 Panel de Búsqueda")
    st.sidebar.write("")
    
    provincias_disponibles = ["Todas"] + sorted(df_main['provincia'].dropna().unique().tolist())
    selected_provincia = st.sidebar.selectbox("Selecciona una provincia", provincias_disponibles)
    
    search_term = st.sidebar.text_input("Busca una empresa (nombre)")

    df_filtered = df_main.copy()
    if selected_provincia != "Todas":
        df_filtered = df_filtered[df_filtered['provincia'] == selected_provincia]
    
    if search_term:
        df_filtered = df_filtered[df_filtered['Nombre'].astype(str).str.contains(search_term, case=False, na=False)]

    empresa_list = sorted(df_filtered['Nombre'].unique().tolist())
    
    if len(empresa_list) > 0:
        selected_empresa = st.sidebar.selectbox("Selecciona una empresa", empresa_list)
    else:
        selected_empresa = None

    st.sidebar.markdown("---")
    
    if len(empresa_list) > 0:
        st.sidebar.success(f"✅ Empresas encontradas: {len(empresa_list)}")
    else:
        st.sidebar.warning("⚠️ No se encontraron empresas.")

    # --- PANEL CENTRAL ---
    if selected_empresa:
        row = df_filtered[df_filtered['Nombre'] == selected_empresa].iloc[0]

        st.title(f"🏢 {get_val(row, 'Nombre')}")
        
        # 1. RESUMEN
        st.markdown('<div class="section-title">Resumen Ejecutivo</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        ubicacion = capitalize_first_letter(get_val(row, 'provincia'))
        clasificacion = get_val(row, 'veredicto_final')
        veredicto_raw = get_val(row, 'conclusion_sueldo_80k')
        parts = veredicto_raw.split()
        veredicto_clean = "".join(filter(str.isalnum, parts[1])) if len(parts) > 1 else "VIABLE"
        clase_viabilidad = "viable" if "VIABLE" in veredicto_clean.upper() else ""

        with col1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">📍 Ubicación</div><div class="kpi-value">{ubicacion}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">📊 Clasificación</div><div class="kpi-value">{clasificacion}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">💰 Viabilidad >80k</div><div class="kpi-value {clase_viabilidad}">{veredicto_clean}</div></div>', unsafe_allow_html=True)

        st.write("") 
        datos_tabla_1 = {
            "Año Constitución": [get_val(row, 'ano_constitucion')],
            "Población": [get_val(row, 'poblacion')],
            "Ventas Estimadas": [clean_number_format(get_val(row, 'ventas_estimado'))],
            "Empleados": [clean_number_format(get_val(row, 'numero_empleados'))],
            "Patentes": [get_val(row, 'patentes')],
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

        # 5. NETWORKING
        st.markdown('<div class="section-title">Networking (Alumni)</div>', unsafe_allow_html=True)
        nombre_limpio = str(selected_empresa).strip()
        matches = df_alumni[df_alumni['nombre_matriz_einforma'] == nombre_limpio]
        total_alumni = matches['Nombre'].nunique() if not matches.empty else 0

        if total_alumni > 0:
            st.success(f"✅ Se han encontrado **{total_alumni}** contactos en esta empresa.")
            tab1, tab2 = st.tabs(["Resumen por Nivel", "Detalle de Personas"])
            with tab1:
                if 'jerarquía' in matches.columns:
                    counts = matches['jerarquía'].value_counts().reset_index()
                    counts.columns = ['Jerarquía', 'Cantidad']
                    render_table(counts)
                else:
                    st.warning("No hay datos de jerarquía disponibles.")
            with tab2:
                cols_posibles = ['Nombre', 'Cargo', 'jerarquía', 'edad', 'provincia', 'url_linkedin']
                cols_finales = [c for c in cols_posibles if c in matches.columns]
                render_table(matches[cols_finales])
        else:
            st.warning("No se han encontrado ex-alumnos en esta empresa.")

    else:
        st.info("👈 Utiliza el panel de la izquierda para comenzar.")
