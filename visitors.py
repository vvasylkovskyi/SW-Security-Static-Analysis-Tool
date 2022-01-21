"""
"""
from pprint import pprint


class Visitor:

    INDENTATION = "    "

    def __init__(self, ast):
        self.ast = ast



    def visit_ast(self):
        return self.visit_Module(self.ast)


    def visit_Module(self, node):
        """
        :param node: {
            'ast_type': 'Module',
            'body': [...]
        }
        :return:
        """
        return self.visit_body(node['body'])


    def visit_body(self, nodes):
        visits = list()
        for node in nodes:
            ast_type = node['ast_type']
            if ast_type == 'Expr':
                visits.append(self.visit_Expr(node))
            elif ast_type == 'Assign':
                visits.append(self.visit_Assign(node))
            elif ast_type == 'While':
                visits.append(self.visit_While(node))
            elif ast_type == 'If':
                visits.append(self.visit_If(node))
        return visits



    def visit_ops(self, node):
        ops = list()
        for node in node['ops']:
            ast_type = node['ast_type']
            if ast_type == 'NotEq':
                ops.append(self.visit_NotEq(node))
            elif ast_type == 'Eq':
                ops.append(self.visit_Eq(node))
            elif ast_type == 'Gt':
                ops.append(self.visit_Gt(node))
            elif ast_type == 'Lt':
                ops.append(self.visit_Lt(node))
        return ops


    def visit_test(self, node):
        return {
            'Compare': self.visit_Compare,
            'Expr': self.visit_Expr,
            'Name': self.visit_Name,
            'BinOp': self.visit_BinOp,
            'Str': self.visit_Str,
            'Num': self.visit_Num
        }[node['ast_type']](node)


    def visit_expression(self, node):
        """
        :param node:
        :return:
        """
        ast_type = node['ast_type']
        if ast_type == 'Call':
            expression = self.visit_Call(node)
        elif ast_type == 'BinOp':
            expression = self.visit_BinOp(node)
        elif ast_type == 'Name':
            expression = self.visit_Name(node)
        elif ast_type == 'Str':
            expression = self.visit_Str(node)
        elif ast_type == 'Num':
            expression = self.visit_Num(node)
        return expression


    def visit_Assign_target(self, node):
        return self.visit_Name(node)


    def visit_Assign_targets(self, nodes):
        return tuple(self.visit_Assign_target(node) for node in nodes)


    def visit_Assign_value(self, node):
        ast_type = node['ast_type']
        if ast_type == 'Str':
            return self.visit_Str(node)
        elif ast_type == 'Num':
            return self.visit_Num(node)
        elif ast_type == 'Name':
            return self.visit_Name(node)
        elif ast_type == 'Call':
            return self.visit_Call(node)
        elif ast_type == 'BinOp':
            return self.visit_BinOp(node)


    def visit_Assign(self, node):
        """
        :param node:
        :return:
        """
        targets = self.visit_Assign_targets(node['targets'])
        value = self.visit_Assign_value(node['value'])
        return targets, value


    def visit_Call_func(self, node):
        """
        :param node: {'ast_type': 'Name',
                      'col_offset': 2,
                      'ctx': {'ast_type': 'Load'},
                      'id': 'c',
                      'lineno': 2}
        :return:
        """
        return self.visit_Name(node)


    def visit_Call_arg(self, node):
        ast_type = node['ast_type']
        if ast_type == 'Str':
            arg = self.visit_Str(node)
        elif ast_type == 'Num':
            arg = self.visit_Num(node)
        elif ast_type == 'Name':
            arg = self.visit_Name(node)
        elif ast_type == 'Call':
            arg = self.visit_Call(node)
        elif ast_type == 'BinOp':
            arg =  self.visit_BinOp(node)
        return arg


    def visit_Call_args(self, nodes):
        return list(self.visit_Call_arg(node) for node in nodes)


    def visit_Call(self, node):
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
        func = self.visit_Call_func(node['func'])
        
        args = self.visit_Call_args(node['args'])

        return func, args


    def visit_Expr(self, node):
        """
        :param node:
        :return:
        """
        value = self.visit_expression(node['value'])

        return value


    def visit_operand(self, node):
        return {
            # 'Expr': self.visit_Expr,
            'Call': self.visit_Call,
            'Name': self.visit_Name,
            'BinOp': self.visit_BinOp,
            'Str': self.visit_Str,
            'Num': self.visit_Num
        }[node['ast_type']](node)


    def visit_BinOp_operand(self, node):
        ast_type = node['ast_type']
        if ast_type == 'Str':
            return self.visit_Str(node)
        elif ast_type == 'Num':
            return self.visit_Num(node)
        elif ast_type == 'Name':
            return self.visit_Name(node)
        elif ast_type == 'Call':
            return self.visit_Call(node)
        elif ast_type == 'BinOp':
            return self.visit_BinOp(node)

    def visit_BinOp(self, node):
        """
        :param node:
        :return:
        """
        left = self.visit_BinOp_operand(node['left'])

        op = {
            'Add': self.visit_Add,
            'Sub': self.visit_Sub
        }[node['op']['ast_type']](node['op'])
        
        right = self.visit_BinOp_operand(node['right'])

        return (left, op, right)


    def visit_Compare(self, node):
        """
        :param node:
        :return:
        """
        left = self.visit_operand(node['left'])

        comparators = list(self.visit_operand(node) for node in node['comparators'])

        ops = self.visit_ops(node)

        return (left, ops, comparators)


    def visit_While(self, node):
        """
        :param node:
        :return:
        """
        test = self.visit_test(node['test'])
        body = self.visit_body(node['body'])
        return test, body


    def visit_If(self, node):
        """
        :param node:
        :return:
        """
        test = self.visit_test(node['test'])
        body = self.visit_body(node['body'])
        orelse = self.visit_body(node['orelse'])
        return test, body, orelse


    def visit_Name(self, node):
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
        return node['id']

    def visit_Str(self, node):
        """
        :param node: {'ast_type': 'Str', 'col_offset': 2, 'lineno': 1, 's': ''}
        :return:
        """
        return repr(node['s'])


    def visit_Num(self, node):
        """
        :param node:
            {
                                "ast_type": "Num",
                                "col_offset": 9,
                                "lineno": 3,
                                "n": {
                                    "ast_type": "int",
                                    "n": 3,
                                    "n_str": "3"
                                }
                            }
        :return:
        """
        return self.visit_int(node['n'])


    def visit_int(self, node):
        """
        :param node: {
                                    "ast_type": "int",
                                    "n": 3,
                                    "n_str": "3"
                                }
        :return:
        """
        return node["n_str"]


    def visit_Break(self, node):
        """
        :param node:
        :return:
        """
        return "break"


    def visit_Continue(self, node):
        """
        :param node:
        :return:
        """
        return "continue"


    def visit_Add(self, node):
        """
        :param node:
        :return:
        """
        return '+'


    def visit_Sub(self, node):
        """
        :param node:
        :return:
        """
        return '-'


    def visit_NotEq(self, node):
        """
        :param node:
        :return:
        """
        return "!="


    def visit_Eq(self, node):
        """
        :param node:
        :return:
        """
        return "=="


    def visit_Gt(self, node):
        """
        :param node:
        :return:
        """
        return ">"


    def visit_Lt(self, node):
        """
        :param node:
        :return:
        """
        return "<"


    def visit_Load(self, node):
        """
        :param node:
        :return:
        """
        raise NotImplementedError(f"visitor for ast_type Load not implemented")


    def visit_Store(self, node):
        """
        :param node:
        :return:
        """
        # key = "k"
        # return node[key]
        raise NotImplementedError(f"visitor for ast_type Store not implemented")


class Driver:
    @staticmethod
    def parser():
        import argparse
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("asts", type=str, nargs='+',
                            help="path of a JSON file containing the program slice to analyse, represented in the form of an Abstract Syntax Tree")
        return parser

    @staticmethod
    def get_asts():
        from utilities import load_json
        from pathlib import Path
        args = Driver.parser().parse_args()
        asts = dict()
        for ast in args.asts:
            p = Path(ast)
            asts[p] = load_json(p)
        return asts

    @staticmethod
    def print_visit(visitor):
        for p, ast in Driver.get_asts().items():
            print(p)
            print(visitor(ast).visit_ast())

    @staticmethod
    def print_ast(visitor):
        for p, ast in Driver.get_asts().items():
            print(p)
            visitor(ast).visit_ast()
            pprint(ast)


if __name__ == '__main__':
    Driver.drive(Visitor)