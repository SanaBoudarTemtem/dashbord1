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

color_scheme = ['#e67e22', '#f5b041', '#d35400', '#f8c471', '#f39c12']

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

    # st.subheader(f"🌍 Geographical Distribution ")
    folium_static(folium_map)

# Load user data from the file uploader
st.sidebar.image("C:/Users/ASUS/Documents/dashbord1/Logo-temtemOne.svg", use_column_width=True)
st.sidebar.subheader("Choose a CSV or Excel file")
uploaded_file = st.sidebar.file_uploader("Drag and drop file here", type=["csv", "xlsx"])




# Sidebar for navigation with buttons
# st.sidebar.title("Navigation")

# CSS for styling buttons to take full width
st.sidebar.markdown(
    """
    <style>
    .stButton button {
        width: 100%;
        margin: 0 auto;
        background-color: #e67e22;
        color: white;
        border-radius: 0px;
        height: 50px;
        font-weight: bold;
        font-size: 16px;
    }
    .stButton button:hover {
        background-color: #0a0a23;
    }
    </style>
    """, unsafe_allow_html=True
)


# Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = 'Submissions'  # Default page

# Sidebar for navigation with buttons
# st.sidebar.title("Navigation")

# Navigation buttons with session state management
if st.sidebar.button("Submissions"):
    st.session_state.page = 'Submissions'
if st.sidebar.button("Cashback"):
    st.session_state.page = 'Cashback'
if st.sidebar.button("Campaigns"):
    st.session_state.page = 'Entreprises'
if st.sidebar.button("Products"):
    st.session_state.page = 'Products'
if st.sidebar.button("Users"):
    st.session_state.page = 'Users'
