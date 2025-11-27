import data_processor
import os
import pandas as pd

def test_processing():
    print("Testing data processing...")
    
    # Ensure test data exists
    if not os.path.exists("test_data.xlsx"):
        print("Test data not found.")
        return

    df, error = data_processor.load_data("test_data.xlsx")
    if error:
        print(f"FAILED: {error}")
        return

    print("Data loaded successfully.")
    df = data_processor.clean_data(df)
    print(f"Data cleaned. Shape: {df.shape}")
    
    # Expecting 3 unique teams (Team A is duplicated)
    # Team A is exact duplicate, so it should be dropped.
    # So 3 rows.
    
    stats = data_processor.generate_statistics(df)
    print("Statistics generated.")
    
    # Check specific values
    total_teams = stats['overall_statistics']['total_teams']
    print(f"Total Teams: {total_teams}")
    assert total_teams == 3, f"Expected 3 teams, got {total_teams}"
    
    total_participants = stats['overall_statistics']['total_participants']
    print(f"Total Participants: {total_participants}")
    assert total_participants == 8, f"Expected 8 participants (4+3+1), got {total_participants}"
    
    print("Verification PASSED!")

if __name__ == "__main__":
    test_processing()
