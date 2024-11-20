import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import json



# Set the page configuration
st.set_page_config(
    page_title="🌟 Temtem One Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load GeoJSON data for Wilayas
@st.cache_data
def load_geojson(geojson_path="all-wilayas.geojson"):
    with open(geojson_path, "r", encoding="utf-8") as file:
        return json.load(file)

color_scheme = ['#e67e22', '#f5b041', '#d35400', '#f8c471','#f39c12']

# Compute metrics per Wilaya for the table
def compute_wilaya_metrics(df):
    if 'Wilaya' in df.columns and 'Cashback Crédité' in df.columns:
        cashback_per_wilaya = df.groupby('Wilaya')['Cashback Crédité'].sum().reset_index()
        cashback_per_wilaya.columns = ['Wilaya', 'Total Cashback']
    else:
        cashback_per_wilaya = pd.DataFrame(columns=['Wilaya', 'Total Cashback'])
    if 'Wilaya' in df.columns and 'submittedBy.id' in df.columns:
        user_count_per_wilaya = df.groupby('Wilaya')['submittedBy.id'].nunique().reset_index()
        user_count_per_wilaya.columns = ['Wilaya', 'Unique Users']
    else:
        user_count_per_wilaya = pd.DataFrame(columns=['Wilaya', 'Unique Users'])
    if 'Wilaya' in df.columns:
        submission_count_per_wilaya = df['Wilaya'].value_counts().reset_index()
        submission_count_per_wilaya.columns = ['Wilaya', 'Submissions']
    else:
        submission_count_per_wilaya = pd.DataFrame(columns=['Wilaya', 'Submissions'])

    wilaya_metrics = cashback_per_wilaya.merge(user_count_per_wilaya, on='Wilaya', how='outer')
    wilaya_metrics = wilaya_metrics.merge(submission_count_per_wilaya, on='Wilaya', how='outer')
    wilaya_metrics = wilaya_metrics.fillna(0)
    wilaya_metrics['Total Cashback'] = wilaya_metrics['Total Cashback'].astype(int)

    return wilaya_metrics

# Function to display Wilaya map
def display_wilaya_map(data, geojson_data, name_column, value_column, metric='submission_count'):
    wilaya_counts = data[[name_column, value_column]].copy()
    wilayas_gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
    wilayas_gdf['name'] = wilayas_gdf['name'].str.lower().str.strip()
    wilaya_counts[name_column] = wilaya_counts[name_column].astype(str).str.lower().str.strip()
    wilayas_gdf = wilayas_gdf.merge(wilaya_counts, left_on='name', right_on=name_column, how='left')
    wilayas_gdf[value_column] = wilayas_gdf[value_column].fillna(0)

    folium_map = folium.Map(location=[28.0339, 1.6596], zoom_start=5)
    folium.Choropleth(
        geo_data=wilayas_gdf.__geo_interface__,
        data=wilayas_gdf,
        columns=['name', value_column],
        key_on='feature.properties.name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f'Number of {metric.replace("_", " ").title()}'
    ).add_to(folium_map)

    folium.GeoJson(
        wilayas_gdf.__geo_interface__,
        tooltip=folium.features.GeoJsonTooltip(fields=['name', value_column], aliases=['Wilaya:', f'{value_column.replace("_", " ").title()}:'])
    ).add_to(folium_map)

    st.subheader(f"🌍 Geographical Distribution ")
    folium_static(folium_map)

# Load user data from the file uploader
st.sidebar.image("C:/Users/ASUS/Documents/dashbord1/Logo-temtemOne.svg", use_column_width=True)
st.sidebar.subheader("Choose a CSV or Excel file")
uploaded_file = st.sidebar.file_uploader("Drag and drop file here", type=["csv", "xlsx"])

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select Page", ["Submissions", "Cashback", "Entreprises", "Products", "Users", "Shops"])

# CSS for the KPI cards
card_style = """
<style>
    .kpi-card {
        background-color: #31333F;
        padding: 15px;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        margin: 8px;
        display: flex;
        flex-direction: column;
        width: 220px; 
        height: 110px; 
        max-width: 220px; 
        min-height: 110px; 
    }
    .kpi-title {
        font-size: 16px;
        font-weight: 500;
        margin-bottom: 5px;
        color: #e0e0e0;
    }
    .kpi-value {
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 5px;
        color: #f39c12;
    }
    .kpi-growth {
        font-size: 12px;
        color: #f39c12;
    }
    .kpi-growth.negative {
        color: #e74c3c;
    }
    .period-selectbox {
        margin-top: 5px;
        width: 50%;
    }
</style>
"""
st.markdown(card_style, unsafe_allow_html=True)

# Main section that displays the content of each page
if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.sidebar.success(f"Successfully loaded file: {uploaded_file.name}")
    st.sidebar.write(f"Data loaded successfully with {df.shape[0]} rows and {df.shape[1]} columns.")
    total_submissions = len(df)



    # Implement the logic for each page based on the sidebar selection
    if page == "Submissions":
        st.title("Submissions Overview")

    # Compute KPIs
        total_submissions = len(df)
        approval_count = df[df['status_challengesubmissions'].isin(['APPROVED', 'CLAIM_APPROVED'])].shape[0]
        approval_rate = (approval_count / total_submissions * 100) if total_submissions > 0 else 0
        most_popular_challenge = df['title.fr'].mode()[0] if 'title.fr' in df.columns and not df['title.fr'].empty else "N/A"
        # Count total tickets by 'photos.$oid'
        total_tickets = df['photos.$oid'].nunique()
        # Count submissions by their status
        submission_status_counts = df['status_challengesubmissions'].value_counts()
        relevant_statuses = ['REJECTED', 'IN_PROGRESS']  # Replace with actual values in your dataset
        filtered_status_counts = submission_status_counts[submission_status_counts.index.isin(relevant_statuses)]


    # Calculate new submissions based on selected period
# convertir la colonne 'createdAt_challengesubmissions' en datetime
    if 'createdAt_challengesubmissions' in df.columns:
        df['createdAt_challengesubmissions'] = pd.to_datetime(df['createdAt_challengesubmissions'], errors='coerce')

        # Filtrez les lignes avec des valeurs nulles après la conversion pour éviter les erreurs
        df = df[df['createdAt_challengesubmissions'].notnull()]

    # Add a period selection dropdown for the user
        period_options = ['Daily', 'Weekly', 'Monthly']
        selected_period = st.selectbox("Select Period", period_options, index=0)  # Default to 'Daily'

    # Calculate new submissions based on selected period
        today = pd.to_datetime('today').normalize()  # Normalize to remove the time part
        if selected_period == 'Daily':
            new_submissions = df[df['createdAt_challengesubmissions'] == today].shape[0]
            previous_period_submissions = df[df['createdAt_challengesubmissions'] == (today - pd.Timedelta(days=1))].shape[0]
        elif selected_period == 'Weekly':
            new_submissions = df[df['createdAt_challengesubmissions'] >= (today - pd.Timedelta(days=7))].shape[0]
            previous_period_submissions = df[(df['createdAt_challengesubmissions'] < (today - pd.Timedelta(days=7))) & 
                                         (df['createdAt_challengesubmissions'] >= (today - pd.Timedelta(days=14)))].shape[0]
        elif selected_period == 'Monthly':
            new_submissions = df[df['createdAt_challengesubmissions'] >= (today - pd.DateOffset(months=1))].shape[0]
            previous_period_submissions = df[(df['createdAt_challengesubmissions'] < (today - pd.DateOffset(months=1))) & 
                                         (df['createdAt_challengesubmissions'] >= (today - pd.DateOffset(months=2)))].shape[0]

        period_growth_rate = ((new_submissions - previous_period_submissions) / previous_period_submissions * 100) if previous_period_submissions > 0 else 0
        growth_class = "kpi-growth" if period_growth_rate >= 0 else "kpi-growth negative"


    # Display KPIs 
        col1, col2, col3= st.columns(3)

        with col1:  
            st.markdown("<div class='kpi-card'><div class='kpi-title'>Total Submissions 📊</div><div class='kpi-value'>{}</div></div>".format(total_submissions), unsafe_allow_html=True)

        with col2:
            st.markdown(
                f"<div class='kpi-card'>"
                f"<div class='kpi-title'>New Submissions ✨</div>"
                f"<div class='kpi-value'>{new_submissions}</div>"
                f"<div class='{growth_class}'>{period_growth_rate:+.2f}% growth</div>"
                f"</div>",
                unsafe_allow_html=True
            )

        with col3:
            st.markdown("<div class='kpi-card'><div class='kpi-title'>Approval Rate ✅</div><div class='kpi-value'>{:.2f}%</div></div>".format(approval_rate), unsafe_allow_html=True)


        col4, col5, col6= st.columns(3)

        # KPI for total tickets
        with col4:
            st.markdown("<div class='kpi-card'><div class='kpi-title'>Total Tickets 🎫</div><div class='kpi-value'>{}</div></div>".format(total_tickets), unsafe_allow_html=True)

        # KPI for submission breakdown by status
# KPI for submission breakdown by status (in a single line)

        with col5:
            st.markdown(
                "<div class='kpi-card'><div class='kpi-title'>Approved Submissions ✅</div>"
                "<div class='kpi-value'>{}</div></div>".format(approval_count),
                unsafe_allow_html=True
            )

        with col6:
            status_breakdown = ", ".join([f"{status}: {count}" for status, count in filtered_status_counts.items()])
            st.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Rejected/Pending</div>
            <div class='kpi-value' style='font-size:15px;'>{status_breakdown}</div>
        </div>
        """, 
        unsafe_allow_html=True
    )


        st.markdown("""
            <style>
            .custom-table-container {
                margin-top: 26px;  /* Adjust the space above the table (e.g., 20px) */
            }
            </style>
        """, unsafe_allow_html=True)

        # Display the map for the number of submissions per Wilaya
        geojson_data = load_geojson()


        if 'Wilaya' in df.columns:
            # Normalize Wilaya names
            df['Wilaya'] = df['Wilaya'].str.lower().str.strip()
    
            # Count submissions per Wilaya
            submission_count_per_wilaya = df['Wilaya'].value_counts().reset_index()
            submission_count_per_wilaya.columns = ['Wilaya', 'submission_count']
    
            # Sort by submission count in descending order
            submission_count_per_wilaya = submission_count_per_wilaya.sort_values(by='submission_count', ascending=False)
    
            # Create the columns for the map and the table
            col_map, col_table = st.columns([2, 1])

            # Display the map
            with col_map:
                display_wilaya_map(submission_count_per_wilaya, geojson_data, 'Wilaya', 'submission_count', metric='submission_count')

    # Display the table for the number of submissions per Wilaya
            with col_table:
            #    st.subheader("Wilaya Submissions Overview")
               st.markdown('<div class="custom-table-container">', unsafe_allow_html=True)
               st.dataframe(submission_count_per_wilaya, height=540, use_container_width=True)
               st.markdown('</div>', unsafe_allow_html=True)





    elif page == "Cashback":
        st.title("Cashback Overview")

    # Ensure that total_submissions is computed for the Cashback page as well
        total_submissions=len(df)

        # Compute Cashback KPIs
        total_cashback = df['Cashback Crédité'].sum() if 'Cashback Crédité' in df.columns else 0
        total_budget = df['Budget Consommé'].sum() if 'Budget Consommé' in df.columns else 1
        cashback_rate = (total_cashback / total_budget * 100) if total_budget > 0 else 0
        avg_cashback_per_submission = total_cashback / total_submissions if total_submissions > 0 else 0

        # Calculate cashback distribution across user types
        if 'userType' in df.columns and 'Cashback Crédité' in df.columns:
            user_cashback_distribution = df.groupby('userType')['Cashback Crédité'].sum().reset_index()

        # Display Cashback KPIs
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("<div class='kpi-card'><div class='kpi-title'>Total Cashback Distributed 💰</div><div class='kpi-value'>{:.2f} DZD</div></div>".format(total_cashback), unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='kpi-card'><div class='kpi-title'>Budget Consumed 💸</div><div class='kpi-value'>{:.2f}%</div></div>".format(cashback_rate), unsafe_allow_html=True)

        with col3:
            st.markdown("<div class='kpi-card'><div class='kpi-title'>Avg Cashback per Submission 💲</div><div class='kpi-value'>{:.2f} DZD</div></div>".format(avg_cashback_per_submission), unsafe_allow_html=True)

        # Additional Visualizations
        col4, col5 = st.columns(2)

    # 1. Cashback distribution across user types (Pie Chart)
        if 'userType' in df.columns and 'Cashback Crédité' in df.columns:
            fig_cashback_distribution = px.pie(
            user_cashback_distribution,
            names='userType',
            values='Cashback Crédité',
            title='Cashback Distribution by User Type',
            color_discrete_sequence=color_scheme,
            hole=0.4  # Creates a donut chart for a modern look
        )
            fig_cashback_distribution.update_traces(textposition='inside', textinfo='percent+label')
            fig_cashback_distribution.update_layout(
            title=dict(font=dict(size=18)),
            margin=dict(t=50, b=20, l=0, r=0)
        )
            col4.plotly_chart(fig_cashback_distribution, use_container_width=True)

    # 2. Cashback rate over time (Line Chart)
        if 'createdAt_challengesubmissions' in df.columns and 'Cashback Crédité' in df.columns:
            cashback_over_time = df.groupby(df['createdAt_challengesubmissions'].dt.to_period('M'))['Cashback Crédité'].sum().reset_index()
            cashback_over_time.columns = ['Month', 'Total Cashback']

            fig_cashback_rate = px.line(
            cashback_over_time,
            x='Month',
            y='Total Cashback',
            title='Cashback Distributed Over Time',
            labels={'Total Cashback': 'Total Cashback (DZD)', 'Month': 'Month'},
            color_discrete_sequence=color_scheme
            )
            fig_cashback_rate.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
            col5.plotly_chart(fig_cashback_rate, use_container_width=True)







    elif page == "Entreprises":
        st.title("Entreprises Overview")
        # Copy over the existing enterprises-related code, e.g. data by challenge owners
        # Display relevant KPIs and visualizations

    elif page == "Products":
        st.title("Products Overview")
        # Copy over the existing product-related code, e.g. visualizations of products, challenges
        # Display product-related KPIs and visualizations

    elif page == "Users":
        st.title("Users Overview")
        # Copy over the existing user-related code, e.g. KPIs and visualizations related to users
        # Display user-related KPIs and visualizations

    elif page == "Shops":
        st.title("Shops Overview")
        # Copy over the existing shops-related code, e.g. KPIs and visualizations related to shops
        # Display shop-related KPIs and visualizations

else:
    st.info("Please upload a CSV or Excel file to see the dashboard content.")
