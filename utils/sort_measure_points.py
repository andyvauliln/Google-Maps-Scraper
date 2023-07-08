import pandas as pd

# Read input CSV file
input_filename = "measure_points.csv"
df = pd.read_csv(input_filename)

# Sort coordinates from left to right
df = df.sort_values(by=['lon', 'lat'])

# Write sorted coordinates to output CSV file
output_filename = "measure_points_sorted.csv"
df.to_csv(output_filename, index=False)

print("Sorted coordinates saved to file:", output_filename)
