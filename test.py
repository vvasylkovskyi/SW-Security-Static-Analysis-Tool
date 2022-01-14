"""

"""

from pathlib import Path
from zipfile import ZipFile
import shutil
import pprint

import tf_analyser
from tf_analysis import visit_ast
from utilities import load_json, dump_json


class Test:
    def __init__(self, src):
        self.src = src
        self.id = self.src.stem.split("-")[0]
        self.name = self.src.stem[len(self.id)+1:]
        self.ast = self.src.with_suffix(f"{self.src.suffix}.json")
        self.patterns = self.src.with_name(f"{self.id}-patterns.json")
        self.output = self.src.with_name(f"{self.id}-output.json")

    def __str__(self):
        return f"{self.id}: {self.name}"

slices = Path("slices")
slices_url = "https://fenix.tecnico.ulisboa.pt/downloadFile/845043405565957/slices-14Jan.zip"

def extract():
    if not slices.exists():
        slices.mkdir()
        archive = slices.with_suffix(".zip")
        if not archive.exists():
            raise RuntimeError(f"{archive} does not exist, download {slices_url}")
        zip = ZipFile(archive)
        zip.extractall(slices)
        zip.close()
        print(zip)
        macos = slices / "__MACOSX"
        if macos.exists():
            shutil.rmtree(macos)
    print("\n".join(map(str, slices.iterdir())))


def get_tests():
    return tuple(map(Test, slices.glob("*.py")))

def test_visitor():
    tests = get_tests()
    for t in tests:
        print(t)
        visit_ast(load_json(t.ast))
    return

def pprint_asts():
    asts = Path("asts")
    if not asts.exists(): asts.mkdir()
    for p in slices.glob("*.py.json"):
        dump_json(asts/p.name, load_json(p), indent=4)
    return

def get_ast_types():
    ast_types = set()
    def f(d):
        for k,v in d.items():
            if k=="ast_type" and v not in ast_types:
                ast_types.add(v)
            elif isinstance(v, dict):
                f(v)
            elif isinstance(v, list):
                for e in v:
                    f(e)
    for p in slices.glob("*.py.json"):
        f(load_json(p))

    return ast_types


def generate_visitors():
    ast_types = get_ast_types()
    for ast_type in get_ast_types():
        print(
            f'''
def visit_{ast_type}(data):
    """
    :param data:
    :return:
    """
    # key = "k"
    # return data[key]
    raise NotImplementedError(f"visitor for ast_type {ast_type} not implemented")
    '''
        )
        #TODO add keys related to ast_type...

    print("{")
    for ast_type in ast_types:
        print(f"    {repr(ast_type)}:visit_{ast_type},")
    print("}")


def main():
    if not slices.exists():
        extract()
    tests = get_tests()
    tests = tests[:1]
    for t in tests:
        print(t)
        analysis = tf_analyser.main(t.ast, t.patterns)
        output = load_json(t.output)
        assert analysis==output, f"{analysis} != {output}"
    return


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extract", action='store_true', help=f"flag to extract slices from zip archive ({slices_url})") #action=argparse.BooleanOptionalAction 3.10
    parser.add_argument("--test_visitor", action='store_true', help="test a visitor defined below")
    parser.add_argument("--pprint_asts", action='store_true', help="pretty print abstract syntax trees")
    parser.add_argument("--generate_visitors", action='store_true', help="generate visitors for available abstract syntax trees (under slices)")

    args = parser.parse_args()
    if args.extract:
        extract()
    elif args.test_visitor:
        test_visitor()
    elif args.pprint_asts:
        pprint_asts()
    elif args.generate_visitors:
        generate_visitors()

    else:
        main()