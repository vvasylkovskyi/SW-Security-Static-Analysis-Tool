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

from src_visitor import SrcVisitor
from clean_ast_visitor import CleanAstVisitor
from instantiation_visitor import InstantiationVisitor
from tf_visitor import TaintedFlowVisitor
from tf_src_visitor import TaintedFlowSrcVisitor
from constraints_visitor import ConstraintsVisitor


def report(context, obj):
    print()
    print(context)
    if isinstance(obj, str):
        print(obj)
    else:
        pprint(obj)


def make_vulnerability(vulnerability, source, sink, unsanitized_flows="yes", sanitized_flows=[]):
    return {"vulnerability": vulnerability, "source": source, "sink": sink, "unsanitized flows": unsanitized_flows, "sanitized flows": sanitized_flows}


def get_vulnerabilities(ast, pattern, constraints):
    return [{}]


def get_constraints(ast, pattern):
    InstantiationVisitor(ast, **pattern).visit_ast()  # mutate pattern

    report("PATTERN:", pattern)

    # report("AST:", ast) #to check progress of instantiation

    tfv = TaintedFlowVisitor(ast)
    tfv.visit_ast()  # assign taint qualifiers

    # report("AST:", ast) # check progress of taint qualifiers atribution

    # report("LABELS:", tfv.labels)

    report("SOURCE WITH TYPE QUALIFIERS:", TaintedFlowSrcVisitor(ast).visit_ast())

    cv = ConstraintsVisitor(ast)
    cv.visit_ast()  # create constraints

    report("CONSTRAINTS:", cv.constraints)

    # pprint(cv.constraints, width=10)
    # report("CONSTRAINTS:", "\n".join(map(repr, sorted(set(cv.constraints)))))

    # # print(f"please solve constraints to detect illegal flows")

    return cv.constraints


def main_experimental(ast, patterns):

    ast = load_json(ast)

    report("SOURCE:", SrcVisitor(ast).visit_ast())

    CleanAstVisitor(ast).visit_ast()

    patterns = load_json(patterns)

    # report("PATTERNS:", patterns) #debug

    vulnerabilities = list()

    for pattern in patterns:

        # report("PATTERN:", pattern) # to compare to after their mutation

        constraints = get_constraints(ast.copy(), pattern)

        vulnerabilities.extend(get_vulnerabilities(ast, pattern, constraints))

    # report("VULNERABILITIES:", vulnerabilities)

    return vulnerabilities

def main(ast, patterns):
    main_experimental(ast, patterns)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("program", type=str, help="path of a JSON file containing the program slice to analyse, represented in the form of an Abstract Syntax Tree")
    parser.add_argument("patterns", type=str, help="path of a JSON file containing the list of vulnerability patterns to consider")

    args = parser.parse_args()

    main(Path(args.program), Path(args.patterns))