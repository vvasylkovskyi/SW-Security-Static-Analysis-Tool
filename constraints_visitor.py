from collections import namedtuple, defaultdict

from visitors import Visitor, AstTypes
from tf_visitor import TaintQualifer, CallArgKeys

"""
x = y -> q_y <= q_x
do not taint x with y
"""
Constraint = namedtuple(
    "Constraint", ("line", "lhs_tq", "lhs_id", "rhs_tq", "rhs_id"))
Constraint.__repr__ = lambda s: f"{s.line:>2}: {s.lhs_tq} <= {s.rhs_tq}"

# TODO FIX, previous working oop version not commited
# also consider mot repeating funcionality in similar visitor pf_sensitivity


class ConstraintsVisitor(Visitor):

    def __init__(self, ast):
        super(ConstraintsVisitor, self).__init__(ast)
        self.super = super(ConstraintsVisitor, self)
        self._constraints = list()

    @property
    def constraints(self):
        return self._constraints

    def visit_Assign_target(self, node):
        return (node[TaintQualifer.__name__], self.super.visit_Name(node))

    def visit_BinOp_operand(self, node):
        if node[AstTypes.Generic.ast_type] == AstTypes.BinOp.Key:
            return self.visit_BinOp_operand(node[AstTypes.BinOp.left]) + self.visit_BinOp_operand(node[AstTypes.BinOp.right])
        else:
            return self.super.visit_BinOp_operand(node)

    def visit_Assign_value(self, node):
        if node[AstTypes.Generic.ast_type] == AstTypes.BinOp.Key:
            return self.visit_BinOp_operand(node[AstTypes.BinOp.left]) + self.visit_BinOp_operand(node[AstTypes.BinOp.right])
        else:
            return self.super.visit_Assign_value(node)

    def visit_Assign(self, node):

        values = self.visit_Assign_value(node['value'])

        targets = self.visit_Assign_targets(node['targets'])
        # if len(targets) > 1: ...
        # assume1 for now, how to treat value
        target_taint_qualifier, target_id = targets[0]

        for taint_qualifier, name in values:
            constraint = Constraint(
                node["lineno"], taint_qualifier, name, target_taint_qualifier, target_id)
            self._constraints.append(constraint)

    def visit_Call_arg(self, node):
        if node[AstTypes.Generic.ast_type] == AstTypes.BinOp.Key:
            return self.visit_BinOp_operand(node[AstTypes.BinOp.left]) + self.visit_BinOp_operand(node[AstTypes.BinOp.right])
        else:
            return self.super.visit_Call_arg(node)

    def visit_Call_arg_as_parameter(self, node):
        return (node[CallArgKeys.Call_arg_TaintQualifer], node[CallArgKeys.Call_arg])

    def visit_Call_args(self, nodes, lineno):
        for node in nodes:
            arg_taint_qualifier, arg = self.visit_Call_arg_as_parameter(node)
            values = self.visit_Call_arg(node)  # >1 if BinOp
            for taint_qualifier, name in values:
                constraint = Constraint(
                    lineno, taint_qualifier, name, arg_taint_qualifier, arg)
                self._constraints.append(constraint)

    def visit_Call_func(self, node):
        return (node['lineno'], node[TaintQualifer.__name__], self.super.visit_Name(node))

    def visit_Call(self, node):
        lineno, taint_qualifier, name = self.visit_Call_func(node['func'])
        self.visit_Call_args(node['args'], lineno)
        return (taint_qualifier, name)

    def visit_Name(self, node):
        return (node[TaintQualifer.__name__], self.super.visit_Name(node))

    def visit_Constant(self, node):
        return (node[TaintQualifer.__name__], self.super.visit_Constant(node))
