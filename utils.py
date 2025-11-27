import pandas as pd
import re
import io

def normalize_text(text):
    """
    Normalizes text by converting to lowercase, removing extra spaces,
    and handling None/NaN values.
    """
    if pd.isna(text) or text == "":
        return "Unknown"
    return str(text).strip().title()

def normalize_college_name(name):
    """
    Specific normalization for college names.
    Can be expanded with a mapping dictionary for common typos.
    """
    if pd.isna(name) or name == "":
        return "Unknown College"
    
    name = str(name).strip()
    # Basic cleanup
    name = re.sub(r'\s+', ' ', name) # Replace multiple spaces with single space
    
    # Common replacements (can be expanded based on data)
    name = name.replace("IIT", "Indian Institute of Technology")
    name = name.replace("NIT", "National Institute of Technology")
    
    return name.title()

def convert_df_to_csv(df):
    """
    Converts a DataFrame to a CSV string for download.
    """
    return df.to_csv(index=False).encode('utf-8')

def convert_df_to_json(df):
    """
    Converts a DataFrame to a JSON string for download.
    """
    return df.to_json(orient="records", indent=2).encode('utf-8')
