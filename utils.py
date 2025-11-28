import pandas as pd
import re
import io

def normalize_text(text):
    """
    Normalizes text by converting to lowercase, removing extra spaces,
    and handling None/NaN values.
    """
    if pd.isna(text) or text == "" or str(text).lower() == 'nan':
        return "Unknown"
    return str(text).strip().title()

# Common college name mappings (normalized lowercase key -> standard name)
COLLEGE_MAPPINGS = {
    "rmk": "R.M.K. Engineering College",
    "r.m.k": "R.M.K. Engineering College",
    "rmk engineering college": "R.M.K. Engineering College",
    "rajalakshmi engineering college": "Rajalakshmi Engineering College",
    "rajakalashmi engineering college": "Rajalakshmi Engineering College",
    "rajakalakshmi engineering college": "Rajalakshmi Engineering College",
    "rec": "Rajalakshmi Engineering College",
    "svce": "Sri Venkateswara College of Engineering",
    "sri venkateswara college of engineering": "Sri Venkateswara College of Engineering",
    "cit": "Chennai Institute of Technology",
    "chennai institute of technology": "Chennai Institute of Technology",
    "ssn": "SSN College of Engineering",
    "ssn college of engineering": "SSN College of Engineering"
}

def normalize_college_name(name):
    """
    Specific normalization for college names.
    Uses a mapping dictionary for common typos and abbreviations.
    """
    if pd.isna(name) or name == "" or str(name).lower() == 'nan':
        return "Unknown College"
    
    name = str(name).strip()
    # Basic cleanup: remove multiple spaces
    name = re.sub(r'\s+', ' ', name)
    
    # Create a normalized key for lookup (lowercase, remove dots for some comparisons if needed)
    # We will try exact lowercase match first
    lower_name = name.lower()
    
    # Check if we have a direct mapping
    if lower_name in COLLEGE_MAPPINGS:
        return COLLEGE_MAPPINGS[lower_name]
        
    # Handle variations like "R.M.K" vs "RMK" by removing dots for lookup
    no_dots_name = lower_name.replace(".", "")
    if no_dots_name in COLLEGE_MAPPINGS:
        return COLLEGE_MAPPINGS[no_dots_name]
        
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
