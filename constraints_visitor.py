from collections import defaultdict, namedtuple
from utilities import greek_letters_lowercase

"""
x = y -> q_y <= q_x
do not taint x with y
"""
Constraint = namedtuple("Constraint", ("line", "lhs_tq", "lhs_id", "rhs_tq", "rhs_id"))
Constraint.__repr__ = lambda s:f"{s.line:>2}: {s.lhs_tq} <= {s.rhs_tq}"

class TypeQualifers:
    TAINTED = "tainted"
    UNTAINTED = "untainted"
    labels = greek_letters_lowercase


def novisit(node, **kwargs):
    raise NotImplementedError(f"no visitor implemented for {node['ast_type']}")


def visit_node(node, **kwargs):
    # print(node);print()
    # print(kwargs["constraints"])
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
    # print(kwargs)
    kwargs.update(dict(indentation_level=0, labels=filter(None, greek_letters_lowercase)))
    visit_nodes(node['body'], **kwargs)


def visit_Assign(node, **kwargs):
    """
    :param node:
    :return:
    """
    target_type_qualifier, target_id = visit_nodes(node['targets'], **kwargs)[0] #assume1
    kwargs["assignment_context"] = (target_type_qualifier, target_id) #for binops
    value = visit_node(node['value'], **kwargs)
    del kwargs["assignment_context"]
    # if value:
    #     value_type_qualifier, value_id = value
    #     kwargs["constraints"].append(Constraint(node["lineno"], value_type_qualifier, value_id, target_type_qualifier, target_id))


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
    # print(kwargs)
    name = node['id']
    if name in kwargs["labels_map"]:
        type_qualifier = kwargs["labels_map"][name]
    else:
        if name in kwargs["sources"]:
            type_qualifier = TypeQualifers.TAINTED
        elif name in kwargs["sanitizers"]:
            type_qualifier = TypeQualifers.UNTAINTED
        elif name in kwargs["sinks"]:
            type_qualifier = TypeQualifers.UNTAINTED  # sink can be a variable or a function, untainted might refer to the variabl or to the arguments of the function
        else:
            type_qualifier = next(kwargs["labels"])
        kwargs["labels_map"][name] = type_qualifier

    if "assignment_context" in kwargs:
        kwargs["constraints"].append(Constraint(node["lineno"], type_qualifier, name, *kwargs["assignment_context"]))

    # print(type_qualifier, name)
    return type_qualifier, name


def visit_Str(node, **kwargs):
    """
    :param node: {'ast_type': 'Str', 'col_offset': 2, 'lineno': 1, 's': ''}
    :return:
    """
    kwargs["labels_map"][node['s']] = TypeQualifers.UNTAINTED

    if "assignment_context" in kwargs:
        kwargs["constraints"].append(Constraint(node["lineno"], TypeQualifers.UNTAINTED, node["s"], *kwargs["assignment_context"]))

    return TypeQualifers.UNTAINTED, node['s']


def visit_Call(node, **kwargs):
    """
    :param node:
        {'args': [],
         'ast_type': 'Call',
         'col_offset': 2,
         'func': {'ast_type': 'Name',
                  'col_offset': 2,
                  'ctx': {'ast_type': 'Load'},
                  'id': 'c',w
                  'lineno': 2},
         'keywords': [],
         'kwargs': None,
         'lineno': 2,
         'starargs': None
        }
    :return:
    """
    func_tq, func_id = visit_node(node['func'], **kwargs)
    arg_type_qualifier = TypeQualifers.UNTAINTED if func_id in kwargs['sinks'] else TypeQualifers.TAINTED
    argc = len(node['args'])
    for i in range(argc):
        kwargs["assignment_context"]=(arg_type_qualifier, f"{func_id}_arg{i}")
        visit_node(node['args'][i], **kwargs) #to work for an argument which is a BinOp
        del kwargs["assignment_context"]
    # for i,(arg_tq, arg_name) in enumerate(args):
    #     kwargs["constraints"].append(Constraint(node['lineno'], arg_tq, arg_name, arg_type_qualifier, f"{func_id}_arg{i}"))

    return func_tq, func_id

def visit_Expr(node, **kwargs):
    """
    :param node:
    :return:
    """
    visit_node(node['value'], **kwargs)


def visit_BinOp(node, **kwargs):
    """
    :param node:
    :return:
    """
    #TODO what is needed here?
    left = visit_node(node['left'], **kwargs)
    right = visit_node(node['right'], **kwargs)
    # if "assignment_context" in kwargs:
    #     if left: #recursive binops
    #         kwargs["constraints"].append(Constraint(node["lineno"], *left, *kwargs["assignment_context"]))
    #     kwargs["constraints"].append(Constraint(node["lineno"], *right, *kwargs["assignment_context"]))

    # print("left", left)
    # print("right", right)
    # return

def visit_Compare(node, **kwargs):
    """
    :param node:
    :return:
    """
    left = visit_node(node['left'], **kwargs)
    comparators = visit_nodes(node['comparators'], **kwargs)
    ops = visit_nodes(node['ops'], **kwargs)


def visit_If(node, **kwargs):
    """
    :param node:
    :return:
    """
    # test = visit_node(node['test'], **kwargs)
    body = visit_nodes(node['body'], **kwargs)
    orelse = visit_nodes(node['orelse'], **kwargs)



def visit_While(node, **kwargs):
    """
    :param node:
    :return:
    """
    # test = visit_node(node['test'], **kwargs)
    body = visit_nodes(node['body'], **kwargs)


def visit_Break(node, **kwargs):
    """
    :param node:
    :return:
    """
    return


def visit_Add(node, **kwargs):
    """
    :param node:
    :return:
    """
    return


def visit_Num(node, **kwargs):
    """
    :param node:
    :return:
    """
    return visit_node(node['n'], lineno=node['lineno'], **kwargs)


def visit_NotEq(node, **kwargs):
    """
    :param node:
    :return:
    """
    return


def visit_Eq(node, **kwargs):
    """
    :param node:
    :return:
    """
    return


def visit_int(node, **kwargs):
    """
    :param node:
    :return:
    """
    kwargs["labels_map"][node['n_str']] = TypeQualifers.UNTAINTED

    if "assignment_context" in kwargs:
        kwargs["constraints"].append(Constraint(kwargs["lineno"], TypeQualifers.UNTAINTED, node["n_str"], *kwargs["assignment_context"]))

    return TypeQualifers.UNTAINTED, node["n_str"]


def visit_Gt(node, **kwargs):
    """
    :param node:
    :return:
    """
    return


def visit_Lt(node, **kwargs):
    """
    :param node:
    :return:
    """
    return

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


ast_type_visitors = defaultdict(lambda: novisit)

# not really until really
implemented_ast_type_visitors = {
    'Store': visit_Store,
    'Compare': visit_Compare,
    'If': visit_If,
    'NotEq': visit_NotEq,
    'Eq': visit_Eq,
    'Load': visit_Load,
    'Expr': visit_Expr,
    'Str': visit_Str,
    'Break': visit_Break,
    'Call': visit_Call,
    'Module': visit_Module,
    'BinOp': visit_BinOp,
    'Name': visit_Name,
    'While': visit_While,
    'Lt': visit_Lt,
    'Add': visit_Add,
    'Num': visit_Num,
    'Gt': visit_Gt,
    'int': visit_int,
    'Assign': visit_Assign,
}
ast_type_visitors.update(implemented_ast_type_visitors)