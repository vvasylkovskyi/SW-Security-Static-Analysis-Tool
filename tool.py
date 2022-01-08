import sys
import json
import os
import ast
from ast_helper.parse_ast import make_ast
from vulnerabilities import find_vulnerabilities
from cfg import make_cfg
from ast_helper.build_ast_tree import build_ast_tree
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


def is_python_module(path):
    if os.path.splitext(path)[1] == '.py':
        return True
    return False


local_modules = list()


def get_directory_modules(directory):

    if not os.path.isdir(directory):
        directory = os.path.dirname(directory)

    if directory == '':
        return local_modules

    if local_modules and os.path.dirname(local_modules[0][1]) == directory:
        return local_modules

    for path in os.listdir(directory):
        if is_python_module(path):
            module_name = os.path.splitext(path)[0]
            local_modules.append((module_name, os.path.join(directory, path)))

    return local_modules


def get_python_modules(path):
    module_root = os.path.split(path)[1]
    modules = list()
    for root, directories, filenames in os.walk(path):
        for filename in filenames:
            if is_python_module(filename):
                directory = os.path.dirname(os.path.realpath(os.path.join(
                    root, filename))).split(module_root)[-1].replace(os.sep, '.')
                directory = directory.replace('.', '', 1)
                if directory:
                    modules.append(('.'.join((module_root, directory, filename.replace(
                        '.py', ''))), os.path.join(root, filename)))
                else:
                    modules.append(('.'.join((module_root, filename.replace(
                        '.py', ''))), os.path.join(root, filename)))

    return modules


def get_project_module_names(path):
    project_modules = get_python_modules(path)
    project_module_names = list()
    for project_module in project_modules:
        project_module_names.append(project_module[0])
    return project_module_names


def is_directory(path):
    if os.path.isdir(path):
        return True
    elif is_python_module(path):
        return False
    raise Exception(path, ' has to be a python module or a directory.')


def analyse(file_path, vulnerability_patterns_file_path):
    print("Analysing")

    # path = os.path.normpath(file_path)

    print("PATH: ", file_path)

    directory = os.path.dirname(file_path)
    project_modules = get_python_modules(directory)
    local_modules = get_directory_modules(directory)
    allow_local_directory_imports = True

    tree = build_ast_tree(file_path)
    print("TREE: ", ast.dump(tree))

    cfg = make_cfg(tree, project_modules, local_modules,
                   file_path, allow_local_directory_imports)

    # vulnerabilities_string = find_vulnerabilities()
    # write_output_result(vulnerabilities_string, file_path)
    # sys.exit()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "ast2json":
            convert_python_code_to_ast_json(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == "analyse":
            analyse(sys.argv[2], sys.argv[3])
    else:
        usage(sys.argv[0])
