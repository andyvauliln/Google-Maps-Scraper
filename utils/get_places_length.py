import json


with open('../data/not_closed_points.json') as f:
    data = json.load(f)


print(len(data))
