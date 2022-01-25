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
import json

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
from constraints_resolver import ConstraintsResolver
from unmarked_visitor import UnmarkedVisitor
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


def print_vulnerabilities_to_json(vulnerabilities, file_path):
    vulnerabilties_str = '['

    for index, vulnerability in enumerate(vulnerabilities):
        json_ready_vulnerability = json.dumps(make_vulnerability(
            vulnerability=vulnerability[0], source=vulnerability[1], sink=vulnerability[2]))
        vulnerabilties_str += json_ready_vulnerability
        if(index < len(vulnerabilities) - 1):
            vulnerabilties_str += ','

    vulnerabilties_str += ']'

    output_file_path = file_path.split(".", 1)[0]
    output_file_path += '.output.json'
    with open(output_file_path, 'w') as formatted_file:
        formatted_file.write(vulnerabilties_str + '\n')


def get_vulnerabilities(ast, pattern, variable_ssa_map, ssa_variable_map, tf_labels, scoped_constraints, path_feasibility_constraints, sources, sinks):
    # TODO
    print("HERE", TaintedFlowSSASrcVisitor(ast).visit_ast())

    constraints_resolver = ConstraintsResolver()
    vulnerabilities = constraints_resolver.resolve_constraints_and_find_vulnerabilties(
        path_feasibility_constraints, pattern, sources, sinks, tf_labels)

    formatted_vulnerabilities = list()
    for vulnerability in vulnerabilities:
        formatted_vulnerabilities.append(make_vulnerability(
            vulnerability[0], vulnerability[1], vulnerability[2]))

    return formatted_vulnerabilities


def resolve_sources(sources, labels):
    resolved_sources = list()
    for source in sources:
        if labels[source] != None:
            resolved_sources.append(labels[source])
    return resolved_sources


def get_analysis_data(ast, pattern, debug=False):

    # mutate pattern, TODO arg names broken, move to before ssa?
    InstantiationVisitor(ast, **pattern).visit_ast()
    print("PATTERN HERE: ", pattern)
    # if debug: report("AST:", ast) #to check progress of instantiation

    tfv = TaintedFlowSSAVisitor(ast)

    tfv.visit_ast()  # assign taint qualifiers

    tf_labels = tfv.labels

    cv = ConstraintsPathFlowSenstivityVisitor(ast)

    cv.labels = tf_labels
    cv.sources = tfv.sources
    cv.sinks = tfv.sinks
    cv.sanitizers = tfv.sanitizers

    cv.visit_ast()  # create constraints

    scoped_constraints = cv.scoped_constraints
    path_feasibility_constraints = cv.path_feasibility_constraints

    sources = tfv.sources
    sinks = tfv.sinks
    if debug:
        report("PATTERN:", pattern)
        report("SOURCE WITH TYPE QUALIFIERS:",
               TaintedFlowSSASrcVisitor(ast).visit_ast())
        report("LABELS:", tf_labels)
        report("SCOPED_CONSTRAINTS:", scoped_constraints)
        report("PATH_FEASIBILITY_CONSTRAINTS:", path_feasibility_constraints)

    # # print(f"please solve constraints to detect illegal flows")

    return tf_labels, scoped_constraints, path_feasibility_constraints, sources, sinks


def main_experimental(ast, patterns, debug=False):

    ast = load_json(ast)

    # report("SOURCE:", SrcVisitor(ast).visit_ast())

    CleanAstVisitor(ast).visit_ast()

    psv = PathSensitivityVisitor(ast)
    psv.visit_ast()

    #if debug: report("PS_CONDITIONS:", psv.conditions)

    ssav = ScopedSingleStaticAssignmentVisitor(ast)
    ssav.visit_ast()
    variable_ssa_map = ssav.variable_ssa_map
    ssa_variable_map = ssav.ssa_variable_map
    if debug:
        report("VARIABLE_SSA:", dict(variable_ssa_map))
    if debug:
        report("SSA_VARIABLE:", ssa_variable_map)

    source_ssa = SSASrcVisitor(ast).visit_ast()
    #if debug: report("SOURCE_SSA:", source_ssa)

    # if debug: report("AST:", ast) # check progress of visitors

    patterns = load_json(patterns)

    #if debug: report("PATTERNS:", patterns)

    vulnerabilities = list()

    for pattern in patterns:

        # if debug: report("PATTERN:", pattern) # to compare to after their mutation

        tf_labels, scoped_constraints, path_feasibility_constraints, sources, sinks = get_analysis_data(
            ast.copy(), pattern, debug=debug)

        vulnerabilities.extend(get_vulnerabilities(ast, pattern, variable_ssa_map,
                               ssa_variable_map, tf_labels, scoped_constraints, path_feasibility_constraints, sources, sinks))

    #if debug: report("VULNERABILITIES:", vulnerabilities)

    return vulnerabilities


def main(ast, patterns, debug=False):
    return main_experimental(ast, patterns, debug=debug)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "program", type=str, help="path of a JSON file containing the program slice to analyse, represented in the form of an Abstract Syntax Tree")
    parser.add_argument(
        "patterns", type=str, help="path of a JSON file containing the list of vulnerability patterns to consider")
    parser.add_argument("--debug", action='store_true',
                        help="print relevant objects")

    args = parser.parse_args()

    main(Path(args.program), Path(args.patterns), args.debug)
