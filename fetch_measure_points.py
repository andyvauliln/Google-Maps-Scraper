
import googlemaps
import numpy as np
import time
import json
import pandas as pd

API_KEY = "AIzaSyC_fvMkaAp8VWuuFJcesZ1UEvi0pS1tlF0"
fetched_places_count = 0
gmaps = googlemaps.Client(key=API_KEY)


def fetch_nearby_places(lat, lon, radius=200, page_token=None):
    print("Fetching nearby places at lat={}, lon={}, radius={}, page_token={}".format(lat, lon, radius, page_token))
    places = []
    next_page_token = None
    result = gmaps.places_nearby(
        location=(lat, lon), radius=radius, page_token=page_token)
    # print(result, lat, lon, radius, page_token, "result")
    if 'results' in result:
        for item in result['results']:
            mappedPlace = map_place_info(item)
            # print(mappedPlace)
            places.append(mappedPlace)

        print("Fetched {} places.".format(len(places)))
    if 'next_page_token' in result:
        print("*********Found a next page token.********")
        next_page_token = result['next_page_token']
    return places, next_page_token


def fetch_all_nearby_places(measure_points):
    print("Fetching all({}) nearby places.".format(len(measure_points)))
    all_places = []
    processed_points = 0
    fetched_places_set = set()  # Keep track of places already fetched
    for index, row in measure_points.iterrows():
        lat, lon = row["lat"], row["lon"]
        page_token = None
        while True:
            places, next_page_token = fetch_nearby_places(
                lat, lon, page_token=page_token)
            for place in places:
                # Check if place is already in set before adding to list
                if place['place_id'] not in fetched_places_set:
                    all_places.append(place)
                    fetched_places_set.add(place['place_id'])
            if next_page_token is not None:
                time.sleep(2)  # Add a delay to handle API limitations
                page_token = next_page_token
            else:
                break
        processed_points += 1
    return all_places, processed_points


def map_place_info(obj):
    place_id = obj.get("place_id")
    compound_code = obj.get("plus_code", {}).get("compound_code")
    business_status = obj.get("business_status")
    location = obj.get("geometry", {}).get("location")
    name = obj.get("name")
    types = obj.get("types")
    vicinity = obj.get("vicinity")
    rating = obj.get("rating", None)
    user_ratings_total = obj.get("user_ratings_total", None)
    return {
        "place_id": place_id,
        "compound_code": compound_code,
        "business_status": business_status,
        "location": location,
        "name": name,
        "types": types,
        "vicinity": vicinity,
        "rating": rating,
        "user_ratings_total": user_ratings_total
    }


def fetch_places():
    global fetched_places_count
    input_filename = "measure_points_5.csv"
    points = pd.read_csv(input_filename)

    points = points[2300: None]

    # Split measure points into batches of 100
    measure_points_batches = [points[i:i+100]
                              for i in range(0, len(points), 100)]

    for i, measure_points_batch in enumerate(measure_points_batches):
        print("Fetching places for batch {}/{}".format(i +
              1, len(measure_points_batches)))
        all_places, processed_points = fetch_all_nearby_places(
            measure_points_batch)
        print("Fetched {} places.".format(len(all_places)))

        # Save the fetched places to a JSON file
        with open('fetched_places_batch{}.json'.format(23+i+1), 'w') as f:
            json.dump(all_places, f)

        fetched_places_count += len(all_places)
        print("Fetched places count: {}, Processed measure points: {}/{}".format(
            fetched_places_count,  processed_points, len(points)))
        # time.sleep(2)


# Run the app
if __name__ == '__main__':
    fetch_places()
