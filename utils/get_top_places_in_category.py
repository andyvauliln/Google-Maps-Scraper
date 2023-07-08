import json
from operator import itemgetter

# Load the data from the json file
with open('data/places.json') as f:
    data = json.load(f)

# Filter out closed places
filtered_data = [place for place in data if place.get('business_status') != "CLOSED_TEMPORARILY"]

top_places_by_type = {}
unique_places = set()

# Go through the filtered data
for place in filtered_data:

    # Filter out unwanted types from the place's types
    place['types'] = [place_type for place_type in place.get('types', [])
                      if place_type not in ["point_of_interest", "establishment"]]

    # If a place has no types left after filtering, skip it
    if not place['types']:
        continue

    for place_type in place['types']:
        if place_type not in top_places_by_type:
            top_places_by_type[place_type] = []

        # Set None ratings to 0
        place['user_ratings_total'] = place.get('user_ratings_total') or 0
        place['rating'] = place.get('rating') or 0

        # Add place to the list for its type
        top_places_by_type[place_type].append(place)

# Sort the places by rating and keep only the top 10 for each type
for place_type, places in top_places_by_type.items():
    places.sort(key=lambda x: (x['user_ratings_total'], x['rating']), reverse=True)
    top_places_by_type[place_type] = places[:10]

# Flatten the dictionary into a list
top_places_list = [place for places in top_places_by_type.values() for place in places]

# Remove duplicates
unique_top_places_list = []
for place in top_places_list:
    if place['place_id'] not in unique_places:
        unique_top_places_list.append(place)
        unique_places.add(place['place_id'])

# Save the top places to a new json file
with open('data/top_places_by_type.json', 'w') as f:
    json.dump(unique_top_places_list, f, indent=4)
