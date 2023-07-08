import json

# Load the data from the file
with open('places.json', 'r') as f:
    data = json.load(f)

# Filter the data
filtered_data = [d for d in data if d['user_ratings_total'] and d['user_ratings_total'] > 200]

# Save the filtered data to a new file
with open('places_rating_>200.json', 'w') as f:
    json.dump(filtered_data, f, indent=4)
