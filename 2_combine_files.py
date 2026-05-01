import pandas as pd
import os

# Change the current working directory to the desired directory
os.chdir('c:\\Users\\ol1822a\\Documents\\pivots')

# List to store DataFrames
dfs = []

# Iterate over each CSV file in the current directory
for filename in os.listdir():
    if filename.endswith(".csv"):
        # Extract participant ID from the filename (e.g., "1_milli_pivot.csv" -> "1")
        participant_id = filename.split('_')[0]  # Gets the number before the underscore

        # Read the CSV file into a DataFrame
        df = pd.read_csv(filename)

        # Add the participant ID column to the DataFrame
        df['participant ID'] = participant_id

        # Add DataFrame to the list
        dfs.append(df)

# Concatenate all DataFrames into one
big_milli_pivot = pd.concat(dfs, ignore_index=True)

# Save the combined DataFrame to a CSV file
big_milli_pivot.to_csv('big_milli_pivot_with_participant_ids.csv', index=False)