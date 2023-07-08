import json

# Load the data from the file
with open('data/places.json', 'r') as f:
    data = json.load(f)

# Sort the data by latitude and longitude
data.sort(key=lambda x: (x['location']['lat'], x['location']['lng']))

# Save the sorted data to a new file
with open('data/places_sorted.json', 'w') as f:
    json.dump(data, f, indent=4)
