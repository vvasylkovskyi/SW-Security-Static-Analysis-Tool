from collections import defaultdict
from enum import Enum

from visitors import Visitor
from utilities import greek_letters_lowercase

class TypeQualifers:
    TAINTED = "tainted"
    UNTAINTED = "untainted"

class AssignmentContext(Enum):
    NONE = 0
    TARGET = 1
    VALUE_VARIABLE = 2
    VALUE_FUNCTION = 3
    VALUE_FUNCTION_ARGUMENT = 4


class TaintedFlowVisitor(Visitor):

    def __init__(self, ast, **kwargs):
        super(TaintedFlowVisitor, self).__init__(ast)
        self.super = super(TaintedFlowVisitor, self)
        self.indentation_level=0
        self._labels = filter(None, greek_letters_lowercase)
        self._labels_map = dict()

        self._variable_ssa_map = defaultdict(list)
        self._variable_ssa_inverse_map = dict()

        self.assignment_context = AssignmentContext.NONE
        self.sources = kwargs['sources']
        self.original_sources = self.sources.copy()

        self.sinks = kwargs['sinks']
        self.sanitizers = kwargs['sanitizers']


    def next_label(self):
        return next(self._labels)

    def make_ssa_variable_name(self, name):
        ssa_name = f"{name}_{len(self._variable_ssa_map[name])}"
        self._variable_ssa_map[name].append(ssa_name)
        self._variable_ssa_inverse_map[ssa_name] = name
        return ssa_name

    def visit_Module(self, node):
        return "\n".join(self.visit_body(node['body']))

    def visit_Assign(self, node):
        assignment_context = self.assignment_context
        self.assignment_context = AssignmentContext.TARGET
        targets = self.visit_assign_targets(node)
        self.assignment_context = AssignmentContext.VALUE_VARIABLE
        value = self.visit_assign_value(node)
        self.assignment_context = assignment_context

        return f"{node['lineno']:>2}: {self.indentation_level * Visitor.INDENTATION}{','.join(targets)} = {value}"


    def visit_Compare(self, node):
        assignment_context = self.assignment_context
        self.assignment_context = AssignmentContext.VALUE_VARIABLE
        left = self.visit_operand(node['left'])
        comparators = list(self.visit_operand(node) for node in node['comparators'])
        self.assignment_context = assignment_context
        ops = self.visit_ops(node)
        return f"{left} {', '.join(ops)} {','.join(comparators)}"


    def visit_Call(self, node):
        
        func_name = node['func']['id']
        if func_name in self.sinks:
            args_type_qualifier = TypeQualifers.UNTAINTED
        elif func_name in self.sanitizers:
            args_type_qualifier = TypeQualifers.TAINTED
        else:
            args_type_qualifier = TypeQualifers.TAINTED

        assignment_context = self.assignment_context

        self.assignment_context = AssignmentContext.VALUE_FUNCTION_ARGUMENT
        arguments = ', '.join(
            f"{args_type_qualifier} {func_name}_arg{i} {arg}" for i, arg in
            enumerate(self.visit_call_args(node))
        )
        self.assignment_context = AssignmentContext.VALUE_FUNCTION
        representation = f"{self.visit_call_func(node)}({arguments})"
        self.assignment_context = assignment_context
        # print("exiting call")
        return representation


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
        name = node['id']
        ssa_name = ''

        if self.assignment_context in {
            AssignmentContext.TARGET,
            AssignmentContext.VALUE_VARIABLE,
            AssignmentContext.VALUE_FUNCTION_ARGUMENT}:
            pass

        if self.assignment_context == AssignmentContext.TARGET:
           if name not in self.sources:
                ssa_name = self.make_ssa_variable_name(name)

        elif self.assignment_context == AssignmentContext.VALUE_VARIABLE:
            if name not in self._variable_ssa_map:#uninstatiated
                if name not in self.sources:
                    ssa_name = self.make_ssa_variable_name(name)
                # self.sources.append(ssa_name)
            else:
                ssa_name = self._variable_ssa_map[name][-1]

        elif self.assignment_context == AssignmentContext.VALUE_FUNCTION_ARGUMENT:
            if name in self._variable_ssa_map:
                ssa_name = self._variable_ssa_map[name][-1]
            else:
                ssa_name = self.make_ssa_variable_name(name)
                #TODO?

        # print(node["lineno"], name, ssa_name, self.assignment_context)

        if ssa_name:
            if name in self.sources:
                self.sources.append(ssa_name)  #second assignment of a source, good idea???
            elif name in self.sinks:
                self.sinks.append(ssa_name)
            name = ssa_name

        if name in self._labels_map:
            type_qualifier = self._labels_map[name]
        else:
            if name in self.sources:
                type_qualifier = TypeQualifers.TAINTED
            elif name in self.sanitizers:
                type_qualifier = TypeQualifers.UNTAINTED
            elif name in self.sinks:
                type_qualifier = TypeQualifers.UNTAINTED  # sink can be a variable or a function, untainted might refer to the variable or to the arguments of the function
            elif self.assignment_context == AssignmentContext.VALUE_VARIABLE:
                type_qualifier = TypeQualifers.TAINTED
            elif self.assignment_context == AssignmentContext.VALUE_FUNCTION_ARGUMENT:
                type_qualifier = TypeQualifers.TAINTED

            else:
                type_qualifier = self.next_label()
            self._labels_map[name] = type_qualifier

        # print(type_qualifier, name)
        representation = f"{type_qualifier} {name}"
        return representation


    def visit_While(self, node):

        indentation = self.indentation_level * Visitor.INDENTATION
        self.indentation_level += 1
        (test, body) = self.super.visit_While(node)
        self.indentation_level -= 1

        representation = f"{node['lineno']:>2}: {indentation}while ({test}):\n"
        representation += "\n".join(body)
        return representation

    def visit_If(self, node):

        indentation = self.indentation_level * Visitor.INDENTATION
        self.indentation_level += 1
        (test, body, orelse) = self.super.visit_If(node)
        self.indentation_level -= 1

        representation = f"{node['lineno']:>2}: {indentation}if({test}):\n"
        representation += "\n".join(body)
        if orelse:
            representation += f"\n{node['lineno']+len(body):>2}: {indentation}else:\n"
            representation += "\n".join(orelse)
        return representation

    def visit_Expr(self, node):
        value = self.super.visit_Expr(node)
        return f"{node['lineno']:>2}: {self.indentation_level * Visitor.INDENTATION}{value}"

    def visit_BinOp(self, node):
        (left, op, right) = self.super.visit_BinOp(node)
        return f"{left} {op} {right}"  # SrcVisitor?

    def visit_Str(self, node):
        return f"{TypeQualifers.UNTAINTED} {self.super.visit_Str(node)}"

    def visit_int(self, node):
        return f"{TypeQualifers.UNTAINTED} {self.super.visit_int(node)}"

    def visit_Break(self, node):
        return f"{self.indentation_level * Visitor.INDENTATION}{self.super.visit_Break(node)}"