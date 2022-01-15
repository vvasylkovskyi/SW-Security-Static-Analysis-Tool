from pathlib import Path

from utilities import load_json

def get_ast_types(*asts):
    ast_types = set()
    def f(d):
        for k,v in d.items():
            if k=="ast_type" and v not in ast_types:
                ast_types.add(v)
            elif isinstance(v, dict):
                f(v)
            elif isinstance(v, list):
                for e in v:
                    f(e)
    for p in asts:
        f(load_json(p))

    return ast_types

def generate_visitors(ast_types, framework=False):
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
    ast_types = get_ast_types(*sorted(asts))
    # print(ast_types)
    with file.open("w") as fp:
        fp.write(generate_visitors(ast_types, **kwargs))
    print(file)
    return


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("filename", type=str, help="filename for generated visitor")
    parser.add_argument("asts", type=str, nargs="+", help="list of Abstract Syntax Trees as json files to base the visitor upon")
    parser.add_argument("--framework", action='store_true', help="test a visitor defined below")
    args = parser.parse_args()
    main(Path(args.filename).with_suffix(".py"), *map(Path, args.asts), framework=args.framework)
