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


    def assign_FlowCategory(self, node, name):
        if name in self.sources:
            node[FlowCategory.__name__] = FlowCategory.SOURCE
        elif name in self.sinks:
            node[FlowCategory.__name__] = FlowCategory.SINK
        elif name in self.sanitizers:
            node[FlowCategory.__name__] = FlowCategory.SANITIZER
        else:
            node[FlowCategory.__name__] = FlowCategory.REGULAR

    def visit_Name_for_value(self, node):
        name = self.visit_Name(node)
        if not name in self.instantiated:
            node[FlowCategory.__name__] = FlowCategory.SOURCE
            self.sources.append(name)
            self.instantiated.add(name)
        else:
            self.assign_FlowCategory(node, name)


    def visit_Name_for_target(self, node):
        name = self.visit_Name(node)
        self.instantiated.add(name)
        self.assign_FlowCategory(node, name)


    def visit_assign_value(self, node):
        ast_type = node['ast_type']
        if ast_type == 'Name':
            self.visit_Name_for_value(node)
        elif ast_type == 'Call':
            self.visit_Call(node)
        elif ast_type == 'BinOp':
            self.visit_BinOp(node)


    def visit_assign_targets(self, nodes):
        for node in nodes:
            self.visit_Name_for_target(node)


    def visit_Assign(self, node):
        self.visit_assign_value(node['value'])
        self.visit_assign_targets(node['targets'])


    def visit_binop_operand(self, node):
        if node['ast_type'] == 'Name':
            self.visit_Name_for_value(node)
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
            self.visit_Name_for_value(node)


    def visit_Name_for_func(self, node):
        self.assign_FlowCategory(node, self.visit_Name(node))


    def visit_func(self, node):
        self.visit_Name_for_func(node)


    def visit_args(self, nodes):
        for node in nodes:
            node_ast_type = node['ast_type']
            if node_ast_type == 'Name':
                self.visit_Name_for_value(node)
            elif node_ast_type == 'BinOp':
                self.visit_BinOp(node)
            elif node_ast_type == 'Call':
                self.visit_Call(node)


    def visit_Call(self, node):
        self.visit_func(node['func'])
        self.visit_args(node['args'])