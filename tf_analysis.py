import pprint

from utilities import load_json
from tf_visitor import visit_node as tf_visit_node
from constraints_visitor import visit_node as constraints_visit_node


class TypeQualifers:
    TAINTED = "tainted"
    UNTAINTED = "untainted"


def print_constraints(constraints):
    pprint.pprint(constraints, width=10)


def visit_with_pattern(ast, pattern, visitor, **kwargs):
    kwargs.update(pattern)
    visited = visitor(ast, **kwargs)
    return visited


def visit_with_patterns(ast, patterns, visitor, **kwargs):
    data = []
    for pattern in patterns:
        data.append(visit_with_pattern(ast, pattern, visitor, **kwargs))
    return data


def main(visitor, func, **kwargs):
    from test import get_tests
    tests = get_tests()
    for test in tests:
        print(test.id, test.name)
        ast = load_json(test.ast)
        for visit in visit_with_patterns(ast, load_json(test.patterns), visitor, **kwargs):
            func(visit)
    return


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tf", action='store_true', help=f"run tainted flow visitor")
    parser.add_argument("--constraints", action='store_true', help="run constraints visitor")

    args = parser.parse_args()
    kwargs={}

    if args.tf:
        visitor = tf_visit_node
        func = lambda x:print("\n".join(x))
    elif args.constraints:
        visitor = constraints_visit_node
        kwargs.update(dict(constraints=list(), labels_map=dict()))
        func = print_constraints
    else:
        parser.print_help()
        import sys
        sys.exit(1)
    main(visitor, func, **kwargs)