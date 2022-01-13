"""

"""

from pathlib import Path
from zipfile import ZipFile
import shutil

import tf_analyser
from utilities import load_json, fix_not_openable_json


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
slices_url = "https://fenix.tecnico.ulisboa.pt/downloadFile/563568428829723/slices.zip"

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
        fix_outputs()
    print("\n".join(map(str, slices.iterdir())))


def fix_outputs():
    for output in slices.glob("*output.json"):
        fix_not_openable_json(output, [("'", '"')])

def main():
    if not slices.exists():
        extract()

    tests = tuple(map(Test, slices.glob("*.py")))
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
    parser.add_argument("--fix_outputs", action='store_true', help="flag to fix output files by replacing single quotes by double quotes")

    args = parser.parse_args()
    if args.extract:
        extract()
    elif args.fix_outputs:
        fix_outputs()
    else:
        main()