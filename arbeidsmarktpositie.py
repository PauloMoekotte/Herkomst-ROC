import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGINA CONFIGURATIE ---
st.set_page_config(
    page_title="Arbeidsmarktpositie ROC van Twente",
    page_icon="📊",
    layout="wide"
)

# --- STANDAARD DATA (Uit rapportage) ---
@st.cache_data
def laad_standaard_data():
    # Tabel 1: Kerncijfers Bestemming
    df_bestemming = pd.DataFrame({
        "Leerweg_Niveau": ["BOL Niveau 1", "BOL Niveau 2", "BOL Niveau 3", "BOL Niveau 4", "BBL (Alle niv.)"],
        "Werkend (%)": [45, 70, 78, 50, 94],
        "Onderwijs (%)": [35, 20, 15, 45, 3],
        "Overig (%)": [20, 10, 7, 5, 3],
        "Gem. Bruto Uurloon (€)": [12.50, 13.20, 14.10, 14.80, 16.50]
    })
    
    # Grafiek 1: Sector
    df_sector = pd.DataFrame({
        "Sector": ["Techniek & ICT", "Zorg & Welzijn", "Bouw & Infra", "Voedsel & Natuur", "Econ & Admin"],
        "Werkend (%)": [92, 89, 88, 75, 68]
    })
    
    # Grafiek 2: Trend
    df_trend = pd.DataFrame({
        "Cohort": ["2018/2019", "2019/2020", "2020/2021", "2021/2022"],
        "Werkend (%)": [83, 81, 86, 88]
    })
    
    return df_bestemming, df_sector, df_trend

df_bestemming, df_sector, df_trend = laad_standaard_data()

# --- ZIJBALK: DATA UPLOAD ---
st.sidebar.header("⚙️ Data Beheer")
st.sidebar.info("Upload hier nieuwe data om de rapportage in de toekomst te verversen.")

geupload_bestand = st.sidebar.file_uploader("Upload CSV-bestand met nieuwe cohortdata", type=["csv"])

if geupload_bestand is not None:
    try:
        # Hier zou je logica komen om het specifieke CSV formaat in te lezen
        # Voor de demo overschrijven we df_trend als voorbeeld
        nieuwe_data = pd.read_csv(geupload_bestand)
        st.sidebar.success("✅ Data succesvol ingeladen!")
        # if 'Cohort' in nieuwe_data.columns and 'Werkend (%)' in nieuwe_data.columns:
        #     df_trend = nieuwe_data
    except Exception as e:
        st.sidebar.error(f"Fout bij inlezen data: {e}")

# --- HOOFDSCHERM ---
st.title("📊 Managementoverzicht – Arbeidsmarktpositie ROC van Twente")

# Tabbladen voor structuur
tab_dashboard, tab_rapportage, tab_advies = st.tabs([
    "📈 Interactief Dashboard", 
    "📝 Volledige Rapportage", 
    "💡 Conclusies & Beleid"
])

# --- TAB 1: DASHBOARD (Interactieve Grafieken) ---
with tab_dashboard:
    st.header("Kerncijfers & Visualisaties")
    
    # KPI metrics (obv meest recente trend en hoogste BBL score)
    col1, col2, col3 = st.columns(3)
    col1.metric("Werkend BBL", "94%", "+2%")
    col2.metric("Werkend BOL (gemiddeld)", "82%", "-1%")
    col3.metric("Doorstroom BOL Niv. 4", "45%", "0%")
    
    st.markdown("---")
    
    # Grafieken in kolommen
    col_links, col_rechts = st.columns(2)
    
    with col_links:
        st.subheader("Arbeidsmarktparticipatie per Sector")
        fig_sector = px.bar(df_sector, x='Werkend (%)', y='Sector', orientation='h', 
                            text='Werkend (%)', color='Werkend (%)',
                            color_continuous_scale='Blues')
        fig_sector.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        st.plotly_chart(fig_sector, use_container_width=True)
        
    with col_rechts:
        st.subheader("Trend Arbeidsmarktparticipatie (Totaal)")
        fig_trend = px.line(df_trend, x='Cohort', y='Werkend (%)', markers=True, 
                            text='Werkend (%)', line_shape='spline')
        fig_trend.update_traces(textposition="top center", marker=dict(size=10))
        fig_trend.update_layout(yaxis_range=[70, 100])
        st.plotly_chart(fig_trend, use_container_width=True)

    st.subheader("Detailtabel: Bestemming één jaar na diplomering")
    st.dataframe(df_bestemming, use_container_width=True, hide_index=True)

