"""
"""


class AstTypes:

    class Generic:
        ast_type = 'ast_type'
        lineno = 'lineno'
        end_lineno = 'end_lineno'
        col_offset = 'col_offset'
        end_col_offset = 'end_col_offset'

    class Add:
        Key = 'Add'

    class Assign:
        Key = 'Assign'
        targets = 'targets'
        value = 'value'
        type_comment = 'type_comment'

    class BinOp:
        Key = 'BinOp'
        left = 'left'
        op = 'op'
        right = 'right'

    class Break:
        Key = 'Break'

    class Call:
        Key = 'Call'
        func = 'func'
        args = 'args'
        starargs = 'starargs'
        kwargs = 'kwargs'
        keywords = 'keywords'

    class Compare:
        Key = 'Compare'
        left = 'left'
        comparators = 'comparators'
        ops = 'ops'

    class Constant:
        Key = 'Constant'
        kind = 'kind'
        value = 'value'

    class Eq:
        Key = 'Eq'

    class Expr:
        Key = 'Expr'
        value = 'value'

    class Gt:
        Key = 'Gt'

    class If:
        Key = 'If'
        test = 'test'
        body = 'body'
        orelse = 'orelse'

    class Load:
        Key = 'Load'

    class Lt:
        Key = 'Lt'

    class Module:
        Key = 'Module'
        type_ignores = 'type_ignores'
        body = 'body'

    class Name:
        Key = 'Name'
        ctx = 'ctx'
        id = 'id'

    class NotEq:
        Key = 'NotEq'

    class Store:
        Key = 'Store'

    class While:
        Key = 'While'
        test = 'test'
        body = 'body'
        orelse = 'orelse'


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

    def visit_body_line(self, node):
        ast_type = node[AstTypes.Generic.ast_type]
        if ast_type == AstTypes.Expr.Key:
            return self.visit_Expr(node)
        elif ast_type == AstTypes.Assign.Key:
            return self.visit_Assign(node)
        elif ast_type == AstTypes.If.Key:
            return self.visit_If(node)
        elif ast_type == AstTypes.While.Key:
            # print("RETURNING HERE: ", )
            return self.visit_While(node)
        elif ast_type == AstTypes.Break.Key:
            return self.visit_Break(node)

    def visit_body(self, nodes):
        return tuple(self.visit_body_line(node) for node in nodes)

    def visit_Compare_ops_op(self, node):
        ast_type = node[AstTypes.Generic.ast_type]
        if ast_type == AstTypes.NotEq.Key:
            op = self.visit_NotEq(node)
        elif ast_type == AstTypes.Eq.Key:
            op = self.visit_Eq(node)
        elif ast_type == AstTypes.Gt.Key:
            op = self.visit_Gt(node)
        elif ast_type == AstTypes.Lt.Key:
            op = self.visit_Lt(node)
        return op

    def visit_Compare_ops(self, nodes):
        return tuple(self.visit_Compare_ops_op(node) for node in nodes)

    def visit_If_test(self, node):
        return {
            AstTypes.Compare.Key: self.visit_Compare,
            AstTypes.Expr.Key: self.visit_Expr,
            AstTypes.Name.Key: self.visit_Name,
            AstTypes.BinOp.Key: self.visit_BinOp,
            AstTypes.Constant.Key: self.visit_Constant
        }[node[AstTypes.Generic.ast_type]](node)

    def visit_Assign_target(self, node):
        return self.visit_Name(node)

    def visit_Assign_targets(self, nodes):
        return tuple(self.visit_Assign_target(node) for node in nodes)

    def visit_Assign_value(self, node):
        ast_type = node[AstTypes.Generic.ast_type]
        if ast_type == AstTypes.Constant.Key:
            return self.visit_Constant(node)
        elif ast_type == AstTypes.Name.Key:
            return self.visit_Name(node)
        elif ast_type == AstTypes.Call.Key:
            return self.visit_Call(node)
        elif ast_type == AstTypes.BinOp.Key:
            return self.visit_BinOp(node)

    def visit_Assign(self, node):
        """
        :param node:
        :return:
        """
        value = self.visit_Assign_value(node[AstTypes.Assign.value])
        targets = self.visit_Assign_targets(node[AstTypes.Assign.targets])
        return targets, value

    def visit_Call_func(self, node):
        """
        :param node: {
            'ast_type': 'Name',
            'col_offset': 2,
            'ctx': {'ast_type': 'Load'},
            'id': 'c',
            'lineno': 2
            }
        :return:
        """
        return self.visit_Name(node)

    def visit_Call_arg(self, node):
        ast_type = node[AstTypes.Generic.ast_type]
        if ast_type == AstTypes.Constant.Key:
            return self.visit_Constant(node)
        elif ast_type == AstTypes.Name.Key:
            arg = self.visit_Name(node)
        elif ast_type == AstTypes.Call.Key:
            arg = self.visit_Call(node)
        elif ast_type == AstTypes.BinOp.Key:
            arg = self.visit_BinOp(node)
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
        func = self.visit_Call_func(node[AstTypes.Call.func])

        args = self.visit_Call_args(node[AstTypes.Call.args])
        return func, args

    def visit_Expr_value(self, node):
        ast_type = node[AstTypes.Generic.ast_type]
        if ast_type == AstTypes.Call.Key:
            return self.visit_Call(node)
        elif ast_type == AstTypes.BinOp.Key:
            return self.visit_BinOp(node)
        elif ast_type == AstTypes.Name.Key:
            return self.visit_Name(node)
        elif ast_type == AstTypes.Constant.Key:
            return self.visit_Constant(node)

    def visit_Expr(self, node):
        """
        :param node:
        :return:
        """
        return self.visit_Expr_value(node[AstTypes.Expr.value])

    def visit_BinOp_operand(self, node):
        ast_type = node[AstTypes.Generic.ast_type]
        if ast_type == AstTypes.Constant.Key:
            return self.visit_Constant(node)
        elif ast_type == AstTypes.Name.Key:
            return self.visit_Name(node)
        elif ast_type == AstTypes.Call.Key:
            return self.visit_Call(node)
        elif ast_type == AstTypes.BinOp.Key:
            return self.visit_BinOp(node)

    def visit_BinOp_op(self, node):
        ast_type = node[AstTypes.Generic.ast_type]
        if ast_type == AstTypes.Add.Key:
            return self.visit_Add(node)
        else:
            raise NotImplementedError

    def visit_BinOp(self, node):
        """
        :param node:
        :return:
        """
        left = self.visit_BinOp_operand(node[AstTypes.BinOp.left])

        op = self.visit_BinOp_op(node[AstTypes.BinOp.op])

        right = self.visit_BinOp_operand(node[AstTypes.BinOp.right])

        return (left, op, right)

    def visit_Compare_operand(self, node):
        return {
            AstTypes.Call.Key: self.visit_Call,
            AstTypes.Name.Key: self.visit_Name,
            AstTypes.BinOp.Key: self.visit_BinOp,
            AstTypes.Constant.Key: self.visit_Constant
        }[node[AstTypes.Generic.ast_type]](node)

    def visit_Compare_comparators(self, nodes):
        return tuple(self.visit_Compare_operand(node) for node in nodes)

    def visit_Compare(self, node):
        """
        :param node:
        :return:
        """
        left = self.visit_Compare_operand(node[AstTypes.Compare.left])

        comparators = self.visit_Compare_comparators(
            node[AstTypes.Compare.comparators])

        ops = self.visit_Compare_ops(node[AstTypes.Compare.ops])

        return (left, ops, comparators)

    def visit_While(self, node):
        """
        :param node:
        :return:
        """
        print("HERE")
        test = self.visit_If_test(node[AstTypes.While.test])
        body = self.visit_body(node[AstTypes.While.body])
        # orelse = self.visit_body(node['orelse']) #TODO propagate to other visitors...
        print("HERE RETURN BODY: ", body)
        return test, body

    def visit_If(self, node):
        """
        :param node:
        :return:
        """
        test = self.visit_If_test(node[AstTypes.If.test])
        body = self.visit_body(node[AstTypes.If.body])
        orelse = self.visit_body(node[AstTypes.If.orelse])
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
        return node[AstTypes.Name.id]

    def visit_Constant(self, node):
        """
        """
        return repr(node[AstTypes.Constant.value])

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
        raise NotImplementedError(
            f"visitor for ast_type Store not implemented")


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
        from pprint import pprint
        for p, ast in Driver.get_asts().items():
            print(p)
            visitor(ast).visit_ast()
            pprint(ast)


if __name__ == '__main__':
    Driver.drive(Visitor)
