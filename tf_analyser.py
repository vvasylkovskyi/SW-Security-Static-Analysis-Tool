"""
Segurança de Software - Instituto Superior Técnico / Universidade de Lisboa
MEIC-A 2021/2022 Periodo 2
Software Vulnerabilities Static Analysis tool:

given a program, a tainted flow analysis
based on the series of lectures https://www.coursera.org/learn/software-security/lecture/c4Dw1/flow-analysis
is performed

Usage:
$ python tf_analyser.py <ast> <vulnerabilities>
"""

from pathlib import Path
from pprint import pprint

from utilities import load_json
from tf_analysis import visit_with_pattern
from src_visitor import visit_node as src_visit_node
from tf_visitor import visit_node as tf_visit_node
from constraints_visitor import visit_node as constraints_visit_node


def make_vulnerability(vulnerability, source, sink, unsanitized_flows="yes", sanitized_flows=[]):
    return {"vulnerability": vulnerability, "source": source, "sink": sink, "unsanitized flows": unsanitized_flows, "sanitized flows": sanitized_flows}


def main_experimental(ast, patterns):
    # print(ast, patterns)
    ast = load_json(ast)
    print()
    print("SOURCE:")
    src = src_visit_node(ast)
    print("\n".join(src))
    patterns = load_json(patterns)
    # print(patterns)
    for pattern in patterns:
        print()
        print("PATTERN:")
        print(pattern)
        src = tf_visit_node(ast, **pattern)
        print()
        print("SRC WITH TYPE QUALIFIERS:")
        print("\n".join(src))
        constraints = list()
        visit_with_pattern(ast, pattern, constraints_visit_node, constraints=constraints, labels_map=dict(), **pattern)
        # pprint(constraints, width=10)
        print()
        print("CONSTRAINTS:")
        print("\n".join(map(repr, sorted(set(constraints)))))
        # print(f"please solve constraints to detect illegal flows")
        # print()

def main(ast, patterns):
    main_experimental(ast, patterns)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("program", type=str, help="path of a JSON file containing the program slice to analyse, represented in the form of an Abstract Syntax Tree")
    parser.add_argument("patterns", type=str, help="path of a JSON file containing the list of vulnerability patterns to consider")

    args = parser.parse_args()

    main(Path(args.program), Path(args.patterns))