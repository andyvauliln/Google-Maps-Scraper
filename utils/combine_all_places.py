import json


def combine_json_files(file1, file2, file3, file4, file5, output_file):
    with open(file1, 'r') as f1, open(file2, 'r') as f2, open(file3, 'r') as f3, open(file4, 'r') as f4, open(file5, 'r') as f5:
        data1 = json.load(f1)
        data2 = json.load(f2)
        data3 = json.load(f3)
        data4 = json.load(f4)
        data5 = json.load(f5)

    seen_ids = set()
    combined_data = []

    for item in data1 + data2 + data3 + data4 + data5:
        if item['place_id'] not in seen_ids:
            seen_ids.add(item['place_id'])
            combined_data.append(item)

    with open(output_file, 'w') as output:
        json.dump(combined_data, output)


# usage
combine_json_files('all_places_3.json', 'all_places_4.json', 'all_places_2.json',
                   'all_places_1.json',  'all_places_5.json', 'places.json')
