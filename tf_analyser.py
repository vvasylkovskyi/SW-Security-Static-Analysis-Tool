"""
Segurança de Software - Instituto Superior Técnico / Universidade de Lisboa
MEIC-A 2021/2022 2nd Period
Software Vulnerabilities Static Analysis tool:

given a pyhon program slice, a tainted flow analysis
based on the series of lectures https://www.coursera.org/learn/software-security/lecture/c4Dw1/flow-analysis
is performed

Usage:
$ python tf_analyser.py <ast> <vulnerabilities>
"""

from pathlib import Path
from pprint import pprint

# from pointers_visitor import PointersVisitor
# from tf_src_visitor import TaintedFlowSrcVisitor
# from ssa_visitor import SingleStaticAssignmentVisitor

from src_visitor import SrcVisitor
from clean_ast_visitor import CleanAstVisitor
from ps_visitor import PathSensitivityVisitor
from scoped_ssa_visitor import ScopedSingleStaticAssignmentVisitor
from ssa_src_visitor import SSASrcVisitor
from instantiation_visitor import InstantiationVisitor
from tf_ssa_visitor import TaintedFlowSSAVisitor
from tf_visitor import TaintedFlowVisitor
from tf_ssa_src_visitor import TaintedFlowSSASrcVisitor
from constraints_pf_sensitivity_visitor import ConstraintsPathFlowSenstivityVisitor

from utilities import load_json


def report(context, obj):
    print()
    print(context)
    if isinstance(obj, str):
        print(obj)
    else:
        pprint(obj)


def make_vulnerability(vulnerability, source, sink, unsanitized_flows="yes", sanitized_flows=[]):
    return {"vulnerability": vulnerability, "source": source, "sink": sink, "unsanitized flows": unsanitized_flows, "sanitized flows": sanitized_flows}


def get_vulnerabilities(ast, pattern, variable_ssa_map, ssa_variable_map, tf_labels, scoped_constraints, path_feasibility_constraints):
    #TODO
    return [{}]


def get_analysis_data(ast, pattern, debug=False):

    InstantiationVisitor(ast, **pattern).visit_ast()  # mutate pattern, TODO arg names broken, move to before ssa?

    #if debug: report("AST:", ast) #to check progress of instantiation

    # tfv = TaintedFlowVisitor(ast)
    tfv = TaintedFlowSSAVisitor(ast)

    tfv.visit_ast()  # assign taint qualifiers

    #if debug: report("AST:", ast) # check progress of taint qualifiers atribution

    tf_labels = tfv.labels

    cv = ConstraintsPathFlowSenstivityVisitor(ast)
    cv.visit_ast()  # create constraints

    scoped_constraints = cv.scoped_constraints
    path_feasibility_constraints = cv.path_feasibility_constraints

    if debug:
        report("PATTERN:", pattern)
        report("SOURCE WITH TYPE QUALIFIERS:", TaintedFlowSSASrcVisitor(ast).visit_ast())
        report("LABELS:", tf_labels)
        report("SCOPED_CONSTRAINTS:", scoped_constraints)
        report("PATH_FEASIBILITY_CONSTRAINTS:", path_feasibility_constraints)

    # # print(f"please solve constraints to detect illegal flows")

    return tf_labels, scoped_constraints, path_feasibility_constraints


def main_experimental(ast, patterns, debug=False):

    ast = load_json(ast)

    report("SOURCE:", SrcVisitor(ast).visit_ast())

    CleanAstVisitor(ast).visit_ast()

    psv = PathSensitivityVisitor(ast)
    psv.visit_ast()

    #if debug: report("PS_CONDITIONS:", psv.conditions)

    ssav = ScopedSingleStaticAssignmentVisitor(ast)
    ssav.visit_ast()
    variable_ssa_map = ssav.variable_ssa_map
    ssa_variable_map = ssav.ssa_variable_map
    if debug: report("VARIABLE_SSA:", dict(variable_ssa_map))
    if debug: report("SSA_VARIABLE:", ssa_variable_map)

    source_ssa = SSASrcVisitor(ast).visit_ast()
    #if debug: report("SOURCE_SSA:", source_ssa)

    #if debug: report("AST:", ast) # check progress of visitors

    patterns = load_json(patterns)

    #if debug: report("PATTERNS:", patterns)

    vulnerabilities = list()

    for pattern in patterns:

        #if debug: report("PATTERN:", pattern) # to compare to after their mutation

        tf_labels, scoped_constraints, path_feasibility_constraints = get_analysis_data(ast.copy(), pattern, debug=debug)

        vulnerabilities.extend(get_vulnerabilities(ast, pattern, variable_ssa_map, ssa_variable_map, tf_labels, scoped_constraints, path_feasibility_constraints))


    #if debug: report("VULNERABILITIES:", vulnerabilities)

    return vulnerabilities



def main(ast, patterns, debug=False):
    main_experimental(ast, patterns, debug=debug)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("program", type=str, help="path of a JSON file containing the program slice to analyse, represented in the form of an Abstract Syntax Tree")
    parser.add_argument("patterns", type=str, help="path of a JSON file containing the list of vulnerability patterns to consider")
    parser.add_argument("--debug", action='store_true', help="print relevant objects")

    args = parser.parse_args()

    main(Path(args.program), Path(args.patterns), args.debug)