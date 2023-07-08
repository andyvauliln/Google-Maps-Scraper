import json
from collections import defaultdict

# Load the data from the file
with open('data/places.json', 'r') as f:
    data = json.load(f)

# Count all types
type_counts = defaultdict(int)
for d in data:
    if 'types' in d:
        for type in d['types']:
            type_counts[type] += 1

# Print the counts
for type, count in type_counts.items():
    print(f'Type: {type}, Count: {count}')

# Save the type counts to a new file
with open('data/places_types.json', 'w') as f:
    json.dump(dict(type_counts), f, indent=4)
