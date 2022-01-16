import sys
import json
from ast_helper.parse_ast import make_ast
from ast import literal_eval
from cfg.make_cfg import make_cfg
from ast_helper.build_ast_tree import build_from_file
from vulnerabilities import find_vulnerabilities
from analysis.fixed_point import FixedPointAnalysis
# Lattice explained - https://math.stackexchange.com/questions/1646832/what-is-a-lattice-in-set-theory/1646863


def usage(file_path):
    print('Segurança de Software - Instituto Superior Técnico / Universidade Lisboa')
    print('Software Vulnerabilities Static Analysis tool: given a program, the tool reveals potential vulnerabiltiesx.\n')
    print('')
    print('Usage:')
    print('This tool provides two options:')
    print('1 - Convert python file to ast and print it in json format. Run program as: ')
    print('-- $ python tool.py ast2json <input_python_file_path> <output_ast_json_file_path>')
    print('2 - Analyse python ast tree to check if there any vulnerabilities. To do so, run program as: ')
    print('-- $ python tool.py analyse <input_ast_json_file_path> <vulnerabilities_file_path>')
    print('-- First argument is the name of the JSON file containing the program slice to analyse, represented in the form of an Abstract Syntax Tree;')
    print('-- Second argument is the name of the JSON file containing the list of vulnerability patterns to consider.')
    print('  %s <file_path> ' % file_path)
    sys.exit()


def convert_python_code_to_ast_json(abstract_syntax_tree_file_path, output_file_path):
    code = open(abstract_syntax_tree_file_path, "r").read()
    json_ast = make_ast(code)
    with open(output_file_path, 'w') as outfile:
        json.dump(json_ast, outfile)


def write_output_result(vulnerabilities_string, ast_json_file_path):
    vulnerabilities_json = json.loads(vulnerabilities_string)
    output_file_path = ast_json_file_path.split(".", 1)[0]
    output_file_path += '.output.json'
    with open(output_file_path, 'w') as outfile:
        json.dump(vulnerabilities_json, outfile)


def is_ascii(s):
    try:
        s.decode('ascii')
        return True
    except UnicodeDecodeError:
        return False


def print_vulnerabilities_to_json(vulnerabilities, file_path):
    vulnerabilties_str = '['

    for index, vulnerability in enumerate(vulnerabilities):
        vulnerabilties_str += json.dumps(vulnerability.__dict__)
        if(index < len(vulnerabilities) - 1):
            vulnerabilties_str += ','

    vulnerabilties_str += ']'

    output_file_path = file_path.split(".", 1)[0]
    output_file_path += '.output.json'
    with open(output_file_path, 'w') as formatted_file:
        formatted_file.write(vulnerabilties_str + '\n')


def run(file_path, vulnerability_patterns_file_path):
    # print("Analysing")

    # print("PATH: ", file_path)

    # TODO
    # Currently working by reading python slices
    # This is wrong
    # Need to work by reading AST from JSON
    tree = build_from_file(file_path)
    # print("TREE: ", tree)

    cfg = make_cfg(tree)
    print("CFG: ", cfg)

    FixedPointAnalysis(cfg)

    vulnerabilities = find_vulnerabilities(
        cfg, vulnerability_patterns_file_path)

    if vulnerabilities:
        print_vulnerabilities_to_json(vulnerabilities, file_path)
    else:
        print("There are no vulnerabilities")
    sys.exit()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "ast2json":
            convert_python_code_to_ast_json(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == "run":
            run(sys.argv[2], sys.argv[3])
    else:
        usage(sys.argv[0])
