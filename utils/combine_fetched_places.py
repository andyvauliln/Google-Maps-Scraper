import os
import json


def combine_json_files(folder_path, output_file, place_id_file):
    places = []
    place_ids = set()
    cleared_places = []

    # Get the list of files in the folder
    files = [f for f in os.listdir(folder_path) if f.endswith('.json')]

    # Load existing places from the output file, if it exists
    existing_places = []
    if os.path.isfile(output_file):
        with open(output_file, 'r') as f:
            existing_places = json.load(f)

    # Iterate over the files
    for file in files:
        file_path = os.path.join(folder_path, file)
        with open(file_path, 'r') as f:
            data = json.load(f)
            places.extend(data)

    # Combine existing places and new places, excluding duplicates based on place_id
    all_places = existing_places + places
    for place in all_places:
        place_id = place['place_id']
        if place_id not in place_ids:
            cleared_places.append(place)
            place_ids.add(place_id)

    # Write the combined and deduplicated places to the output file
    with open(output_file, 'w') as f:
        json.dump(list(cleared_places), f)

    # Write the place_ids to the separate file
    with open(place_id_file, 'w') as f:
        json.dump(list(place_ids), f)


# Example usage
folder_path = 'data'
output_file = 'all_places_5.json'
place_id_file = 'all_place_ids_5.json'

combine_json_files(folder_path, output_file, place_id_file)
