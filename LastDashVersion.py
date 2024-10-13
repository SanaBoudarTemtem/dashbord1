import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import json


# Set the page configuration
st.set_page_config(
    page_title="🌟 Temtem One Submissions Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to load GeoJSON data for Wilayas
@st.cache_data
def load_geojson(geojson_path="all-wilayas.geojson"):
    with open(geojson_path, "r", encoding="utf-8") as file:
        return json.load(file)



color_scheme = ['#e67e22', '#f5b041', '#d35400', '#f8c471','#f39c12']

# Compute metrics per Wilaya for the table
def compute_wilaya_metrics(df):
    # Calculate total cashback per Wilaya
    if 'Wilaya' in df.columns and 'Cashback Crédité' in df.columns:
        cashback_per_wilaya = df.groupby('Wilaya')['Cashback Crédité'].sum().reset_index()
        cashback_per_wilaya.columns = ['Wilaya', 'Total Cashback']
    else:
        cashback_per_wilaya = pd.DataFrame(columns=['Wilaya', 'Total Cashback'])

    # Calculate the number of unique users per Wilaya
    if 'Wilaya' in df.columns and 'submittedBy.id' in df.columns:
        user_count_per_wilaya = df.groupby('Wilaya')['submittedBy.id'].nunique().reset_index()
        user_count_per_wilaya.columns = ['Wilaya', 'Unique Users']
    else:
        user_count_per_wilaya = pd.DataFrame(columns=['Wilaya', 'Unique Users'])

    # Calculate the number of submissions per Wilaya
    if 'Wilaya' in df.columns:
        submission_count_per_wilaya = df['Wilaya'].value_counts().reset_index()
        submission_count_per_wilaya.columns = ['Wilaya', 'Submissions']
    else:
        submission_count_per_wilaya = pd.DataFrame(columns=['Wilaya', 'Submissions'])

    # Merge the three dataframes on 'Wilaya'
    wilaya_metrics = cashback_per_wilaya.merge(user_count_per_wilaya, on='Wilaya', how='outer')
    wilaya_metrics = wilaya_metrics.merge(submission_count_per_wilaya, on='Wilaya', how='outer')

    # Fill NaN values with zeros for easier readability
    wilaya_metrics = wilaya_metrics.fillna(0)

    # Convert 'Total Cashback' to integer for better presentation if applicable
    wilaya_metrics['Total Cashback'] = wilaya_metrics['Total Cashback'].astype(int)

    return wilaya_metrics


# Function to display Wilaya map for users or submissions
def display_wilaya_map(data, geojson_data, name_column, value_column, metric='submission_count'):
    # Ensure the data is in a format compatible with .value_counts() and string handling
    wilaya_counts = data[[name_column, value_column]].copy()

    # Convert the GeoJSON to a GeoDataFrame for merging
    wilayas_gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])

    # Ensure consistency in name formatting (lowercase and strip spaces)
    wilayas_gdf['name'] = wilayas_gdf['name'].str.lower().str.strip()
    wilaya_counts[name_column] = wilaya_counts[name_column].astype(str).str.lower().str.strip()

    # Merge the counts into the GeoDataFrame
    wilayas_gdf = wilayas_gdf.merge(wilaya_counts, left_on='name', right_on=name_column, how='left')
    wilayas_gdf[value_column] = wilayas_gdf[value_column].fillna(0)  # Replace NaN with zero

    # Create the folium map
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

    # Add tooltips for more information
    folium.GeoJson(
        wilayas_gdf.__geo_interface__,
        tooltip=folium.features.GeoJsonTooltip(fields=['name', value_column],
                                               aliases=['Wilaya:', f'{value_column.replace("_", " ").title()}:'])
    ).add_to(folium_map)

    # Display the map using streamlit_folium
    st.subheader(f"🌍 Geographical Distribution ")
    folium_static(folium_map)






# logo in the sidebar
st.sidebar.image("C:/Users/ASUS/Documents/dashbord1/Logo-temtemOne.svg", use_column_width=True)

# Sidebar 
st.sidebar.subheader("Choose a CSV or Excel file")
uploaded_file = st.sidebar.file_uploader(
    "Drag and drop file here",
    type=["csv", "xlsx"]
)



