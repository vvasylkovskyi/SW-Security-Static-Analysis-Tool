"""
x = y -> q_y <= q_x
do not taint x with y
"""

from collections import defaultdict

from ps_visitor import Keys as PSKeys
from ssa_visitor import Keys as SSAKeys
from visitors import Visitor, AstTypes
from tf_visitor import TaintQualifer, CallArgKeys
from constraints_visitor import Constraint
from utilities import GreekLetters


class Keys(PSKeys, SSAKeys):
    pass


class ScopedConstraints():
    def __init__(self):
        self._scoped_constraints = list()
        self._instantiated_variables = list()
        self._functions = list()

    def __repr__(self):
        return f"{self._scoped_constraints}"


class ConstraintsPathFlowSenstivityVisitor(Visitor):

    def __init__(self, ast):
        super(ConstraintsPathFlowSenstivityVisitor, self).__init__(ast)
        self.super = super(ConstraintsPathFlowSenstivityVisitor, self)
        self._scoped_constraints_object = defaultdict(ScopedConstraints)
        self._path_feasibility_constraints_object = defaultdict(
            ScopedConstraints)
        self._scope = None
        self.sources = list()
        self.sinks = list()
        self.sanitizers = list()
        self.labels = list()
        self.sym_connect_to_next_constraint_open = False

    @property
    def scoped_constraints(self):
        return self._scoped_constraints_object

    @property
    def path_feasibility_constraints(self):
        return self._path_feasibility_constraints_object

    def next_label(self):
        greek_letters_list = list(GreekLetters.greek_letters_lowercase)
        next_greek_letter = greek_letters_list.pop(0)
        GreekLetters.greek_letters_lowercase = tuple(greek_letters_list)
        return next_greek_letter

    def make_path_feasibility_constraints(self):
        """
        :return:
        """
        for scope, scoped_constraints in self._scoped_constraints_object.items():
            self._path_feasibility_constraints_object[scope]._scoped_constraints.extend(
                self._scoped_constraints_object[scope]._scoped_constraints.copy())
            self._path_feasibility_constraints_object[scope]._instantiated_variables.extend(
                self._scoped_constraints_object[scope]._instantiated_variables.copy())
            self._path_feasibility_constraints_object[scope]._functions.extend(
                self._scoped_constraints_object[scope]._functions.copy())
            for key in self._scoped_constraints_object.keys()-{scope}:
                if ','.join(map(str, scope)) in ','.join(map(str, key)):  # order matters
                    self._path_feasibility_constraints_object[key]._scoped_constraints.extend(
                        scoped_constraints._scoped_constraints)
                    self._path_feasibility_constraints_object[key]._instantiated_variables.extend(
                        scoped_constraints._instantiated_variables)
                    self._path_feasibility_constraints_object[key]._functions.extend(
                        scoped_constraints._functions)
        for pf_constraints in self._path_feasibility_constraints_object.values():
            pf_constraints._scoped_constraints.sort()

    def find_parent_scopes(self, current_scope):
        parent_scopes = list()
        for scope, _ in self._scoped_constraints_object.items():
            level = 0
            while level < len(current_scope):
                if level > len(scope) - 1 or level > len(current_scope) - 1:
                    break
                if current_scope[level] == scope[level]:
                    parent_scopes.append(scope)
                level += 1

        return parent_scopes

    def extend_instantiated_variables_with_parent_scopes(self, current_scope):
        parent_scopes_list = self.find_parent_scopes(current_scope)

        instantiated_variables = list()

        for parent_scope in parent_scopes_list:
            instantiated_variables.extend(
                self._scoped_constraints_object[parent_scope]._instantiated_variables)
        return instantiated_variables

    def extend_defined_functions_with_parent_scopes(self, current_scope):
        parent_scopes_list = self.find_parent_scopes(current_scope)

        defined_functions = list()
        for parent_scope in parent_scopes_list:
            defined_functions.extend(
                self._scoped_constraints_object[parent_scope]._functions)
        return defined_functions

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
        ((target_taint_qualifier, target_id),) = targets[0]

        for taint_qualifier, name in values:
            # print("Constraint line: ", node[AstTypes.Generic.lineno])
            # print("Constraint TQ: ", taint_qualifier)
            # print("Constraint Name: ", name)
            # print("Constraint Target TQ: ", target_taint_qualifier)
            # print("Constraint Target Name: ", target_id)
            constraint = Constraint(
                node[AstTypes.Generic.lineno], taint_qualifier, name, target_taint_qualifier, target_id)

            # Add function calls
            value_is_function = node[AstTypes.Assign.value]['ast_type'] == 'Call'
            if value_is_function:
                self._scoped_constraints_object[self._scope]._instantiated_variables.append(
                    name)

            self._scoped_constraints_object[self._scope]._instantiated_variables.append(
                target_id)

            if self.find_parent_scopes(self._scope) != None:
                self._scoped_constraints_object[self._scope]._instantiated_variables.extend(
                    self.extend_instantiated_variables_with_parent_scopes(self._scope))

            self._scoped_constraints_object[self._scope]._instantiated_variables = list(
                dict.fromkeys(self._scoped_constraints_object[self._scope]._instantiated_variables))
            self._scoped_constraints_object[self._scope]._scoped_constraints.append(
                constraint)
        return self.super.visit_Assign(node)

    def visit_Call_arg(self, node):
        if node[AstTypes.Generic.ast_type] == AstTypes.BinOp.Key:
            return self.visit_BinOp_operand(node[AstTypes.BinOp.left]) + self.visit_BinOp_operand(node[AstTypes.BinOp.right])
        else:
            return self.super.visit_Call_arg(node)

    def get_qualifier(self, arg):
        return self.labels[arg]

    def visit_Call_arg_as_parameter(self, node):
        return (node[CallArgKeys.Call_arg_TaintQualifer], node[CallArgKeys.Call_arg])

    def visit_While(self, node):
        _, body = self.super.visit_While(node)

        if len(self._scoped_constraints_object[self._scope]._scoped_constraints) > 0:
            last_constraint = self._scoped_constraints_object[self._scope]._scoped_constraints[-1]
            next_symbolic_qualifier = self.next_label()
            sym_constraint_from_last_constraint_to_test_tq = Constraint(
                node[AstTypes.Generic.lineno], last_constraint.rhs_tq, last_constraint.rhs_id, next_symbolic_qualifier, '')
            self._scoped_constraints_object[self._scope]._scoped_constraints.append(
                sym_constraint_from_last_constraint_to_test_tq)

            target_body_tq = body[0][1][0][0]
            sym_constraint_from_sym_tq_to_first_body_tq = Constraint(
                node[AstTypes.Generic.lineno], next_symbolic_qualifier, '', target_body_tq, '')
            self._scoped_constraints_object[self._scope]._scoped_constraints.append(
                sym_constraint_from_sym_tq_to_first_body_tq)

    def visit_If(self, node):
        print("Visiting If")
        test, body, orelse = self.super.visit_If(node)
        print("TEST: ", test)
        print("Body: ", body)
        print("Orelse: ", orelse)

        print("Openning sym connect to next constraint")
        self.sym_connect_to_next_constraint_open = True
        # return self.super.visit_While(node)

    # def get_last_constraints_with_same_inflow(self):
    #     print("Getting them constraints")
    #     last_constraints_with_same_inflow = list()
    #     last_constraint = self._scoped_constraints_object[self._scope]._scoped_constraints[-1]
    #     print("Last constraint rhs tq: ", last_constraint.rhs_tq)
    #     inflow_tq = last_constraint.rhs_tq
    #     new_inflow_tq = inflow_tq
    #     last_constraints_with_same_inflow.append(last_constraint)
    #     index = 1
    #     print("Constraints: ",
    #           self._scoped_constraints_object[self._scope]._scoped_constraints)
    #     last_constraint = self._scoped_constraints_object[self._scope]._scoped_constraints[-2]

    #     while new_inflow_tq == inflow_tq:
    #         if len(self._scoped_constraints_object[
    #                 self._scope]._scoped_constraints) < 1 + index - 1:
    #             last_constraint = self._scoped_constraints_object[
    #                 self._scope]._scoped_constraints[-1 - index]
    #             last_constraints_with_same_inflow.append(last_constraint)
    #             new_inflow_tq = last_constraint.rhs_tq
    #             index += 1
    #         else:
    #             break
    #     return last_constraints_with_same_inflow

    def visit_Call_args(self, nodes, lineno, return_qualifier, return_name):
        for node in nodes:
            arg_taint_qualifier, arg = self.visit_Call_arg_as_parameter(node)
            values = self.visit_Call_arg(node)  # >1 if BinOp
            arg_qualifier = self.get_qualifier(arg)
            for taint_qualifier, name in values:
                # print("Return QF: ", return_qualifier)
                # print("Return Name: ", return_name)
                # print("Visit Call Args: ", values)
                # print("YOO")
                # print("TARGET_Function: ", return_name)
                # print("Target function name: ", name)
                constraint_return = Constraint(
                    lineno, taint_qualifier, name, return_qualifier, return_name)
                self._scoped_constraints_object[self._scope]._scoped_constraints.append(
                    constraint_return)
                self._scoped_constraints_object[self._scope]._functions.append(
                    return_name)

                if self.find_parent_scopes(self._scope) != None:
                    self._scoped_constraints_object[self._scope]._functions.extend(
                        self.extend_defined_functions_with_parent_scopes(self._scope))

                self._scoped_constraints_object[self._scope]._functions = list(
                    dict.fromkeys(self._scoped_constraints_object[self._scope]._functions))
                # print("CONSTRAINT RETURN: ", constraint_return)
                # constraint_arg = Constraint(
                #     lineno, taint_qualifier, name, arg_qualifier, arg)
                # print("CONSTRAINT: ", constraint_arg)
                # print("CONSTRAINT arg taint qualifier: ", arg_taint_qualifier)
                # print("CONSTRAINT arg : ", arg)
                # print("CONSTRAINT name : ", name)
                # print("CONSTRAINT taint_q : ", taint_qualifier)
                # print("CONSTRAINT ARG QF: ", arg_qualifier)
                # print("Constraint args: ", constraint_arg)
                # self._scoped_constraints_object[self._scope]._scoped_constraints.append(
                # constraint_arg)
        return self.super.visit_Call_args(nodes)

    def visit_Call_func(self, node):
        ((taint_qualifier, name),) = self.visit_Name(node)
        return (node[AstTypes.Generic.lineno], taint_qualifier, name)

    def visit_Call(self, node):
        lineno, taint_qualifier, name = self.visit_Call_func(node['func'])
        # print("Calling function and then going into arguments")
        self.visit_Call_args(node[AstTypes.Call.args],
                             lineno, taint_qualifier, name)
        # print("Called function already")
        # if self.sym_connect_to_next_constraint_open and len(self._scoped_constraints_object[self._scope]._scoped_constraints) > 0:
        #     print("Got the sym connect oppened?: ",
        #           self.sym_connect_to_next_constraint_open)
        #     last_constraints_with_same_inflow = self.get_last_constraints_with_same_inflow()
        #     last_constraint = self._scoped_constraints_object[self._scope]._scoped_constraints[-1]
        #     print("Last Constraint: ", last_constraint)

        #     print("Last constraints with same inflow: ",
        #           last_constraints_with_same_inflow)
        #     self.sym_connect_to_next_constraint_open = False
        return ((taint_qualifier, name), )

    def visit_Name(self, node):
        taint_qualifier, name = node[TaintQualifer.__name__], node[Keys.SSA_NAME]
        return ((taint_qualifier, name), )

    def visit_Constant(self, node):
        taint_qualifier, v = node[TaintQualifer.__name__], self.super.visit_Constant(
            node)
        # homogeneize return values, BinOp's fault
        return ((taint_qualifier, v), )
