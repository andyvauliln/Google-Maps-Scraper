# {"place_id": "ChIJjx-t1cZE0i0R9FBMGRkBhHM", "compound_code": null, "business_status": null, "location": {"lat": -8.7815919, "lng": 115.1787738}, "name": "Kuta Selatan", "types": ["locality", "political"], "vicinity": "Kuta Selatan", "rating": null, "user_ratings_total": null}

import json

# Load the data from the file
with open('./places.json', 'r') as f:
    data = json.load(f)

closed_points = [point for point in data if point.get("business_status") != "CLOSED_TEMPORARILY"]


# Save the filtered data to a new file
with open('not_closed_points.json', 'w') as f:
    json.dump(closed_points, f, indent=4)
