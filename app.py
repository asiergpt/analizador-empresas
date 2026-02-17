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

# --- 2. CSS PREMIUM & ELEMENTOS DINÁMICOS (HOME, MÓVIL, ALERTAS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; font-size: 16px; color: #2c3e50; }
    
    /* --- BOTÓN FLOTANTE MÓVIL (TIPO HAMBURGUESA) --- */
    @media (max-width: 768px) {
        .floating-menu-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background-color: #1F4E79;
            color: white !important;
            width: 65px;
            height: 65px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            z-index: 999999;
            cursor: pointer;
            border: 2px solid #DAE9F7;
            text-decoration: none;
            transition: all 0.3s ease;
        }
        .floating-menu-btn:active { transform: scale(0.9) rotate(10deg); }
        .burger-icon { font-size: 28px; }
        
        .menu-label-tag {
            position: fixed;
            bottom: 45px;
            right: 105px;
            background: #1F4E79;
            color: white;
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 700;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            letter-spacing: 1px;
        }
    }
    @media (min-width: 769px) {
        .floating-menu-btn, .menu-label-tag { display: none; }
    }

    /* Títulos y Secciones */
    .section-title { color: #1F4E79; font-size: 1.8rem; font-weight: 700; margin-top: 2.5rem; border-bottom: 4px solid #DAE9F7; padding-bottom: 5px; }
    
    /* Home Estilizada */
    .hero-title { color: #1F4E79; font-size: 3rem; font-weight: 800; text-align: center; margin-bottom: 10px; padding-top: 40px; }
    .hero-subtitle { color: #555; font-size: 1.2rem; text-align: center; margin-bottom: 40px; }
    
    .feature-card { 
        background-color: white; border-radius: 12px; padding: 25px; text-align: center; 
        border: 1px solid #eee; box-shadow: 0 4px 12px rgba(0,0,0,0.05); height: 100%;
        transition: transform 0.3s ease;
    }
    .feature-card:hover { transform: translateY(-5px); border-color: #DAE9F7; }
    .feature-icon { font-size: 2.5rem; margin-bottom: 15px; display: block; }
    .feature-title { color: #1F4E79; font-weight: 700; font-size: 1.1rem; margin-bottom: 10px; }
    .feature-desc { color: #666; font-size: 0.95rem; line-height: 1.5; }

    /* KPIs */
    .kpi-card { background-color: #DAE9F7; border-radius: 12px; padding: 20px; text-align: center; border: 2px solid #1F4E79; box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: 100%; display: flex; flex-direction: column; justify-content: center; }
    .kpi-value { color: #1F4E79; font-size: 2.2rem; font-weight: 800; line-height: 1.2; }
    .kpi-label { font-size: 0.85rem; text-transform: uppercase; font-weight: 700; color: #1F4E79; margin-top: 5px; letter-spacing: 1px; }

    /* Alertas Buscador */
    .search-alert { background-color: #e3f2fd; border-left: 4px solid #1F4E79; padding: 12px; border-radius: 4px; color: #0d47a1; font-size: 0.9rem; margin-bottom: 15px; }
    .search-count { font-weight: 700; color: #1F4E79; }

    /* Tarjetas Tech */
    .tech-hero { background-color: #1F4E79; color: white; border-radius: 10px; padding: 20px; text-align: center; }
    .tech-hero-val { font-size: 1.3rem; font-weight: 700; }
    .tech-card { background-color: white; border: 1px solid #e0e0e0; border-top: 4px solid #1F4E79; border-radius: 10px; padding: 20px; height: 100%; }

    /* Tablas */
    .custom-table { width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 8px; overflow: hidden; border: 1px solid #eee; }
    .custom-table th { background-color: #1F4E79; color: white; padding: 12px; text-align: center; }
    .custom-table td { border-bottom: 1px solid #f0f0f0; padding: 12px; text-align: center; }
    .table-container { overflow-x: auto; border-radius: 8px; margin-bottom: 20px; }

    /* Profile Card */
    .profile-card { background-color: #f8f9fa; border-left: 5px solid #1F4E79; padding: 15px; border-radius: 8px; margin-top: 15px; }
    .profile-name { font-weight: 800; color: #1F4E79; font-size: 1.1rem; }
    
    /* Layouts */
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
    .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px; }
    @media (max-width: 768px) { .grid-2, .grid-3 { grid-template-columns: 1fr; } }
    </style>

    <div class="menu-label-tag">BUSCAR</div>
    <div class="floating-menu-btn" onclick="const b=window.parent.document.querySelector('button[aria-label=\'Open sidebar\']'); if(b) b.click();">
        <span class="burger-icon">🔍</span>
    </div>
""", unsafe_allow_html=True)

# --- 3. UTILIDADES ---
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
            for col in ['Nombre', 'Cargo', 'jerarquía', 'función', 'funcion']:
                c = next((x for x in df_alumni.columns if x.lower() == col.lower()), None)
                if c: df_alumni[c] = df_alumni[c].astype(str).str.strip().str.title()
    except: pass
    return df, df_alumni

df_main, df_alumni = load_data()

# --- 5. GESTIÓN DE ESTADO ---
if 'selected_empresa' not in st.session_state: st.session_state['selected_empresa'] = None

# --- 6. SIDEBAR (BUSCADOR MEJORADO) ---
if df_main is not None:
    st.sidebar.header("🔍 Buscador")
    tab_empresa, tab_profesional = st.sidebar.tabs(["🏢 Empresa", "🧑‍💼 Profesional"])
    
    with tab_empresa:
        st.write("")
        provincias = ["Todas"] + sorted(df_main['provincia'].dropna().unique().tolist())
        selected_provincia = st.selectbox("Provincia", provincias)
        search_term_emp = st.text_input("Nombre Empresa", placeholder="Ej: Caf")
        df_f = df_main.copy()
        if selected_provincia != "Todas": df_f = df_f[df_f['provincia'] == selected_provincia]
        if search_term_emp: df_f = df_f[df_f['Nombre'].astype(str).str.contains(search_term_emp, case=False, na=False)]
        lista = sorted(df_f['Nombre'].unique().tolist())
        if lista:
            sel = st.selectbox("Resultados:", lista)
            if st.button("Ver Análisis", use_container_width=True):
                st.session_state['selected_empresa'] = sel
                st.rerun()
        else: st.warning("Sin resultados.")

    with tab_profesional:
        st.write("")
        if df_alumni.empty: st.warning("Datos no disponibles.")
        else:
            col_nom = next((c for c in df_alumni.columns if c.lower() == 'nombre'), None)
            col_emp = next((c for c in df_alumni.columns if 'informa' in c.lower()), None)
            col_car = next((c for c in df_alumni.columns if c.lower() == 'cargo'), None)

            if col_nom:
                search_prof = st.text_input("Filtrar por Nombre:", placeholder="Ej: Dorronsoro")
                
                # Filtrar lista
                lista_prof = []
                if search_prof:
                    mask = df_alumni[col_nom].astype(str).str.contains(search_prof, case=False, na=False)
                    lista_prof = sorted(df_alumni[mask][col_nom].unique().tolist())
                
                match_count = len(lista_prof)
                sel_prof = None
                
                if search_prof:
                    if match_count > 1:
                        st.markdown(f'<div class="search-alert">🔍 He encontrado <span class="search-count">{match_count}</span> coincidencias. Selecciona una:</div>', unsafe_allow_html=True)
                        sel_prof = st.selectbox("Selecciona:", lista_prof, index=None, placeholder="Elige un profesional...")
                    elif match_count == 1:
                        st.success("✅ ¡Contacto único encontrado!")
                        sel_prof = lista_prof[0]
                        st.selectbox("Selecciona:", lista_prof, index=0, disabled=True)
                    else: st.error("❌ No hay resultados.")

                if sel_prof and col_emp:
                    d = df_alumni[df_alumni[col_nom] == sel_prof].iloc[0]
                    emp_p = d[col_emp]
                    cargo_p = d[col_car] if col_car else "N/A"
                    st.markdown(f'<div class="profile-card"><div class="profile-name">{sel_prof}</div><div class="profile-role">{cargo_p}</div><div class="profile-company">🏢 {emp_p}</div></div>', unsafe_allow_html=True)
                    if st.button("Ir a Empresa ➔", use_container_width=True):
                        st.session_state['selected_empresa'] = emp_p
                        st.rerun()
else: st.sidebar.error("❌ Error archivo empresas.")

# --- 7. PANEL CENTRAL ---
selected_empresa = st.session_state['selected_empresa']
if str(selected_empresa).lower() == 'nan': selected_empresa = None

if selected_empresa and df_main is not None:
    # 1. Intentar buscar en DB Principal
    row_data = df_main[df_main['Nombre'] == selected_empresa]
    if row_data.empty:
        try: row_data = df_main[df_main['Nombre'].str.contains(re.escape(selected_empresa), case=False, na=False)]
        except: pass

    # --- CASO: EMPRESA ENCONTRADA EN DB PRINCIPAL ---
    if not row_data.empty:
        r = row_data.iloc[0]
        st.title(f"🏢 {get_val(r, 'Nombre')}")
        
        # Resumen KPIs
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

        # Negocio y Tecnología
        st.markdown('<div class="section-title">Tecnología</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="grid-2"><div class="tech-hero"><div class="tech-hero-label">CTO</div><div class="tech-hero-val">{get_val(r, "cto_actual")}</div></div><div class="tech-hero"><div class="tech-hero-label">Ingeniería</div><div class="tech-hero-val">{get_val(r, "tamano_ing")}</div></div></div>', unsafe_allow_html=True)
        
        # Alumni
        st.markdown('<div class="section-title">Networking (Alumni)</div>', unsafe_allow_html=True)
        col_matriz = next((c for c in df_alumni.columns if 'informa' in c.lower()), None)
        if col_matriz:
            match = df_alumni[df_alumni[col_matriz].astype(str).str.contains(re.escape(str(selected_empresa)), case=False, na=False)]
            if not match.empty:
                st.success(f"Encontrados {match['Nombre'].nunique()} contactos.")
                render_table(match[['Nombre', 'Cargo', 'jerarquía']].rename(columns={'jerarquía':'Categoría'}))
            else: st.info("No hay contactos alumni.")

    # --- CASO: EMPRESA NO EN DB PRINCIPAL (FALLBACK TABLA DBA) ---
    else:
        st.title(f"🏢 {selected_empresa}")
        st.error("❌ No se disponen de datos financieros/estructurales para esa empresa particular.")
        
        if not df_alumni.empty:
            col_emp = next((c for c in df_alumni.columns if 'informa' in c.lower()), 'Empresa')
            col_car = next((c for c in df_alumni.columns if c.lower() == 'cargo'), 'Cargo')
            col_area = next((c for c in df_alumni.columns if 'funcion' in c.lower() or 'función' in c.lower()), 'Área')
            col_cat = next((c for c in df_alumni.columns if 'jerarquía' in c.lower()), 'Categoría')
            
            al_match = df_alumni[df_alumni[col_emp].astype(str).str.strip() == str(selected_empresa).strip()]
            if not al_match.empty:
                st.markdown("### 📋 Datos disponibles en fichero Alumni (DBA)")
                df_dba = al_match[['Nombre', col_emp, col_car, col_area, col_cat]].copy()
                df_dba.rename(columns={col_emp: 'Empresa (DBA)', col_area: 'Área', col_cat: 'Categoría'}, inplace=True)
                render_table(df_dba)
            else: st.warning("No se encontraron registros en el fichero de Alumni.")

else:
    # --- 8. PÁGINA DE INICIO (HOME) ---
    st.markdown('<div class="hero-title">Analizador de Empresas 360°</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Inteligencia de mercado y red de contactos alumni en una sola plataforma.</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns([1, 2, 2, 1])
    with m2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{len(df_main) if df_main is not None else 0}</div><div class="kpi-label">EMPRESAS ANALIZADAS</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{df_alumni["Nombre"].nunique() if not df_alumni.empty else 0}</div><div class="kpi-label">CONTACTOS ALUMNI</div></div>', unsafe_allow_html=True)

    st.write("")
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="feature-card"><span class="feature-icon">📊</span><div class="feature-title">Análisis Financiero</div><p class="feature-desc">Facturación, empleados y viabilidad económica real.</p></div>', unsafe_allow_html=True)
    c2.markdown('<div class="feature-card"><span class="feature-icon">💻</span><div class="feature-title">Stack Tecnológico</div><p class="feature-desc">Descubre quién lidera la tecnología y sus equipos IT.</p></div>', unsafe_allow_html=True)
    c3.markdown('<div class="feature-card"><span class="feature-icon">🤝</span><div class="feature-title">Red Alumni</div><p class="feature-desc">Localiza ex-compañeros por cargo y jerarquía.</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.info("👈 **Para comenzar:** Abre el buscador en el lateral (o pulsa el botón 🔍 en móvil).")