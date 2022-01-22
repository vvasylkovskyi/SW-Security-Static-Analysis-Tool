from collections import namedtuple, defaultdict

from ps_visitor import Keys as PSKeys
from ssa_visitor import Keys as SSAKeys
from visitors import Visitor
from tf_visitor import TaintQualifer, CallArgKeys

"""
x = y -> q_y <= q_x
do not taint x with y
"""
Constraint = namedtuple("Constraint", ("line", "lhs_tq", "lhs_id", "rhs_tq", "rhs_id"))
Constraint.__repr__ = lambda s:f"{s.line:>2}: {s.lhs_tq} <= {s.rhs_tq}"


class Keys(PSKeys, SSAKeys):
    pass

class ConstraintsPathFlowSenstivityVisitor(Visitor):

    def __init__(self, ast):
        super(ConstraintsPathFlowSenstivityVisitor, self).__init__(ast)
        self.super = super(ConstraintsPathFlowSenstivityVisitor, self)
        self._constraints = defaultdict(list)
        self._scope = None


    @property
    def constraints(self):
        return self._constraints


    def visit_body_line(self, node):
        self._scope = tuple(node[Keys.CONDITIONS])
        return self.super.visit_body_line(node)


    def visit_Assign_target(self, node):
        return (node[TaintQualifer.__name__], self.visit_Name(node))


    def visit_BinOp_operand(self, node):
        if node['ast_type'] == 'BinOp':
            return self.visit_BinOp_operand(node['left']) + self.visit_BinOp_operand(node['right'])
        else:
            return self.super.visit_BinOp_operand(node)


    def visit_Assign_value(self, node):
        if node['ast_type'] == 'BinOp':
            return self.visit_BinOp_operand(node['left']) + self.visit_BinOp_operand(node['right'])
        else:
            return self.super.visit_Assign_value(node)


    def visit_Assign(self, node):

        values = self.visit_Assign_value(node['value'])

        targets = self.visit_Assign_targets(node['targets'])
        # if len(targets) > 1: ...
        target_taint_qualifier, target_id = targets[0]  # assume1 for now, how to treat value

        for taint_qualifier,name in values:
            constraint = Constraint(node["lineno"], taint_qualifier, name, target_taint_qualifier, target_id)
            self._constraints[self._scope].append(constraint)

            # self._constraints_map[]


    def visit_Call_arg(self, node):
        if node['ast_type'] == 'BinOp':
            return self.visit_BinOp_operand(node['left']) + self.visit_BinOp_operand(node['right'])
        else:
            return self.super.visit_Call_arg(node)


    def visit_Call_arg_as_parameter(self, node):
        return (node[CallArgKeys.Call_arg_TaintQualifer], node[CallArgKeys.Call_arg])


    def visit_Call_args(self, nodes, lineno):
        for node in nodes:
            arg_taint_qualifier, arg = self.visit_Call_arg_as_parameter(node)
            values = self.visit_Call_arg(node) #>1 if BinOp
            for taint_qualifier, name in values:
                constraint = Constraint(lineno, taint_qualifier, name, arg_taint_qualifier, arg)
                self._constraints[self._scope].append(constraint)


    def visit_Call_func(self, node):
        return (node['lineno'], node[TaintQualifer.__name__], self.visit_Name(node))


    def visit_Call(self, node):
        lineno, taint_qualifier, name = self.visit_Call_func(node['func'])
        self.visit_Call_args(node['args'], lineno)
        return ((taint_qualifier, name), )


    def visit_Name(self, node):
        taint_qualifier, name = node[TaintQualifer.__name__], node[Keys.SSA_NAME]
        return ((taint_qualifier, name), )


    def visit_Str(self, node):
        taint_qualifier, s = node[TaintQualifer.__name__], self.super.visit_Str(node)
        return ((taint_qualifier, s), )


    def visit_Num(self, node):
        taint_qualifier, n = node[TaintQualifer.__name__], node['n']
        return ((taint_qualifier, n),) #homogenize return values, BinOp's fault


    def visit_Constant(self, node):
        taint_qualifier, v = node[TaintQualifer.__name__], self.super.visit_Constant(node)
        return ((taint_qualifier, v), )