if st.sidebar.button("Shops"):
    st.session_state.page = 'Shops'


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
</style>
"""
st.markdown(card_style, unsafe_allow_html=True)

# Main section that displays the content of each page
if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, on_bad_lines='skip')
    else:
        df = pd.read_excel(uploaded_file, on_bad_lines='skip')
    
    st.sidebar.success(f"Successfully loaded file: {uploaded_file.name}")
    st.sidebar.write(f"Data loaded successfully with {df.shape[0]} rows and {df.shape[1]} columns.")
    total_submissions = len(df)

    # Implement the logic for each page based on the sidebar selection
    if st.session_state.page == "Submissions":
        st.title("Submissions Overview")

        # Period selection for Submissions page only
        period_options = ['Daily', 'Weekly', 'Monthly']
        selected_period = st.selectbox("Select Period", period_options, index=0)

        # Compute KPIs for Submissions
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
        if 'createdAt_challengesubmissions' in df.columns:
            df['createdAt_challengesubmissions'] = pd.to_datetime(df['createdAt_challengesubmissions'], errors='coerce')
            df = df[df['createdAt_challengesubmissions'].notnull()]

        today = pd.to_datetime('today').normalize()
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

        # Display KPIs for the Submissions page
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Total Submissions 📊</div><div class='kpi-value'>{total_submissions}</div></div>", unsafe_allow_html=True)

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
            st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Approval Rate ✅</div><div class='kpi-value'>{approval_rate:.2f}%</div></div>", unsafe_allow_html=True)

        col4, col5, col6 = st.columns(3)

        with col4:
            st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Total Tickets 🎫</div><div class='kpi-value'>{total_tickets}</div></div>", unsafe_allow_html=True)

        with col5:
            st.markdown(
                f"<div class='kpi-card'><div class='kpi-title'>Approved Submissions ✅</div>"
                f"<div class='kpi-value'>{approval_count}</div></div>",
                unsafe_allow_html=True
            )

        with col6:
            status_breakdown = ", ".join([f"{status}: {count}" for status, count in filtered_status_counts.items()])
            st.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Rejected/Pending ❌</div>
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

        

        # Ensure the 'createdAt_challengesubmissions' column is in datetime format
        if 'createdAt_challengesubmissions' in df.columns:
            df['createdAt_challengesubmissions'] = pd.to_datetime(df['createdAt_challengesubmissions'], errors='coerce')
            df = df[df['createdAt_challengesubmissions'].notnull()]  # Remove null dates

            # Daily submissions
            daily_submissions = df.groupby(df['createdAt_challengesubmissions'].dt.date).size().reset_index(name='Submissions')
            fig_daily = px.line(
                daily_submissions,
                x='createdAt_challengesubmissions',
                y='Submissions',
                title='Daily Submissions',
                labels={'createdAt_challengesubmissions': 'Date', 'Submissions': 'Number of Submissions'},
                color_discrete_sequence=color_scheme
            )
            fig_daily.update_layout(xaxis_title='Date', yaxis_title='Submissions')

            # Weekly submissions
            weekly_submissions = df.groupby(df['createdAt_challengesubmissions'].dt.to_period('W')).size().reset_index(name='Submissions')
            weekly_submissions['createdAt_challengesubmissions'] = weekly_submissions['createdAt_challengesubmissions'].astype(str)  # Convert period to string
            fig_weekly = px.line(
                weekly_submissions,
                x='createdAt_challengesubmissions',
                y='Submissions',
                title='Weekly Submissions',
                labels={'createdAt_challengesubmissions': 'Week', 'Submissions': 'Number of Submissions'},
                color_discrete_sequence=color_scheme
            )
            fig_weekly.update_layout(xaxis_title='Week', yaxis_title='Submissions')

            # Monthly submissions
            monthly_submissions = df.groupby(df['createdAt_challengesubmissions'].dt.to_period('M')).size().reset_index(name='Submissions')
            monthly_submissions['createdAt_challengesubmissions'] = monthly_submissions['createdAt_challengesubmissions'].astype(str)  # Convert period to string
            fig_monthly = px.line(
                monthly_submissions,
                x='createdAt_challengesubmissions',
                y='Submissions',
                title='Monthly Submissions',
                labels={'createdAt_challengesubmissions': 'Month', 'Submissions': 'Number of Submissions'},
                color_discrete_sequence=color_scheme
            )
            fig_monthly.update_layout(xaxis_title='Month', yaxis_title='Submissions')

            # Display the 3 graphs
            # st.subheader("Submissions Over Time")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.plotly_chart(fig_daily, use_container_width=True)
            with col2:
                st.plotly_chart(fig_weekly, use_container_width=True)
            with col3:
                st.plotly_chart(fig_monthly, use_container_width=True)



    elif st.session_state.page == "Cashback":
        st.title("Cashback Overview")

        # Compute Cashback KPIs
        total_cashback = df['Cashback Crédité'].sum() if 'Cashback Crédité' in df.columns else 0
        total_budget = df['Budget Consommé'].sum() if 'Budget Consommé' in df.columns else 1
        cashback_rate = (total_cashback / total_budget * 100) if total_budget > 0 else 0
        avg_cashback_per_submission = total_cashback / total_submissions if total_submissions > 0 else 0

        # Display Cashback KPIs
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Total Cashback Distributed 💰</div><div class='kpi-value'>{total_cashback:.2f} DZD</div></div>", unsafe_allow_html=True)

        with col2:
            st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Budget Consumed 💸</div><div class='kpi-value'>{cashback_rate:.2f}%</div></div>", unsafe_allow_html=True)

        with col3:
            st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Avg Cashback per Submission 💲</div><div class='kpi-value'>{avg_cashback_per_submission:.2f} DZD</div></div>", unsafe_allow_html=True)

        # Additional Visualizations for Cashback
        if 'userType' in df.columns and 'Cashback Crédité' in df.columns:
            user_cashback_distribution = df.groupby('userType')['Cashback Crédité'].sum().reset_index()

            fig_cashback_distribution = px.pie(
                user_cashback_distribution,
                names='userType',
                values='Cashback Crédité',
                title='Cashback Distribution by User Type',
                color_discrete_sequence=color_scheme,
                hole=0.4
            )
            fig_cashback_distribution.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_cashback_distribution, use_container_width=True)


# Ensure the 'createdAt_challengesubmissions' is in datetime format
        # Ensure the 'createdAt_challengesubmissions' is in datetime format
        if 'createdAt_challengesubmissions' in df.columns:
    # Try to convert the column to datetime, coercing errors to NaT (Not a Time)
            df['createdAt_challengesubmissions'] = pd.to_datetime(df['createdAt_challengesubmissions'], errors='coerce')

    # Filter out any rows where the datetime conversion failed (NaT values)
            df = df[df['createdAt_challengesubmissions'].notnull()]

    # Proceed with grouping by the month if the column is successfully converted
            cashback_over_time = df.groupby(df['createdAt_challengesubmissions'].dt.to_period('M'))['Cashback Crédité'].sum().reset_index()

    # Inspect the columns of cashback_over_time
            # st.write(cashback_over_time.columns)

    # Adjust column renaming based on what is returned from reset_index()
    # Assuming the columns are ['createdAt_challengesubmissions', 'Cashback Crédité']
            cashback_over_time.columns = ['Month', 'Total Cashback']

    # Convert 'Month' (Period) to string to avoid JSON serialization issues
            cashback_over_time['Month'] = cashback_over_time['Month'].astype(str)

    # Create the line chart
            fig_cashback_rate = px.line(
        cashback_over_time,
        x='Month',
        y='Total Cashback',
        title='Cashback Distributed Over Time',
        labels={'Total Cashback': 'Total Cashback (DZD)', 'Month': 'Month'},
        color_discrete_sequence=color_scheme
    )
            st.plotly_chart(fig_cashback_rate, use_container_width=True)



    elif st.session_state.page == "Entreprises":
        st.title("Entreprises Overview")
        # Add logic for KPIs and visualizations related to entreprises




    elif st.session_state.page == "Products":
    
        st.title("Products Overview")

    # Check if 'title.fr' and 'Cashback Crédité' exist in the dataframe
        if 'title.fr' in df.columns and 'Cashback Crédité' in df.columns:
        # Total number of unique products
            total_products = df['title.fr'].nunique()
        
        # Top products by number of submissions
            top_products_by_submissions = df['title.fr'].value_counts().head(10)
        
        # Cashback credited per product
            cashback_per_product = df.groupby('title.fr')['Cashback Crédité'].sum().reset_index()
            cashback_per_product = cashback_per_product.sort_values(by='Cashback Crédité', ascending=False).head(10)
        
        # Product submissions over time (if 'createdAt_challengesubmissions' exists)
            if 'createdAt_challengesubmissions' in df.columns:
                df['createdAt_challengesubmissions'] = pd.to_datetime(df['createdAt_challengesubmissions'], errors='coerce')
                df = df[df['createdAt_challengesubmissions'].notnull()]

                submissions_over_time = df.groupby([df['createdAt_challengesubmissions'].dt.to_period('M'), 'title.fr']).size().unstack(fill_value=0)
                submissions_over_time.index = submissions_over_time.index.astype(str)  # Convert periods to strings for plotting

            # Plot submissions over time for top products
                top_products = top_products_by_submissions.index.tolist()
                submissions_over_time_top = submissions_over_time[top_products]

                fig_submissions_over_time = px.line(
                submissions_over_time_top,
                title='Product Submissions Over Time (Top Products)',
                labels={'createdAt_challengesubmissions': 'Month', 'value': 'Submissions'},
                color_discrete_sequence=color_scheme
            )
                fig_submissions_over_time.update_layout(xaxis_title='Month', yaxis_title='Number of Submissions')

    # Display KPIs for Products
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Total Products 🛍️</div><div class='kpi-value'>{total_products}</div></div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Top Product📈</div><div class='kpi-value'>{top_products_by_submissions.index[0]}</div></div>", unsafe_allow_html=True)

          
            # Display the two tables in the same line with full width
            # st.subheader("Top 10 Products by Submissions and Cashback Credited")

# Create two columns
            col1, col2 = st.columns(2)

# Display Top 10 Products by Submissions in the first column
            with col1:
                st.markdown("###### Top 10 Products by Submissions")
                st.dataframe(top_products_by_submissions, use_container_width=True)

            # Display Cashback per Product in the second column
            with col2:
                st.markdown("###### Top 10 Products by Cashback Credited")
                st.dataframe(cashback_per_product, use_container_width=True)


                    # Plot submissions over time
            st.plotly_chart(fig_submissions_over_time, use_container_width=True)







    elif st.session_state.page == "Users":
        st.title("Users Overview")

    # Check if 'submittedBy.id' and name/surname columns exist in the dataframe
        if 'submittedBy.id' in df.columns and 'Prenom' in df.columns and 'Nom' in df.columns:
        # Total number of unique users
            total_unique_users = df['submittedBy.id'].nunique()

        # Get a dataframe of users with their name and surname, and the count of submissions per user
            user_submissions = df.groupby(['submittedBy.id', 'Prenom', 'Nom']).size().reset_index(name='Submissions')

        # Sort by submissions and take the top 10 (or show all unique users)
            top_users_by_name = user_submissions.sort_values(by='Submissions', ascending=False).head(10)

        # User submissions over time (if 'createdAt_challengesubmissions' exists)
            if 'createdAt_challengesubmissions' in df.columns:
                df['createdAt_challengesubmissions'] = pd.to_datetime(df['createdAt_challengesubmissions'], errors='coerce')
                df = df[df['createdAt_challengesubmissions'].notnull()]

                submissions_over_time_by_users = df.groupby([df['createdAt_challengesubmissions'].dt.to_period('M'), 'submittedBy.id']).size().unstack(fill_value=0)
                submissions_over_time_by_users.index = submissions_over_time_by_users.index.astype(str)  # Convert periods to strings for plotting

            # Plot submissions over time for top users
                top_user_ids = top_users_by_name['submittedBy.id'].tolist()
                submissions_over_time_top_users = submissions_over_time_by_users[top_user_ids]

                fig_submissions_over_time_users = px.line(
                    submissions_over_time_top_users,
                title='User Submissions Over Time (Top Users)',
                labels={'createdAt_challengesubmissions': 'Month', 'value': 'Submissions'},
                color_discrete_sequence=color_scheme
            )
                fig_submissions_over_time_users.update_layout(xaxis_title='Month', yaxis_title='Number of Submissions')

        # User type distribution (if 'userType' exists)
                    # Calculate age from 'dateOfBirth'
        df['Date de naissance'] = pd.to_datetime(df['Date de naissance'], errors='coerce')
        today = pd.to_datetime('today').normalize()
        df['Age'] = df['Date de naissance'].apply(lambda dob: today.year - dob.year if pd.notnull(dob) else None)

        # Gender distribution
        if 'Genre' in df.columns:
            gender_distribution = df['Genre'].value_counts()

            # Plot gender distribution (Pie chart)
            fig_gender_distribution = px.pie(
                gender_distribution,
                names=gender_distribution.index,
                values=gender_distribution.values,
                title="Gender Distribution",
                color_discrete_sequence=color_scheme,
                hole=0.4
            )
            fig_gender_distribution.update_traces(textposition='inside', textinfo='percent+label')

        # Age distribution
        if 'Age' in df.columns:
            fig_age_distribution = px.histogram(
                df[df['Age'].notnull()],  # Exclude null values for age
                x='Age',
                nbins=10,  # Adjust the number of bins for age ranges
                title="Age Distribution",
                labels={'Age': 'Age', 'count': 'Number of Users'},
                color_discrete_sequence=color_scheme
            )
            fig_age_distribution.update_layout(bargap=0.1)  # Adjust spacing between bars if needed

        # User type distribution
        if 'userType' in df.columns:
            user_type_distribution = df['userType'].value_counts()

            # Plot user type distribution (Pie chart)
            fig_user_type_distribution = px.pie(
                user_type_distribution,
                names=user_type_distribution.index,
                values=user_type_distribution.values,
                title="User Type Distribution",
                color_discrete_sequence=color_scheme,
                hole=0.4
            )
            fig_user_type_distribution.update_traces(textposition='inside', textinfo='percent+label')

    # Display KPIs for Users
            col1, col2 = st.columns(2)
            # Calculer la moyenne des soumissions par utilisateur
            unique_users = df['submittedBy.id'].nunique()
            total_user_submissions = df['submittedBy.id'].count() if 'submittedBy.id' in df.columns else 0
            avg_submissions_per_user = total_user_submissions / unique_users if unique_users > 0 else 0

            with col1:
                st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Total Unique Users 👤</div><div class='kpi-value'>{total_unique_users}</div></div>", unsafe_allow_html=True)
            
            with col2:
                    # Afficher le KPI pour la moyenne des soumissions par utilisateur
                st.markdown(
        f"<div class='kpi-card'><div class='kpi-title'>Average Submissions per User 📝</div><div class='kpi-value'>{avg_submissions_per_user:.2f}</div></div>",
        unsafe_allow_html=True
    )

        # Display Users (Name, Surname, Submissions)
            st.subheader("Top Users by Submissions")
            st.dataframe(top_users_by_name[['Prenom', 'Nom', 'Submissions']],use_container_width=True)

        # Plot submissions over time
            st.subheader("User Submissions Over Time (Top Users)")
            st.plotly_chart(fig_submissions_over_time_users, use_container_width=True)

        # Plot User Type Distribution (if applicable)
                    # Display the three charts (Gender, Age, and User Type Distribution) on the same line
        col1, col2, col3 = st.columns(3)

        # Plot Gender Distribution
        with col1:
            st.subheader("Gender Distribution")
            st.plotly_chart(fig_gender_distribution, use_container_width=True)

        # Plot Age Distribution
        with col2:
            st.subheader("Age Distribution")
            st.plotly_chart(fig_age_distribution, use_container_width=True)

        # Plot User Type Distribution
        with col3:
            st.subheader("User Type Distribution")
            st.plotly_chart(fig_user_type_distribution, use_container_width=True)


 
    elif st.session_state.page == "Shops":
        st.title("Shops Overview")

    # Vérifier si 'storeName' est dans le fichier
        if 'storeName' in df.columns:
        # Calculer le nombre total de magasins uniques
            unique_stores = df['storeName'].nunique()

        # Calculer le nombre total de soumissions associées aux magasins
            total_store_submissions = df['storeName'].count()

        # Calculer la moyenne des soumissions par magasin
            avg_submissions_per_store = total_store_submissions / unique_stores if unique_stores > 0 else 0

        # Créer une table qui montre le nombre de soumissions par magasin
            submissions_per_store = df['storeName'].value_counts().reset_index()
            submissions_per_store.columns = ['Store Name', 'Submissions']

        # Afficher les KPI
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                f"<div class='kpi-card'><div class='kpi-title'>Total Unique Stores 🏪</div><div class='kpi-value'>{unique_stores}</div></div>",
                unsafe_allow_html=True
            )

            with col2:
                st.markdown(
                f"<div class='kpi-card'><div class='kpi-title'>Average Submissions per Store 📊</div><div class='kpi-value'>{avg_submissions_per_store:.2f}</div></div>",
                unsafe_allow_html=True
            )

        # Afficher le tableau des soumissions par magasin
            st.subheader("Submissions per Store")
            st.dataframe(submissions_per_store, height=500, use_container_width=True)

        else:
            st.warning("No store information available in the dataset.")



else:
    st.info("Please upload a CSV or Excel file to see the dashboard content.")
