import json

def load_json(path):
    with path.open("r") as fp:
        d = json.load(fp)
    return d

def dump_json(path, data, **kwargs):
    with path.open("w") as fp:
        json.dump(data, fp, **kwargs)



greek_letters_lowercase = tuple(map(chr, range(0x03b1, 0x03c9+1)))
greek_letters_uppercase = tuple(map(chr, range(0x0391, 0x03a9+1)))

