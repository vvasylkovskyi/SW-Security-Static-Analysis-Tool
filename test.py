"""

"""

from pathlib import Path
from pprint import pprint
from zipfile import ZipFile
import shutil

import tf_analyser
from utilities import load_json, dump_json, dump_jsons


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


def get_tests(glob_expr=""):
    return tuple(map(Test, slices.glob(f"{glob_expr}*.py")))


def pprint_objects(path, objects):
    dump_jsons(path, objects, indent=4)


def pprint_asts():
    pprint_objects(Path("asts"), slices.glob("*.py.json"))


def pprint_patterns():
    pprint_objects(Path("patterns"), slices.glob("*patterns.json"))


def pprint_outputs():
    pprint_objects(Path("outputs"), slices.glob("*output.json"))


def run(test):
    print()
    print(test)
    analysis = tf_analyser.main(test.ast, test.patterns)
    print()
    # output = load_json(t.output)
    # assert analysis==output, f"{analysis} != {output}"


def run_tests(glob_expr=""):
    tests = get_tests(glob_expr=glob_expr)
    for t in tests:
        run(t)

def main():
    if not slices.exists(): extract()
    run_tests()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extract", action='store_true', help=f"flag to extract slices from zip archive ({slices_url})") #action=argparse.BooleanOptionalAction 3.10
    parser.add_argument("--pprint_asts", action='store_true', help="pretty print abstract syntax trees")
    parser.add_argument("--pprint_outputs", action='store_true', help="pretty print output objects")
    parser.add_argument("--pprint_patterns", action='store_true', help="pretty print patterns objects")
    parser.add_argument("--tests", nargs='+', help="expression to id tests (example 1a 2)")

    args = parser.parse_args()
    if args.extract:
        extract()
    elif args.pprint_asts:
        pprint_asts()
    elif args.pprint_patterns:
        pprint_patterns()
    elif args.pprint_outputs:
        pprint_outputs()
    elif args.tests:
        for e in args.tests:
            run_tests(glob_expr=e)
    else:
        main()