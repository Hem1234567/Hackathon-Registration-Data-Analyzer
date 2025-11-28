import pandas as pd
import utils

VERSION = "1.1"



# Mapping various column names to a standard set
COLUMN_MAPPING = {
    "Team Name": "Team Name",
    "Team name": "Team Name",
    "College Name": "College Name",
    "College State": "State",
    "State": "State",
    "Domain": "Domain",
    "Team Strength": "Team Strength",
    "All Girls": "All Girls",
    "City": "City",
    "College City": "City",
    "Reviewed by": "Reviewed By"
}

def load_data(file):
    """
    Loads data from the specified Excel file, reading only supported sheets.
    Returns a dictionary of {sheet_name: dataframe}.
    """
    try:
        xls = pd.ExcelFile(file)
    except Exception as e:
        return None, f"Error reading Excel file: {str(e)}"

    all_data = []
    sheets_found = []
    
    for sheet_name in xls.sheet_names:
        try:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            df['Source Sheet'] = sheet_name
            
            # Normalize columns immediately to handle variations across sheets
            # We do a partial rename here to help with merging later if needed, 
            # but main cleaning happens in clean_data
            all_data.append(df)
            sheets_found.append(sheet_name)
        except Exception as e:
            print(f"Error reading sheet {sheet_name}: {e}")

    if not all_data:
        return {}, "No matching sheets found. Please check the sheet names."
        
    # Return a dictionary of {sheet_name: dataframe}
    sheets_dict = {name: df for name, df in zip(sheets_found, all_data)}
    return sheets_dict, None

def merge_sheets(sheets_dict):
    """
    Merges all sheets in the dictionary into a single DataFrame.
    """
    if not sheets_dict:
        return pd.DataFrame()
        
    return pd.concat(sheets_dict.values(), ignore_index=True)

def clean_data(df):
    """
    Cleans and normalizes the DataFrame.
    """
    if df.empty:
        return df

    # Drop rows where all elements are missing
    df = df.dropna(how='all')

    # 1. Normalize Column Names
    # Create a map that handles case insensitivity if needed, but for now use the direct mapping
    # We iterate through columns and try to map them
    
    new_columns = {}
    for col in df.columns:
        # Check if this column maps to one of our standard columns
        # We check exact match in keys
        if col in COLUMN_MAPPING:
            new_columns[col] = COLUMN_MAPPING[col]
        else:
            # Try case insensitive match
            for key, val in COLUMN_MAPPING.items():
                if str(col).lower() == key.lower():
                    new_columns[col] = val
                    break
    
    df = df.rename(columns=new_columns)
    
    # Remove duplicate columns (keep first occurrence)
    df = df.loc[:, ~df.columns.duplicated()]
    
    # 2. Ensure all standard columns exist
    standard_cols = ["Team Name", "College Name", "State", "Domain", "Team Strength", "All Girls", "City", "Reviewed By"]
    for col in standard_cols:
        if col not in df.columns:
            df[col] = None
            
    # 3. Data Type Conversion and Filling
    df['Team Strength'] = pd.to_numeric(df['Team Strength'], errors='coerce').fillna(1)
    
    # 4. Value Normalization
    df['College Name'] = df['College Name'].apply(utils.normalize_college_name)
    df['State'] = df['State'].apply(utils.normalize_text)
    df['City'] = df['City'].apply(utils.normalize_text)
    df['Domain'] = df['Domain'].apply(utils.normalize_text)
    df['Team Name'] = df['Team Name'].apply(lambda x: str(x).strip() if pd.notna(x) else "Unknown Team")
    
    # 5. Deduplication
    # If a team appears multiple times, we might want to keep the latest or just drop duplicates.
    # Assuming 'Team Name' + 'College Name' is a unique identifier, or just 'Team Name'.
    # For now, let's drop exact duplicates across all columns
    df = df.drop_duplicates()
    
    return df

