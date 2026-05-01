import pandas as pd
import os
import numpy as np

# Set path and working directory
path = 'c:\\Users\\ol1822a\\Documents\\looking_time'
os.chdir(path)

# Configure pandas options
np.set_printoptions(linewidth=320)
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 30)

# Initialize lists and counters
include = []  # List of participants to include
exclude = []  # List of participants to exclude
total_trials = 0  # Total valid trials
all_data = []  # List to store data for all participants

# Iterate through files in the directory
for filename in os.listdir():
    full_path = os.path.join(path, filename)

    # Skip non-CSV files and system files
    if os.path.isdir(full_path) or filename in ['Thumbs.db', '.DS_Store']:
        continue

    # Read the CSV file into a DataFrame
    data = pd.read_csv(full_path)

    # Ensure required columns exist
    if 'left' not in data.columns or 'right' not in data.columns:
        print(f"Skipping {filename}, missing 'left' or 'right' columns.")
        continue

    # Replace NaN values with 0 for calculation
    data_notnull = data.fillna(0)

    # Add inclusion criteria based on 'left' and 'right' columns
    data_notnull['include?'] = (data_notnull['left'] + data_notnull['right'] >= 1000)

    # Extract participant ID (first part of filename)
    participant_id = filename.split('_')[0]

    # Print count of included vs excluded trials
    print(f'{participant_id}:', '\n', data_notnull['include?'].value_counts())

    # If the participant has at least 12 valid trials, include them
    if data_notnull['include?'].value_counts().get(True, 0) >= 12:
        include.append(participant_id)
        total_trials += data_notnull['include?'].value_counts().get(True, 0)

        # Add the valid trials (included trials) to the all_data list
        valid_data = data_notnull[data_notnull['include?'] == True]  # Filter out excluded trials
        all_data.append(valid_data)
    else:
        exclude.append(participant_id)

# Combine all included valid data into a single DataFrame
all_included_data = pd.concat(all_data, ignore_index=True)

# Save the filtered data as a new CSV file
all_included_data.to_csv('looking_times_all_final_noises.csv', index=False)

# Output summary of inclusion and exclusion
print(f'include: {include}')
print(f'exclude: {exclude}')
print(f'Total included participants: {len(include)}')
print(f'Total valid trials: {total_trials}')
print(f'Average trials per included participant: {total_trials / len(include) if len(include) > 0 else 0}')
