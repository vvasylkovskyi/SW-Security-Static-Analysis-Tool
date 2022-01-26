import json


def load_json(path):
    with path.open("r") as fp:
        d = json.load(fp)
    return d


def dump_json(path, data, **kwargs):
    with path.open("w") as fp:
        json.dump(data, fp, **kwargs)


def dump_jsons(path, objects, **kwargs):
    if not path.exists():
        path.mkdir()
    for p in objects:
        f = path/p.name
        dump_json(f, load_json(p), **kwargs)
        print(f)
    return


class GreekLetters():
    greek_letters_lowercase = tuple(
        map(chr, range(0x03b1, 0x03c9+1)))
    greek_letters_uppercase = tuple(
        map(chr, range(0x0391, 0x03a9+1)))

    # @property
    # def greek_letters_lowercase(self):
    #     return self.greek_letters_lowercase
