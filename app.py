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

# --- 2. CSS "BULLETPROOF" PARA MÓVIL Y ESTILOS GENERALES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; font-size: 16px; color: #2c3e50; }

    /* --- ESTILO RADICAL PARA EL BOTÓN DE MENÚ EN MÓVIL --- */
    /* Forzamos que el botón que Streamlit ya crea sea visible y bonito */
    @media (max-width: 768px) {
        /* El botón nativo de Streamlit */
        button[data-testid="stSidebarCollapse"] {
            display: flex !important;
            position: fixed !important;
            top: 15px !important;
            left: 15px !important;
            background-color: #1F4E79 !important;
            color: white !important;
            width: 50px !important;
            height: 50px !important;
            border-radius: 50% !important;
            z-index: 9999999 !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
            border: 2px solid white !important;
            justify-content: center !important;
            align-items: center !important;
        }
        
        /* Forzamos que el icono dentro del botón sea blanco y grande */
        button[data-testid="stSidebarCollapse"] svg {
            fill: white !important;
            width: 25px !important;
            height: 25px !important;
        }

        /* Espacio para que el título no choque con el botón */
        .hero-title {
            margin-top: 40px !important;
            font-size: 2rem !important;
        }
    }

    /* --- ESTILOS DE COMPONENTES --- */
    .section-title { color: #1F4E79; font-size: 1.8rem; font-weight: 700; margin-top: 2.5rem; border-bottom: 4px solid #DAE9F7; padding-bottom: 5px; }
    
    .hero-title { color: #1F4E79; font-size: 3rem; font-weight: 800; text-align: center; margin-bottom: 10px; padding-top: 20px; }
    .hero-subtitle { color: #555; font-size: 1.2rem; text-align: center; margin-bottom: 40px; }
    
    .feature-card { 
        background-color: white; border-radius: 12px; padding: 25px; text-align: center; 
        border: 1px solid #eee; box-shadow: 0 4px 12px rgba(0,0,0,0.05); height: 100%;
    }
    .feature-icon { font-size: 2.5rem; margin-bottom: 15px; display: block; }
    .feature-title { color: #1F4E79; font-weight: 700; font-size: 1.1rem; margin-bottom: 10px; }

    .kpi-card { background-color: #DAE9F7; border-radius: 12px; padding: 20px; text-align: center; border: 2px solid #1F4E79; height: 100%; display: flex; flex-direction: column; justify-content: center; }
    .kpi-value { color: #1F4E79; font-size: 2rem; font-weight: 800; }
    .kpi-label { font-size: 0.85rem; text-transform: uppercase; font-weight: 700; color: #1F4E79; }

    .search-alert { background-color: #e3f2fd; border-left: 4px solid #1F4E79; padding: 12px; border-radius: 4px; color: #0d47a1; margin-bottom: 15px; }
    .search-count { font-weight: 700; }

    .custom-table { width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 8px; overflow: hidden; border: 1px solid #eee; }
    .custom-table th { background-color: #1F4E79; color: white; padding: 12px; text-align: center; }
    .custom-table td { border-bottom: 1px solid #f0f0f0; padding: 12px; text-align: center; }
    .table-container { overflow-x: auto; border-radius: 8px; margin-bottom: 20px; }

    .profile-card { background-color: #f8f9fa; border-left: 5px solid #1F4E79; padding: 15px; border-radius: 8px; margin-top: 15px; }
    .profile-name { font-weight: 800; color: #1F4E79; }
    
    .grid-2, .grid-3 { display: grid; gap: 20px; margin-bottom: 20px; }
    .grid-2 { grid-template-columns: 1fr 1fr; }
    .grid-3 { grid-template-columns: 1fr 1fr 1fr; }
    @media (max-width: 768px) { .grid-2, .grid-3 { grid-template-columns: 1fr; } }
    </style>
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
    try: df = pd.read_csv(archivo_empresas, sep=';', encoding='utf-8')
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

# --- 5. SIDEBAR (BUSCADOR) ---
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
                search_prof = st.text_input("Filtrar por Nombre:", placeholder="Ej: Asier")
                lista_prof = sorted(df_alumni[df_alumni[col_nom].astype(str).str.contains(search_prof, case=False, na=False)][col_nom].unique().tolist()) if search_prof else []
                match_count = len(lista_prof)
                sel_prof = None
                
                if search_prof:
                    if match_count > 1:
                        st.markdown(f'<div class="search-alert">🔍 {match_count} coincidencias. Selecciona:</div>', unsafe_allow_html=True)
                        sel_prof = st.selectbox("Resultados:", lista_prof, index=None, placeholder="Elige...")
                    elif match_count == 1:
                        st.success("✅ ¡Encontrado!")
                        sel_prof = lista_prof[0]
                        st.selectbox("Resultados:", lista_prof, index=0, disabled=True)
                    else: st.error("❌ Sin resultados.")

                if sel_prof and col_emp:
                    d = df_alumni[df_alumni[col_nom] == sel_prof].iloc[0]
                    emp_p = d[col_emp]
                    cargo_p = d[col_car] if col_car else "N/A"
                    st.markdown(f'<div class="profile-card"><div class="profile-name">{sel_prof}</div><div class="profile-role">{cargo_p}</div><div class="profile-company">🏢 {emp_p}</div></div>', unsafe_allow_html=True)
                    if st.button("Ir a Empresa ➔", use_container_width=True):
                        st.session_state['selected_empresa'] = emp_p
                        st.rerun()

# --- 6. PANEL CENTRAL ---
selected_empresa = st.session_state.get('selected_empresa')

if selected_empresa and df_main is not None:
    row_data = df_main[df_main['Nombre'] == selected_empresa]
    if row_data.empty:
        try: row_data = df_main[df_main['Nombre'].str.contains(re.escape(str(selected_empresa)), case=False, na=False)]
        except: pass

    if not row_data.empty:
        # --- CASO 1: EMPRESA EN DB PRINCIPAL ---
        r = row_data.iloc[0]
        st.title(f"🏢 {get_val(r, 'Nombre')}")
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
    else:
        # --- CASO 2: FALLBACK ALUMNI (No hay datos financieros) ---
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
                render_table(al_match[['Nombre', col_emp, col_car, col_area, col_cat]].rename(columns={col_emp: 'Empresa DBA', col_area: 'Área', col_cat: 'Categoría'}))

else:
    # --- PÁGINA DE INICIO (HOME) ---
    st.markdown('<div class="hero-title">Analizador de Empresas 360°</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Inteligencia de mercado y red de contactos alumni.</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns([1, 2, 2, 1])
    with m2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{len(df_main) if df_main is not None else 0}</div><div class="kpi-label">EMPRESAS ANALIZADAS</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{df_alumni["Nombre"].nunique() if not df_alumni.empty else 0}</div><div class="kpi-label">CONTACTOS ALUMNI</div></div>', unsafe_allow_html=True)

    st.write("")
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="feature-card"><span class="feature-icon">📊</span><div class="feature-title">Análisis Financiero</div><p>Facturación y viabilidad.</p></div>', unsafe_allow_html=True)
    c2.markdown('<div class="feature-card"><span class="feature-icon">💻</span><div class="feature-title">Stack Tecnológico</div><p>Equipos IT y responsables.</p></div>', unsafe_allow_html=True)
    c3.markdown('<div class="feature-card"><span class="feature-icon">🤝</span><div class="feature-title">Red Alumni</div><p>Cargos y jerarquías clave.</p></div>', unsafe_allow_html=True)