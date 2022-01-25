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
        self.sources = list()
        self.sinks = list()
        self.sanitizers = list()
        self.labels = list()

    @property
    def scoped_constraints(self):
        return self._scoped_constraints

    @property
    def path_feasibility_constraints(self):
        return self._path_feasibility_constraints

    def make_path_feasibility_constraints(self):
        """
        :return:
        """
        print("Scoped constraints: ", self._scoped_constraints.items())
        for scope, constraints in self._scoped_constraints.items():
            self._path_feasibility_constraints[scope].extend(
                self._scoped_constraints[scope].copy())
            for key in self._scoped_constraints.keys()-{scope}:
                if ','.join(map(str, scope)) in ','.join(map(str, key)):  # order matters
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
        # assume1 for now, how to treat value
        print("---------")
        print("Sources: ", self.sources)
        print("TARGETS: ", targets)
        print("VALUES: ", values)
        print("---------")
        ((target_taint_qualifier, target_id),) = targets[0]

        for taint_qualifier, name in values:
            print("Assign: ", values)
            constraint = Constraint(
                node[AstTypes.Generic.lineno], taint_qualifier, name, target_taint_qualifier, target_id)
            print("FINAL CONSTRAINT: ", constraint)
            self._scoped_constraints[self._scope].append(constraint)

    def visit_Call_arg(self, node):
        if node[AstTypes.Generic.ast_type] == AstTypes.BinOp.Key:
            return self.visit_BinOp_operand(node[AstTypes.BinOp.left]) + self.visit_BinOp_operand(node[AstTypes.BinOp.right])
        else:
            return self.super.visit_Call_arg(node)

    def get_qualifier(self, arg):
        print("LABELS: ", self.labels)
        return self.labels[arg]

    def visit_Call_arg_as_parameter(self, node):
        return (node[CallArgKeys.Call_arg_TaintQualifer], node[CallArgKeys.Call_arg])

    def visit_Call_args(self, nodes, lineno, return_qualifier, return_name):
        print("HERE NOW")
        for node in nodes:
            arg_taint_qualifier, arg = self.visit_Call_arg_as_parameter(node)
            values = self.visit_Call_arg(node)  # >1 if BinOp
            arg_qualifier = self.get_qualifier(arg)
            for taint_qualifier, name in values:
                print("Return QF: ", return_qualifier)
                print("Return Name: ", return_name)
                print("Visit Call Args: ", values)
                print("YOO")
                # constraint_return = Constraint(
                #     lineno, return_qualifier, return_name, taint_qualifier, name)
                # self._scoped_constraints[self._scope].append(constraint_return)

                constraint_arg = Constraint(
                    lineno, taint_qualifier, name, arg_qualifier, arg)
                print("CONSTRAINT: ", constraint_arg)
                print("CONSTRAINT arg taint qualifier: ", arg_taint_qualifier)
                print("CONSTRAINT arg : ", arg)
                print("CONSTRAINT name : ", name)
                print("CONSTRAINT taint_q : ", taint_qualifier)
                print("CONSTRAINT ARG QF: ", arg_qualifier)

                self._scoped_constraints[self._scope].append(constraint_arg)

    def visit_Call_func(self, node):
        ((taint_qualifier, name),) = self.visit_Name(node)
        print("CALL FN")
        return (node[AstTypes.Generic.lineno], taint_qualifier, name)

    def visit_Call(self, node):
        lineno, taint_qualifier, name = self.visit_Call_func(node['func'])
        print("CALL: ", taint_qualifier, name)
        self.visit_Call_args(node[AstTypes.Call.args],
                             lineno, taint_qualifier, name)
        return ((taint_qualifier, name), )

    def visit_Name(self, node):
        taint_qualifier, name = node[TaintQualifer.__name__], node[Keys.SSA_NAME]
        return ((taint_qualifier, name), )

    def visit_Constant(self, node):
        taint_qualifier, v = node[TaintQualifer.__name__], self.super.visit_Constant(
            node)
        # homogeneize return values, BinOp's fault
        return ((taint_qualifier, v), )
