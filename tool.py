import sys
import json

from utils.parse_ast import make_ast 

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
    print(json_ast)
    with open(output_file_path, 'w') as outfile:
        json.dump(json_ast, outfile)

def analyse(ast_json_file_path, vulnerability_patterns_file_path):
    print("Analysing")
    print(ast_json_file_path)
    print(vulnerability_patterns_file_path)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "ast2json":
            convert_python_code_to_ast_json(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == "analyse":
            analyse(sys.argv[2], sys.argv[3])
    else:
        usage(sys.argv[0]) 
