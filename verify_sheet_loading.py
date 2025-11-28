import pandas as pd
import data_processor
import os

def verify_loading():
    file_path = "test_data.xlsx"
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return

    print(f"Testing with {file_path}...")
    
    # Get actual sheets using pandas directly
    xls = pd.ExcelFile(file_path)
    actual_sheets = xls.sheet_names
    print(f"Actual sheets in file: {actual_sheets}")
    
    # Use data_processor to load
    sheets_dict, error = data_processor.load_data(file_path)
    
    if error:
        print(f"Error loading data: {error}")
    else:
        loaded_sheets = list(sheets_dict.keys())
        print(f"Loaded sheets: {loaded_sheets}")
        
        if len(loaded_sheets) == len(actual_sheets):
            print("SUCCESS: All sheets loaded.")
        else:
            print(f"FAILURE: Expected {len(actual_sheets)} sheets, got {len(loaded_sheets)}.")

if __name__ == "__main__":
    verify_loading()
