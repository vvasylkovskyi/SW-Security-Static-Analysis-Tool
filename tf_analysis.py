import pprint

from utilities import load_json, greek_letters_lowercase
from src_visitor import visit_node
from tf_visitor import visit_node as tf_visit_node

class TypeQualifers:
    TAINTED = "tainted"
    UNTAINTED = "untainted"

def visit_ast(jast):
    # pprint.pprint(jast)
    visited = visit_node(jast)
    # pprint.pprint(visited)
    print("\n".join(visited))
    return

# tf_visit_node

def vulnerabilities(ast, patterns):
    for pattern in patterns:
        print(pattern)
        visited = tf_visit_node(ast, **pattern)
        print("\n".join(visited))
        print()

    return []

def main():
    from test import get_tests
    tests = get_tests()
    for test in tests:
        print(test.id, test.name)
        vulnerabilities(load_json(test.ast), load_json(test.patterns))

    return


if __name__ == '__main__':
    main()