# CSS for the KPI cards
card_style = """
<style>
    .kpi-card {
        background-color: #31333F;
        padding: 15px;
        border-radius: 12px;
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

if uploaded_file is not None:
    # Read the uploaded file based on file type
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.sidebar.success(f"Successfully loaded file: {uploaded_file.name}")
    st.sidebar.write(f"Data loaded successfully with {df.shape[0]} rows and {df.shape[1]} columns.")
    
    # Date range selector
    st.sidebar.subheader("Select Date Range")
    date_range = st.sidebar.date_input(
        "Select date range",
        [pd.to_datetime('2024-07-23'), pd.to_datetime('2024-10-03')]
    )

    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])


    # Filter data based on date range
    if 'createdAt_challengesubmissions' in df.columns:
        df['createdAt_challengesubmissions'] = pd.to_datetime(df['createdAt_challengesubmissions'], errors='coerce')
        df = df[(df['createdAt_challengesubmissions'] >= start_date) & 
                (df['createdAt_challengesubmissions'] <= end_date)]
    
    # Challenge selector based on `title.fr`
    st.sidebar.subheader("Select Challenge")
    challenge_options = ['All'] + df['title.fr'].unique().tolist() if 'title.fr' in df.columns else ['All']
    selected_challenge = st.sidebar.selectbox("Select Challenge", challenge_options)

    # Filter data based on selected challenge
    if selected_challenge != 'All' and 'title.fr' in df.columns:
        df = df[df['title.fr'] == selected_challenge]

    # Compute KPIs
    total_submissions = len(df)
    approval_count = df[df['status_challengesubmissions'].isin(['APPROVED', 'CLAIM_APPROVED'])].shape[0]
    approval_rate = (approval_count / total_submissions * 100) if total_submissions > 0 else 0
    most_popular_challenge = df['title.fr'].mode()[0] if 'title.fr' in df.columns and not df['title.fr'].empty else "N/A"
    
    # Unique users
    unique_users = df['submittedBy.id'].nunique() if 'submittedBy.id' in df.columns else 0
    active_users = df['submittedBy.id'].value_counts()[df['submittedBy.id'].value_counts() >= 2].count() if 'submittedBy.id' in df.columns else 0
    retention_rate = (active_users / unique_users * 100) if unique_users > 0 else 0
    
    # Cashback and budget
    total_cashback = df['Cashback Crédité'].sum() if 'Cashback Crédité' in df.columns else 0
    total_budget = df['Budget Consommé'].sum() if 'Budget Consommé' in df.columns else 1
    budget_rate = (total_cashback / total_budget * 100) if total_budget > 0 else 0
    avg_cashback_per_submission = total_cashback / total_submissions if total_submissions > 0 else 0

    # Calculate new submissions based on selected period
    period_options = ['Daily', 'Weekly', 'Monthly']
    selected_period = 'Daily'  # Default to 'Daily'

    # Calculate based on selected period
    if selected_period == 'Daily':
        new_submissions = df[df['createdAt_challengesubmissions'] == pd.to_datetime('today').normalize()].shape[0]
        previous_period_submissions = df[df['createdAt_challengesubmissions'] == (pd.to_datetime('today') - pd.Timedelta(days=1)).normalize()].shape[0]
    elif selected_period == 'Weekly':
        new_submissions = df[df['createdAt_challengesubmissions'] >= (pd.to_datetime('today') - pd.Timedelta(days=7))].shape[0]
        previous_period_submissions = df[(df['createdAt_challengesubmissions'] < (pd.to_datetime('today') - pd.Timedelta(days=7))) & 
                                         (df['createdAt_challengesubmissions'] >= (pd.to_datetime('today') - pd.Timedelta(days=14)))].shape[0]
    elif selected_period == 'Monthly':
        new_submissions = df[df['createdAt_challengesubmissions'] >= (pd.to_datetime('today') - pd.DateOffset(months=1))].shape[0]
        previous_period_submissions = df[(df['createdAt_challengesubmissions'] < (pd.to_datetime('today') - pd.DateOffset(months=1))) & 
                                         (df['createdAt_challengesubmissions'] >= (pd.to_datetime('today') - pd.DateOffset(months=2)))].shape[0]

    period_growth_rate = ((new_submissions - previous_period_submissions) / previous_period_submissions * 100) if previous_period_submissions > 0 else 0
    growth_class = "kpi-growth" if period_growth_rate >= 0 else "kpi-growth negative"

    # Display KPIs 
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:  
        st.markdown("<div class='kpi-card'><div class='kpi-title'>Total Submissions 📊</div><div class='kpi-value'>{}</div></div>".format(total_submissions), unsafe_allow_html=True)

    with col2:
        # New Submissions card with the period selector 
        with st.container():
            selected_period = st.selectbox(
                "Period",
                period_options,
                index=period_options.index('Daily'),  # Default to 'Daily'
                key="period_selector",
                label_visibility="collapsed"
            )

            # Calculate based on selected period
            if selected_period == 'Daily':
                new_submissions = df[df['createdAt_challengesubmissions'] == pd.to_datetime('today').normalize()].shape[0]
                previous_period_submissions = df[df['createdAt_challengesubmissions'] == (pd.to_datetime('today') - pd.Timedelta(days=1)).normalize()].shape[0]
            elif selected_period == 'Weekly':
                new_submissions = df[df['createdAt_challengesubmissions'] >= (pd.to_datetime('today') - pd.Timedelta(days=7))].shape[0]
                previous_period_submissions = df[(df['createdAt_challengesubmissions'] < (pd.to_datetime('today') - pd.Timedelta(days=7))) & 
                                                  (df['createdAt_challengesubmissions'] >= (pd.to_datetime('today') - pd.Timedelta(days=14)))].shape[0]
            elif selected_period == 'Monthly':
                new_submissions = df[df['createdAt_challengesubmissions'] >= (pd.to_datetime('today') - pd.DateOffset(months=1))].shape[0]
                previous_period_submissions = df[(df['createdAt_challengesubmissions'] < (pd.to_datetime('today') - pd.DateOffset(months=1))) & 
                                                 (df['createdAt_challengesubmissions'] >= (pd.to_datetime('today') - pd.DateOffset(months=2)))].shape[0]

            period_growth_rate = ((new_submissions - previous_period_submissions) / previous_period_submissions * 100) if previous_period_submissions > 0 else 0
            growth_class = "kpi-growth" if period_growth_rate >= 0 else "kpi-growth negative"

        # Display the New Submissions KPI card
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

    with col4:
        st.markdown("<div class='kpi-card'><div class='kpi-title'>Most Popular Challenge 🏆</div><div class='kpi-value'>{}</div></div>".format(most_popular_challenge), unsafe_allow_html=True)
    
    with col5:
        st.markdown("<div class='kpi-card'><div class='kpi-title'>Unique Users 🧒🏻</div><div class='kpi-value'>{}</div></div>".format(unique_users), unsafe_allow_html=True)

    # Row 2
    col6, col7, col8, col9, col10 = st.columns(5)
    
    with col6:
        st.markdown(
            "<div class='kpi-card'><div class='kpi-title'>Active Users 🧑🏻‍💻</div>"
            "<div class='kpi-value'>{}</div>"
            "<div class='kpi-growth'>{:.2f}% Retention</div></div>".format(active_users, retention_rate),
            unsafe_allow_html=True
        )
    
    with col7:
        st.markdown(
            "<div class='kpi-card'><div class='kpi-title'>Total Cashback Distributed 💰</div>"
            "<div class='kpi-value'>{} DZD</div></div>".format(total_cashback),
            unsafe_allow_html=True
        )

    with col8:
        st.markdown(
            "<div class='kpi-card'><div class='kpi-title'>Budget Consumed 💸</div>"
            "<div class='kpi-value'>{:.2f}%</div></div>".format(budget_rate),
            unsafe_allow_html=True
        )
    
    with col9:
        st.markdown(
            "<div class='kpi-card'><div class='kpi-title'>Avg Cashback per Submission💲</div>"
            "<div class='kpi-value'>{:.2f} DZD</div></div>".format(avg_cashback_per_submission),
            unsafe_allow_html=True
        )
    
    with col10:
        st.markdown(
            "<div class='kpi-card'><div class='kpi-title'>Approved Submissions ✅</div>"
            "<div class='kpi-value'>{}</div></div>".format(approval_count),
            unsafe_allow_html=True
        )


    # Geographical Analysis
    # st.subheader("🌍 Geographical Analysis")

    # Load GeoJSON data for Wilayas
    geojson_data = load_geojson()


    # Display the map for the number of submissions per Wilaya
    # Calculer le nombre de soumissions par Wilaya pour la carte

    # Display the map and the table for the number of submissions per Wilaya
    if 'Wilaya' in df.columns:
        # Normalize Wilaya names in the DataFrame
        df['Wilaya'] = df['Wilaya'].str.lower().str.strip()
        submission_count_per_wilaya = df['Wilaya'].value_counts().reset_index()
        submission_count_per_wilaya.columns = ['Wilaya', 'submission_count']

        # Create columns for the map and the table
        col_map, col_table = st.columns([2, 1])  # Adjust ratio to control space, [2, 1] makes the map wider

        with col_map:
            # Display the map
            display_wilaya_map(submission_count_per_wilaya, geojson_data, 'Wilaya', 'submission_count', metric='submission_count')

        with col_table:
            # Compute metrics for the table
            wilaya_metrics = compute_wilaya_metrics(df)

            # Select only the required columns: 'Wilaya', 'Total Cashback', 'Unique Users'
            wilaya_table = wilaya_metrics[['Wilaya', 'Total Cashback', 'Unique Users']]

            # Adjust CSS for a smaller table display
            st.markdown(
            """
            <style>
                .small-table-container {
                    max-height: 300px;
                    overflow-y: auto;
                    font-size: 12px;
                }
            </style>
            """,
            unsafe_allow_html=True
        )
        
            st.markdown('<div class="small-table-container">', unsafe_allow_html=True)
            st.dataframe(wilaya_table, height=540, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)



    # # Display the map for the number of submissions per Wilaya
    # if 'Wilaya' in df.columns:
    #     submission_count_per_wilaya = df['Wilaya'].value_counts().reset_index()
    #     submission_count_per_wilaya.columns = ['Wilaya', 'submission_count']
    #     display_wilaya_map(submission_count_per_wilaya, geojson_data, 'Wilaya', 'submission_count', metric='submission_count')

        # Compute metrics and display the table after the map
    #     wilaya_metrics = compute_wilaya_metrics(df)
    #     # st.subheader("📊 Wilaya Metrics Overview")
    #     st.markdown(
    #     """
    #     <style>
    #     .dataframe-container {
    #         display: flex;
    #         justify-content: center;
    #         margin: 20px 0;
    #     }
    #     .dataframe-content {
    #         width: 100%;
    #         max-width: 1000px;
    #     }
    #     </style>
    #     """,
    #     unsafe_allow_html=True
    # )
    #     st.markdown('<div class="dataframe-container"><div class="dataframe-content">', unsafe_allow_html=True)
    #     st.dataframe(wilaya_metrics, use_container_width=True)
    #     st.markdown('</div></div>', unsafe_allow_html=True)




    # Additional Visualizations after the unique users table
    # Row 3: Cashback Distribution, Gender Distribution, Submissions per Gender
    col11, col12, col13 = st.columns(3)

    # 1. Cashback distribution across user types
    if 'userType' in df.columns and 'Cashback Crédité' in df.columns:
        user_cashback_distribution = df.groupby('userType')['Cashback Crédité'].sum().reset_index()
        fig1 = px.pie(
            user_cashback_distribution,
            names='userType',
            values='Cashback Crédité',
            title='Cashback Distribution by User Type',
            color_discrete_sequence=color_scheme,
            hole=0.4  # Creates a donut chart for a modern look
        )
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        fig1.update_layout(
            title=dict(font=dict(size=18)),
            margin=dict(t=50, b=20, l=0, r=0)
        )
        col11.plotly_chart(fig1, use_container_width=True)



    # 2. Enhanced Gender Distribution (number of unique users per gender)
    if 'Genre' in df.columns and 'submittedBy.id' in df.columns:
        gender_distribution = df.groupby('Genre')['submittedBy.id'].nunique().reset_index()
        gender_distribution.columns = ['Gender', 'Number of Unique Users']
        fig2 = px.pie(
            gender_distribution,
            names='Gender',
            values='Number of Unique Users',
            title='Gender Distribution of Unique Users',
            color_discrete_sequence=color_scheme,
            hole=0.4
        )
        fig2.update_traces(textposition='inside', textinfo='percent+label')
        fig2.update_layout(
            title=dict(font=dict(size=18)),
            margin=dict(t=50, b=20, l=0, r=0)
        )
        col12.plotly_chart(fig2, use_container_width=True)

    # 4. Distribution of users per segment
    if 'segment' in df.columns and 'submittedBy.id' in df.columns:
        users_per_segment = df.groupby('segment')['submittedBy.id'].nunique().reset_index()
        users_per_segment.columns = ['Segment', 'Number of Unique Users']
        fig4 = px.pie(
            users_per_segment,
            names='Segment',
            values='Number of Unique Users',
            title='Distribution of Users per Segment',
            color_discrete_sequence=color_scheme
        )
        fig4.update_traces(textposition='inside', textinfo='percent+label')
        fig4.update_layout(
            title=dict(font=dict(size=18)),
            margin=dict(t=50, b=20, l=0, r=0)
        )
        col13.plotly_chart(fig4, use_container_width=True)



    # Row 4: Users per Segment, Submissions per Segment, Submissions per Age Group
    col14, col15, col16 = st.columns(3)


    # 3. Number of submissions per gender
    if 'Genre' in df.columns:
        submissions_per_gender = df['Genre'].value_counts().reset_index()
        submissions_per_gender.columns = ['Gender', 'Number of Submissions']
        fig3 = px.bar(
            submissions_per_gender,
            x='Gender',
            y='Number of Submissions',
            title='Number of Submissions per Gender',
            text='Number of Submissions',
            color='Gender',
            color_discrete_sequence=color_scheme
        )
        fig3.update_traces(texttemplate='%{text}', textposition='outside', marker_line_width=1.5)
        fig3.update_layout(
            title=dict(font=dict(size=18)),
            xaxis_title='Gender',
            yaxis_title='Submissions Count',
            margin=dict(t=50, b=20, l=0, r=0)
        )
        col14.plotly_chart(fig3, use_container_width=True)



    # 5. Distribution of submissions per segment
    if 'segment' in df.columns:
        submissions_per_segment = df['segment'].value_counts().reset_index()
        submissions_per_segment.columns = ['Segment', 'Number of Submissions']
        fig5 = px.bar(
            submissions_per_segment,
            x='Segment',
            y='Number of Submissions',
            title='Number of Submissions per Segment',
            text='Number of Submissions',
            color='Segment',
            color_discrete_sequence=color_scheme
        )
        fig5.update_traces(texttemplate='%{text}', textposition='outside', marker_line_width=1.5)
        fig5.update_layout(
            title=dict(font=dict(size=18)),
            xaxis_title='Segment',
            yaxis_title='Submissions Count',
            margin=dict(t=50, b=20, l=0, r=0)
        )
        col15.plotly_chart(fig5, use_container_width=True)



    # Updated 6. Submissions distribution per calculated age bins
    # 6. Enhanced Submissions Distribution per Age Group
    if 'Date de naissance' in df.columns:
        # Convert 'Date de naissance' to datetime format if it's not already
        df['Date de naissance'] = pd.to_datetime(df['Date de naissance'], errors='coerce')

        # Calculate the age
        today = pd.to_datetime('today')
        df['Calculated Age'] = df['Date de naissance'].apply(
            lambda dob: today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day)) if pd.notnull(dob) else None
        )

        # Update the age distribution chart using the 'Calculated Age'
        age_bins = pd.cut(df['Calculated Age'], bins=[0, 18, 25, 35, 45, 60, 100], labels=['<18', '18-25', '26-35', '36-45', '46-60', '60+'])
        age_distribution = age_bins.value_counts().sort_index().reset_index()
        age_distribution.columns = ['Age Group', 'Number of Submissions']
        fig6 = px.bar(
            age_distribution,
            x='Age Group',
            y='Number of Submissions',
            title='Submissions Distribution per Age Group',
            text='Number of Submissions',
            color='Age Group',
            color_discrete_sequence=color_scheme
        )
        fig6.update_traces(texttemplate='%{text}', textposition='outside', marker_line_width=1.5)
        fig6.update_layout(
            title=dict(font=dict(size=18)),
            xaxis_title='Age Group',
            yaxis_title='Submissions Count',
            margin=dict(t=50, b=20, l=0, r=0)
        )
        col16.plotly_chart(fig6, use_container_width=True)


        
    # Table of unique users with their details
    st.subheader("Unique Users Overview")

    # Check if required columns exist in the DataFrame
    if 'Prenom' in df.columns and 'Nom' in df.columns and 'submittedBy.id' in df.columns and 'createdAt_challengesubmissions' in df.columns:
        # Calculate number of submissions per user and their first/last submission dates
        user_summary = df.groupby(['submittedBy.id', 'Prenom', 'Nom']).agg(
            number_of_submissions=('submittedBy.id', 'count'),
            first_submission_date=('createdAt_challengesubmissions', 'min'),
            last_submission_date=('createdAt_challengesubmissions', 'max')
        ).reset_index()

         # Convert datetime columns to date-only format
        user_summary['first_submission_date'] = user_summary['first_submission_date'].dt.date
        user_summary['last_submission_date'] = user_summary['last_submission_date'].dt.date

        # Concatenate full name for display purposes
        user_summary['full_name'] = user_summary['Prenom'] + ' ' + user_summary['Nom']

        # Reorder columns for better readability
        user_summary = user_summary[['full_name', 'number_of_submissions', 'first_submission_date', 'last_submission_date']]
    
        user_summary = user_summary.sort_values(by='number_of_submissions', ascending=False).reset_index(drop=True)
        # Display the table in a scrollable format
        st.dataframe(user_summary, height=300, use_container_width=True)
    else:
        st.info("The required columns for displaying user details are not available in the uploaded file.")



    # Sidebar for Chronological Analysis
    st.subheader("🕐 Chronological Analysis")
    chronological_period = st.selectbox(
        "Choose a period for time-based analysis",
        ['Daily', 'Weekly', 'Monthly'],
        index=0  # Default to 'Daily'
    )

    # Convert the dates into the selected period format
    if 'createdAt_challengesubmissions' in df.columns:
        period_mapping = {
            'Daily': 'D',
            'Weekly': 'W',
            'Monthly': 'M'
        }
        # Get the correct frequency based on user selection
        selected_frequency = period_mapping[chronological_period]
        df['date'] = df['createdAt_challengesubmissions'].dt.to_period(selected_frequency).dt.to_timestamp()

    # 1. Taux d'épuisement du budget over a given period
    if 'Cashback Crédité' in df.columns:
        budget_over_time = df.groupby('date')['Cashback Crédité'].sum().cumsum().reset_index()
        budget_over_time.columns = ['Date', 'Cumulative Cashback']
        fig_budget = px.line(
            budget_over_time,
            x='Date',
            y='Cumulative Cashback',
            title=f"Taux d'épuisement du budget over {chronological_period}",
            labels={'Cumulative Cashback': 'Cumulative Budget Depletion (DZD)', 'Date': 'Date'},
            color_discrete_sequence=color_scheme
        )
        fig_budget.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
        st.plotly_chart(fig_budget, use_container_width=True)

    # 2. User retention over time
    if 'submittedBy.id' in df.columns:
        user_counts = df.groupby('date')['submittedBy.id'].nunique()
        active_users = df[df['submittedBy.id'].duplicated(keep=False)].groupby('date')['submittedBy.id'].nunique()
        retention_over_time = (active_users / user_counts).fillna(0).reset_index()
        retention_over_time.columns = ['Date', 'Retention Rate']
        fig_retention = px.line(
            retention_over_time,
            x='Date',
            y='Retention Rate',
            title=f"User Retention Over {chronological_period}",
            labels={'Retention Rate': 'Retention Rate (%)', 'Date': 'Date'},
            color_discrete_sequence=color_scheme
        )
        fig_retention.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
        st.plotly_chart(fig_retention, use_container_width=True)

    # 3. Growth rate of new unique users over time
    if 'submittedBy.id' in df.columns:
        new_users = df.groupby('date')['submittedBy.id'].nunique().diff().fillna(0).reset_index()
        new_users.columns = ['Date', 'New Users']
        new_users['Growth Rate (%)'] = new_users['New Users'].pct_change().fillna(0) * 100
        fig_new_user_growth = px.line(
            new_users,
            x='Date',
            y='Growth Rate (%)',
            title=f"Growth Rate of New Unique Users Over {chronological_period}",
            labels={'Growth Rate (%)': 'Growth Rate (%)', 'Date': 'Date'},
            color_discrete_sequence=color_scheme
        )
        fig_new_user_growth.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
        st.plotly_chart(fig_new_user_growth, use_container_width=True)

    # 4. Growth rate of submissions over time
    if 'createdAt_challengesubmissions' in df.columns:
        submission_growth = df.groupby('date').size().diff().fillna(0).reset_index()
        submission_growth.columns = ['Date', 'New Submissions']
        submission_growth['Growth Rate (%)'] = submission_growth['New Submissions'].pct_change().fillna(0) * 100
        fig_submission_growth = px.line(
            submission_growth,
            x='Date',
            y='Growth Rate (%)',
            title=f"Growth Rate of Submissions Over {chronological_period}",
            labels={'Growth Rate (%)': 'Growth Rate (%)', 'Date': 'Date'},
            color_discrete_sequence=color_scheme
        )
        fig_submission_growth.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
        st.plotly_chart(fig_submission_growth, use_container_width=True)


    # Section for Stores Analysis
    st.subheader("🏪 Stores Analysis")

    # 1. Number of submissions per store (Table sorted in descending order)
    if 'storeName' in df.columns:
        store_submissions = df['storeName'].value_counts().reset_index()
        store_submissions.columns = ['Store', 'Number of Submissions']
        store_submissions = store_submissions.sort_values(by='Number of Submissions', ascending=False).reset_index(drop=True)
    
        st.markdown(
        """
        <style>
        .store-table-container {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }
        .store-table-content {
            width: 100%;
            max-width: 800px;
        }
        </style>
        """,
        unsafe_allow_html=True
        )
        st.markdown('<div class="store-table-container"><div class="store-table-content">', unsafe_allow_html=True)
        st.dataframe(store_submissions, use_container_width=True)
        st.markdown('</div></div>', unsafe_allow_html=True)
    else:
        st.info("The required column 'storeName' for store analysis is not available in the uploaded file.")


    # Section for Scan Type Analysis
    st.subheader("🔍 Scan Type Analysis")

    # Check if 'Type de scan' and 'status_challengesubmissions' columns are present
    if 'Type de scan' in df.columns and 'status_challengesubmissions' in df.columns:
    
        # 1. Approval rate per scan type
        scan_approval_data = df.groupby('Type de scan')['status_challengesubmissions'].apply(
            lambda x: (x.isin(['APPROVED', 'CLAIM_APPROVED']).sum() / len(x)) * 100
        ).reset_index()
        scan_approval_data.columns = ['Scan Type', 'Approval Rate (%)']

    # Create a styled bar chart for approval rates
        fig_approval_rate = px.bar(
        scan_approval_data,
        x='Scan Type',
        y='Approval Rate (%)',
        title='📊 Approval Rate per Scan Type',
        labels={'Approval Rate (%)': 'Approval Rate (%)', 'Scan Type': 'Type of Scan'},
        color='Approval Rate (%)',
        color_continuous_scale=color_scheme,
        template='plotly_dark'
    )
        fig_approval_rate.update_traces(marker_line_width=1.5, marker_line_color='black')
        fig_approval_rate.update_layout(
        title_x=0.5,
        title_font_size=18,
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # 2. Number of submissions per scan type
        scan_submission_data = df['Type de scan'].value_counts().reset_index()
        scan_submission_data.columns = ['Scan Type', 'Number of Submissions']

    # Create a styled pie chart for the number of submissions
        fig_submissions_per_scan = px.pie(
            scan_submission_data,
        names='Scan Type',
        values='Number of Submissions',
        title='📈 Number of Submissions per Scan Type',
        color_discrete_sequence=color_scheme,
        hole=0.4  # Creates a donut-like chart for better aesthetics
    )
        fig_submissions_per_scan.update_traces(textinfo='percent+label')
        fig_submissions_per_scan.update_layout(
        title_x=0.5,
        title_font_size=18,
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # Display both visualizations side by side
        col_scan1, col_scan2 = st.columns(2)
        with col_scan1:
            st.plotly_chart(fig_approval_rate, use_container_width=True)
        with col_scan2:
            st.plotly_chart(fig_submissions_per_scan, use_container_width=True)
    else:
        st.info("The required columns 'Type de scan' and 'status_challengesubmissions' are not available in the uploaded file.")




 
else:
    st.info("Please upload a CSV or Excel file to see the dashboard content.")
