import pandas as pd

# Create dummy data
data = {
    "Team Name": ["Team A", "Team B", "Team C", "Team A"], # Duplicate team
    "College Name": ["IIT Bombay", "NIT Trichy", "Unknown College", "IIT Bombay"],
    "State": ["Maharashtra", "Tamil Nadu", "Delhi", "Maharashtra"],
    "Domain": ["Edu Tech", "Health-Care", "Open", "Edu Tech"],
    "Team Strength": [4, 3, 1, 4],
    "All Girls": ["No", "Yes", "No", "No"],
    "City": ["Mumbai", "Trichy", "Delhi", "Mumbai"],
    "Reviewed By": ["Alice", "", "Bob", "Alice"]
}

df = pd.DataFrame(data)
# Save to Excel with one of the required sheet names
with pd.ExcelWriter("test_data.xlsx") as writer:
    df.to_excel(writer, sheet_name="Early Bird Individuals 3.0", index=False)
    
print("test_data.xlsx created.")
