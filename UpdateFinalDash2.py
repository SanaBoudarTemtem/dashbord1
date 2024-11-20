
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
if st.sidebar.button("Entreprises"):
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
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8', on_bad_lines='skip')
        except UnicodeDecodeError:
             
            df = pd.read_csv(uploaded_file, encoding='iso-8859-1', on_bad_lines='skip')

        df = df.rename(columns={'Date de crÃ©ation_user': 'Date de création_user'})
    
    st.sidebar.success(f"Successfully loaded file: {uploaded_file.name}")
    st.sidebar.write(f"Data loaded successfully with {df.shape[0]} rows and {df.shape[1]} columns.")
    total_submissions = len(df)

    # Implement the logic for each page based on the sidebar selection
    if st.session_state.page == "Submissions":
        st.title("Submissions Overview")

        # Period selection for Submissions page only
        period_options = ['Daily', 'Weekly', 'Monthly']
        selected_period = st.selectbox("Select Period to calculate submissions growth", period_options, index=0)

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
         

        avg_submissions_per_ticket = int(round(total_submissions / total_tickets)) if total_tickets > 0 else 0
        with col3:
            st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Avg Submissions per Ticket 🎫</div><div class='kpi-value'>{avg_submissions_per_ticket:.2f}</div></div>", unsafe_allow_html=True)

        col4, col5, col6 = st.columns(3)

        with col4:
            st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Total Tickets 🎫</div><div class='kpi-value'>{total_tickets}</div></div>", unsafe_allow_html=True)

        with col5:
            st.markdown(
                        f"<div class='kpi-card'><div class='kpi-title'>Approved Submissions ✅</div>"
                          f"<div class='kpi-value'>{approval_count}</div>"
                          f"<div class='kpi-growth'>{approval_rate:.2f}% Approval Rate</div></div>",
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
                margin-top: 18px;  /* Adjust the space above the table (e.g., 20px) */
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
            submission_count_per_wilaya.columns = ['Wilaya', 'submission count']
    
            # Sort by submission count in descending order
            submission_count_per_wilaya = submission_count_per_wilaya.sort_values('submission count', ascending=False).reset_index(drop=True)
    
            # Create the columns for the map and the table
            col_map, col_table = st.columns([2, 1])

            # Display the map
            with col_map:
                display_wilaya_map(submission_count_per_wilaya, geojson_data, 'Wilaya', 'submission count', metric='submission count')


            submission_count_per_wilaya['Participation Rate %'] = (submission_count_per_wilaya['submission count'] / total_submissions) * 100
            submission_count_per_wilaya['Participation Rate %'] = submission_count_per_wilaya['Participation Rate %'].round(2)

    # Display the table for the number of submissions per Wilaya
            with col_table:
            #    st.subheader("Wilaya Submissions Overview")
               st.markdown('<div class="custom-table-container">', unsafe_allow_html=True)
               st.dataframe(submission_count_per_wilaya[['Wilaya', 'submission count', 'Participation Rate %']].set_index('Wilaya'), height=510, use_container_width=True)
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

            # # Monthly submissions
            # monthly_submissions = df.groupby(df['createdAt_challengesubmissions'].dt.to_period('M')).size().reset_index(name='Submissions')
            # monthly_submissions['createdAt_challengesubmissions'] = monthly_submissions['createdAt_challengesubmissions'].astype(str)  # Convert period to string
            # fig_monthly = px.line(
            #     monthly_submissions,
            #     x='createdAt_challengesubmissions',
            #     y='Submissions',
            #     title='Monthly Submissions',
            #     labels={'createdAt_challengesubmissions': 'Month', 'Submissions': 'Number of Submissions'},
            #     color_discrete_sequence=color_scheme
            # )
            # fig_monthly.update_layout(xaxis_title='Month', yaxis_title='Submissions')


            # Monthly submissions as a histogram
            df['createdAt_challengesubmissions'] = pd.to_datetime(df['createdAt_challengesubmissions'], errors='coerce')
            monthly_submissions = df.groupby(df['createdAt_challengesubmissions'].dt.to_period('M')).size().reset_index(name='Submissions')

            # Convert Periods back to a datetime for consistency in the x-axis
            monthly_submissions['createdAt_challengesubmissions'] = monthly_submissions['createdAt_challengesubmissions'].dt.to_timestamp()

            # Ensure that all months in the range are included, even if no submissions happened
            start_date = monthly_submissions['createdAt_challengesubmissions'].min()            
            end_date = monthly_submissions['createdAt_challengesubmissions'].max()

            # Generate a complete range of months between the first and last submission
            full_range = pd.date_range(start=start_date, end=end_date, freq='MS')

            # Reindex the data to ensure all months are included, filling missing months with zero submissions
            monthly_submissions = monthly_submissions.set_index('createdAt_challengesubmissions').reindex(full_range, fill_value=0).reset_index()
            monthly_submissions.columns = ['Month', 'Submissions']  # Rename for clarity

            # Plot the histogram with the full range of months
            fig_monthly = px.bar(
    monthly_submissions,
    x='Month',
    y='Submissions',
    title='Monthly Submissions',
    labels={'Month': 'Month', 'Submissions': 'Number of Submissions'},
    color_discrete_sequence=color_scheme
)
            fig_monthly.update_layout(xaxis_title='Month', yaxis_title='Submissions')


            # Display the 3 graphs
            # st.subheader("Submissions Over Time")
            col1, col2= st.columns(2)
            with col1:
                st.plotly_chart(fig_daily, use_container_width=True)
            with col2:
                st.plotly_chart(fig_weekly, use_container_width=True)
            # with col3:
            
            st.plotly_chart(fig_monthly, use_container_width=True)

        # Créer deux colonnes pour afficher les graphiques sur la même ligne
        col1, col2 = st.columns(2)

        # Graphique 1: Number of submissions by scan type
        with col1:
            if 'Type de scan' in df.columns:
                submissions_by_scan_type = df['Type de scan'].value_counts().reset_index()
                submissions_by_scan_type.columns = ['Scan Type', 'Submissions']

                fig_scan_type = px.bar(submissions_by_scan_type, x='Scan Type', y='Submissions',
                               title="Number of Submissions by Scan Type",
                               labels={'Scan Type': 'Scan Type', 'Submissions': 'Number of Submissions'},
                               color_discrete_sequence=color_scheme)
                st.plotly_chart(fig_scan_type, use_container_width=True)

        # Graphique 2: Submissions approved by scan type
        with col2:
            if 'Type de scan' in df.columns and 'status_challengesubmissions' in df.columns:
                approved_submissions_by_scan_type = df[df['status_challengesubmissions'].isin(['APPROVED', 'CLAIM_APPROVED'])]['Type de scan'].value_counts().reset_index()
                approved_submissions_by_scan_type.columns = ['Scan Type', 'Approved Submissions']

                fig_approved_scan_type = px.bar(approved_submissions_by_scan_type, x='Scan Type', y='Approved Submissions',
                                        title="Approved Submissions by Scan Type",
                                        labels={'Scan Type': 'Scan Type', 'Approved Submissions': 'Approved Submissions'},
                                        color_discrete_sequence=color_scheme)
                st.plotly_chart(fig_approved_scan_type, use_container_width=True)                



    elif st.session_state.page == "Cashback":
        st.title("Cashback Overview")

        # Compute Cashback KPIs
        total_cashback = df['Cashback Crédité'].sum() if 'Cashback Crédité' in df.columns else 0
        # total_budget_consumed = df['Budget Consommé'].sum() if 'Budget Consommé' in df.columns else 1


        # cashback_rate = (total_cashback / total_budget_consumed * 100) if total_budget > 0 else 0
        avg_cashback_per_submission = round(total_cashback / total_submissions) if total_submissions > 0 else 0

         
            # Regrouper les données par ticket (photo ID) pour calculer les cashbacks par ticket
        if 'photos.$oid' in df.columns and 'Cashback Crédité' in df.columns:
            cashback_per_ticket = df.groupby('photos.$oid')['Cashback Crédité'].sum()

        # Calculer les KPI
            min_cashback_per_ticket = cashback_per_ticket.min() if not cashback_per_ticket.empty else 0
            max_cashback_per_ticket = cashback_per_ticket.max() if not cashback_per_ticket.empty else 0
            avg_cashback_per_ticket = round(cashback_per_ticket.mean()) if not cashback_per_ticket.empty else 0
        else:
            min_cashback_per_ticket = 0
            max_cashback_per_ticket = 0
            avg_cashback_per_ticket = 0

        # Display Cashback KPIs
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Total Cashback Distributed 💰</div><div class='kpi-value'>{total_cashback:,.2f} DZD</div></div>", unsafe_allow_html=True)

        with col2:
            # st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Budget Consumed 💸</div><div class='kpi-value'>{total_budget_consumed:.2f}%</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Avg Cashback per Submission 💲</div><div class='kpi-value'>{avg_cashback_per_submission:,.2f} DZD</div></div>", unsafe_allow_html=True)
      
        with col3:
            st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Avg Cashback per Ticket 💲</div><div class='kpi-value'>{avg_cashback_per_ticket:,.2f} DZD</div></div>", unsafe_allow_html=True)
            

        # Display Cashback KPIs
        col1, col2, col3= st.columns(3)

        with col1:
            st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Min Cashback💵</div><div class='kpi-value'>{min_cashback_per_ticket:,.2f} DZD</div></div>", unsafe_allow_html=True)

        with col2:
            st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Max Cashback💸</div><div class='kpi-value'>{max_cashback_per_ticket:,.2f} DZD</div></div>", unsafe_allow_html=True)
      



        # Check if the necessary columns exist in the dataframe
        if {'photos.$oid', 'submittedBy.id', 'Prenom', 'Nom', 'Cashback Crédité'}.issubset(df.columns):
            cashback_by_ticket = df.groupby('photos.$oid').agg(
        user_id=('submittedBy.id', 'first'),  # Get the first user ID (assuming it's the same for all submissions in a ticket)
        prenom=('Prenom', 'first'),           # Get the first first name
        nom=('Nom', 'first'),                 # Get the first last name
        total_cashback=('Cashback Crédité', 'sum')  # Sum of cashback credited for the ticket
    ).reset_index()

    # Rename the columns for better display
            cashback_by_ticket.columns = ['Ticket ID', 'User ID', 'First Name', 'Last Name', 'Total Cashback']
            cashback_by_ticket = cashback_by_ticket.sort_values(by='Total Cashback', ascending=False).reset_index(drop=True)

    # Display the resulting dataframe as a table in Streamlit
            st.markdown('<div class="custom-table-container">', unsafe_allow_html=True)
            st.dataframe(cashback_by_ticket, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.warning("The necessary columns ('photos.$oid', 'submittedBy.id', 'Prenom', 'Nom', 'Cashback Crédité') are missing in the dataset.")
       
       
        # Additional Visualizations for Cashback
        # Visualisation Cashback par Genre et par Âge
        col1, col2 = st.columns(2)

# Graphique 1: Cashback Distribution by Gender
        with col1:
            if 'Genre' in df.columns and 'Cashback Crédité' in df.columns:
                cashback_by_gender = df.groupby('Genre')['Cashback Crédité'].sum().reset_index()

                fig_gender_cashback = px.pie(cashback_by_gender, names='Genre', values='Cashback Crédité', 
                                     title='Cashback Distribution by Gender', 
                                     color_discrete_sequence=color_scheme)
                fig_gender_cashback.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_gender_cashback, use_container_width=True)

# Graphique 2: Cashback Distribution by Age
        with col2:
            if 'Date de naissance' in df.columns and 'Cashback Crédité' in df.columns:
        # Calcul de l'âge
                df['Date de naissance'] = pd.to_datetime(df['Date de naissance'], errors='coerce')
                today = pd.to_datetime('today').normalize()
                df['Age'] = df['Date de naissance'].apply(lambda dob: today.year - dob.year if pd.notnull(dob) else None)

        # Filtrer les âges valides
                df_age_valid = df[df['Age'].notnull() & (df['Age'] > 0)]

        # Regrouper par âge et calculer le cashback total par tranche d'âge
                cashback_by_age = df_age_valid.groupby('Age')['Cashback Crédité'].sum().reset_index()

                fig_age_cashback = px.histogram(cashback_by_age, x='Age', y='Cashback Crédité',
                                        title='Cashback Distribution by Age',
                                        labels={'Age': 'Age', 'Cashback Crédité': 'Total Cashback'},
                                        color_discrete_sequence=color_scheme)
                st.plotly_chart(fig_age_cashback, use_container_width=True)


        # Visualisation Cashback par Type d'utilisateur et Segment
        col3, col4 = st.columns(2)

# Graphique 1: Cashback Distribution by User Type
        with col3:
            if 'userType' in df.columns and 'Cashback Crédité' in df.columns:
                cashback_by_user_type = df.groupby('userType')['Cashback Crédité'].sum().reset_index()

                fig_user_type_cashback = px.pie(cashback_by_user_type, names='userType', values='Cashback Crédité', 
                                        title='Cashback Distribution by User Type', 
                                        color_discrete_sequence=color_scheme)
                fig_user_type_cashback.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_user_type_cashback, use_container_width=True)

