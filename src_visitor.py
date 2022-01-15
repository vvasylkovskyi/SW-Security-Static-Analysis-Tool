"""
Using the terms in the definition of the Python's AST module, the mandatory constructs are:
    Literals (Constant),
    Variables (Name),
    Expressions (Expr, BinOp, Compare, Call, Attribute),
    Statements (Assign),
    Control flow (If and While)
"""

from collections import defaultdict

#TODO indentation level, how to

INDENTATION = "    "

def novisit(node, **kwargs):
    raise NotImplementedError(f"no visitor implemented for {node['ast_type']}")

def visit_node(node, **kwargs):
    # print(node);print()
    return ast_type_visitors[node['ast_type']](node, **kwargs)

def visit_nodes(nodes, **kwargs):
    return tuple(ast_type_visitors[e['ast_type']](e, **kwargs) for e in nodes)

def visit_Module(node, **kwargs):
    """
    :param node: {
        'ast_type': 'Module',
        'body': [...]
    }
    :return:
    """
    return visit_nodes(node['body'], indentation_level=0)

def visit_Assign(node, **kwargs):
    """
    :param node:
    :return:
    """
    
    targets = visit_nodes(node['targets'], **kwargs)
    value = visit_node(node['value'], **kwargs)
    # r = f"{','.join(targets)}={value}"
    r = f"{kwargs['indentation_level']*INDENTATION}{','.join(targets)}={value}"
    return r


def visit_Name(node, **kwargs):
    """
    :param node: {
        'ast_type': 'Name',
        'col_offset': 2,
        'ctx': {'ast_type': 'Load'},
        'id': 'b',
        'lineno': 4
    }
    :return:
    """
    # alpha node['id']
    return node['id']


def visit_Str(node, **kwargs):
    """
    :param node: {'ast_type': 'Str', 'col_offset': 2, 'lineno': 1, 's': ''}
    :return:
    """
    return repr(node['s'])


def visit_Call(node, **kwargs):
    """
    :param node:
        {'args': [],
         'ast_type': 'Call',
         'col_offset': 2,
         'func': {'ast_type': 'Name',
                  'col_offset': 2,
                  'ctx': {'ast_type': 'Load'},
                  'id': 'c',
                  'lineno': 2},
         'keywords': [],
         'kwargs': None,
         'lineno': 2,
         'starargs': None
        }
    :return:
    """
    args = visit_nodes(node['args'], **kwargs)
    func = visit_node(node['func'], **kwargs)
    r = f"{func}({','.join(args)})"
    return r


def visit_Expr(node, **kwargs):
    """
    :param node:
    :return:
    """
    
    value = visit_node(node['value'], **kwargs)
    return f"{kwargs['indentation_level']*INDENTATION}{value}"


def visit_BinOp(node, **kwargs):
    """
    :param node:
    :return:
    """
    left = visit_node(node['left'], **kwargs)
    right = visit_node(node['right'], **kwargs)
    op = visit_node(node['op'], **kwargs)
    representation = f"{left}{op}{right}"
    return representation


def visit_Compare(node, **kwargs):
    """
    :param node:
    :return:
    """
    left = visit_node(node['left'], **kwargs)
    comparators = visit_nodes(node['comparators'], **kwargs)
    ops = visit_nodes(node['ops'], **kwargs)
    representation = f"{left}{','.join(ops)}{','.join(comparators)}"
    return representation


def visit_If(node, **kwargs):
    """
    :param node:
    :return:
    """

    test = visit_node(node['test'], **kwargs)

    indentation_level = kwargs['indentation_level']
    indentation = indentation_level * INDENTATION

    representation = f"{indentation}if({test}):\n"

    body = visit_nodes(node['body'], indentation_level=indentation_level+1)
    representation += "\n".join(body)

    orelse = visit_nodes(node['orelse'], indentation_level=indentation_level+1)

    if orelse:
        representation += f"\n{indentation}else:\n"
        representation += "\n".join(orelse)

    return representation


def visit_While(node, **kwargs):
    """
    :param node:
    :return:
    """
    indentation_level = kwargs['indentation_level']
    indentation = indentation_level * INDENTATION

    test = visit_node(node['test'], **kwargs)
    body = visit_nodes(node['body'], indentation_level=indentation_level+1)

    representation = f"{indentation}while ({test}):\n"
    representation += "\n".join(body)

    return representation


def visit_Break(node, **kwargs):
    """
    :param node:
    :return:
    """
    return f"{kwargs['indentation_level'] * INDENTATION}break"


def visit_Add(node, **kwargs):
    """
    :param node:
    :return:
    """
    return '+'


def visit_Num(node, **kwargs):
    """
    :param node:
    :return:
    """
    return visit_node(node['n'], **kwargs)


def visit_NotEq(node, **kwargs):
    """
    :param node:
    :return:
    """
    return "!="


def visit_Eq(node, **kwargs):
    """
    :param node:
    :return:
    """
    return "=="


def visit_int(node, **kwargs):
    """
    :param node:
    :return:
    """
    key = "n_str"
    return node[key]


def visit_Gt(node, **kwargs):
    """
    :param node:
    :return:
    """
    return ">"


def visit_Lt(node, **kwargs):
    """
    :param node:
    :return:
    """
    return "<"


def visit_Load(node, **kwargs):
    """
    :param node:
    :return:
    """
    raise NotImplementedError(f"visitor for ast_type Load not implemented")


def visit_Store(node, **kwargs):
    """
    :param node:
    :return:
    """
    # key = "k"
    # return node[key]
    raise NotImplementedError(f"visitor for ast_type Store not implemented")


ast_type_visitors = defaultdict(lambda : novisit)

#not really until really
implemented_ast_type_visitors = {
    'Store':visit_Store,
    'Compare':visit_Compare,
    'If':visit_If,
    'NotEq':visit_NotEq,
    'Eq':visit_Eq,
    'Load':visit_Load,
    'Expr':visit_Expr,
    'Str':visit_Str,
    'Break':visit_Break,
    'Call':visit_Call,
    'Module':visit_Module,
    'BinOp':visit_BinOp,
    'Name':visit_Name,
    'While':visit_While,
    'Lt':visit_Lt,
    'Add':visit_Add,
    'Num':visit_Num,
    'Gt':visit_Gt,
    'int':visit_int,
    'Assign':visit_Assign,
}
ast_type_visitors.update(implemented_ast_type_visitors)