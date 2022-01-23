from pathlib import Path

from utilities import load_json


AST_TYPE = "ast_type"

def get_ast_types_enriched(ast, data):
    for k, v in ast.items():
        continue


def get_ast_types(ast, data):
    for k, v in ast.items():
        if k == AST_TYPE and v not in data:
            data.add(v)
        elif isinstance(v, dict):
            get_ast_types(v, data)
        elif isinstance(v, list):
            for e in v:
                get_ast_types(e, data)


def get_all_ast_types(*asts, func = get_ast_types, constructor = set ):
    data = constructor()
    for p in asts:
        func(load_json(p), data)
    return data


def generate_visitor(ast_types, class_name):
    t = f"""
from visitors import Visitor


class {class_name}(Visitor):

    def __init__(self, ast):
        super({class_name}, self).__init__(ast)
        self.super = super({class_name}, self)

"""

    for ast_type in ast_types:
        method = f"visit_{ast_type}"
        t += f"""
    def {method}(self, node):
        value = self.super.{method}(node)
        #process
        return value

"""

    return t


def generate_visitors(ast_types, framework=False, oop=""):
    t = ""
    for ast_type in ast_types:
        t += f'''
def visit_{ast_type}(node, **kwargs):
    """
    :param data:
    :return:
    """
    # key = "k"
    # return visit_nodes(node[key], **kwargs)
    # return visit_node(node[key], **kwargs)
    # return node[key]
    raise NotImplementedError(f"visitor for ast_type {ast_type} not implemented")
    '''
    #TODO add keys related to ast_type...

    if oop:
        return generate_visitor(ast_types, oop)

    if framework:
        t += """
def novisit(node, **kwargs):
    raise NotImplementedError(f"no visitor implemented for {node['ast_type']}")

def visit_node(node, **kwargs):
    # print(node);print()
    return ast_type_visitors[node['ast_type']](node, **kwargs)

def visit_nodes(nodes, **kwargs):
    return tuple(ast_type_visitors[node['ast_type']](node, **kwargs) for node in nodes)
    
from collections import defaultdict
ast_type_visitors = defaultdict(lambda : novisit)

implemented_ast_type_visitors = {
"""
        for ast_type in ast_types:
            t += f"    {repr(ast_type)}:visit_{ast_type},\n"
        t += """}
ast_type_visitors.update(implemented_ast_type_visitors) #not really until really
        """
    return t

def main(file, *asts, **kwargs):
    ast_types = get_all_ast_types(*asts)
    # print(ast_types)

    with file.open("w") as fp:
        fp.write(generate_visitors(sorted(ast_types), **kwargs))
    print(file)
    return


def generate_keys(*asts):
    ast_types = get_all_ast_types(*asts)
    t = f"""
class AstTypes:
    Key = {repr(AST_TYPE)}
    """
    for ast_type in sorted(ast_types):
        t += f"""
    class {ast_type}:
        Key = {repr(ast_type)}
"""

    print(t)


if __name__ == '__main__':
    import argparse
    import datetime
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("asts", type=str, nargs="+", help="list of Abstract Syntax Trees as json files to base the visitor upon")
    parser.add_argument("--filename", default=f"new_visitor_{datetime.datetime.now().timestamp()}", type=str, help="filename for generated visitor")
    parser.add_argument("--framework", action='store_true', help="include generic functions")
    parser.add_argument("--oop", type=str, default="", help="class with methods, example python3 generate_visitors.py pointers_visitor asts/* --oop PointersVisitor")
    parser.add_argument("--keys", type=str, default="", help="class with keys related to the ast types ast_type")

    args = parser.parse_args()
    if args.keys:
        generate_keys(*map(Path, args.asts))
    else:
        main(Path(args.filename).with_suffix(".py"), *map(Path, args.asts), framework=args.framework, oop=args.oop)