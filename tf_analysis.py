import pprint

from utilities import load_json, greek_letters_lowercase
from src_visitor import visit_node

class TypeQualifers:
    TAINTED = "tainted"
    UNTAINTED = "untainted"

def visit_ast(jast):
    # pprint.pprint(jast)
    visited = visit_node(jast)
    # pprint.pprint(visited)
    print("\n".join(visited))
    return

def main():
    from test import get_tests
    f = get_tests()[0]
    visit_ast(load_json(f.ast))
    return


if __name__ == '__main__':
    main()