import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

# --- CONFIGURATIE ---
st.set_page_config(
    page_title="ROC van Twente | Arbeidsmarktmonitor 2025",
    page_icon="📊",
    layout="wide"
)

# Functie om getallen op te schonen (komma naar punt voor berekeningen)
def clean_numeric(val):
    if isinstance(val, str):
        val = val.replace(',', '.')
        try:
            return float(val)
        except:
            return None
    return val

@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        try:
            content = uploaded_file.getvalue().decode('utf-8')
            df = pd.read_csv(io.StringIO(content), sep=';')
            
            # Data opschonen op basis van kolomnamen in de geüploade CSV
            if 'waarde' in df.columns:
                df['waarde'] = df['waarde'].apply(clean_numeric)
            if 'gemiddelde' in df.columns:
                df['gemiddelde'] = df['gemiddelde'].apply(clean_numeric)
            return df
        except Exception as e:
            st.error(f"Fout bij het inlezen van het bestand: {e}")
    return None

# --- SIDEBAR ---
st.sidebar.header("📁 Data & Beheer")
st.sidebar.markdown("Upload hier de CBS-export om de monitor te verversen.")

uploaded_file = st.sidebar.file_uploader(
    "Upload CBS data (CSV)", 
    type=["csv"],
    help="Zorg voor een CSV-bestand met ';' als scheidingsteken."
)

df = load_data(uploaded_file)

if df is not None:
    st.sidebar.header("🔍 Filters")
    
    # Filter opties op basis van de dataset
    jaren = sorted(df['uitstroomjaar'].unique())
    selected_year = st.sidebar.selectbox("Selecteer Uitstroomjaar", jaren, index=len(jaren)-1)
    
    niveaus = st.sidebar.multiselect("Niveau", options=df['niveau'].unique(), default=df['niveau'].unique())
    leerwegen = st.sidebar.multiselect("Leerweg", options=df['leerweg'].unique(), default=df['leerweg'].unique())

    # Filteren van de dataset
    mask = (df['uitstroomjaar'] == selected_year) & \
           (df['niveau'].isin(niveaus)) & \
           (df['leerweg'].isin(leerwegen))
    filtered_df = df[mask]

    # --- HOOFDSCHERM ---
    st.title("📊 Arbeidsmarktmonitor ROC van Twente")
    st.info(f"Gegevens op basis van cohort: **{selected_year}**")

    # --- KPI SECTIE ---
    kpi1, kpi2, kpi3 = st.columns(3)
    
    # KPI 1: Uurloon Niveau 4
    loon_filter = (filtered_df['naam'] == 'uurloon werknemer') & (filtered_df['niveau'] == 'niveau 4')
    avg_loon = filtered_df[loon_filter]['gemiddelde'].mean()
    kpi1.metric("Gem. Uurloon (Niv 4)", f"€ {avg_loon:.2f}" if not pd.isna(avg_loon) else "N/A")

    # KPI 2: Doorstroom Cross-over
    doorstroom_filter = (filtered_df['domein'] == 'cross-over') & (filtered_df['naam'] == 'doorstroom')
    avg_doorstroom = filtered_df[doorstroom_filter]['waarde'].mean()
    kpi2.metric("Doorstroom Cross-over", f"{avg_doorstroom:.1f}%" if not pd.isna(avg_doorstroom) else "N/A")

    # KPI 3: Uitstroom Volume
    uitstroom_vol = filtered_df[filtered_df['naam'] == 'uitstroom']['waarde'].sum()
    kpi3.metric("Totaal Uitstroom", f"{int(uitstroom_vol)} gediplomeerden")

    # --- VISUALISATIES ---
    tab1, tab2, tab3 = st.tabs(["📈 Trends & Loon", "🧬 Cross-over Analyse", "📋 Datatabel"])

    with tab1:
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader("Uurloon trend per Niveau")
            df_loon_trend = df[df['naam'] == 'uurloon werknemer'].groupby(['uitstroomjaar', 'niveau'])['gemiddelde'].mean().reset_index()
            fig_loon = px.line(df_loon_trend, x='uitstroomjaar', y='gemiddelde', color='niveau', markers=True, 
                               color_discrete_sequence=px.colors.qualitative.Prism)
            fig_loon.update_layout(yaxis_title="Euro (€)", hovermode="x unified")
            st.plotly_chart(fig_loon, use_container_width=True)

        with col_b:
            st.subheader("Verdeling Uitstroom per Domein")
            df_domein = filtered_df[filtered_df['naam'] == 'uitstroom'].groupby('domein')['waarde'].sum().reset_index()
            fig_domein = px.pie(df_domein, values='waarde', names='domein', hole=.4, 
                                color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_domein, use_container_width=True)

    with tab2:
        st.subheader("Focus: Cross-over Opleidingen")
        cross_df = filtered_df[filtered_df['domein'] == 'cross-over']
        
        if not cross_df.empty:
            # Vergelijking uitstroom vs doorstroom
            fig_cross = px.bar(
                cross_df[cross_df['naam'].isin(['uitstroom', 'doorstroom'])], 
                x='beroepsopleiding', y='waarde', color='naam', barmode='group',
                title="Aantallen en percentages per opleiding",
                color_discrete_map={'uitstroom': '#1f77b4', 'doorstroom': '#ff7f0e'}
            )
            st.plotly_chart(fig_cross, use_container_width=True)
            
            st.markdown("""
            **Analyse:** Zoals beschreven in de rapportage zien we bij de cross-over domeinen een hoge doorstroomintentie. 
            Dit bevestigt de noodzaak voor goede aansluiting op het HBO.
            """)
        else:
            st.warning("Geen cross-over data beschikbaar voor de huidige selectie.")

    with tab3:
        st.subheader("Gefilterde Dataset")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
    # --- DYNAMISCH TOEVOEGEN VAN GRAFIEKEN ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🛠️ Custom Visualisatie")
    x_axis = st.sidebar.selectbox("Kies X-as", options=df.columns, index=0)
    y_axis = st.sidebar.selectbox("Kies Y-as", options=['waarde', 'gemiddelde'])
    
    if st.sidebar.button("Voeg Custom Grafiek toe"):
        st.markdown("---")
        st.subheader(f"Custom Analyse: {x_axis} vs {y_axis}")
        fig_custom = px.box(filtered_df, x=x_axis, y=y_axis, color='niveau')
        st.plotly_chart(fig_custom, use_container_width=True)

else:
    st.warning("⚠️ Upload het bestand 'Data_mbo_arbeidsmarktpositie_2025_ROCvT.csv' om de monitor te starten.")
    st.markdown("""
    ### Hoe werkt dit?
    1. Pak de CSV-export van het CBS.
    2. Upload deze via het menu aan de linkerkant.
    3. De applicatie verwerkt automatisch de trends, uurlonen en doorstroomcijfers zoals gedefinieerd in de managementrapportage.
    """)
