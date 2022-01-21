"""
"""

from visitors import Visitor


class CleanAstVisitor(Visitor):


    def __init__(self, ast):
        self.ast = ast
        self.super = super(CleanAstVisitor, self)

    def visit_Assign(self, node):
        del node['col_offset']
        self.visit_Assign_targets(node['targets'])
        self.visit_Assign_value(node['value'])


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

        self.visit_Call_func(node['func'])
        self.visit_Call_args(node['args'])


    def visit_Expr(self, node):
        del node['col_offset']
        self.super.visit_Expr(node)


    def visit_BinOp(self, node):

        del node['col_offset']
        self.visit_operand(node['left'])
        self.visit_operand(node['right'])


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
        # del node['lineno']
        del node['ctx']

    def visit_Str(self, node):
        del node['col_offset']
        del node['lineno']

    def visit_Num(self, node):
        del node['col_offset']
        del node['lineno']
        self.visit_int(node['n'])
        node['n'] = node['n']['n_str']


    def visit_Break(self, node):
        del node['col_offset']


if __name__ == '__main__':
    from visitors import Driver
    Driver.print_ast(CleanAstVisitor)