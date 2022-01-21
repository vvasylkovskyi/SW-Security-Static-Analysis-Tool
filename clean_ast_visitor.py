"""
"""

from visitors import Visitor


class CleanAstVisitor(Visitor):


    def __init__(self, ast):
        self.ast = ast
        self.super = super(CleanAstVisitor, self)

    
    def delete_keys(self, node, *keys):
        for key in keys:
            if key in node:
                del node[key]


    def visit_Module(self, node):
        self.delete_keys(
            node,
            'type_ignores',
        )
        self.super.visit_Module(node)


    def visit_Assign(self, node):
        self.delete_keys(
            node, 
            'end_lineno',
            'col_offset',
            'end_col_offset',
            "type_comment"
        )
        self.visit_Assign_targets(node['targets'])
        self.visit_Assign_value(node['value'])


    def visit_Call(self, node):
        keys = (
            'end_lineno',
            'col_offset',
            'end_col_offset',
            'starargs',
            'kwargs',
            'keywords'
        )
        self.delete_keys(node, *keys)

        self.visit_Call_func(node['func'])
        self.visit_Call_args(node['args'])


    def visit_Expr(self, node):
        self.delete_keys(
            node,
            'end_lineno',
            'col_offset',
            'end_col_offset'
        )
        self.super.visit_Expr(node)


    def visit_BinOp(self, node):
        self.delete_keys(
            node,
            'lineno',
            'end_lineno',
            'col_offset',
            'end_col_offset'
        )

        self.visit_BinOp_operand(node['left'])
        self.visit_BinOp_operand(node['right'])


    def visit_While(self, node):
        self.delete_keys(
            node,
            'end_lineno',
            'col_offset',
            'end_col_offset'
        )

        self.visit_test(node['test'])
        self.visit_body(node['body'])


    def visit_If(self, node):
        self.delete_keys(
            node,
            'end_lineno',
            'col_offset',
            'end_col_offset'
        )

        self.visit_test(node['test'])
        self.visit_body(node['body'])
        self.visit_body(node['orelse'])


    def visit_Name(self, node):
        self.delete_keys(
            node,
            'end_lineno',
            'col_offset',
            'end_col_offset',
            'ctx'
        )


    def visit_Str(self, node):
        self.delete_keys(
            node,
            'lineno',
            'end_lineno',
            'col_offset',
            'end_col_offset',
            'kind'
        )


    def visit_Num(self, node):
        self.delete_keys(
            node,
            'lineno',
            'end_lineno',
            'col_offset',
            'end_col_offset',
            'kind'
        )
        self.visit_int(node['n'])
        node['n'] = node['n']['n_str']


    def visit_Constant(self, node):
        self.delete_keys(
            node,
            'lineno',
            'end_lineno',
            'col_offset',
            'end_col_offset',
            'kind'
        )


    def visit_Break(self, node):
        self.delete_keys(
            node,
            'end_lineno',
            'col_offset',
            'end_col_offset'
        )


if __name__ == '__main__':
    from visitors import Driver
    Driver.print_ast(CleanAstVisitor)