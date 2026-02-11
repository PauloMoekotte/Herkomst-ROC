import streamlit as st
import pandas as pd
import plotly.express as px

# Pagina configuratie
st.set_page_config(page_title="Dashboard Herkomst MBO Twente", layout="wide")

st.title("📊 Monitor Herkomst MBO Twente")
st.markdown("""
Dit dashboard analyseert de instroom van mbo-studenten vanuit het VO naar regionale mbo-instellingen. 
Gebruik de zijbalk om nieuwe DUO-data toe te voegen.
""")

# --- FUNCTIES VOOR DATA LADEN ---
@st.cache_data
def load_initial_data(files):
    all_data = []
    for f in files:
        try:
            # DUO bestanden gebruiken vaak ';' als delimiter en latin-1 of utf-8 encoding
            # We proberen eerst utf-8, dan latin-1
            try:
                df = pd.read_csv(f, sep=';', encoding='utf-8')
            except UnicodeDecodeError:
                f.seek(0) # Reset file pointer
                df = pd.read_csv(f, sep=';', encoding='latin-1')
            
            all_data.append(df)
        except Exception as e:
            # HERSTELD: f.name ipv file.name om NameError te voorkomen
            st.error(f"Fout bij laden van {f.name}: {e}")
    
    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        # Zorg dat 'Aantal' numeriek is en vervang NaN door 0
        if 'Aantal' in combined.columns:
            combined['Aantal'] = pd.to_numeric(combined['Aantal'], errors='coerce').fillna(0)
        return combined
    return pd.DataFrame()

# --- ZIJBALK: DATA BEHEER ---
st.sidebar.header("Data Beheer")
uploaded_files = st.sidebar.file_uploader(
    "Upload DUO CSV-bestanden (2022, 2023, 2024...)", 
    type="csv", 
    accept_multiple_files=True
)

# Indien geen bestanden geüpload, toon instructie
if not uploaded_files:
    st.info("Upload de herkomst-bestanden in de zijbalk om de analyse te starten.")
    st.stop()

df = load_initial_data(uploaded_files)

if df.empty:
    st.warning("De geüploade bestanden konden niet worden verwerkt of zijn leeg.")
    st.stop()

# --- FILTERS ---
st.sidebar.header("Filters")
# Check of vereiste kolommen aanwezig zijn
needed_cols = ['Jaar', 'MBO naam instelling', 'Aantal']
if not all(col in df.columns for col in needed_cols):
    st.error(f"De dataset mist cruciale kolommen. Vereist: {needed_cols}")
    st.stop()

jaren = sorted(df['Jaar'].unique())
geselecteerde_jaren = st.sidebar.multiselect("Selecteer Jaren", jaren, default=jaren)

instellingen = sorted(df['MBO naam instelling'].unique())
# Slimme default selectie voor Twente regio
default_mbo = [inst for inst in ["ROC van Twente", "Zone.college"] if inst in instellingen]
if not default_mbo:
    default_mbo = instellingen[:2]

geselecteerde_instellingen = st.sidebar.multiselect(
    "MBO Instellingen", 
    instellingen, 
    default=default_mbo
)

# Filter de dataset
filtered_df = df[
    (df['Jaar'].isin(geselecteerde_jaren)) & 
    (df['MBO naam instelling'].isin(geselecteerde_instellingen))
]

# --- KPI'S ---
total_students = filtered_df['Aantal'].sum()
col1, col2, col3 = st.columns(3)
col1.metric("Totaal Instroom (selectie)", f"{int(total_students):,}")
col2.metric("Aantal Instellingen", len(geselecteerde_instellingen))
col3.metric("Aantal Cohorten", len(geselecteerde_jaren))

# --- VISUALISATIES ---

tab1, tab2, tab3 = st.tabs(["Trends & Marktaandeel", "Toelevering VO", "Niveau & Leerweg"])

with tab1:
    st.subheader("Trend van Instroom per Jaar")
    if not filtered_df.empty:
        trend_data = filtered_df.groupby(['Jaar', 'MBO naam instelling'])['Aantal'].sum().reset_index()
        fig_trend = px.line(
            trend_data, x='Jaar', y='Aantal', color='MBO naam instelling',
            markers=True, title="Instroom per mbo-instelling over de jaren"
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.write("Geen data beschikbaar voor de geselecteerde filters.")

with tab2:
    st.subheader("Top Toeleverende VO-scholen")
    if not filtered_df.empty and 'Herkomst naam instelling' in filtered_df.columns:
        vo_data = filtered_df.groupby('Herkomst naam instelling')['Aantal'].sum().sort_values(ascending=False).head(15).reset_index()
        fig_vo = px.bar(
            vo_data, x='Aantal', y='Herkomst naam instelling', orientation='h',
            title="Top 15 Toeleverende Scholen",
            color='Aantal', color_continuous_scale='Viridis'
        )
        fig_vo.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_vo, use_container_width=True)

with tab3:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Verdeling per MBO Niveau")
        if not filtered_df.empty and 'MBO niveau' in filtered_df.columns:
            lvl_data = filtered_df.groupby('MBO niveau')['Aantal'].sum().reset_index()
            fig_pie = px.pie(lvl_data, values='Aantal', names='MBO niveau', hole=0.4, title="Instroom per Niveau")
            st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_b:
        st.subheader("Verdeling Leerweg (BOL/BBL)")
        if not filtered_df.empty and 'MBO leerweg' in filtered_df.columns:
            leerweg_data = filtered_df.groupby('MBO leerweg')['Aantal'].sum().reset_index()
            fig_leer = px.bar(leerweg_data, x='MBO leerweg', y='Aantal', title="BOL vs BBL")
            st.plotly_chart(fig_leer, use_container_width=True)

# --- TABEL WEERGAVE ---
st.divider()
st.subheader("Gedetailleerde Gegevens (eerste 100 rijen)")
st.dataframe(filtered_df.head(100), use_container_width=True)

# Download knop
if not filtered_df.empty:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download gefilterde data als CSV",
        csv,
        "gefilterde_mbo_data.csv",
        "text/csv",
        key='download-csv'
    )
