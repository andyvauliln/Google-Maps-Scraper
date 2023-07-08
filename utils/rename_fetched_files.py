import os
import re

# Define the directory where your files are stored
directory = "./generatedPoints"

# Define the base name of your files
base_file_name = "fetched_places_batch"

# Define the starting number
start_num = 400

# Get a list of all the files in the directory
files = os.listdir(directory)

# Filter out the files that match your base file name
filtered_files = [file for file in files if re.match(f"{base_file_name}\d+\.json", file)]
print(len(filtered_files))

# Sort the files (if necessary)
filtered_files.sort()

for file in filtered_files:
    # Construct the new file name
    new_file_name = f"{base_file_name}{start_num}.json"

    # Get the full path to the file
    old_file_path = os.path.join(directory, file)

    # Get the full path to the new file
    new_file_path = os.path.join(directory, new_file_name)

    # Rename the file
    os.rename(old_file_path, new_file_path)

    # Increment the starting number
    start_num += 1