def generate_statistics(df):
    """
    Generates the comprehensive statistics dictionary.
    """
    if df.empty:
        return {}
        
    stats = {}
    
    # --- Overall Statistics ---
    stats['overall_statistics'] = {
        "total_teams": int(df['Team Name'].nunique()),
        "total_colleges": int(df['College Name'].nunique()),
        "total_states": int(df['State'].nunique()),
        "total_participants": int(df['Team Strength'].sum()),
        "all_girls_teams": int(df[df['All Girls'].astype(str).str.lower().isin(['yes', 'true', '1'])].shape[0]),
        "review_status": {
            "reviewed": int(df[df['Reviewed By'].notna() & (df['Reviewed By'] != '')].shape[0]),
            "pending": int(df[df['Reviewed By'].isna() | (df['Reviewed By'] == '')].shape[0])
        }
    }
    
    # --- College Wise Statistics ---
    college_stats = []
    college_groups = df.groupby('College Name')
    for name, group in college_groups:
        college_stats.append({
            "college_name": name,
            "total_teams": int(group['Team Name'].nunique()),
            "total_participants": int(group['Team Strength'].sum()),
            "domains": list(group['Domain'].unique()),
            "cities": list(group['City'].unique())
        })
    
    # Sort by total teams desc
    college_stats.sort(key=lambda x: x['total_teams'], reverse=True)
    
    stats['college_wise_statistics'] = {
        "all_colleges": college_stats, # Return all
        "colleges_with_single_team": int(sum(1 for c in college_stats if c['total_teams'] == 1)),
        "unique_colleges_list": [c['college_name'] for c in college_stats]
    }
    
    # --- Domain Wise Distribution ---
    # Mapping domains to the requested keys if possible, or just using raw domains
    # The prompt asks for specific keys: edu_tech, healthcare, fin_tech, open, sus_green_tech
    # We will try to categorize, or just return all domains found.
    # Let's do a dynamic approach but try to map to the requested structure if names match.
    
    domain_groups = df.groupby('Domain')
    domain_stats = {}
    for name, group in domain_groups:
        # Normalize key for JSON (e.g., "Edu Tech" -> "edu_tech")
        key = name.lower().replace(" ", "_").replace("-", "_")
        
        # Find top colleges for this domain
        top_colleges = group['College Name'].value_counts().head(5).index.tolist()
        
        domain_stats[key] = {
            "total_teams": int(group['Team Name'].nunique()),
            "total_participants": int(group['Team Strength'].sum()),
            "top_colleges": top_colleges
        }
    stats['domain_wise_distribution'] = domain_stats
    
    # --- Geographical Distribution ---
    state_stats = []
    for name, group in df.groupby('State'):
        state_stats.append({
            "state": name,
            "total_teams": int(group['Team Name'].nunique()),
            "total_colleges": int(group['College Name'].nunique()),
            "top_colleges": group['College Name'].value_counts().head(3).index.tolist()
        })
    stats['geographical_distribution'] = {
        "state_wise": state_stats,
        "city_wise": [{"city": n, "total_teams": int(g['Team Name'].nunique()), "total_colleges": int(g['College Name'].nunique())} for n, g in df.groupby('City')]
    }
    
    # --- Team Size Analysis ---
    stats['team_size_analysis'] = {
        "solo_teams": int(df[df['Team Strength'] == 1].shape[0]),
        "small_teams_2_3": int(df[df['Team Strength'].between(2, 3)].shape[0]),
        "full_teams_4_5": int(df[df['Team Strength'] >= 4].shape[0]),
        "average_team_size": float(round(df['Team Strength'].mean(), 2)),
        "largest_team_size": int(df['Team Strength'].max()) if not df.empty else 0
    }
    
    # --- Reviewer Statistics ---
    reviewer_stats = []
    if 'Reviewed By' in df.columns:
        for name, group in df.groupby('Reviewed By'):
            if pd.isna(name) or name == "": continue
            reviewer_stats.append({
                "reviewer_name": name,
                "teams_reviewed": int(group.shape[0]),
                "domains_reviewed": list(group['Domain'].unique())
            })
    stats['reviewer_statistics'] = {"by_reviewer": reviewer_stats}
    
    return stats