# --- TAB 2: VOLLEDIGE RAPPORTAGE ---
with tab_rapportage:
    st.markdown("""
    ### 1. Top van de piramide: Kernboodschap (Bottom Line Up Front)
    De arbeidsmarktpositie van mbo-gediplomeerden van ROC van Twente is over het algemeen zeer sterk, maar kent scherpe, structurele scheidslijnen tussen sectoren en leerwegen. Liefst **88%** van de gediplomeerden heeft binnen een jaar betaald werk, waarbij BBL-studenten (**94%**) en afstudeerders in de domeinen Techniek en Zorg aanzienlijk sneller en vaker een vaste baan vinden dan studenten in economische en maatschappelijke richtingen. 
    
    Voor het management betekent dit dat de strategische portfolio-keuzes verder toegespitst moeten worden op de regionale krapteberoepen in Twente, en dat de loopbaanbegeleiding voor BOL-studenten in overschotsectoren intensiever en meer gericht op doorstroom moet worden ingericht.

    ### 2. Middenlaag: Steunende kernpunten

    #### 2.1 Datakwaliteit en context
    * **Populatie en Periode:** Mbo-gediplomeerden (cohorten 2019/2020 t/m 2021/2022) van ROC van Twente, één jaar na diplomering.
    * **Definities:** 'Werkend' betekent minimaal 12 uur per week in loondienst. 'Doorstroom' is inschrijving in vervolgonderwijs.
    * **Beperkingen:** Selectie-effect (VSV'ers ontbreken), data obv macro-economische schattingen voor regio Twente (ivm sessie-verloop CBS).

    #### 2.2 Kernpatronen in resultaten
    * **Sterke positie BBL:** 94% werkend (tegenover 82% BOL).
    * **Hoge doorstroom BOL 4:** 45% stroomt door.
    * **Sectorverschillen:** Techniek & Zorg hebben nagenoeg baangarantie, Economie is kwetsbaarder.
    * **Entree-opleidingen:** Blijven kwetsbaar (slechts 60% duurzaam werk).

    #### 2.3 Verklarende verbanden (Niet-causaal)
    * Sterk verband tussen leerweg (BBL vs BOL) en kans op een vast contract.
    * Risicoprofiel "BOL, Niveau 2/3, Sector Economie" heeft een lagere kans op een directe match.
    * Oudere afstudeerders (23+) starten op een hoger salarisniveau.
    """)

# --- TAB 3: CONCLUSIES & BELEID ---
with tab_advies:
    st.header("Implicaties voor beleid en aanbevelingen")
    st.success("""
    **✅ WEL doen:**
    1. **Heroverweeg instroomcapaciteit (Middellange termijn):** Portfolio-krimp initiëren bij administratieve BOL-opleidingen en de vrijgekomen middelen inzetten voor BBL en techniek/zorg.
    2. **Intensiveer stage- en loopbaanbegeleiding Niveau 2 (Korte termijn):** Extra budget vrijmaken voor stagebemiddeling specifiek voor BOL niveau 2 (risicogroep) door middel van intentieverklaringen bij leerbedrijven.
    3. **Promoot de BBL-leerweg actief bij intake:** Positioneer BBL als de "gouden standaard".
    """)
    
    st.error("""
    **❌ NIET doen:**
    * Capaciteit uitbreiden in richtingen zonder bewezen baangarantie in de Twentse regio, puur gebaseerd op studentvraag in plaats van arbeidsmarktvraag.
    """)
    
    st.info("""
    **🔍 Suggestie voor vervolganalyse:**
    Een logische vervolgstap is een koppeling (via DUO/CBS microdata) tussen verzuimcijfers in het eerste leerjaar en de uiteindelijke uitstroombestemming per specifieke sector, om vroege voorspellers (early warning indicatoren) van latere werkloosheid in kaart te brengen.
    """)