# Graphique 2: Cashback Distribution by Segment
        with col4:
            if 'segment' in df.columns and 'Cashback Crédité' in df.columns:
                cashback_by_segment = df.groupby('segment')['Cashback Crédité'].sum().reset_index()

                fig_segment_cashback = px.pie(cashback_by_segment, names='segment', values='Cashback Crédité', 
                                      title='Cashback Distribution by Segment', 
                                      color_discrete_sequence=color_scheme)
                fig_segment_cashback.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_segment_cashback, use_container_width=True)

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
    #         fig_cashback_rate = px.line(
    #     cashback_over_time,
    #     x='Month',
    #     y='Total Cashback',
    #     title='Cashback Distributed Over Time',
    #     labels={'Total Cashback': 'Total Cashback (DZD)', 'Month': 'Month'},
    #     color_discrete_sequence=color_scheme
    # )
    #         st.plotly_chart(fig_cashback_rate, use_container_width=True)


            fig_cashback_rate = px.bar(
    cashback_over_time,  # DataFrame with cashback distribution over time
    x='Month',           # X-axis: Month
    y='Total Cashback',  # Y-axis: Total Cashback
    title='Cashback Distributed Over Time',  # Title of the chart
    labels={'Total Cashback': 'Total Cashback (DZD)', 'Month': 'Month'},  # Axis labels
    color_discrete_sequence=color_scheme     # Custom color scheme
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
            top_products_by_submissions = df['title.fr'].value_counts()
            # Top 5 products by number of submissions
            # top_products_by_submissions2 = df['title.fr'].value_counts().head(5).index.tolist()
    
        # Cashback credited per product
            cashback_per_product = df.groupby('title.fr')['Cashback Crédité'].sum().reset_index()
            cashback_per_product = cashback_per_product.sort_values(by='Cashback Crédité', ascending=False)
        

                        # Product submissions over time (if 'createdAt_challengesubmissions' exists)
            if 'createdAt_challengesubmissions' in df.columns:
                        # Convertir les dates en format datetime si ce n'est pas fait
                df['createdAt_challengesubmissions'] = pd.to_datetime(df['createdAt_challengesubmissions'], errors='coerce')
        
        # Supprimer les valeurs nulles dans les dates
                df = df[df['createdAt_challengesubmissions'].notnull()]
        
        # Sélectionner les 5 produits avec le plus de soumissions
                top_products = df['title.fr'].value_counts().head(5).index.tolist()
        
        # Grouper les soumissions par mois et par produit pour ces 5 produits
                monthly_product_submissions = df[df['title.fr'].isin(top_products)] \
                    .groupby([df['createdAt_challengesubmissions'].dt.to_period('M'), 'title.fr']) \
                    .size().reset_index(name='Submissions')
        
        # Convertir les périodes en datetime pour une meilleure gestion de l'axe des X
                monthly_product_submissions['createdAt_challengesubmissions'] = monthly_product_submissions['createdAt_challengesubmissions'].dt.to_timestamp()

        # Créer le graphique à barres groupées
                fig_monthly_products = px.bar(
            monthly_product_submissions,
            x='createdAt_challengesubmissions',
            y='Submissions',
            color='title.fr',
            title='Monthly Submissions for Top 5 Products',
            labels={'createdAt_challengesubmissions': 'Month', 'Submissions': 'Number of Submissions'},
            barmode='group',
            color_discrete_sequence=color_scheme
        )



    # Display KPIs for Products
            col1, col2 , col3= st.columns(3)

            with col1:
                st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Total Products 🛍️</div><div class='kpi-value'>{total_products}</div></div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Top Product📈</div><div class='kpi-value'>{top_products_by_submissions.index[0]}</div></div>", unsafe_allow_html=True)


            lowest_product = df['title.fr'].value_counts().idxmin()
            with col3:
                st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Lowest Product 📉</div><div class='kpi-value'>{lowest_product}</div></div>", unsafe_allow_html=True)
          
            # Display the two tables in the same line with full width
            # st.subheader("Top 10 Products by Submissions and Cashback Credited")

# Create two columns
            col1, col2 = st.columns(2)

# Display Top 10 Products by Submissions in the first column
            with col1:
                st.markdown("Submissions per Product")
                st.dataframe(top_products_by_submissions, use_container_width=True)

            # Display Cashback per Product in the second column
            with col2:
                st.markdown("Budget consumed per product")
                st.dataframe(cashback_per_product, use_container_width=True)


                    # Plot submissions over time
            st.plotly_chart(fig_monthly_products, use_container_width=True)







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

            period_options = ['Today', 'Last 7 Days', 'Last 30 Days', 'Last 3 Months']
            selected_period = st.selectbox("Select Period for New Users", period_options, index=2)
        # Calcul du nombre de nouveaux utilisateurs (inscrits récemment) en fonction de la période sélectionnée
            if 'Date de création_user' in df.columns:  # Supposons que 'createdAt' soit la colonne de date d'inscription
                df['Date de création_user'] = pd.to_datetime(df['Date de création_user'], errors='coerce')
                today = pd.to_datetime('today')

                if selected_period == 'Today':
                    recent_period = today  # Utilisateurs créés aujourd'hui
                    new_users = df[df['Date de création_user'] >= recent_period]['submittedBy.id'].nunique()
                elif selected_period == 'Last 7 Days':
                    recent_period = today - pd.Timedelta(days=7)
                    new_users = df[df['Date de création_user'] >= recent_period]['submittedBy.id'].nunique()
                elif selected_period == 'Last 30 Days':
                    recent_period = today - pd.Timedelta(days=30)
                    new_users = df[df['Date de création_user'] >= recent_period]['submittedBy.id'].nunique()
                elif selected_period == 'Last 3 Months':
                    recent_period = today - pd.DateOffset(months=3)
                    new_users = df[df['Date de création_user'] >= recent_period]['submittedBy.id'].nunique()
            else:
                new_users = 0

        # User submissions over time (if 'createdAt_challengesubmissions' exists)


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
            col1, col2 ,col3= st.columns(3)
            # Calculer la moyenne des soumissions par utilisateur
            unique_users = df['submittedBy.id'].nunique()
            total_user_submissions = df['submittedBy.id'].count() if 'submittedBy.id' in df.columns else 0
            avg_submissions_per_user = round(total_user_submissions / unique_users) if unique_users > 0 else 0

            with col1:
                st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Total Unique Users 👤</div><div class='kpi-value'>{total_unique_users}</div></div>", unsafe_allow_html=True)
            
            with col2:
                    # Afficher le KPI pour la moyenne des soumissions par utilisateur
                st.markdown(
        f"<div class='kpi-card'><div class='kpi-title'>Average Submissions per User 📝</div><div class='kpi-value'>{avg_submissions_per_user:.2f}</div></div>",
        unsafe_allow_html=True
    )
            with col3:
                st.markdown(f"<div class='kpi-card'><div class='kpi-title'>New Users 🚀 ({selected_period})</div><div class='kpi-value'>{new_users}</div></div>", unsafe_allow_html=True)

  


            # Vérifier si 'submittedBy.id', 'Prenom', 'Nom' et 'Cashback Crédité' existent dans le dataframe
            if {'submittedBy.id', 'Prenom', 'Nom', 'Cashback Crédité'}.issubset(df.columns):
            # Grouper les utilisateurs par ID et calculer le cashback total et le nombre de soumissions
                user_stats = df.groupby(['submittedBy.id', 'Prenom', 'Nom']).agg(
                total_cashback=('Cashback Crédité', 'sum'),
                total_submissions=('submittedBy.id', 'size')  # Le nombre de soumissions est la taille du groupe
            ).reset_index()

        # Trier par cashback total ou par nombre de soumissions en ordre décroissant
            sorted_user_stats = user_stats.sort_values(by='total_submissions', ascending=False)
        # Display Users (Name, Surname, Submissions)
            st.subheader("User Statistics: ID, Name, Cashback, Submissions")
            st.dataframe(sorted_user_stats, use_container_width=True)
        # Plot submissions over time
            # st.plotly_chart(fig_submissions_over_time_users, use_container_width=True)



                    # Submissions over time for top 5 users
        if 'createdAt_challengesubmissions' in df.columns:
            df['createdAt_challengesubmissions'] = pd.to_datetime(df['createdAt_challengesubmissions'], errors='coerce')
            df = df[df['createdAt_challengesubmissions'].notnull()]

            # Filter for top 5 users
            top_user_ids = top_users_by_name['submittedBy.id'].tolist()
            df_top_users = df[df['submittedBy.id'].isin(top_user_ids)]

            # Group by month and user, then count submissions
            df_top_users['Month'] = df_top_users['createdAt_challengesubmissions'].dt.to_period('M')
            user_submissions_over_time = df_top_users.groupby(['Month', 'submittedBy.id', 'Prenom', 'Nom']).size().reset_index(name='Submissions')

            # Convert 'Month' back to datetime for proper plotting on the x-axis
            user_submissions_over_time['Month'] = user_submissions_over_time['Month'].dt.to_timestamp()

            # Create the bar chart using 'Prenom' and 'Nom' as the legend
            user_submissions_over_time['Full Name'] = user_submissions_over_time['Prenom'] + ' ' + user_submissions_over_time['Nom']

            fig_user_submissions = px.bar(
                user_submissions_over_time,
                x='Month',
                y='Submissions',
                color='Full Name',
                title='Monthly Submissions for Top 5 Users',
                labels={'Month': 'Month', 'Submissions': 'Number of Submissions'},
                barmode='group',
                color_discrete_sequence=color_scheme
            )

            # Display the bar chart
            st.plotly_chart(fig_user_submissions, use_container_width=True)
        # Plot User Type Distribution (if applicable)
                    # Display the three charts (Gender, Age, and User Type Distribution) on the same line
        col1, col2, col3 = st.columns(3)

        # Plot Gender Distribution
        with col1:
            # st.subheader("Gender Distribution")
            st.plotly_chart(fig_gender_distribution, use_container_width=True)

        # Plot Age Distribution
        with col2:
            # st.subheader("Age Distribution")
            st.plotly_chart(fig_age_distribution, use_container_width=True)

        # Plot User Type Distribution
        with col3:
            # st.subheader("User Type Distribution")
            st.plotly_chart(fig_user_type_distribution, use_container_width=True)



        if {'Wilaya', 'submittedBy.id'}.issubset(df.columns):
            user_distribution = df.groupby('Wilaya')['submittedBy.id'].nunique().reset_index()

        # Renommer les colonnes pour une meilleure lisibilité
            user_distribution.columns = ['Wilaya', 'Unique Users']

        # Trier le tableau par nombre d'utilisateurs uniques, en ordre décroissant
            user_distribution = user_distribution.sort_values(by='Unique Users', ascending=False)
            user_distribution = user_distribution.reset_index(drop=True)
        # Afficher le tableau avec la distribution des utilisateurs par Wilaya
            st.subheader("User Distribution by Wilaya")
            st.dataframe(user_distribution, use_container_width=True)

        else:
            st.warning("Les colonnes nécessaires pour calculer la distribution des utilisateurs par Wilaya sont manquantes.")
 
        if {'submittedBy.id', 'title.fr'}.issubset(df.columns):
            users_per_challenge = df.groupby('title.fr')['submittedBy.id'].nunique().reset_index()

        # Renommer les colonnes pour une meilleure lisibilité
            users_per_challenge.columns = ['Challenge', 'Unique Users']

        # Trier le tableau par nombre d'utilisateurs, en ordre décroissant
            users_per_challenge = users_per_challenge.sort_values(by='Unique Users', ascending=False)

        # Afficher le tableau avec le nombre d'utilisateurs par challenge
            st.subheader("Number of Users per Challenge")
            st.dataframe(users_per_challenge, use_container_width=True)
 


        df['createdAt_challengesubmissions'] = pd.to_datetime(df['createdAt_challengesubmissions'], errors='coerce')

        # Date d'aujourd'hui
        today = pd.to_datetime('today')

        # Churned Users (Inactive users based on selected period)
        st.subheader("Churned Users (Inactive for a Selected Period)")

# Filter to choose inactivity period
        churn_period_options = {
    '7 Days': pd.DateOffset(days=7),
    '2 Weeks': pd.DateOffset(weeks=2),
    '1 Month': pd.DateOffset(months=1),
    '3 Months': pd.DateOffset(months=3),
    '6 Months': pd.DateOffset(months=6)
}
        selected_churn_period = st.selectbox("Select the inactivity period", list(churn_period_options.keys()), index=2)

# Calculate churned users based on selected inactivity period
        churn_period = pd.to_datetime('today') - churn_period_options[selected_churn_period]

        if 'createdAt_challengesubmissions' in df.columns:
            df['createdAt_challengesubmissions'] = pd.to_datetime(df['createdAt_challengesubmissions'], errors='coerce')

    # Group by user to get the last submission date for each user
            last_submission_per_user = df.groupby(['submittedBy.id', 'Nom', 'Prenom'])['createdAt_challengesubmissions'].max().reset_index()
            last_submission_per_user.columns = ['User ID', 'Nom', 'Prenom', 'Last Submission Date']

    # Identify churned users (inactive for the selected period)
            churned_users = last_submission_per_user[last_submission_per_user['Last Submission Date'] < churn_period].reset_index(drop=True)

    # Total number of users
            total_users = df['submittedBy.id'].nunique()

    # Number of churned (inactive) users
            churned_user_count = churned_users['User ID'].nunique()

    # Number of active users
            active_user_count = total_users - churned_user_count

    # Calculate churn rate (percentage of inactive users)
            churn_rate = (churned_user_count / total_users) * 100
            active_rate = 100 - churn_rate

    # Prepare data for the pie chart
            user_status = pd.DataFrame({
        'User Status': ['Active Users', 'Inactive Users'],
        'Count': [active_user_count, churned_user_count]
    })

    # Plot the pie chart for Active vs Inactive Users
            fig_churn_pie = px.pie(
        user_status,
        names='User Status',
        values='Count',
        title=f'Active vs Inactive Users (Inactivity Period: {selected_churn_period})',
        color_discrete_sequence=color_scheme,
        hole=0.4
    )
            fig_churn_pie.update_traces(textposition='inside', textinfo='percent+label')

    # Display the pie chart
            st.plotly_chart(fig_churn_pie, use_container_width=True)

    # Display the table of churned users
            st.subheader(f"Churned Users (Inactive for {selected_churn_period})")
            st.dataframe(churned_users[['Nom', 'Prenom', 'Last Submission Date']].set_index('Nom'), use_container_width=True)

        else:
            st.warning("The 'createdAt_challengesubmissions' column is missing in the dataset.")

       












    elif st.session_state.page == "Shops":
        st.title("Shops Overview")

    # Vérifier si 'storeName' est dans le fichier
        if 'storeName' in df.columns:
        # Calculer le nombre total de magasins uniques
            # unique_stores = df['storeName'].nunique()

        # Calculer le nombre total de soumissions associées aux magasins
            total_store_submissions = df['storeName'].count()

        # Calculer la moyenne des soumissions par magasin
            # avg_submissions_per_store = total_store_submissions / unique_stores if unique_stores > 0 else 0

        # Créer une table qui montre le nombre de soumissions par magasin
            submissions_per_store = df['storeName'].value_counts().reset_index()
            submissions_per_store.columns = ['Store Name', 'Submissions']


        # Calcul du nombre total de magasins uniques
            total_unique_stores = df['storeName'].nunique()

        # Calcul du cashback total par magasin
            cashback_per_store = df.groupby('storeName')['Cashback Crédité'].sum()

        # Calcul du cashback moyen, minimum et maximum par magasin
            avg_cashback_per_store = cashback_per_store.mean()
            min_cashback_per_store = cashback_per_store.min()
            max_cashback_per_store = cashback_per_store.max()

        # Afficher les 4 cartes KPI dans une ligne
            col1, col2, col3, col4 = st.columns(4)

        # Carte KPI: Total Unique Stores
            with col1:
                st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Total Unique Stores 🏪</div><div class='kpi-value'>{total_unique_stores}</div></div>", unsafe_allow_html=True)

        # Carte KPI: Average Cashback per Store
            with col2:
                st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Avg Cashback per Store 💵</div><div class='kpi-value'>{avg_cashback_per_store:,.2f} DZD</div></div>", unsafe_allow_html=True)

        # Carte KPI: Min Cashback per Store
            with col3:
                st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Min Cashback per Store 💰</div><div class='kpi-value'>{min_cashback_per_store:,.2f} DZD</div></div>", unsafe_allow_html=True)

        # Carte KPI: Max Cashback per Store
            with col4:
                st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Max Cashback per Store 💸</div><div class='kpi-value'>{max_cashback_per_store:,.2f} DZD</div></div>", unsafe_allow_html=True)

           


        else:
            st.warning("Certaines colonnes nécessaires sont manquantes (storeName ou Cashback Crédité).")




        store_stats = df.groupby('storeName').agg(
            total_submissions=('submittedBy.id', 'size'),  # Nombre de soumissions (taille du groupe)
            total_cashback=('Cashback Crédité', 'sum'),    # Cashback total
            total_tickets=('photos.$oid', 'nunique')       # Nombre unique de tickets (photos.$oid)
        ).reset_index()

        # Trier le tableau par nombre de soumissions en ordre décroissant
        store_stats_sorted = store_stats.sort_values(by='total_submissions', ascending=False)

        # Afficher le tableau
        st.subheader("Store Statistics: Submissions, Cashback, and Tickets")
        st.dataframe(store_stats_sorted, use_container_width=True)



else:
    st.info("Please upload a CSV or Excel file to see the dashboard content.")
