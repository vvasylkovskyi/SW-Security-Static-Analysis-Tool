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
from constraints_visitor import Constraint

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
from utilities import GreekLetters, load_json


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
        ssa_variable_map, path_feasibility_constraints, pattern, sources, sinks, tf_labels)

    formatted_vulnerabilities = list()
    for index, vulnerability in enumerate(vulnerabilities):
        count = index + 1
        vulnerability_name = vulnerability.name + "_" + count.__str__()
        formatted_vulnerabilities.append(make_vulnerability(
            vulnerability_name, vulnerability.source, vulnerability.sink))

    return formatted_vulnerabilities


def resolve_sources(sources, labels):
    resolved_sources = list()
    for source in sources:
        if labels[source] != None:
            resolved_sources.append(labels[source])
    return resolved_sources


def get_variables_ssa(key, ssa_variable_map):
    print("")
    variables_ssa = list()
    for ssa_key in ssa_variable_map:
        print("SSA KEY: ", ssa_key)
        print("KEY: ", key)
        print("MAP: ", ssa_variable_map[ssa_key])
        if ssa_variable_map[ssa_key] == key:
            variables_ssa.append(ssa_key)
    return variables_ssa


def link_constraints_for_the_same_ssa_per_path_feasibility_constraints(variable_ssa_map, ssa_variable_map, path_feasibility_constraints, tf_labels):
    for scope in variable_ssa_map:
        print("Variable to SSA: ", scope)
        print("Variables: ", variable_ssa_map[scope])
        for key in variable_ssa_map[scope].keys():
            print("var: ", key)
            print("SSSA VAR MAP: ", ssa_variable_map)
            values = variable_ssa_map[scope][key]
            # values = get_variables_ssa(key, ssa_variable_map)
            print("value: ", values)
            if len(values) > 1:
                type_qualifiers = list()
                for value in values:
                    type_qualifiers.append(tf_labels[value])
                print("Type qualifiers: ", type_qualifiers)
                first_type_qualifier = type_qualifiers[0]
                single_path_feasibility_constraints = path_feasibility_constraints[scope]
                print("PATH FEASIBILITY: ", single_path_feasibility_constraints)
                updated_scoped_constraints = list()
                print("Original constraints: ",
                      single_path_feasibility_constraints._scoped_constraints)
                for constraint in single_path_feasibility_constraints._scoped_constraints:
                    lhs_tq = constraint.lhs_tq
                    if lhs_tq in type_qualifiers and lhs_tq is not first_type_qualifier:
                        lhs_tq = first_type_qualifier
                    rhs_tq = constraint.rhs_tq
                    if rhs_tq in type_qualifiers and rhs_tq is not first_type_qualifier:
                        rhs_tq = first_type_qualifier
                    new_constraint = Constraint(
                        constraint.line, lhs_tq, constraint.lhs_id, rhs_tq, constraint.rhs_id)
                    updated_scoped_constraints.append(new_constraint)
                    print("Constraint: ", constraint)
                single_path_feasibility_constraints._scoped_constraints = updated_scoped_constraints
                print("Updated constraints: ",
                      single_path_feasibility_constraints._scoped_constraints)


def get_analysis_data(ast, pattern, variable_ssa_map, ssa_variable_map, debug=False):

    # mutate pattern, TODO arg names broken, move to before ssa?
    InstantiationVisitor(ast, **pattern).visit_ast()
    GreekLetters.greek_letters_lowercase = tuple(
        map(chr, range(0x03b1, 0x03c9+1)))
    GreekLetters.greek_letters_uppercase = tuple(
        map(chr, range(0x0391, 0x03a9+1)))
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

    print("HERE Checking variable ssa map: ", variable_ssa_map)
    print("Here checking ssa_variable_map: ", ssa_variable_map)

    # This is to link if/else inner branches to outer branches
    link_constraints_for_the_same_ssa_per_path_feasibility_constraints(
        variable_ssa_map, ssa_variable_map, path_feasibility_constraints, tf_labels)

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

    if debug:
        report("PS_CONDITIONS:", psv.conditions)

    ssav = ScopedSingleStaticAssignmentVisitor(ast)
    ssav.visit_ast()
    variable_ssa_map = ssav.variable_ssa_map
    ssa_variable_map = ssav.ssa_variable_map
    if debug:
        report("VARIABLE_SSA:", dict(variable_ssa_map))
    if debug:
        report("SSA_VARIABLE:", ssa_variable_map)

    source_ssa = SSASrcVisitor(ast).visit_ast()
    # if debug: report("SOURCE_SSA:", source_ssa)

    # if debug: report("AST:", ast) # check progress of visitors

    patterns = load_json(patterns)

    # if debug: report("PATTERNS:", patterns)

    vulnerabilities = list()

    for pattern in patterns:
        CleanAstVisitor(ast).visit_ast()

        # if debug: report("PATTERN:", pattern) # to compare to after their mutation

        tf_labels, scoped_constraints, path_feasibility_constraints, sources, sinks = get_analysis_data(
            ast.copy(), pattern, variable_ssa_map, ssa_variable_map, debug=debug)

        vulnerabilities.extend(get_vulnerabilities(ast, pattern, variable_ssa_map,
                               ssa_variable_map, tf_labels, scoped_constraints, path_feasibility_constraints, sources, sinks))

    # if debug: report("VULNERABILITIES:", vulnerabilities)

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
