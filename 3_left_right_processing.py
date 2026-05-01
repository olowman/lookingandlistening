import pandas as pd
import os as os
import numpy as np

# Read the CSV file into a DataFrame
os.chdir('c:\\Users\\ol1822a\\Documents\\pivots')
looking_times = pd.read_csv('big_milli_pivot_with_participant_ids.csv')

looking_times[['left', 'right']] = looking_times[['left', 'right']].fillna(0)
# Define a function to perform the division based on the condition
def calculate_looking_time(row):
    print(looking_times)
    denominator = row['left'] + row['right']
    if denominator == 0:
        return np.nan  # If denominator is 0, result is NaN
    if "_L_" in row['image']:
        return row['right'] / denominator
    else:
        return row['left'] / denominator


# Apply the function row-wise using apply() and store the result in a new column
looking_times['looking time'] = looking_times.apply(calculate_looking_time, axis=1)

# Print or further process the DataFrame with the new 'looking time' column
print(looking_times)

looking_times.to_csv('looking_times_participant_ID_newest.csv', index=False)