"""
Segurança de Software - Instituto Superior Técnico / Universidade Lisboa
Software Vulnerabilities Static Analysis tool: TODO rewrite given a program, the tool reveals potential vulnerabilties.

Analyse python ast tree to check if there any vulnerabilities.

Usage:
$ python tf_analyser.py analyse <input_ast_json_file_path> <vulnerabilities_file_path>
"""

# import ast
import pprint
from utilities import load_json

def make_vulnerability(vulnerability, source, sink, unsanitized_flows="yes", sanitized_flows=[]):
    return {"vulnerability": vulnerability, "source": source, "sink": sink, "unsanitized flows": unsanitized_flows, "sanitized flows": sanitized_flows}


def main(ast, patterns):
    print(ast, patterns)

    patterns = load_json(patterns)
    print(patterns)
    ast = load_json(ast)
    pprint.pprint(ast)
    analysis = []

    return analysis

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("program", type=str, help="path of a JSON file containing the program slice to analyse, represented in the form of an Abstract Syntax Tree")
    parser.add_argument("patterns", type=str, help="path of a JSON file containing the list of vulnerability patterns to consider")

    args = parser.parse_args()

    main(args.program, args.patterns)