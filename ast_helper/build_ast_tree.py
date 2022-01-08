import ast
import os


def build_ast_tree(file_path):
    """Generate an Abstract Syntax Tree using the ast module."""
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            return ast.parse(f.read())
    raise IOError('Input needs to be a file. Path: ' + file_path)
