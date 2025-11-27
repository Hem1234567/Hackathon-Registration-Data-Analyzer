import streamlit as st
import pandas as pd
import json
import plotly.express as px
import data_processor
import utils

st.set_page_config(page_title="Hackathon Data Analyzer", layout="wide")

st.title("📊 Hackathon Registration Data Analyzer")
st.sidebar.text(f"DP Version: {getattr(data_processor, 'VERSION', 'Unknown')}")
st.markdown("Upload your Excel file to generate comprehensive statistics and insights.")

# File Uploader
uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls'])

if uploaded_file is not None:
    with st.spinner("Processing data..."):
        # Load Data
        # Load Data
        sheets_dict, error = data_processor.load_data(uploaded_file)
        
        if error:
            st.error(error)
        else:
            # Analysis Mode Selection
            analysis_mode = st.radio(
                "Select Analysis Mode",
                ["Full Analysis (Merge All Sheets)", "Individual Sheet Analysis"],
                horizontal=True
            )
            
            df = None
            
            if analysis_mode == "Full Analysis (Merge All Sheets)":
                df = data_processor.merge_sheets(sheets_dict)
                st.info(f"Analyzing merged data from {len(sheets_dict)} sheets.")
            else:
                sheet_names = list(sheets_dict.keys())
                selected_sheet = st.selectbox("Select Sheet to Analyze", sheet_names)
                if selected_sheet:
                    df = sheets_dict[selected_sheet]
                    st.info(f"Analyzing data from sheet: {selected_sheet}")
            
            if df is not None:
                # Clean Data
                df = data_processor.clean_data(df)
                
                # Generate Statistics
                stats = data_processor.generate_statistics(df)
            
            # --- Dashboard ---
            
            # Overall Metrics
            st.header("Overall Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            overall = stats.get('overall_statistics', {})
            col1.metric("Total Teams", overall.get('total_teams', 0))
            col2.metric("Total Participants", overall.get('total_participants', 0))
            col3.metric("Total Colleges", overall.get('total_colleges', 0))
            col4.metric("All Girls Teams", overall.get('all_girls_teams', 0))
            
            # Tabs for detailed analysis
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["College Analysis", "Domain Distribution", "Geography", "Team Size", "Raw Data"])
            
            with tab1:
                st.subheader("College Participation Analysis")
                all_colleges = stats.get('college_wise_statistics', {}).get('all_colleges', [])
                
                if all_colleges:
                    college_df = pd.DataFrame(all_colleges)
                    
                    # Explicit Filter for College Name
                    search_term = st.text_input("🔍 Search College Name", "")
                    if search_term:
                        college_df = college_df[college_df['college_name'].str.contains(search_term, case=False, na=False)]
                    
                    # Display full table
                    st.caption(f"Showing {len(college_df)} colleges")
                    st.dataframe(
                        college_df[['college_name', 'total_teams', 'total_participants']], 
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Chart for top 20 only to keep it readable
                    st.subheader("Top 20 Colleges")
                    top_20_df = college_df.head(20)
                    fig = px.bar(top_20_df, x='college_name', y='total_teams', title="Top 20 Colleges by Team Count")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No college data available.")
                    
            with tab2:
                st.subheader("Domain Distribution")
                domain_data = stats.get('domain_wise_distribution', {})
                if domain_data:
                    # Convert dict to list for plotting
                    domain_list = []
                    for d, data in domain_data.items():
                        domain_list.append({"Domain": d, "Teams": data['total_teams']})
                    
                    domain_df = pd.DataFrame(domain_list)
                    fig = px.pie(domain_df, values='Teams', names='Domain', title="Teams per Domain")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No domain data available.")

            with tab3:
                st.subheader("Geographical Distribution")
                state_data = stats.get('geographical_distribution', {}).get('state_wise', [])
                if state_data:
                    state_df = pd.DataFrame(state_data)
                    fig = px.bar(state_df, x='state', y='total_teams', title="Teams by State")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No state data available.")

            with tab4:
                st.subheader("Team Size Analysis")
                size_stats = stats.get('team_size_analysis', {})
                if size_stats:
                    # Create a simple dataframe for the bar chart
                    size_data = {
                        "Category": ["Solo", "Small (2-3)", "Full (4-5)"],
                        "Count": [size_stats.get('solo_teams', 0), size_stats.get('small_teams_2_3', 0), size_stats.get('full_teams_4_5', 0)]
                    }
                    fig = px.bar(pd.DataFrame(size_data), x='Category', y='Count', title="Team Size Distribution")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.metric("Average Team Size", size_stats.get('average_team_size', 0))
                else:
                    st.info("No team size data available.")
            
            with tab5:
                st.subheader("Raw Data")
                
                # Dynamic Filters for Raw Data
                with st.expander("🔍 Advanced Filters (All Columns)", expanded=False):
                    filtered_df = df.copy()
                    
                    # Create 3 columns for filters to save space
                    cols = st.columns(3)
                    
                    for i, column in enumerate(filtered_df.columns):
                        col_idx = i % 3
                        with cols[col_idx]:
                            # Check if column is categorical (few unique values)
                            if filtered_df[column].nunique() < 20:
                                options = sorted([str(x) for x in filtered_df[column].unique() if pd.notna(x)])
                                selected = st.multiselect(f"Filter {column}", options, key=f"filter_{column}")
                                if selected:
                                    filtered_df = filtered_df[filtered_df[column].astype(str).isin(selected)]
                            else:
                                # Text search for other columns
                                search_txt = st.text_input(f"Search {column}", key=f"search_{column}")
                                if search_txt:
                                    filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(search_txt, case=False, na=False)]
                
                st.caption(f"Showing {len(filtered_df)} records")
                st.dataframe(filtered_df, use_container_width=True, hide_index=True)

            # --- Downloads ---
            st.divider()
            st.subheader("Export Reports")
            
            c1, c2 = st.columns(2)
            
            # JSON Report
            json_str = json.dumps(stats, indent=2)
            c1.download_button(
                label="Download Full Statistics (JSON)",
                data=json_str,
                file_name="hackathon_statistics.json",
                mime="application/json"
            )
            
            # CSV Report (Summary of Colleges)
            if all_colleges:
                csv_data = pd.DataFrame(all_colleges).to_csv(index=False).encode('utf-8')
                c2.download_button(
                    label="Download College Summary (CSV)",
                    data=csv_data,
                    file_name="college_summary.csv",
                    mime="text/csv"
                )

else:
    st.info("Please upload an Excel file to begin.")
