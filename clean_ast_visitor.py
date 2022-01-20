"""
"""
from pprint import pprint

from visitors import Visitor


class CleanAstVisitor(Visitor):


    def __init__(self, ast):
        self.ast = ast


    def visit_Assign(self, node):
        del node['col_offset']
        self.visit_Assign_targets(node)
        self.visit_Assign_value(node)


    def visit_Call(self, node):
        keys = (
            'col_offset',
            'starargs',
            'kwargs',
            'keywords'
        )
        for key in keys:
            del node[key]

        del node['lineno']

        # node['func'] = node['func']['id']
        self.visit_Call_func(node)
        self.visit_Call_args(node)


    def visit_Expr(self, node):
        del node['col_offset']
        self.visit_expression(node['value'])


    def visit_BinOp(self, node):

        del node['col_offset']
        # node['op'] = node['op']['ast_type']

        self.visit_operand(node['left'])
        self.visit_operand(node['right'])


    # def visit_Compare(self, node):
    #     # print(node.keys())
    #     # del node['ops'] # must be first due to recursion... can't explain much for now
    #
    #     self.visit_operand(node['left'])
    #
    #     for node in node['comparators']:
    #         self.visit_operand(node)


    def visit_While(self, node):
        del node['col_offset']

        self.visit_test(node['test'])
        self.visit_body(node['body'])


    def visit_If(self, node):
        del node['col_offset']

        self.visit_test(node['test'])
        self.visit_body(node['body'])
        self.visit_body(node['orelse'])


    def visit_Name(self, node):
        del node['col_offset']
        del node['lineno']
        del node['ctx']

    def visit_Str(self, node):
        del node['col_offset']
        del node['lineno']

    def visit_Num(self, node):
        del node['col_offset']
        del node['lineno']
        self.visit_int(node['n'])
        node['n'] = node['n']['n_str']

    # def visit_int(self, node):
    #     del node["n"]

    def visit_Break(self, node):
        del node['col_offset']


if __name__ == '__main__':
    from visitors import Driver
    Driver.print_ast(CleanAstVisitor)