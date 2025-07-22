import json

def to_json(data):
    return json.dumps(data, ensure_ascii=False)

def from_json(json_str):
    return json.loads(json_str)
