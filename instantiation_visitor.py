from enum import Enum

from visitors import Visitor

class FlowCategory:
    SOURCE = "sources"
    SANITIZER = "sanitizers"
    SINK = "sinks"
    REGULAR = None #instantiated and no source, sink or sanitizer


class InstantiationVisitor(Visitor):

    def __init__(self, ast, **kwargs):
        super(InstantiationVisitor, self).__init__(ast)

        self.pattern = kwargs
        self.sources = self.pattern['sources']
        self.sinks = self.pattern['sinks']
        self.sanitizers = self.pattern['sanitizers']

        self.instantiated = set(self.sources).union(self.sinks) #variables only


    def visit_ast(self):
        module = self.visit_Module(self.ast)


    def visit_Name(self, node):
        name = super(InstantiationVisitor, self).visit_Name(node)
        return name


    def visit_Name_for_variable(self, node):
        name = self.visit_Name(node)
        if not name in self.instantiated:
            node["FlowCategory"] = FlowCategory.SOURCE
            self.sources.append(name)
            self.instantiated.add(name)
        elif name in self.sources:
            node["FlowCategory"] = FlowCategory.SOURCE
        elif name in self.sinks:
            node["FlowCategory"] = FlowCategory.SINK
        else:
            node["FlowCategory"] = FlowCategory.REGULAR


    def visit_assign_value(self, node):
        ast_type = node['ast_type']
        if ast_type == 'Name':
            self.visit_Name_for_variable(node)
        elif ast_type == 'Call':
            self.visit_Call(node)


    def visit_assign_targets(self, nodes):
        for node in nodes:
            target_id = self.visit_Name(node)
            self.instantiated.add(target_id)


    def visit_Assign(self, node):
        self.visit_assign_value(node['value'])
        self.visit_assign_targets(node['targets'])


    def visit_binop_operand(self, node):
        if node['ast_type'] == 'Name':
            self.visit_Name_for_variable(node)
        elif node['ast_type'] == 'Call':
            self.visit_Call(node)
        elif node['ast_type'] == 'BinOp':
            self.visit_BinOp(node)


    def visit_BinOp(self, node):
        self.visit_binop_operand(node['left'])
        self.visit_binop_operand(node['right'])


    def visit_Compare(self, node):
        self.visit_binop_operand(node['left'])
        for node in node['comparators']:
            self.visit_binop_operand(node)


    def visit_test(self, node):
        ast_type = node['ast_type']
        if ast_type == 'Compare':
            self.visit_Compare(node)
        elif ast_type == 'Name':
            self.visit_Name_for_variable(node)


    def visit_func(self, node):
        name = self.visit_Name(node)
        if name in self.sources:
            node["FlowCategory"] = FlowCategory.SOURCE
        elif name in self.sinks:
            node["FlowCategory"] = FlowCategory.SINK
        elif name in self.sanitizers:
            node["FlowCategory"] = FlowCategory.SANITIZER
        else:
            node["FlowCategory"] = FlowCategory.REGULAR
        return name


    def visit_args(self, nodes):
        for node in nodes:
            node_ast_type = node['ast_type']
            if node_ast_type == 'Name':
                self.visit_Name_for_variable(node)
            elif node_ast_type == 'BinOp':
                self.visit_BinOp(node)
            elif node_ast_type == 'Call':
                self.visit_Call(node)


    def visit_Call(self, node):
        self.visit_func(node['func'])
        self.visit_args(node['args'])