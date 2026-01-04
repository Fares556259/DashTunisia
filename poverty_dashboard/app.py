import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# Page configuration
st.set_page_config(
    page_title="Carte de la Pauvreté - Tunisie 2015",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        df_poverty = pd.read_csv('data/poverty_tunisia.csv')
        with open('geo/tunisia_governorates.geojson', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)

        # Data enrichment to match app's expectations
        df_poverty.rename(columns={'Governorate': 'Name'}, inplace=True)
        df_poverty['Type'] = 'Gouvernorat'

        region_map = {
            'Tunis': 'Grand Tunis', 'Ariana': 'Grand Tunis', 'Ben Arous': 'Grand Tunis', 'Manouba': 'Grand Tunis',
            'Nabeul': 'Nord-Est', 'Zaghouan': 'Nord-Est', 'Bizerte': 'Nord-Est',
            'Beja': 'Nord-Ouest', 'Jendouba': 'Nord-Ouest', 'Le Kef': 'Nord-Ouest', 'Siliana': 'Nord-Ouest',
            'Sousse': 'Centre-Est', 'Monastir': 'Centre-Est', 'Mahdia': 'Centre-Est', 'Sfax': 'Centre-Est',
            'Kairouan': 'Centre-Ouest', 'Kasserine': 'Centre-Ouest', 'Sidi Bouzid': 'Centre-Ouest',
            'Gabes': 'Sud-Est', 'Medenine': 'Sud-Est', 'Tataouine': 'Sud-Est',
            'Gafsa': 'Sud-Ouest', 'Tozeur': 'Sud-Ouest', 'Kebili': 'Sud-Ouest'
        }
        df_poverty['Region'] = df_poverty['Name'].map(region_map)

        # The app expects delegation data, which is missing.
        # We will add a placeholder for the structure, but it will be empty.
        # The delegation-specific page will be adapted to show a message.
        df_delegations = pd.DataFrame(columns=['Name', 'Governorate', 'Region', 'Poverty_Rate', 'Type'])
        df_poverty = pd.concat([df_poverty, df_delegations], ignore_index=True)

        return df_poverty, geojson_data
    except FileNotFoundError as e:
        st.error(f"Data files not found: {e}")
        return None, None

df_poverty, geojson_data = load_data()

# Regional summary data
region_summary = {
    'Région': ['Grand Tunis', 'Nord-Est', 'Nord-Ouest', 'Centre-Est', 'Centre-Ouest', 'Sud-Est', 'Sud-Ouest'],
    'Taux_Pauvreté': [6.1, 11.9, 25.8, 11.7, 29.3, 17.8, 18.2],
    'Population': [2719000, 1533064, 1378596, 2580032, 1439714, 1003273, 602204],
    'Gouvernorats': [
        'Tunis, Ariana, Ben Arous, Manouba',
        'Nabeul, Zaghouan, Bizerte',
        'Beja, Jendouba, Le Kef, Seliana',
        'Sousse, Monastir, Mahdia, Sfax',
        'Kairouan, Kasserine, Sidi Bouzid',
        'Gabes, Médenine, Tataouine',
        'Gafsa, Tozeur, Kebili'
    ]
}
df_regions = pd.DataFrame(region_summary)

# Sidebar
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Flag_of_Tunisia.svg/320px-Flag_of_Tunisia.svg.png", width=100)
st.sidebar.title("🗺️ Navigation")
page = st.sidebar.radio(
    "Sélectionner une vue:",
    ["📊 Vue d'ensemble", "🌍 Analyse par Région", "🏛️ Analyse par Gouvernorat", 
     "📍 Détails des Délégations", "📈 Comparaisons & Corrélations"]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Source des données:**  
Carte de la Pauvreté en Tunisie 2015  
Institut National de la Statistique (INS)  
Banque Mondiale
""")

# ============= MAIN CONTENT =============

# Title
st.markdown('<p class="main-header">🗺️ Carte de la Pauvreté en Tunisie 2015</p>', unsafe_allow_html=True)

# ============= VUE D'ENSEMBLE =============
if page == "📊 Vue d'ensemble":
    st.header("📊 Vue d'ensemble nationale")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Taux National", "15.3%", help="Taux de pauvreté national en 2015")
    with col2:
        st.metric("Région la plus pauvre", "Centre-Ouest", "29.3%")
    with col3:
        st.metric("Région la plus riche", "Grand Tunis", "6.1%")
    with col4:
        st.metric("Écart régional", "23.2 pts", help="Différence entre régions extrêmes")
    
    st.markdown("---")
    
    # Regional overview
    col1, col2 = st.columns(2)
    
    with col1:
        fig_regions = px.bar(
            df_regions.sort_values('Taux_Pauvreté'),
            x='Taux_Pauvreté',
            y='Région',
            orientation='h',
            title="Taux de Pauvreté par Région (%)",
            color='Taux_Pauvreté',
            color_continuous_scale=['#2E7D32', '#66BB6A', '#FDD835', '#FB8C00', '#E53935', '#B71C1C'],
            text='Taux_Pauvreté'
        )
        fig_regions.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_regions.update_layout(height=400, showlegend=False, xaxis_title="Taux de Pauvreté (%)")
        st.plotly_chart(fig_regions, use_container_width=True)
    
    with col2:
        # Population vs Poverty
        fig_pop = px.scatter(
            df_regions,
            x='Population',
            y='Taux_Pauvreté',
            size='Population',
            color='Taux_Pauvreté',
            hover_name='Région',
            title="Population vs Taux de Pauvreté",
            color_continuous_scale=['#2E7D32', '#66BB6A', '#FDD835', '#FB8C00', '#E53935', '#B71C1C'],
            labels={'Population': 'Population', 'Taux_Pauvreté': 'Taux de Pauvreté (%)'}
        )
        fig_pop.update_layout(height=400)
        st.plotly_chart(fig_pop, use_container_width=True)
    
    # Map (if data available)
    if df_poverty is not None and geojson_data is not None:
        st.subheader("🗺️ Carte Interactive de la Pauvreté")
        
        gov_data_for_map = df_poverty[df_poverty['Type'] == 'Gouvernorat'].copy()
        gov_data_for_map['display_name'] = gov_data_for_map['Name'] # Keep original name for hover
        name_mapping = {
            'Ben Arous': 'BenArous(TunisSud)',
            'Beja': 'Béja',
            'Gabes': 'Gabès',
            'Kasserine': 'Kassérine',
            'Le Kef': 'LeKef',
            'Manouba': 'Manubah',
            'Medenine': 'Médenine',
            'Sidi Bouzid': 'SidiBouZid'
        }
        gov_data_for_map['Name'] = gov_data_for_map['Name'].replace(name_mapping)

        map_fig = px.choropleth(
            gov_data_for_map,
            geojson=geojson_data,
            locations="Name",
            featureidkey="properties.NAME_1",
            color="Poverty_Rate",
            hover_name="display_name",
            hover_data={"Poverty_Rate": ":.1f%"},
            color_continuous_scale=['#2E7D32', '#66BB6A', '#FDD835', '#FB8C00', '#E53935', '#B71C1C'],
            labels={"Poverty_Rate": "Taux de Pauvreté (%)"}
        )
        
        map_fig.update_geos(
            fitbounds="locations",
            visible=False
        )
        
        map_fig.update_layout(
            height=600,
            margin={"r":0,"t":0,"l":0,"b":0}
        )
        
        st.plotly_chart(map_fig, use_container_width=True)
    
    # ============= INSIGHTS =============
    st.markdown("---")
    st.subheader("🔍 Key Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔴 Zones à Forte Pauvreté:**
        - **Kasserine**, **Le Kef**, and **Kairouan** have the highest poverty rates.
        - Coastal governorates show significantly lower poverty levels.
        - Strong spatial inequality persists between inland and coastal Tunisia.
        """)
    
    with col2:
        st.markdown("""
        **🟡 Disparités Régionales:**
        - Centre-Ouest: 29.3% (la plus pauvre)
        - Nord-Ouest: 25.8% (deuxième plus pauvre)
        - Grand Tunis: 6.1% (la plus riche)
        - Écart de 4.8x entre régions extrêmes
        """)
    
    with col3:
        st.markdown("""
        **🟢 Facteurs Corrélés:**
        - Urbanisation ↓ → Pauvreté ↑
        - Chômage ↑ → Pauvreté ↑
        - Éducation ↓ → Pauvreté ↑
        - Infrastructure ↓ → Pauvreté ↑
        """)

# ============= ANALYSE PAR RÉGION =============
elif page == "🌍 Analyse par Région":
    st.header("🌍 Analyse par Région")
    
    selected_region = st.selectbox("Sélectionner une région:", df_regions['Région'].tolist())
    
    region_data = df_regions[df_regions['Région'] == selected_region].iloc[0]
    
    # Metrics for selected region
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Taux de Pauvreté", f"{region_data['Taux_Pauvreté']}%")
    with col2:
        st.metric("Population", f"{region_data['Population']:,}")
    with col3:
        poor_population = int(region_data['Population'] * region_data['Taux_Pauvreté'] / 100)
        st.metric("Population Pauvre (estimation)", f"{poor_population:,}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"📌 Gouvernorats de {selected_region}")
        st.info(region_data['Gouvernorats'])
        
        # Comparison with national average
        diff = region_data['Taux_Pauvreté'] - 15.3
        if diff > 0:
            st.warning(f"⚠️ Taux de pauvreté **{diff:.1f} points** au-dessus de la moyenne nationale")
        else:
            st.success(f"✅ Taux de pauvreté **{abs(diff):.1f} points** en dessous de la moyenne nationale")
    
    with col2:
        # Regional comparison chart
        fig_comparison = go.Figure()
        
        fig_comparison.add_trace(go.Bar(
            x=df_regions['Région'],
            y=df_regions['Taux_Pauvreté'],
            marker_color=['#E53935' if r == selected_region else '#90CAF9' for r in df_regions['Région']],
            text=df_regions['Taux_Pauvreté'],
            texttemplate='%{text:.1f}%',
            textposition='outside'
        ))
        
        fig_comparison.add_hline(y=15.3, line_dash="dash", line_color="red", 
                                annotation_text="Moyenne nationale (15.3%)")
        
        fig_comparison.update_layout(
            title=f"Comparaison: {selected_region} vs Autres Régions",
            xaxis_title="Région",
            yaxis_title="Taux de Pauvreté (%)",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Detailed analysis
    st.markdown("---")
    st.subheader(f"📊 Analyse Détaillée: {selected_region}")
    
    # Regional characteristics (based on document data)
    region_insights = {
        'Grand Tunis': {
            'Caractéristiques': [
                "Region la plus nantie de Tunisie",
                "Forte densité démographique",
                "Économie diversifiée (services, industrie)",
                "Infrastructure moderne développée"
            ],
            'Délégations pauvres': "Tebourba (15.2%), El Battane (14.5%), Kalaat El Andalous (12.5%)",
            'Délégations riches': "El Menzah (0.2%), La Goulette (1.1%), L'Ariana Ville (1.3%)"
        },
        'Nord-Est': {
            'Caractéristiques': [
                "Zone côtière avec activité touristique",
                "Agriculture développée (primeurs)",
                "Poches de pauvreté dans zones rurales",
                "Disparités entre côte et intérieur"
            ],
            'Délégations pauvres': "Sedjnane (39.9%), Djoumine (36.6%), Ghezala (34%)",
            'Délégations riches': "Nabeul (4.7%), Dar Chaabane Fehri (4.9%), Bizerte Nord (5.3%)"
        },
        'Nord-Ouest': {
            'Caractéristiques': [
                "Region parmi les plus pauvres",
                "Vocation agricole dominante",
                "Exode rural important",
                "Infrastructure de base limitée"
            ],
            'Délégations pauvres': "Nebeur (45.4%), El-Rouhia (40.7%), Sakiet Sidi Youssef (39.7%)",
            'Délégations riches': "Jendouba Sud (10.7%), Bou Salem (16.6%), Tabarka (16.7%)"
        },
        'Centre-Est': {
            'Caractéristiques': [
                "Region hétérogène",
                "Tourisme et industrie développés",
                "Sfax: pôle économique majeur",
                "Disparités importantes internes"
            ],
            'Délégations pauvres': "Chorbane (36.9%), Ouled Chamekh (35%), Hebira (33.4%)",
            'Délégations riches': "Sfax Ville (2.5%), Sfax Ouest (3.0%), Sfax Sud (3.0%)"
        },
        'Centre-Ouest': {
            'Caractéristiques': [
                "Region la plus pauvre de Tunisie",
                "Agriculture vivrière prédominante",
                "Taux de chômage très élevé",
                "Déficit d'infrastructure important"
            ],
            'Délégations pauvres': "Hassi Ferid (53.5%), Djedeliane (53.1%), El Ayoun (50.1%)",
            'Délégations riches': "Sidi Bouzid Ouest (17.4%), Kasserine Nord (18.9%), Souk Jedid (20.8%)"
        },
        'Sud-Est': {
            'Caractéristiques': [
                "Hétérogénéité importante",
                "Zones urbaines plus riches",
                "Zones rurales plus pauvres",
                "Tourisme sur les îles (Djerba)"
            ],
            'Délégations pauvres': "Beni Khedache (36.9%), Menzel El Habib (33.6%), Sidi Makhlouf (33.4%)",
            'Délégations riches': "Gabes Sud (9.4%), Djerba Houmet Souk (9.5%)"
        },
        'Sud-Ouest': {
            'Caractéristiques': [
                "Zones urbaines relativement riches",
                "Poches de pauvreté au Nord-Est",
                "Ressources naturelles (phosphate)",
                "Oasis et agriculture spécialisée"
            ],
            'Délégations pauvres': "Belkhir (31.2%), Sned (27.2%), Douz Sud (25.9%)",
            'Délégations riches': "Tozeur (10.3%), Kebili Nord (12.3%), Gafsa Sud (15.4%)"
        }
    }
    
    if selected_region in region_insights:
        insights = region_insights[selected_region]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🏞️ Caractéristiques principales:**")
            for char in insights['Caractéristiques']:
                st.markdown(f"- {char}")
        
        with col2:
            st.markdown("**🔴 Délégations les plus pauvres:**")
            st.write(insights['Délégations pauvres'])
            
            st.markdown("**🟢 Délégations les plus riches:**")
            st.write(insights['Délégations riches'])

# ============= ANALYSE PAR GOUVERNORAT =============
elif page == "🏛️ Analyse par Gouvernorat":
    st.header("🏛️ Analyse par Gouvernorat")
    
    if df_poverty is not None:
        gov_data = df_poverty[df_poverty['Type'] == 'Gouvernorat'].copy()
        
        # Filters
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_gov = st.selectbox("Sélectionner un gouvernorat:", gov_data['Name'].sort_values().tolist())
        
        with col2:
            sort_by = st.radio("Trier par:", ["Alphabétique", "Taux de Pauvreté"])
        
        # Display selected governorate details
        gov_info = gov_data[gov_data['Name'] == selected_gov].iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Taux de Pauvreté", f"{gov_info['Poverty_Rate']:.1f}%")
        with col2:
            st.metric("Région", gov_info['Region'])
        with col3:
            rank = (gov_data['Poverty_Rate'] > gov_info['Poverty_Rate']).sum() + 1
            st.metric("Classement", f"{rank}/24")
        with col4:
            diff = gov_info['Poverty_Rate'] - 15.3
            st.metric("vs National", f"{diff:+.1f} pts")
        
        st.markdown("---")
        
        # Comparison chart
        if sort_by == "Taux de Pauvreté":
            gov_data_sorted = gov_data.sort_values('Poverty_Rate', ascending=False)
        else:
            gov_data_sorted = gov_data.sort_values('Name')
        
        fig_gov = px.bar(
            gov_data_sorted,
            x='Name',
            y='Poverty_Rate',
            color='Poverty_Rate',
            color_continuous_scale=['#2E7D32', '#66BB6A', '#FDD835', '#FB8C00', '#E53935', '#B71C1C'],
            title="Taux de Pauvreté par Gouvernorat",
            labels={'Name': 'Gouvernorat', 'Poverty_Rate': 'Taux de Pauvreté (%)'},
            hover_data={'Poverty_Rate': ':.1f%'}
        )
        
        fig_gov.update_layout(
            height=500,
            xaxis_tickangle=-45,
            showlegend=False
        )
        
        fig_gov.add_hline(y=15.3, line_dash="dash", line_color="red", 
                         annotation_text="Moyenne nationale (15.3%)")
        
        # Highlight selected governorate
        colors = ['#E53935' if name == selected_gov else '#1f77b4' for name in gov_data_sorted['Name']]
        fig_gov.update_traces(marker_color=colors)
        
        st.plotly_chart(fig_gov, use_container_width=True)
        
        # Top and bottom governorates
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔴 Top 5 Plus Pauvres")
            top5_poor = gov_data.nlargest(5, 'Poverty_Rate')[['Name', 'Poverty_Rate', 'Region']]
            for idx, row in top5_poor.iterrows():
                st.write(f"**{row['Name']}** ({row['Region']}): {row['Poverty_Rate']:.1f}%")
        
        with col2:
            st.subheader("🟢 Top 5 Plus Riches")
            top5_rich = gov_data.nsmallest(5, 'Poverty_Rate')[['Name', 'Poverty_Rate', 'Region']]
            for idx, row in top5_rich.iterrows():
                st.write(f"**{row['Name']}** ({row['Region']}): {row['Poverty_Rate']:.1f}%")

# ============= DÉTAILS DES DÉLÉGATIONS =============
elif page == "📍 Détails des Délégations":
    st.header("📍 Analyse des Délégations")
    st.warning("Les données détaillées pour les délégations ne sont pas disponibles dans le fichier de données actuel.")
    st.info("Les informations sur les délégations les plus et les moins pauvres par région sont disponibles dans l'onglet 'Analyse par Région'.")

# ============= COMPARAISONS & CORRÉLATIONS =============
elif page == "📈 Comparaisons & Corrélations":
    st.header("📈 Comparaisons & Corrélations")
    
    tab1, tab2, tab3 = st.tabs(["📊 Comparaisons", "🔗 Corrélations", "📉 Disparités"])
    
    with tab1:
        st.subheader("Comparaisons Inter-régionales")
        
        # Box plot by region
        if df_poverty is not None:
            gov_data = df_poverty[df_poverty['Type'] == 'Gouvernorat']
            
            fig_box = px.box(
                gov_data,
                x='Region',
                y='Poverty_Rate',
                color='Region',
                title="Distribution des Taux de Pauvreté par Région",
                labels={'Poverty_Rate': 'Taux de Pauvreté (%)', 'Region': 'Région'}
            )
            fig_box.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)
            
            # Statistical summary
            st.markdown("---")
            st.subheader("📊 Statistiques Descriptives par Région")
            
            stats = gov_data.groupby('Region')['Poverty_Rate'].agg([
                ('Moyenne', 'mean'),
                ('Médiane', 'median'),
                ('Min', 'min'),
                ('Max', 'max'),
                ('Écart-type', 'std')
            ]).round(2)
            
            st.dataframe(stats, use_container_width=True)
    
    with tab2:
        st.subheader("🔗 Facteurs Corrélés à la Pauvreté")
        
        st.markdown("""
        Selon l'analyse du rapport INS 2015, plusieurs facteurs montrent une forte corrélation avec les taux de pauvreté:
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📉 Corrélations Négatives (inverse):**
            - **Taux d'urbanisation** ↓ → Pauvreté ↑
            - **Niveau d'éducation** ↓ → Pauvreté ↑
            - **Accès à l'infrastructure** ↓ → Pauvreté ↑
            - **Taux d'emploi** ↓ → Pauvreté ↑
            - **Accès aux services de base** ↓ → Pauvreté ↑
            """)
        
        with col2:
            st.markdown("""
            **📈 Corrélations Positives (directe):**
            - **Taux de chômage** ↑ → Pauvreté ↑
            - **Taux d'analphabétisme** ↑ → Pauvreté ↑
            - **Abandon scolaire** ↑ → Pauvreté ↑
            - **Logement rudimentaire** ↑ → Pauvreté ↑
            - **Taille des ménages** ↑ → Pauvreté ↑
            """)
        
        st.info("""
        💡 **Insight clé:** Les délégations rurales, éloignées des centres urbains, 
        avec une faible infrastructure et un faible niveau d'éducation sont 
        systématiquement les plus touchées par la pauvreté.
        """)
    
    with tab3:
        st.subheader("📉 Analyse des Disparités")
        
        # Calculate disparities
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Écart Régional Maximum",
                "23.2 pts",
                help="Différence entre Centre-Ouest (29.3%) et Grand Tunis (6.1%)"
            )
        
        with col2:
            st.metric(
                "Écart Gouvernorats",
                "28.5 pts",
                help="Différence entre Le Kef (33.1%) et Tunis (4.6%)"
            )
        
        with col3:
            st.metric(
                "Écart Délégations",
                "53.3 pts",
                help="Différence entre Hassi Ferid (53.5%) et El Menzah (0.2%)"
            )
        
        st.markdown("---")
        
        # Inequality visualization
        st.subheader("🎯 Visualisation des Inégalités")
        
        fig_inequality = go.Figure()
        
        regions_sorted = df_regions.sort_values('Taux_Pauvreté')
        
        fig_inequality.add_trace(go.Scatter(
            x=list(range(len(regions_sorted))),
            y=regions_sorted['Taux_Pauvreté'].values,
            mode='lines+markers',
            name='Taux de Pauvreté',
            line=dict(color='#E53935', width=3),
            marker=dict(size=10)
        ))
        
        fig_inequality.add_hline(y=15.3, line_dash="dash", line_color="blue", 
                                annotation_text="Moyenne nationale")
        
        fig_inequality.update_layout(
            title="Courbe des Inégalités Régionales",
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(len(regions_sorted))),
                ticktext=regions_sorted['Région'].values
            ),
            yaxis_title="Taux de Pauvreté (%)",
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig_inequality, use_container_width=True)

# ============= FOOTER =============
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **📊 À propos des données:**
    - Année de référence: 2015
    - Source: Institut National de la Statistique (INS)
    - Méthodologie: Approche monétaire
    - Seuil de pauvreté: Basé sur la consommation
    """)

with col2:
    st.markdown("""
    **🏛️ Définitions:**
    - **Pauvreté:** Dépense par tête < seuil de pauvreté
    - **Seuil extrême:** Dépense minimale alimentaire
    - **Seuil global:** Dépense minimale totale
    - **Indigence:** Pauvreté extrême
    """)

with col3:
    st.markdown("""
    **📌 Limites:**
    - Données de 2015 (pré-Révolution)
    - Approche monétaire uniquement
    - Ne capture pas la pauvreté multidimensionnelle
    - Aggrégations masquent les micro-disparités
    """)

# Add disclaimer
st.markdown("---")
st.caption("""
**Note méthodologique:** Cette analyse utilise les données de la Carte de la Pauvreté 2015 de l'INS. 
Les taux de pauvreté sont calculés sur la base de la dépense par tête. Les données peuvent 
ne pas refléter la situation post-Révolution de 2011 ou les changements récents. 
L'analyse est présentée à des fins éducatives et de recherche.
""")