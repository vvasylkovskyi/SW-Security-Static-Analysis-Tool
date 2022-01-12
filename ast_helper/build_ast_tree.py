import ast
import os


def build_ast_tree(file_path):
    """Generate an Abstract Syntax Tree using the ast module."""
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            return ast.parse(f.read())
    raise IOError('Input needs to be a file. Path: ' + file_path)


def build_from_src(src):
    """
    Build a CFG from some Python source code.
    Args:
        name: The name of the CFG being built.
        src: A string containing the source code to build the CFG from.
    Returns:
        The CFG produced from the source code.
    """
    tree = ast.parse(src, mode='exec')
    return tree


def build_from_file(filepath):
    """
    Build a CFG from some Python source file.
    Args:
        name: The name of the CFG being built.
        filepath: The path to the file containing the Python source code
                    to build the CFG from.
    Returns:
        The CFG produced from the source file.
    """
    with open(filepath, 'r') as src_file:
        src = src_file.read()
        return build_from_src(src)
