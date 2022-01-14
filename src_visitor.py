"""
Using the terms in the definition of the Python's AST module, the mandatory constructs are:
    Literals (Constant),
    Variables (Name),
    Expressions (Expr, BinOp, Compare, Call, Attribute),
    Statements (Assign),
    Control flow (If and While)
"""

from collections import defaultdict
import string

#TODO indentation level, how to

INDENTATION = "    "
indentation = ""

def novisit(data):
    raise NotImplementedError(f"no visitor implemented for {data['ast_type']}")

def visit_component(data):
    # print(data);print()
    return ast_type_visitors[data['ast_type']](data)

def visit_components(data, key):
    return tuple(ast_type_visitors[e['ast_type']](e) for e in data[key])

def visit_Module(data):
    """
    :param data: {
        'ast_type': 'Module',
        'body': [...]
    }
    :return:
    """

    return visit_components(data, 'body')

def visit_Assign(data):
    """
    :param data:
    :return:
    """
    targets = visit_components(data, 'targets')
    value = visit_component(data['value'])
    r = f"{','.join(targets)}={value}"
    return r

def visit_Name(data):
    """
    :param data: {
        'ast_type': 'Name',
        'col_offset': 2,
        'ctx': {'ast_type': 'Load'},
        'id': 'b',
        'lineno': 4
    }
    :return:
    """
    # alpha data['id']

    return data['id']

def visit_Str(data):
    """
    :param data: {'ast_type': 'Str', 'col_offset': 2, 'lineno': 1, 's': ''}
    :return:
    """
    return repr(data['s'])

def visit_Call(data):
    """
    :param data:
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
    args = visit_components(data, 'args')
    func = visit_component(data['func'])
    r = f"{func}({','.join(args)})"
    return r

def visit_Expr(data):
    """
    :param data:
    :return:
    """
    value = visit_component(data['value'])
    return value

def visit_BinOp(data):
    """
    :param data:
    :return:
    """
    left = visit_component(data['left'])
    right = visit_component(data['right'])
    op = visit_component(data['op'])
    representation = f"{left}{op}{right}"
    return representation

def visit_Add(data):
    """
    :param data:
    :return:
    """
    return '+'

def visit_If(data):
    """
    :param data:
    :return:
    """
    # indentation_level = data['col_offset']
    # col_offset = data['col_offset']
    global indentation
    old_indentation = indentation
    indentation = data['col_offset']*' '
    test = visit_component(data['test'])
    body = visit_components(data, 'body')
    representation = f"{indentation}if({test}):\n"
    orelse = visit_components(data, 'orelse')
    for l in body:
        indent = "" if any({l.lstrip().startswith("if"), l.lstrip().startswith("while")}) else indentation+INDENTATION
        representation += f"{indent}{l}\n"
    if orelse:
        representation += f"{indentation}else:\n"
        representation += "\n".join(f"{indentation+INDENTATION}{e}" for e in orelse)

    indentation = old_indentation
    return representation

def visit_Break(data):
    """
    :param data:
    :return:
    """
    # key = "k"
    # return data[key]
    return "break"


def visit_Store(data):
    """
    :param data:
    :return:
    """
    # key = "k"
    # return data[key]
    raise NotImplementedError(f"visitor for ast_type Store not implemented")


def visit_Compare(data):
    """
    :param data:
    :return:
    """
    left = visit_component(data['left'])
    comparators = visit_components(data, 'comparators')
    ops = visit_components(data, 'ops')
    representation = f"{left}{','.join(ops)}{','.join(comparators)}"
    return representation

def visit_Num(data):
    """
    :param data:
    :return:
    """
    return visit_component(data['n'])


def visit_NotEq(data):
    """
    :param data:
    :return:
    """
    return "!="


def visit_Load(data):
    """
    :param data:
    :return:
    """
    raise NotImplementedError(f"visitor for ast_type Load not implemented")


def visit_Eq(data):
    """
    :param data:
    :return:
    """
    return "=="


def visit_int(data):
    """
    :param data:
    :return:
    """
    key = "n_str"
    return data[key]


def visit_Gt(data):
    """
    :param data:
    :return:
    """
    return ">"


def visit_While(data):
    """
    :param data:
    :return:
    """
    global indentation
    old_indentation = indentation
    indentation = data['col_offset']*' '
    test = visit_component(data['test'])
    body = visit_components(data, 'body')
    representation = f"{indentation}while ({test}):\n"
    for l in body:
        indent = "" if any({l.lstrip().startswith("if"), l.lstrip().startswith("while")}) else indentation+INDENTATION
        representation += f"{indent}{l}\n"
    indentation = old_indentation
    return representation


def visit_Lt(data):
    """
    :param data:
    :return:
    """
    return "<"

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

