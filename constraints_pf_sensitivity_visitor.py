"""
x = y -> q_y <= q_x
do not taint x with y
"""

from collections import namedtuple, defaultdict

from ps_visitor import Keys as PSKeys
from ssa_visitor import Keys as SSAKeys
from visitors import Visitor, AstTypes
from tf_visitor import TaintQualifer, CallArgKeys
from constraints_visitor import Constraint


class Keys(PSKeys, SSAKeys):
    pass


class ConstraintsPathFlowSenstivityVisitor(Visitor):

    def __init__(self, ast):
        super(ConstraintsPathFlowSenstivityVisitor, self).__init__(ast)
        self.super = super(ConstraintsPathFlowSenstivityVisitor, self)
        self._scoped_constraints = defaultdict(list)
        self._path_feasibility_constraints = defaultdict(list)
        self._scope = None


    @property
    def constraints(self):
        return self._scoped_constraints


    @property
    def path_feasibility_constraints(self):
        return self._path_feasibility_constraints


    def make_path_feasibility_constraints(self):
        """
        :return:
        """
        for scope,constraints in self._scoped_constraints.items():
            self._path_feasibility_constraints[scope].extend(self._scoped_constraints[scope].copy())
            for key in self._scoped_constraints.keys()-{scope}:
                if ','.join(map(str, scope)) in ','.join(map(str, key)):#order matters
                    self._path_feasibility_constraints[key].extend(constraints)
        for pf_constraints in self._path_feasibility_constraints.values():
            pf_constraints.sort()


    def visit_ast(self):
        v = self.super.visit_ast()
        self.make_path_feasibility_constraints()
        return v

    def visit_body_line(self, node):
        self._scope = tuple(node[Keys.CONDITIONS])
        return self.super.visit_body_line(node)


    def visit_Assign_target(self, node):
        return self.visit_Name(node)


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

        values = self.visit_Assign_value(node[AstTypes.Assign.value])

        targets = self.visit_Assign_targets(node[AstTypes.Assign.targets])
        # if len(targets) > 1: ...
        ((target_taint_qualifier, target_id),) = targets[0]  # assume1 for now, how to treat value

        for taint_qualifier,name in values:
            constraint = Constraint(node[AstTypes.Generic.lineno], taint_qualifier, name, target_taint_qualifier, target_id)
            self._scoped_constraints[self._scope].append(constraint)


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
            values = self.visit_Call_arg(node) #>1 if BinOp
            for taint_qualifier, name in values:
                constraint = Constraint(lineno, taint_qualifier, name, arg_taint_qualifier, arg)
                self._scoped_constraints[self._scope].append(constraint)


    def visit_Call_func(self, node):
        ((taint_qualifier, name),) = self.visit_Name(node)
        return (node[AstTypes.Generic.lineno], taint_qualifier, name)


    def visit_Call(self, node):
        lineno, taint_qualifier, name = self.visit_Call_func(node['func'])
        self.visit_Call_args(node[AstTypes.Call.args], lineno)
        return ((taint_qualifier, name), )


    def visit_Name(self, node):
        taint_qualifier, name = node[TaintQualifer.__name__], node[Keys.SSA_NAME]
        return ((taint_qualifier, name), )


    def visit_Constant(self, node):
        taint_qualifier, v = node[TaintQualifer.__name__], self.super.visit_Constant(node)
        return ((taint_qualifier, v), ) #homogeneize return values, BinOp's fault