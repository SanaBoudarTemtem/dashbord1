# app.py

import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np
from datetime import datetime
from collections import Counter
import re

# -----------------------------
# Dashboard Configuration
# -----------------------------
st.set_page_config(
    page_title="🌟 Temtem One Market Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Helper Functions
# -----------------------------

@st.cache_data
def load_data(file):
    """
    Load data from uploaded file based on its extension.

    Parameters:
        file (UploadedFile): The uploaded file object.

    Returns:
        DataFrame: Loaded pandas DataFrame or None if error occurs.
    """
    file_extension = Path(file.name).suffix.lower()
    try:
        if file_extension in ['.csv', '.txt']:
            # Try different encodings
            encodings = ['utf-8', 'ISO-8859-1', 'latin1', 'cp1252']
            for encoding in encodings:
                try:
                    df = pd.read_csv(file, encoding=encoding)
                    st.sidebar.success(f"Successfully loaded CSV with encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                st.sidebar.error("Failed to decode the CSV file with attempted encodings.")
                return None
        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(file, engine='openpyxl')
            st.sidebar.success("Successfully loaded Excel file.")
        else:
            st.sidebar.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None

        # Convert date columns to datetime
        date_columns = ['createdAt_challengesubmissions', 'startDate_challenge', 'endDate_challenge', 'Date de naissance', 'Date de création_user']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        return df
    except Exception as e:
        st.sidebar.error(f"Error loading file: {str(e)}")
        return None

# -----------------------------
# Main Dashboard
# -----------------------------

st.title("🌟 Temtem One Market Dashboard")

# Sidebar for file upload and filters
# st.sidebar.title("📊 Dashboard Controls")
logo_path = "Logo-temtemOne.svg"  # Replace with your logo file path

if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_column_width=True)
else:
    st.sidebar.warning("Logo image not found. Please ensure 'logo.png' is in the project directory.")

uploaded_file = st.sidebar.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    if df is not None:
        st.sidebar.success("Data loaded successfully!")
        
        # Date range filter
        min_date = df['createdAt_challengesubmissions'].min().date()
        max_date = df['createdAt_challengesubmissions'].max().date()
        start_date, end_date = st.sidebar.date_input(
            "Select Date Range",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        
        # Campaign selector
        campaigns = df['title.fr'].unique()
        selected_campaign = st.sidebar.selectbox("Select Campaign", ["All"] + list(campaigns))
        
        # Filter data based on selections
        mask = (df['createdAt_challengesubmissions'].dt.date >= start_date) & (df['createdAt_challengesubmissions'].dt.date <= end_date)
        filtered_df = df.loc[mask]
        if selected_campaign != "All":
            filtered_df = filtered_df[filtered_df['title.fr'] == selected_campaign]
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Submissions", len(filtered_df))
        col2.metric("Approval Rate", f"{(filtered_df['status_challengeticketsubmissions'] == 'APPROVED').mean():.2%}")
        col3.metric("Total Cashback", f"${filtered_df['Montant Cashback'].sum():,.2f}")
        col4.metric("Avg Cashback per Submission", f"${filtered_df['Montant Cashback'].mean():.2f}")
        
        # Additional KPIs
        col5, col6, col7, col8 = st.columns(4)
        col5.metric("Unique Users", filtered_df['submittedBy.id'].nunique())
        col6.metric("Conversion Rate", f"{len(filtered_df[filtered_df['status_challengeticketsubmissions'] == 'APPROVED']) / len(filtered_df):.2%}")
        col7.metric("Avg Processing Time", f"{(filtered_df['createdAt_challengesubmissions'] - filtered_df['startDate_challenge']).mean().days:.1f} days")
        col8.metric("Most Popular Campaign", filtered_df['title.fr'].mode().iloc[0])
        
        # Submissions Over Time
        st.subheader("📅 Submissions Over Time")
        submissions_over_time = filtered_df.groupby('createdAt_challengesubmissions').size().reset_index(name='count')
        fig = px.line(submissions_over_time, x='createdAt_challengesubmissions', y='count', title='Submissions Over Time')
        st.plotly_chart(fig, use_container_width=True)
        
        # Campaign Performance
        st.subheader("🏆 Campaign Performance")
        campaign_performance = filtered_df.groupby('title.fr').agg({
            'submission.$oid': 'count',
            'Montant Cashback': 'sum'
        }).reset_index()
        campaign_performance.columns = ['Campaign', 'Submissions', 'Total Cashback']
        fig = px.bar(campaign_performance, x='Campaign', y=['Submissions', 'Total Cashback'], title='Campaign Performance')
        st.plotly_chart(fig, use_container_width=True)
        
        # Geographical Distribution (if 'Wilaya' column exists)
        if 'Wilaya' in filtered_df.columns:
            st.subheader("🗺️ Geographical Distribution")
            geo_distribution = filtered_df['Wilaya'].value_counts().reset_index()
            geo_distribution.columns = ['Wilaya', 'Count']
            fig = px.bar(geo_distribution, x='Wilaya', y='Count', title='Submission Distribution by Wilaya')
            st.plotly_chart(fig, use_container_width=True)
        
        # User Type Distribution
        if 'userType' in filtered_df.columns:
            st.subheader("👥 User Type Distribution")
            user_type_dist = filtered_df['userType'].value_counts().reset_index()
            user_type_dist.columns = ['User Type', 'Count']
            fig = px.pie(user_type_dist, values='Count', names='User Type', title='User Type Distribution')
            st.plotly_chart(fig, use_container_width=True)
        
        # Status Distribution
        if 'status_challengeticketsubmissions' in filtered_df.columns:
            st.subheader("✅ Submission Status Distribution")
            status_dist = filtered_df['status_challengeticketsubmissions'].value_counts().reset_index()
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
        top_users = get_top_users(filtered_df)
        st.write(top_users[['Full Name', 'Submission Count', 'Total Cashback']])

        # Calculate and display additional statistics
        total_submissions = filtered_df['submission.$oid'].nunique()
        total_cashback = filtered_df['Montant Cashback'].sum()
        top_users_submissions = top_users['Submission Count'].sum()
        top_users_cashback = top_users['Total Cashback'].sum()

        st.write(f"Top 10 users account for:")
        st.write(f"- {top_users_submissions / total_submissions:.2%} of total submissions")
        st.write(f"- {top_users_cashback / total_cashback:.2%} of total cashback")
        


        # Function to calculate submission status metrics
        # def get_submission_status_metrics(df):
        #     total_submissions = len(df)
        #     approved = df['status_challengeticketsubmissions'].value_counts().get('approved', 0)
        #     rejected = df['status_challengeticketsubmissions'].value_counts().get('rejected', 0)
            
        #     approval_rate = approved / total_submissions
        #     rejection_rate = rejected / total_submissions
            
        #     rejection_reasons = df[df['status_challengeticketsubmissions'] == 'rejected']['rejectReason'].value_counts()
            
        #     # Calculate processing time (assuming 'createdAt_challengesubmissions' is the submission time)
        #     # df['processing_time'] = (pd.to_datetime(df['updatedAt_challengeticketsubmissions']) - 
        #     #                         pd.to_datetime(df['createdAt_challengesubmissions'])).dt.total_seconds() / 3600
        #     # avg_processing_time = df['processing_time'].mean()
            
        #     claim_rate = df['status_challengesubmissions'].value_counts().get('claimed', 0) / total_submissions
            
        #     return {
        #         'approval_rate': approval_rate,
        #         'rejection_rate': rejection_rate,
        #         'rejection_reasons': rejection_reasons,
        #         # 'avg_processing_time': avg_processing_time,
        #         'claim_rate': claim_rate
        #     }


        # # Submission Status Metrics
        # st.subheader("📊 Submission Status Metrics")
        # metrics = get_submission_status_metrics(filtered_df)

        # col1, col2, col3, col4 = st.columns(4)
        # col1.metric("Approval Rate", f"{metrics['approval_rate']:.2%}")
        # col2.metric("Rejection Rate", f"{metrics['rejection_rate']:.2%}")
        # # col3.metric("Avg. Processing Time", f"{metrics['avg_processing_time']:.2f} hours")
        # col4.metric("Claim Rate", f"{metrics['claim_rate']:.2%}")

        # Rejection Reasons
        # st.subheader("Rejection Reasons")
        # if not metrics['rejection_reasons'].empty:
        #     fig = px.pie(values=metrics['rejection_reasons'].values, names=metrics['rejection_reasons'].index, title="Rejection Reasons Distribution")
        #     st.plotly_chart(fig)
        # else:
        #     st.write("No rejections in the current data.")



        # Claims Over Time
        st.subheader("Claims Over Time")
        claims_over_time = filtered_df[filtered_df['status_challengesubmissions'] == 'claimed'].groupby(pd.Grouper(key='createdAt_challengesubmissions', freq='D')).size().reset_index(name='count')
        fig = px.line(claims_over_time, x='createdAt_challengesubmissions', y='count', title="Number of Claims per Day")
        st.plotly_chart(fig)





        # Function to calculate age
        def calculate_age(born):
            today = datetime.now()
            return today.year - born.year - ((today.month, today.day) < (born.month, born.day))



        # User Demographics
        st.subheader("👥 User Demographics")

        # Age Distribution
        if 'Date de naissance' in df.columns:
            df['age'] = df['Date de naissance'].apply(calculate_age)
            st.write("### Age Distribution")
            fig = px.histogram(df, x='age', nbins=20, title="Age Distribution of Users")
            st.plotly_chart(fig)
        else:
            st.write("Date of birth information is not available in the dataset.")

        # Gender Distribution
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




        # Function to normalize tags
        def normalize_tag(tag):
            # Convert to lowercase
            tag = tag.lower()
            # Remove leading/trailing whitespace
            tag = tag.strip()
            # Remove special characters and replace spaces with underscores
            tag = re.sub(r'[^\w\s-]', '', tag)
            tag = re.sub(r'[-\s]+', '_', tag)
            return tag

        # Tag Analysis
        st.subheader("🏷️ Tag Analysis")

        if 'tags' in df.columns:
            # Normalize tags
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

            # Calculate average cashback for each tag
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
            st.write("Tag Performance Table")
            st.dataframe(tag_performance)

        else:
            st.write("Tag information is not available in the dataset.")



        
        # Display raw data
        if st.checkbox("Show Raw Data"):
            st.subheader("Raw Data")
            st.write(filtered_df)
    else:
        st.write("### ❓ Please upload a file to get started.")
        st.sidebar.info("Please upload a CSV or Excel file to begin.")