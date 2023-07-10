import json


with open('../data/[0-40000]-error-places.json') as f:
    data = json.load(f)


print(len(data))
