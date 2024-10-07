import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# Ajout du logo dans la barre latérale
logo = Image.open("temtem_logo.png")  # Remplacez 'logo.png' par le chemin de votre logo
st.sidebar.image(logo, use_column_width=True)

# Titre de l'application avec une police stylée
st.markdown("<h1 style='text-align: center; color: #2C3E50;'>Analyse des données des soumissions</h1>", unsafe_allow_html=True)

# Ajout d'un sidebar pour les différentes sections de l'entreprise
section = st.sidebar.selectbox(
    "Sélectionnez une section",
    ['Vue globale', 'Marketing', 'Ressources humaines']
)

# Chargement du fichier CSV par l'utilisateur
uploaded_file = st.file_uploader("Choisissez un fichier CSV", type=["csv"])

if uploaded_file is not None:
    # Charger les données à partir du fichier CSV sélectionné
    data = pd.read_csv(uploaded_file)
    
    # Supprimer les valeurs manquantes dans les colonnes essentielles
    data = data.dropna(subset=['title.fr', 'Wilaya', 'Genre', 'Date de naissance'])

    # Créer une liste de produits uniques
    produits = data['title.fr'].unique()

    # Sélection du produit par l'utilisateur
    produit_selectionne = st.selectbox("Sélectionnez un produit", produits)

    # Filtrer les données en fonction de la sélection de l'utilisateur
    data_filtered = data[data['title.fr'] == produit_selectionne]

    # Nettoyer les données de Genre
    data_filtered['Genre'] = data_filtered['Genre'].fillna('Non spécifié')

    # Calculer l'âge des utilisateurs
    data_filtered['Date de naissance'] = pd.to_datetime(data_filtered['Date de naissance'], errors='coerce')
    data_filtered['Age'] = pd.Timestamp.now().year - data_filtered['Date de naissance'].dt.year

    # Visualisations
    st.markdown(f"<h2 style='color: #34495E;'>Section: {section}</h2>", unsafe_allow_html=True)

    # Répartition par Genre (Plotly)
    st.markdown(f"<h3 style='color: #2C3E50;'>1. Répartition par Genre pour {produit_selectionne}</h3>", unsafe_allow_html=True)
    genre_counts = data_filtered['Genre'].value_counts()

    fig = px.bar(genre_counts, x=genre_counts.index, y=genre_counts.values, labels={'x': 'Genre', 'y': 'Nombre'}, 
                 title=f"Répartition par Genre pour {produit_selectionne}", color_discrete_sequence=['#FF8C00'])
    st.plotly_chart(fig)



    # Répartition géographique (Wilaya) (Plotly)
    st.markdown(f"<h3 style='color: #2C3E50;'>2. Répartition géographique par Wilaya pour {produit_selectionne}</h3>", unsafe_allow_html=True)
    wilaya_counts = data_filtered['Wilaya'].value_counts()

    fig = px.bar(wilaya_counts, x=wilaya_counts.index, y=wilaya_counts.values, labels={'x': 'Wilaya', 'y': 'Nombre'}, 
                 title=f"Répartition géographique par Wilaya pour {produit_selectionne}", color_discrete_sequence=['#FF8C00'])
    fig.update_layout(xaxis_tickangle=-90)
    st.plotly_chart(fig)

    # Répartition géographique (Commune) (Nouveau)
    st.markdown(f"<h3 style='color: #2C3E50;'>3. Répartition par Commune pour {produit_selectionne}</h3>", unsafe_allow_html=True)
    commune_counts = data_filtered['commune'].value_counts()

    fig = px.bar(commune_counts, x=commune_counts.index, y=commune_counts.values, labels={'x': 'Commune', 'y': 'Nombre'}, 
                 title=f"Répartition géographique par Commune pour {produit_selectionne}", color_discrete_sequence=['#FF8C00'])
    st.plotly_chart(fig)

    # Distribution par tranche d'âge (Plotly)
    st.markdown(f"<h3 style='color: #2C3E50;'>4. Distribution par tranche d'âge pour {produit_selectionne}</h3>", unsafe_allow_html=True)
    fig = px.histogram(data_filtered, x="Age", nbins=10, title=f"Distribution d'âge pour {produit_selectionne}", 
                       labels={'x': 'Âge', 'y': 'Nombre de personnes'}, color_discrete_sequence=['#FF8C00'])
    st.plotly_chart(fig)


    # Statut des soumissions (Plotly)
    st.markdown(f"<h3 style='color: #2C3E50;'>6. Statut des soumissions pour {produit_selectionne}</h3>", unsafe_allow_html=True)
    status_counts = data_filtered['status_challengeticketsubmissions'].value_counts()

    fig = px.bar(status_counts, x=status_counts.index, y=status_counts.values, labels={'x': 'Statut', 'y': 'Nombre'}, 
                 title=f"Statut des soumissions pour {produit_selectionne}", color_discrete_sequence=['#FF8C00'])
    st.plotly_chart(fig)


    # Proportion par région et par genre (Tableau croisé et Heatmap)
    st.markdown(f"<h3 style='color: #2C3E50;'>8. Proportion par région (Wilaya) et genre pour {produit_selectionne}</h3>", unsafe_allow_html=True)
    wilaya_genre = pd.crosstab(data_filtered['Wilaya'], data_filtered['Genre'])
    st.write("Tableau croisé (Genre x Wilaya)")
    st.dataframe(wilaya_genre)

    # Création de la heatmap interactive avec Plotly
    heatmap_fig = go.Figure(data=go.Heatmap(
        z=wilaya_genre.values,
        x=wilaya_genre.columns,
        y=wilaya_genre.index,
        colorscale='Oranges'))

    heatmap_fig.update_layout(
        title=f"Proportion par région (Wilaya) et genre pour {produit_selectionne}",
        xaxis_title="Genre",
        yaxis_title="Wilaya")

    st.plotly_chart(heatmap_fig)


    # Analyse des segments de marché (Plotly)
    st.markdown(f"<h3 style='color: #2C3E50;'>10. Répartition par segment pour {produit_selectionne}</h3>", unsafe_allow_html=True)
    segment_counts = data_filtered['segment'].value_counts()

    fig = px.bar(segment_counts, x=segment_counts.index, y=segment_counts.values, labels={'x': 'Segment', 'y': 'Nombre'}, 
                 title=f"Répartition par segment pour {produit_selectionne}", color_discrete_sequence=['#FF8C00'])
    st.plotly_chart(fig)

    # Répartition des magasins (Plotly)
    st.markdown(f"<h3 style='color: #2C3E50;'>11. Répartition des magasins pour {produit_selectionne}</h3>", unsafe_allow_html=True)
    store_counts = data_filtered['storeName'].value_counts()

    fig = px.bar(store_counts, x=store_counts.index, y=store_counts.values, labels={'x': 'Magasin', 'y': 'Nombre'}, 
                 title=f"Répartition des magasins pour {produit_selectionne}", color_discrete_sequence=['#FF8C00'])
    fig.update_layout(xaxis_tickangle=-90)
    st.plotly_chart(fig)

    # Analyse des tags (Plotly)
    st.markdown(f"<h3 style='color: #2C3E50;'>12. Analyse des tags pour {produit_selectionne}</h3>", unsafe_allow_html=True)
    tags = data_filtered['tags'].apply(lambda x: ', '.join(eval(x)) if pd.notna(x) else '')
    all_tags = ', '.join(tags).split(', ')
    tag_counts = pd.Series(all_tags).value_counts()

    fig = px.bar(tag_counts, x=tag_counts.index, y=tag_counts.values, labels={'x': 'Tag', 'y': 'Nombre'}, 
                 title=f"Analyse des tags pour {produit_selectionne}", color_discrete_sequence=['#FF8C00'])
    fig.update_layout(xaxis_tickangle=-90)
    st.plotly_chart(fig)

    # Moyenne des montants de cashback par Wilaya (Nouveau)
    st.markdown(f"<h3 style='color: #2C3E50;'>13. Moyenne des montants de cashback par Wilaya pour {produit_selectionne}</h3>", unsafe_allow_html=True)
    wilaya_cashback = data_filtered.groupby('Wilaya')['Montant Cashback'].mean().sort_values(ascending=False)

    fig = px.bar(wilaya_cashback, x=wilaya_cashback.index, y=wilaya_cashback.values, labels={'x': 'Wilaya', 'y': 'Montant moyen de Cashback'}, 
                 title=f"Moyenne des montants de Cashback par Wilaya pour {produit_selectionne}", color_discrete_sequence=['#FF8C00'])
    st.plotly_chart(fig)



    # Submissions over time (Nouveau)
    st.markdown(f"<h3 style='color: #2C3E50;'>15. Nombre de soumissions dans le temps pour {produit_selectionne}</h3>", unsafe_allow_html=True)
    data_filtered['createdAt_challengesubmissions'] = pd.to_datetime(data_filtered['createdAt_challengesubmissions'], errors='coerce')
    submissions_over_time = data_filtered.groupby(data_filtered['createdAt_challengesubmissions'].dt.date).size()

    fig = px.line(submissions_over_time, x=submissions_over_time.index, y=submissions_over_time.values, 
                  labels={'x': 'Date', 'y': 'Nombre de soumissions'}, title=f"Nombre de soumissions dans le temps pour {produit_selectionne}")
    st.plotly_chart(fig)

    # submissions par user type
    st.markdown(f"<h3 style='color: #2C3E50;'>Submissions par type d'utilisateur (B2C, B2B)</h3>", unsafe_allow_html=True)
    if 'userType' in data_filtered.columns:
        usertype_counts = data_filtered['userType'].value_counts()
        fig = px.bar(usertype_counts, x=usertype_counts.index, y=usertype_counts.values, 
                     labels={'x': 'Type d\'utilisateur', 'y': 'Nombre de soumissions'}, 
                     title=f"Submissions par type d'utilisateur (B2C, B2B)", color_discrete_sequence=['#FF8C00'])
        st.plotly_chart(fig)


    # Average Age by Wilaya
    st.markdown(f"<h3 style='color: #2C3E50;'>Âge moyen par Wilaya</h3>", unsafe_allow_html=True)
    wilaya_age = data_filtered.groupby('Wilaya')['Age'].mean().sort_values(ascending=False)
    fig = px.bar(wilaya_age, x=wilaya_age.index, y=wilaya_age.values, labels={'x': 'Wilaya', 'y': 'Âge moyen'}, 
                 title=f"Âge moyen par Wilaya", color_discrete_sequence=['#FF8C00'])
    st.plotly_chart(fig)


    # Submissions by Day of the Week
    st.markdown(f"<h3 style='color: #2C3E50;'>Soumissions par jour de la semaine</h3>", unsafe_allow_html=True)
    data_filtered['createdAt_challengesubmissions'] = pd.to_datetime(data_filtered['createdAt_challengesubmissions'], errors='coerce')
    data_filtered['Day of Week'] = data_filtered['createdAt_challengesubmissions'].dt.day_name()
    day_of_week_counts = data_filtered['Day of Week'].value_counts()
    
    fig = px.bar(day_of_week_counts, x=day_of_week_counts.index, y=day_of_week_counts.values, 
                 labels={'x': 'Jour de la semaine', 'y': 'Nombre de soumissions'}, 
                 title=f"Soumissions par jour de la semaine", color_discrete_sequence=['#FF8C00'])
    st.plotly_chart(fig)

    # Top 10 Wilayas by Number of Submissions
    st.markdown(f"<h3 style='color: #2C3E50;'>Top 10 Wilayas par nombre de soumissions</h3>", unsafe_allow_html=True)
    top_wilayas = wilaya_counts.nlargest(10)
    
    fig = px.bar(top_wilayas, x=top_wilayas.values, y=top_wilayas.index, 
                 labels={'x': 'Nombre de soumissions', 'y': 'Wilaya'}, orientation='h', 
                 title=f"Top 10 Wilayas par nombre de soumissions", color_discrete_sequence=['#FF8C00'])
    st.plotly_chart(fig)




else:
    st.markdown("<h4 style='text-align: center; color: #FF8C00;'>Veuillez charger un fichier CSV pour commencer l'analyse.</h4>", unsafe_allow_html=True)

# CSS personnalisé pour améliorer l'apparence
st.markdown("""
    <style>
    /* Changer la couleur de fond */
    .reportview-container {
        background: #F0F2F6;
    }
    /* Styliser les titres */
    .stTitle, .stHeader, .stSubheader {
        color: #2C3E50;
        font-family: 'Arial Black', sans-serif;
    }
    .stSelectbox, .stFileUploader {
        border: 2px solid #2C3E50;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

