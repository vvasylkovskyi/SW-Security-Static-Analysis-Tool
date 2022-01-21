from tf_analyser import main_experimental
from pathlib import Path


def test_solution():
    list_of_tests = [('slices/1a-basic-flow.py.json',
                      'slices/1a-patterns.json'),
                     ('slices/1b-basic-flow.py.json',
                      'slices/1b-patterns.json')]

    for k, v in list_of_tests:
        file_path = k
        patterns = v
        main_experimental(file_path, Path(file_path), Path(patterns))


if __name__ == "__main__":

    test_solution()
