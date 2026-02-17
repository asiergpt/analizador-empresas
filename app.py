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


# --- CSS PREMIUM (LIMPIO Y CORREGIDO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; font-size: 16px; color: #2c3e50; }
    
    /* Títulos */
    .section-title {
        color: #1F4E79;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        border-bottom: 4px solid #DAE9F7;
        padding-bottom: 5px;
        letter-spacing: -0.5px;
    }

    /* Tarjetas KPI */
    .kpi-card {
        background-color: #DAE9F7;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 2px solid #1F4E79;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        height: 100%;
        display: flex; flex-direction: column; justify-content: center;
    }
    .kpi-value { color: #1F4E79; font-size: 2rem; font-weight: 800; line-height: 1.2; }
    .kpi-label { font-size: 0.85rem; text-transform: uppercase; font-weight: 700; color: #1F4E79; margin-top: 5px; letter-spacing: 1px; }
    .kpi-value.viable { color: #2E7D32; }

    /* Cajas de Texto */
    .content-box {
        background-color: white;
        border: 1px solid #dcdcdc;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.03);
        height: 100%;
    }
    .box-header {
        color: #1F4E79;
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 15px;
        border-bottom: 2px solid #DAE9F7;
        padding-bottom: 5px;
        display: block;
    }
    .box-text { font-size: 1rem; color: #34495e; line-height: 1.6; }

    /* Tarjetas Tecnológicas (Hero y Grid) */
    .tech-hero {
        background-color: #1F4E79;
        color: white;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(31, 78, 121, 0.2);
        height: 100%;
        display: flex; flex-direction: column; justify-content: center;
    }
    .tech-hero-label { font-size: 0.85rem; text-transform: uppercase; opacity: 0.9; font-weight: 600; margin-bottom: 5px; }
    .tech-hero-val { font-size: 1.3rem; font-weight: 700; }

    .tech-card {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-top: 4px solid #1F4E79;
        border-radius: 10px;
        padding: 20px;
        height: 100%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .tech-card:hover { transform: translateY(-3px); }
    .tech-icon { font-size: 1.8rem; margin-bottom: 10px; display: block; }
    .tech-title { color: #1F4E79; font-weight: 700; font-size: 0.95rem; margin-bottom: 8px; text-transform: uppercase; }
    .tech-text { font-size: 1rem; color: #444; line-height: 1.4; }

    /* Tarjeta Perfil Sidebar */
    .profile-card {
        background-color: #f8f9fa;
        border-left: 5px solid #1F4E79;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .profile-name { font-weight: 800; color: #1F4E79; font-size: 1.1rem; margin-bottom: 4px; }
    .profile-role { font-size: 0.9rem; color: #666; margin-bottom: 10px; font-style: italic; }
    .profile-company { font-weight: 600; color: #333; font-size: 0.9rem; border-top: 1px solid #ddd; padding-top: 8px;}

    /* Tablas */
    .custom-table { width: 100%; border-collapse: separate; border-spacing: 0; min-width: 500px; border-radius: 8px; overflow: hidden; border: 1px solid #eee; }
    .custom-table th { background-color: #1F4E79; color: white; padding: 12px; text-align: center; font-weight: 600; }
    .custom-table td { border-bottom: 1px solid #f0f0f0; padding: 12px; text-align: center; color: #333; }
    .table-container { overflow-x: auto; box-shadow: 0 2px 5px rgba(0,0,0,0.03); border-radius: 8px; margin-bottom: 20px; }

    /* Layouts */
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
    .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px; }
    @media (max-width: 768px) { .grid-2, .grid-3 { grid-template-columns: 1fr; } }
    
    /* Ajustes Sidebar */
    [data-testid="stSidebar"] h1 { font-size: 1.5rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- UTILIDADES ---
def clean_number_format(val):
    if pd.isna(val): return "-"
    s = re.sub(r'[^\d]', '', str(val))
    return "{:,}".format(int(s)) if s else str(val)

def get_val(row, col):
    val = str(row[col]) if col in row and pd.notna(row[col]) else "-"
    return val if val.lower() != "nan" else "-"

def capitalize_first_letter(text):
    text = str(text).strip()
    if not text or text == "-": return "-"
    return " ".join([word.capitalize() for word in text.split()])

def render_table(df):
    if df.empty: st.write("Sin datos."); return
    st.markdown(f'<div class="table-container">{df.to_html(index=False, border=0, classes="custom-table")}</div>', unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    df = None
    df_alumni = pd.DataFrame()
    
    # 1. EMPRESAS - Intentamos leer el archivo correcto
    # IMPORTANTE: He corregido el nombre aquí para que coincida con tu GitHub
    archivo_empresas = 'euskadi_navarra_dollar.csv'
    
    try:
        df = pd.read_csv(archivo_empresas, sep=';', encoding='utf-8')
    except:
        try:
            df = pd.read_csv(archivo_empresas, sep=';', encoding='latin-1')
        except:
            # Si falla, probamos con comas por si acaso
            try:
                df = pd.read_csv(archivo_empresas, sep=',', encoding='utf-8')
            except:
                return None, pd.DataFrame() # Fallo total

    # 2. ALUMNI - Desencriptado y Limpieza
    try:
        if "encryption_key" in st.secrets:
            key = st.secrets["encryption_key"]
            cipher_suite = Fernet(key)
            with open('alumni_seguro.enc', 'rb') as file: encrypted_data = file.read()
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            
            try: df_alumni = pd.read_csv(io.BytesIO(decrypted_data), sep=';', encoding='utf-8')
            except: df_alumni = pd.read_csv(io.BytesIO(decrypted_data), sep=';', encoding='latin-1')

            # Limpiar nombres de columnas
            df_alumni.columns = [c.strip() for c in df_alumni.columns]
            
            # Formatear Texto (Mayúscula inicial)
            for col in ['Nombre', 'Cargo', 'jerarquía']:
                c = next((x for x in df_alumni.columns if x.lower() == col.lower()), None)
                if c: df_alumni[c] = df_alumni[c].astype(str).str.strip().str.title()
            
            # Limpiar nombre de empresa
            c_matriz = next((x for x in df_alumni.columns if 'informa' in x.lower()), 'nombre_matriz_einforma')
            if c_matriz in df_alumni.columns: 
                df_alumni[c_matriz] = df_alumni[c_matriz].astype(str).str.strip()

    except: pass
        
    return df, df_alumni

df_main, df_alumni = load_data()

# --- GESTIÓN DE ESTADO ---
if 'selected_empresa' not in st.session_state:
    st.session_state['selected_empresa'] = None

# --- SIDEBAR (BÚSQUEDA) ---
if df_main is not None:
    st.sidebar.header("🔍 Buscador")
    tab_empresa, tab_profesional = st.sidebar.tabs(["🏢 Empresa", "🧑‍💼 Profesional"])
    
    # 1. PESTAÑA EMPRESA
    with tab_empresa:
        st.write("")
        provincias = ["Todas"] + sorted(df_main['provincia'].dropna().unique().tolist())
        selected_provincia = st.selectbox("Provincia", provincias)
        search_term_emp = st.text_input("Nombre Empresa", placeholder="Ej: Caf")

        df_f = df_main.copy()
        if selected_provincia != "Todas":
            df_f = df_f[df_f['provincia'] == selected_provincia]
        if search_term_emp:
            df_f = df_f[df_f['Nombre'].astype(str).str.contains(search_term_emp, case=False, na=False)]

        lista = sorted(df_f['Nombre'].unique().tolist())
        if lista:
            sel = st.selectbox("Resultados:", lista)
            if st.button("Ver Análisis", use_container_width=True):
                st.session_state['selected_empresa'] = sel
                st.rerun()
        else:
            st.warning("Sin resultados.")

    # 2. PESTAÑA PROFESIONAL
    with tab_profesional:
        st.write("")
        if df_alumni.empty:
            st.warning("⚠️ Datos Alumni no disponibles.")
        else:
            col_nom = next((c for c in df_alumni.columns if c.lower() == 'nombre'), None)
            col_emp = next((c for c in df_alumni.columns if 'informa' in c.lower()), None)
            col_car = next((c for c in df_alumni.columns if c.lower() == 'cargo'), None)

            if col_nom:
                search_prof = st.text_input("Filtrar Nombre:", placeholder="Ej: Ignacio")
                
                if search_prof:
                    mask = df_alumni[col_nom].astype(str).str.contains(search_prof, case=False, na=False)
                    lista_prof = sorted(df_alumni[mask][col_nom].unique().tolist())
                else:
                    lista_prof = sorted(df_alumni[col_nom].head(50).unique().tolist())

                if lista_prof:
                    sel_prof = st.selectbox("Selecciona:", lista_prof, index=None, placeholder="Elige...")
                    
                    if sel_prof and col_emp:
                        d = df_alumni[df_alumni[col_nom] == sel_prof].iloc[0]
                        emp_p = d[col_emp]
                        cargo_p = d[col_car] if col_car else "N/A"
                        
                        st.markdown(f"""
                        <div class="profile-card">
                            <div class="profile-name">{sel_prof}</div>
                            <div class="profile-role">{cargo_p}</div>
                            <div class="profile-company">🏢 {emp_p}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("Ir a Empresa ->", key="go_prof", use_container_width=True):
                            st.session_state['selected_empresa'] = emp_p
                            st.rerun()
                elif search_prof:
                    st.warning("No encontrado.")

else:
    st.sidebar.error("❌ Error cargando archivo de empresas.")

# --- PANEL CENTRAL ---
selected_empresa = st.session_state['selected_empresa']

if selected_empresa and df_main is not None:
    row_data = df_main[df_main['Nombre'] == selected_empresa]
    if row_data.empty:
        try: row_data = df_main[df_main['Nombre'].str.contains(re.escape(selected_empresa), case=False, na=False)]
        except: pass

    if not row_data.empty:
        r = row_data.iloc[0]
        st.title(f"🏢 {get_val(r, 'Nombre')}")
        
        # 1. RESUMEN
        st.markdown('<div class="section-title">Resumen</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="kpi-card"><div class="kpi-value">{capitalize_first_letter(get_val(r, "provincia"))}</div><div class="kpi-label">UBICACIÓN</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi-card"><div class="kpi-value">{get_val(r, "veredicto_final")}</div><div class="kpi-label">CLASIFICACIÓN</div></div>', unsafe_allow_html=True)
        
        v_raw = get_val(r, "conclusion_sueldo_80k")
        v_clean = "".join(filter(str.isalnum, v_raw.split()[1])) if len(v_raw.split()) > 1 else "VIABLE"
        c3.markdown(f'<div class="kpi-card"><div class="kpi-value" style="color:{"#2E7D32" if "VIABLE" in v_clean else "#1F4E79"}">{v_clean}</div><div class="kpi-label">VIABILIDAD >80k</div></div>', unsafe_allow_html=True)
        
        st.write("")
        render_table(pd.DataFrame({
            "Ventas": [clean_number_format(get_val(r, 'ventas_estimado'))],
            "Empleados": [clean_number_format(get_val(r, 'numero_empleados'))],
            "Año": [get_val(r, 'ano_constitucion')],
            "Web": [get_val(r, 'web_oficial')]
        }))

        # 2. SECTOR & PROPIEDAD
        st.markdown('<div class="section-title">Negocio</div>', unsafe_allow_html=True)
        html_biz = f"""
        <div class="grid-2">
            <div class="content-box"><span class="box-header">Actividad</span><span class="box-text">{get_val(r, 'actividad_resumen')}</span></div>
            <div class="content-box">
                <span class="box-header">Propiedad</span>
                <span class="box-text"><b>Accionistas:</b> {get_val(r, 'propiedad_accionistas')}<br><br><b>PE:</b> {get_val(r, 'private_equity_firmas')}</span>
            </div>
        </div>
        """
        st.markdown(html_biz, unsafe_allow_html=True)

        # 3. TECH (DISEÑO VISUAL MEJORADO)
        st.markdown('<div class="section-title">Tecnología</div>', unsafe_allow_html=True)
        
        cto = get_val(r, 'cto_actual')
        ing = get_val(r, 'tamano_ing')
        
        st.markdown(f"""
        <div class="grid-2">
            <div class="tech-hero">
                <div class="tech-hero-label">CTO / Responsable</div>
                <div class="tech-hero-val">{cto}</div>
            </div>
            <div class="tech-hero">
                <div class="tech-hero-label">Equipo Ingeniería</div>
                <div class="tech-hero-val">{ing}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="grid-3">
            <div class="tech-card">
                <span class="tech-icon">🧠</span>
                <div class="tech-title">IA & Automatización</div>
                <div class="tech-text">{get_val(r, 'usa_inteligencia_artificial')}</div>
            </div>
            <div class="tech-card">
                <span class="tech-icon">☁️</span>
                <div class="tech-title">Infraestructura</div>
                <div class="tech-text">{get_val(r, 'plataforma_cloud')}</div>
            </div>
            <div class="tech-card">
                <span class="tech-icon">💻</span>
                <div class="tech-title">Perfil Técnico</div>
                <div class="tech-text">{get_val(r, 'perfil_txt')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 4. ALUMNI (DISEÑO KPI)
        st.markdown('<div class="section-title">Networking (Alumni)</div>', unsafe_allow_html=True)
        col_matriz = next((c for c in df_alumni.columns if 'informa' in c.lower()), None)
        
        if col_matriz and not df_alumni.empty:
            match = df_alumni[df_alumni[col_matriz] == str(selected_empresa).strip()]
            if match.empty:
                match = df_alumni[df_alumni[col_matriz].astype(str).str.contains(re.escape(str(selected_empresa).strip()), case=False, na=False)]
            
            if not match.empty:
                num = match['Nombre'].nunique()
                st.markdown(f"""
                <div style="background-color: #E8F5E9; border: 1px solid #2E7D32; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 20px;">
                    <div style="color: #2E7D32; font-size: 2rem; font-weight: 800;">{num}</div>
                    <div style="color: #1B5E20; font-weight: 700; text-transform: uppercase; font-size: 0.9rem; letter-spacing: 1px;">Contactos Encontrados</div>
                </div>
                """, unsafe_allow_html=True)

                t1, t2 = st.tabs(["📊 Desglose por Nivel", "📋 Lista Completa"])
                with t1:
                    if 'jerarquía' in match.columns:
                        try:
                            om = {'Top Management': 1, 'Middle Management': 2, 'Entry Level/Others': 3}
                            cts = match['jerarquía'].value_counts().reset_index()
                            cts.columns = ['Nivel', 'Total']
                            cts['s'] = cts['Nivel'].map(om).fillna(99)
                            render_table(cts.sort_values('s').drop('s', axis=1))
                        except: st.write(match['jerarquía'].value_counts())
                with t2:
                    cols = [c for c in ['Nombre', 'Cargo', 'jerarquía', 'url_linkedin'] if c in match.columns]
                    render_table(match[cols])
            else:
                st.info("No hay contactos alumni en esta empresa.")
        else:
            st.warning("Datos de alumni no disponibles.")
            
    else:
        st.error("Error cargando datos.")

# --- LANDING PAGE ---
else:
    st.markdown("""
    <div style="text-align: center; margin-top: 50px;">
        <h1 style="color: #1F4E79; font-size: 3rem;">🔍 Analizador de Empresas</h1>
        <p style="font-size: 1.2rem; color: #555;">Busca empresas y encuentra contactos clave.</p>
    </div>
    """, unsafe_allow_html=True)
    
    n_emp = len(df_main) if df_main is not None else 0
    n_alu = df_alumni['Nombre'].nunique() if not df_alumni.empty else 0
    
    c1, c2 = st.columns(2)
    c1.metric("🏢 Empresas Rastreadas", n_emp)
    c2.metric("🎓 Profesionales Alumni", n_alu)
    
    st.info("👈 **Para comenzar:** Abre el menú lateral.")
    
    if df_main is not None and not df_main.empty:
        st.markdown("### 🎲 O explora:")
        top = df_main.sample(min(3, len(df_main)))['Nombre'].tolist()
        cols = st.columns(len(top))
        for i, emp in enumerate(top):
            with cols[i]:
                if st.button(f"🔎 {emp}", key=f"btn_{i}", use_container_width=True):
                    st.session_state['selected_empresa'] = emp
                    st.rerun()