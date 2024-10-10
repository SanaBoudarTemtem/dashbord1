import streamlit as st
import pandas as pd
import plotly.express as px

# Set the page configuration
st.set_page_config(
    page_title="🌟 Temtem One Submissions Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)


color_scheme = ['#e67e22', '#f5b041', '#d35400', '#f8c471','#f39c12']


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
            st.markdown(
                f"<div class='kpi-card'>"
                f"<div class='kpi-title'>New Submissions ✨</div>"
                f"<div class='kpi-value'>{new_submissions}</div>"
                f"<div class='{growth_class}'>{period_growth_rate:+.2f}% growth</div>"
                f"</div>",
                unsafe_allow_html=True
            )
            selected_period = st.selectbox(
                "Period",
                period_options,
                index=period_options.index(selected_period),
                key="period_selector",
                label_visibility="collapsed"
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

    # Additional Visualizations
    # Row 3
    col11, col12 = st.columns(2)

    # 1. Cashback distribution across user types
    if 'userType' in df.columns and 'Cashback Crédité' in df.columns:
        user_cashback_distribution = df.groupby('userType')['Cashback Crédité'].sum().reset_index()
        fig1 = px.pie(
            user_cashback_distribution,
            names='userType',
            values='Cashback Crédité',
            title='Cashback Distribution by User Type',
            color_discrete_sequence=color_scheme
        )
        col11.plotly_chart(fig1, use_container_width=True)

    # 2. Top 10 most active users
    if 'submittedBy.id' in df.columns:
        top_active_users = df['submittedBy.id'].value_counts().nlargest(10).reset_index()
        top_active_users.columns = ['User ID', 'Number of Submissions']
        fig2 = px.bar(
            top_active_users,
            x='User ID',
            y='Number of Submissions',
            title='Top 10 Most Active Users',
            color_discrete_sequence=color_scheme

        )
        col12.plotly_chart(fig2, use_container_width=True)

    # Row 4: Gender Distribution and Number of Submissions per Gender
    col13, col14 = st.columns(2)

    # 3. Gender distribution (number of unique users per gender)
    if 'Genre' in df.columns and 'submittedBy.id' in df.columns:
        gender_distribution = df.groupby('Genre')['submittedBy.id'].nunique().reset_index()
        gender_distribution.columns = ['Gender', 'Number of Unique Users']
        fig3 = px.pie(
            gender_distribution,
            names='Gender',
            values='Number of Unique Users',
            title='Gender Distribution of Unique Users',
            color_discrete_sequence=color_scheme
        )
        col13.plotly_chart(fig3, use_container_width=True)

    # 4. Number of submissions per gender
    if 'Genre' in df.columns:
        submissions_per_gender = df['Genre'].value_counts().reset_index()
        submissions_per_gender.columns = ['Gender', 'Number of Submissions']
        fig4 = px.bar(
            submissions_per_gender,
            x='Gender',
            y='Number of Submissions',
            title='Number of Submissions per Gender',
            color_discrete_sequence=color_scheme
        )
        col14.plotly_chart(fig4, use_container_width=True)

    # Row 5: Distribution of Users per Segment and Submissions per Segment
    col15, col16 = st.columns(2)

    # 5. Distribution of users per segment
    if 'segment' in df.columns and 'submittedBy.id' in df.columns:
        users_per_segment = df.groupby('segment')['submittedBy.id'].nunique().reset_index()
        users_per_segment.columns = ['Segment', 'Number of Unique Users']
        fig5 = px.pie(
            users_per_segment,
            names='Segment',
            values='Number of Unique Users',
            title='Distribution of Users per Segment',
            color_discrete_sequence=color_scheme
        )
        col15.plotly_chart(fig5, use_container_width=True)

    # 6. Distribution of submissions per segment
    if 'segment' in df.columns:
        submissions_per_segment = df['segment'].value_counts().reset_index()
        submissions_per_segment.columns = ['Segment', 'Number of Submissions']
        fig6 = px.bar(
            submissions_per_segment,
            x='Segment',
            y='Number of Submissions',
            title='Number of Submissions per Segment',
            color_discrete_sequence=color_scheme
        )
        col16.plotly_chart(fig6, use_container_width=True)

    # Row 6: Top 10 Performing Stores and Approval Rate by Type of Scan
    col17, col18 = st.columns(2)

    # 7. Top 10 performing stores
    if 'storeName' in df.columns:
        top_stores = df['storeName'].value_counts().nlargest(10).reset_index()
        top_stores.columns = ['Store Name', 'Number of Submissions']
        fig7 = px.bar(
            top_stores,
            x='Store Name',
            y='Number of Submissions',
            title='Top 10 Performing Stores',
            color_discrete_sequence=color_scheme
        )
        col17.plotly_chart(fig7, use_container_width=True)

    # 8. Approval rate by type of scan
    if 'Type de scan' in df.columns and 'status_challengesubmissions' in df.columns:
        scan_approval_rate = df[df['status_challengesubmissions'].isin(['APPROVED', 'CLAIM_APPROVED'])].groupby('Type de scan').size() / df.groupby('Type de scan').size() * 100
        scan_approval_rate = scan_approval_rate.reset_index()
        scan_approval_rate.columns = ['Type de scan', 'Approval Rate']
        fig8 = px.bar(
            scan_approval_rate,
            x='Type de scan',
            y='Approval Rate',
            title='Approval Rate by Type of Scan',
            color_discrete_sequence=color_scheme
        )
        col18.plotly_chart(fig8, use_container_width=True)

    # Row 7: Number of Submissions by Type of Scan and Budget Consumption Over Time
    col19, col20 = st.columns(2)

    # 9. Number of submissions by type of scan
    if 'Type de scan' in df.columns:
        submissions_by_scan = df['Type de scan'].value_counts().reset_index()
        submissions_by_scan.columns = ['Type de scan', 'Number of Submissions']
        fig9 = px.bar(
            submissions_by_scan,
            x='Type de scan',
            y='Number of Submissions',
            title='Number of Submissions by Type of Scan',
            color_discrete_sequence=color_scheme
        )
        col19.plotly_chart(fig9, use_container_width=True)

    # 10. Budget consumption over time (daily, weekly, monthly)
    budget_time_options = ['Daily', 'Weekly', 'Monthly']
    selected_time_option = st.selectbox("Select Time Period for Visualizations", budget_time_options)

    if 'createdAt_challengesubmissions' in df.columns:
        if selected_time_option == 'Daily':
            budget_over_time = df.resample('D', on='createdAt_challengesubmissions')['Budget Consommé'].sum().reset_index()
            submissions_over_time = df.resample('D', on='createdAt_challengesubmissions').size().reset_index(name='Number of Submissions')
            unique_users_over_time = df.resample('D', on='createdAt_challengesubmissions')['submittedBy.id'].nunique().reset_index(name='Number of Unique Users')
        elif selected_time_option == 'Weekly':
            budget_over_time = df.resample('W', on='createdAt_challengesubmissions')['Budget Consommé'].sum().reset_index()
            submissions_over_time = df.resample('W', on='createdAt_challengesubmissions').size().reset_index(name='Number of Submissions')
            unique_users_over_time = df.resample('W', on='createdAt_challengesubmissions')['submittedBy.id'].nunique().reset_index(name='Number of Unique Users')
        elif selected_time_option == 'Monthly':
            budget_over_time = df.resample('M', on='createdAt_challengesubmissions')['Budget Consommé'].sum().reset_index()
            submissions_over_time = df.resample('M', on='createdAt_challengesubmissions').size().reset_index(name='Number of Submissions')
            unique_users_over_time = df.resample('M', on='createdAt_challengesubmissions')['submittedBy.id'].nunique().reset_index(name='Number of Unique Users')

        # Row 8: Budget Consumption Over Time and Number of Submissions Over Time
        col21, col22 = st.columns(2)

        # Use the date column directly for plotting
        fig10 = px.line(
            budget_over_time,
            x='createdAt_challengesubmissions',
            y='Budget Consommé',
            title=f'Budget Consumption Over Time ({selected_time_option})',
            color_discrete_sequence=color_scheme
        )
        col21.plotly_chart(fig10, use_container_width=True)

        # 11. Number of Submissions Over Time
        fig11 = px.line(
            submissions_over_time,
            x='createdAt_challengesubmissions',
            y='Number of Submissions',
            title=f'Number of Submissions Over Time ({selected_time_option})',
            color_discrete_sequence=color_scheme
        )
        col22.plotly_chart(fig11, use_container_width=True)

        # Row 9: Number of Unique Users Over Time
        col23, col24 = st.columns(2)

        # 12. Number of Unique Users Over Time
        fig12 = px.line(
            unique_users_over_time,
            x='createdAt_challengesubmissions',
            y='Number of Unique Users',
            title=f'Number of Unique Users Over Time ({selected_time_option})',
            color_discrete_sequence=color_scheme
        )
        col23.plotly_chart(fig12, use_container_width=True)



    
else:
    st.info("Please upload a CSV or Excel file to see the dashboard content.")
