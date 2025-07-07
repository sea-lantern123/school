# merge_coords.py
import json, glob
NODE_COORDS = {}
for fn in glob.glob("coords_floor*.json"):
    NODE_COORDS.update(json.load(open(fn)))
json.dump(NODE_COORDS, open("all_coords.json","w"), ensure_ascii=False, indent=2)
print("NODE_COORDS 완성 -> all_coords.json")
