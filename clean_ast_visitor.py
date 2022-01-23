"""
"""

from visitors import Visitor, AstTypes


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
            AstTypes.Module.type_ignores,
        )
        self.super.visit_Module(node)


    def visit_Assign(self, node):
        self.delete_keys(
            node, 
            AstTypes.Generic.end_lineno,
            AstTypes.Generic.col_offset,
            AstTypes.Generic.end_col_offset,
            AstTypes.Assign.type_comment
        )
        self.visit_Assign_targets(node[AstTypes.Assign.targets])
        self.visit_Assign_value(node[AstTypes.Assign.value])


    def visit_Call(self, node):
        keys = (
            AstTypes.Generic.end_lineno,
            AstTypes.Generic.col_offset,
            AstTypes.Generic.end_col_offset,
            AstTypes.Call.starargs,
            AstTypes.Call.kwargs,
            AstTypes.Call.keywords
        )
        self.delete_keys(node, *keys)

        self.visit_Call_func(node[AstTypes.Call.func])
        self.visit_Call_args(node[AstTypes.Call.args])


    def visit_Expr(self, node):
        self.delete_keys(
            node,
            AstTypes.Generic.end_lineno,
            AstTypes.Generic.col_offset,
            AstTypes.Generic.end_col_offset,
        )
        self.super.visit_Expr(node)


    def visit_BinOp(self, node):
        self.delete_keys(
            node,
            AstTypes.Generic.lineno,
            AstTypes.Generic.end_lineno,
            AstTypes.Generic.col_offset,
            AstTypes.Generic.end_col_offset,
        )

        self.visit_BinOp_operand(node[AstTypes.BinOp.left])
        self.visit_BinOp_operand(node[AstTypes.BinOp.right])


    def visit_While(self, node):
        self.delete_keys(
            node,
            AstTypes.Generic.end_lineno,
            AstTypes.Generic.col_offset,
            AstTypes.Generic.end_col_offset,
        )

        self.visit_If_test(node['test'])
        self.visit_body(node['body'])


    def visit_If(self, node):
        self.delete_keys(
            node,
            AstTypes.Generic.end_lineno,
            AstTypes.Generic.col_offset,
            AstTypes.Generic.end_col_offset,
        )

        self.visit_If_test(node['test'])
        self.visit_body(node['body'])
        self.visit_body(node['orelse'])


    def visit_Name(self, node):
        self.delete_keys(
            node,
            AstTypes.Generic.end_lineno,
            AstTypes.Generic.col_offset,
            AstTypes.Generic.end_col_offset,
            AstTypes.Name.ctx
        )


    def visit_Constant(self, node):
        self.delete_keys(
            node,
            AstTypes.Generic.lineno,
            AstTypes.Generic.end_lineno,
            AstTypes.Generic.col_offset,
            AstTypes.Generic.end_col_offset,
            AstTypes.Constant.kind
        )


    def visit_Break(self, node):
        self.delete_keys(
            node,
            AstTypes.Generic.end_lineno,
            AstTypes.Generic.col_offset,
            AstTypes.Generic.end_col_offset,
        )


if __name__ == '__main__':
    from visitors import Driver
    Driver.print_ast(CleanAstVisitor)