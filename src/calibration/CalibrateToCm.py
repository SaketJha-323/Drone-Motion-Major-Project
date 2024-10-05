import pandas as pd
import numpy as np

# Load the calibrated drone data
file_path = 'data/raw/Drone_CoD.csv'
drone_data = pd.read_csv(file_path)

# Ensure the columns are named correctly: 'Frame', 'Time', 'X', 'Y', 'Z'
drone_data.columns = ['Frame', 'Time', 'X', 'Y', 'Z']

# Convert data to numpy array for easier manipulation
data = np.array(drone_data)

# Extract columns
frames = data[:, 0]
times = data[:, 1]
x = data[:, 2] / 10  # Convert mm to cm
y = data[:, 3] / 10  # Convert mm to cm
z = data[:, 4] / 10  # Convert mm to cm

# Prepare the DataFrame for saving
output_data = {
    'Frame': frames,
    'Time': times,
    'X (cm)': x,
    'Y (cm)': y,
    'Z (cm)': z
}

# Create DataFrame
output_df = pd.DataFrame(output_data)

# Define the output file path
output_file_path = 'data/processed/Drone_Data_cm.csv'

# Save the DataFrame to a CSV file
output_df.to_csv(output_file_path, index=False)

print(f"Data saved to {output_file_path}")