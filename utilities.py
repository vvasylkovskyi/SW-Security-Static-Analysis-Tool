import json
def load_json(path):
    with path.open("r") as fp:
        d = json.load(fp)
    return d

def dump_json(path, data):
    with path.open("w") as fp:
        json.dump(data, fp)

def fix_not_openable_json(path, replacements):
    with path.open() as fp:
        r = fp.read()
    for old,new in replacements:
        r = r.replace(old,new)
    with path.open("w") as fp:
        fp.write(r)


greek_letters_lowercase = tuple(map(chr, range(0x03b1, 0x03c9+1)))
greek_letters_uppercase = tuple(map(chr, range(0x0391, 0x03a9+1)))

