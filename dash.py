import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import json
from datetime import datetime
from pathlib import Path
from collections import Counter
import re
import os

# Streamlit Configuration
st.set_page_config(page_title="🌟 Temtem One Market Dashboard", layout="wide", initial_sidebar_state="expanded")

# Helper Functions
@st.cache_data
def load_data(file):
    file_extension = Path(file.name).suffix.lower()
    try:
        if file_extension in ['.csv', '.txt']:
            return pd.read_csv(file, encoding="ISO-8859-1")
        elif file_extension in ['.xlsx', '.xls']:
            return pd.read_excel(file, engine='openpyxl')
        else:
            st.sidebar.error("Unsupported file format. Please upload a CSV or Excel file.")
    except Exception as e:
        st.sidebar.error(f"Error loading file: {str(e)}")
    return None


@st.cache_data
def load_geojson(geojson_path="all-wilayas.geojson"):
    with open(geojson_path, "r", encoding="utf-8") as file:
        return json.load(file)


def preprocess_data(df, date_columns):
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

def custom_card(title, value, subtitle, color="#3498DB", border_radius="10px"):
    card_html = f"""
    <div style='background-color: {color}; border-radius: {border_radius}; padding: 20px; text-align: center;'>
        <h3 style='color: white;'>{title}</h3>
        <h1 style='color: white; font-size: 30px;'>{value}</h1>
        <p style='color: white; font-size: 14px;'>{subtitle}</p>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def display_custom_kpis(df):
    total_submissions = len(df)
    total_cashback = df['Montant Cashback'].sum()
    avg_cashback = df['Montant Cashback'].mean()
    approval_rate = (df['status_challengeticketsubmissions'] == 'APPROVED').mean()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        custom_card("Total Submissions", f"{total_submissions:,}", "All time submissions", color="#1ABC9C")
    with col2:
        custom_card("Total Cashback", f"${total_cashback:,.2f}", "Cashback awarded", color="#F39C12")
    with col3:
        custom_card("Approval Rate", f"{approval_rate:.2%}", "Approval rate of submissions", color="#3498DB")
    with col4:
        custom_card("Avg Cashback", f"${avg_cashback:.2f}", "Average cashback per submission", color="#E74C3C")

def display_summary_stats(df):
    total_submissions = df.shape[0]
    unique_wilayas = df['Wilaya'].nunique()
    unique_users = df['submittedBy.id'].nunique()
    
    st.subheader('🔎 Summary Statistics')
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Submissions", total_submissions)
    col2.metric("Unique Wilayas", unique_wilayas)
    col3.metric("Unique Users", unique_users)

def display_wilaya_map(df, wilayas_gdf):
    wilaya_counts = df['Wilaya'].value_counts().reset_index()
    wilaya_counts.columns = ['name', 'submission_count']

    wilayas_gdf['name'] = wilayas_gdf['name'].str.lower()
    wilayas_gdf = wilayas_gdf.merge(wilaya_counts, on='name', how='left')
    wilayas_gdf['submission_count'] = wilayas_gdf['submission_count'].fillna(0)

    folium_map = folium.Map(location=[28.0339, 1.6596], zoom_start=5)
    folium.Choropleth(
        geo_data=wilayas_gdf.__geo_interface__,
        data=wilayas_gdf,
        columns=['name', 'submission_count'],
        key_on='feature.properties.name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Number of Submissions'
    ).add_to(folium_map)

    folium.GeoJson(
        wilayas_gdf.__geo_interface__,
        tooltip=folium.features.GeoJsonTooltip(fields=['name', 'submission_count'],
                                               aliases=['Wilaya:', 'Submissions:'])
    ).add_to(folium_map)

    st.subheader("🌍 Geographical Distribution of Submissions by Wilaya")
    folium_static(folium_map)

def display_line_chart(df, x, y, title):
    fig = px.line(df, x=x, y=y, title=title)
    st.plotly_chart(fig, use_container_width=True)

# Sidebar Controls
st.sidebar.title("📊 Dashboard Controls")

uploaded_file = st.sidebar.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        date_columns = ['createdAt_challengesubmissions', 'startDate_challenge', 'endDate_challenge']
        df = preprocess_data(df, date_columns)

        st.title("🌟 Temtem One Market Dashboard")
        st.subheader("✨ Key Performance Indicators")
        display_custom_kpis(df)

        st.subheader("🔍 Data Overview")
        display_summary_stats(df)

        geojson_data = load_geojson()
        wilayas_gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
        display_wilaya_map(df, wilayas_gdf)

        st.subheader("📅 Submissions Over Time")
        submissions_over_time = df.groupby('createdAt_challengesubmissions').size().reset_index(name='count')
        display_line_chart(submissions_over_time, 'createdAt_challengesubmissions', 'count', 'Submissions Over Time')
        
        # Campaign Performance Analysis
        if 'title.fr' in df.columns:
            st.subheader("🏆 Campaign Performance")
            campaign_performance = df.groupby('title.fr').agg({'submission.$oid': 'count', 'Montant Cashback': 'sum'}).reset_index()
            campaign_performance.columns = ['Campaign', 'Submissions', 'Total Cashback']
            fig = px.bar(campaign_performance, x='Campaign', y=['Submissions', 'Total Cashback'], title='Campaign Performance')
            st.plotly_chart(fig, use_container_width=True)

        # Geographical Distribution Analysis
        if 'Wilaya' in df.columns:
            st.subheader("🗺️ Geographical Distribution")
            geo_distribution = df['Wilaya'].value_counts().reset_index()
            geo_distribution.columns = ['Wilaya', 'Count']
            fig = px.bar(geo_distribution, x='Wilaya', y='Count', title='Submission Distribution by Wilaya')
            st.plotly_chart(fig, use_container_width=True)

        # User Type Distribution
        if 'userType' in df.columns:
            st.subheader("👥 User Type Distribution")
            user_type_dist = df['userType'].value_counts().reset_index()
            user_type_dist.columns = ['User Type', 'Count']
            fig = px.pie(user_type_dist, values='Count', names='User Type', title='User Type Distribution')
            st.plotly_chart(fig, use_container_width=True)

        # Submission Status Distribution
        if 'status_challengeticketsubmissions' in df.columns:
            st.subheader("✅ Submission Status Distribution")
            status_dist = df['status_challengeticketsubmissions'].value_counts().reset_index()
            status_dist.columns = ['Status', 'Count']
            fig = px.pie(status_dist, values='Count', names='Status', title='Submission Status Distribution')
            st.plotly_chart(fig, use_container_width=True)

        # Function to get top users
        def get_top_users(df, n=10):
            top_users = df.groupby(['submittedBy.id', 'Prenom', 'Nom']).agg({
                'submission.$oid': 'count',
                'Montant Cashback': 'sum'
            }).reset_index()
            top_users.columns = ['User ID', 'First Name', 'Last Name', 'Submission Count', 'Total Cashback']
            top_users['Full Name'] = top_users['First Name'] + ' ' + top_users['Last Name']
            top_users = top_users.sort_values('Submission Count', ascending=False).head(n)
            return top_users

        st.subheader("🏆 Top Users Performance")
        top_users = get_top_users(df)
        st.write(top_users[['Full Name', 'Submission Count', 'Total Cashback']])

       # Additional Analysis Sections (Tag Analysis, User Demographics, Claims Over Time, etc.)

        # Claims Over Time
        st.subheader("📈 Claims Over Time")
        if 'status_challengesubmissions' in df.columns and 'createdAt_challengesubmissions' in df.columns:
            claims_over_time = df[df['status_challengesubmissions'] == 'claimed'].groupby(pd.Grouper(key='createdAt_challengesubmissions', freq='D')).size().reset_index(name='count')
            fig = px.line(claims_over_time, x='createdAt_challengesubmissions', y='count', title="Number of Claims per Day")
            st.plotly_chart(fig)

        # User Demographics
        st.subheader("👥 User Demographics")

        if 'Genre' in df.columns:
            st.write("### Gender Distribution")
            gender_dist = df['Genre'].value_counts()
            fig = px.pie(values=gender_dist.values, names=gender_dist.index, title="Gender Distribution")
            st.plotly_chart(fig)
        else:
            st.write("Gender information is not available in the dataset.")

        # Geographical Distribution
        st.write("### Geographical Distribution")

        # By Wilaya
        if 'Wilaya' in df.columns:
            st.write("Distribution by Wilaya")
            wilaya_dist = df['Wilaya'].value_counts()
            fig = px.bar(x=wilaya_dist.index, y=wilaya_dist.values, title="User Distribution by Wilaya")
            st.plotly_chart(fig)
        else:
            st.write("Wilaya information is not available in the dataset.")

        # By Country
        if 'country' in df.columns:
            st.write("Distribution by Country")
            country_dist = df['country'].value_counts()
            fig = px.pie(values=country_dist.values, names=country_dist.index, title="User Distribution by Country")
            st.plotly_chart(fig)
        else:
            st.write("Country information is not available in the dataset.")


        # Geographical Distribution by Country
        if 'country' in df.columns:
            st.write("### Geographical Distribution by Country")
            country_dist = df['country'].value_counts()
            fig = px.pie(values=country_dist.values, names=country_dist.index, title="User Distribution by Country")
            st.plotly_chart(fig)
        else:
            st.write("Country information is not available in the dataset.")

        # Tag Analysis
        st.subheader("🏷️ Tag Analysis")
        if 'tags' in df.columns:
            # Normalize tags
            def normalize_tag(tag):
                tag = tag.lower()
                tag = tag.strip()
                tag = re.sub(r'[^\w\s-]', '', tag)
                tag = re.sub(r'[-\s]+', '_', tag)
                return tag

            df['normalized_tags'] = df['tags'].apply(lambda x: ','.join([normalize_tag(tag) for tag in x.split(',')]))

            # Most common tags
            st.write("### Most Common Tags")
            all_tags = [tag for tags in df['normalized_tags'].str.split(',') for tag in tags]
            tag_counts = Counter(all_tags)
            top_tags = pd.DataFrame(tag_counts.most_common(10), columns=['Tag', 'Count'])

            fig = px.bar(top_tags, x='Tag', y='Count', title="Top 10 Most Common Tags")
            st.plotly_chart(fig)

            # Performance of promotions by tag
            st.write("### Performance of Promotions by Tag")
            tag_performance = df.assign(tags=df['normalized_tags'].str.split(',')).explode('tags')
            tag_performance = tag_performance.groupby('tags')['Montant Cashback'].agg(['mean', 'count']).reset_index()
            tag_performance.columns = ['Tag', 'Avg Cashback', 'Submission Count']
            tag_performance = tag_performance.sort_values('Avg Cashback', ascending=False)

            fig = px.scatter(tag_performance, x='Submission Count', y='Avg Cashback', text='Tag', 
                            title="Tag Performance: Average Cashback vs Submission Count",
                            labels={'Submission Count': 'Number of Submissions', 'Avg Cashback': 'Average Cashback Amount'})
            fig.update_traces(textposition='top center')
            st.plotly_chart(fig)

            # Table view of tag performance
            st.write("### Tag Performance Table")
            st.dataframe(tag_performance)
        else:
            st.write("Tag information is not available in the dataset.")

        # Display raw data if checkbox is selected
        if st.checkbox("Show Raw Data"):
            st.subheader("📜 Raw Data")
            st.write(df)
    # Add more sections as needed
else:
    st.sidebar.info("Please upload a CSV or Excel file to begin.")
