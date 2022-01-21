from enum import Enum

from visitors import Visitor

class FlowCategory:
    SOURCE = "sources"
    SANITIZER = "sanitizers"
    SINK = "sinks"
    REGULAR = None #instantiated and no source, sink or sanitizer


class CallArgKeys:
    Call_arg = "Call_arg"
    Call_arg_CallFlowCategory = "Call_arg_CallFlowCategory"


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
        return node[FlowCategory.__name__]


    def visit_Name_for_target(self, node):
        name = self.visit_Name(node)
        self.instantiated.add(name)
        self.assign_FlowCategory(node, name)


    def visit_Assign_targets(self, nodes):
        for node in nodes:
            self.visit_Name_for_target(node)


    def visit_Name_for_value(self, node):
        name = self.visit_Name(node)
        if not name in self.instantiated:
            node[FlowCategory.__name__] = FlowCategory.SOURCE
            self.sources.append(name)
            self.instantiated.add(name)
        else:
            self.assign_FlowCategory(node, name)


    def visit_BinOp_operand(self, node):
        if node['ast_type'] == 'Name':
            self.visit_Name_for_value(node)
        elif node['ast_type'] == 'Call':
            self.visit_Call(node)
        elif node['ast_type'] == 'BinOp':
            self.visit_BinOp(node)


    def visit_Compare(self, node):
        self.visit_BinOp_operand(node['left'])
        for node in node['comparators']:
            self.visit_BinOp_operand(node)


    def visit_test(self, node):
        ast_type = node['ast_type']
        if ast_type == 'Compare':
            self.visit_Compare(node)
        elif ast_type == 'Name':
            self.visit_Name_for_value(node)

#TODO needed?
    def visit_BinOp_operand_as_Call_arg(self, node, func_flow_category):
        node[CallArgKeys.Call_arg_CallFlowCategory] = func_flow_category
        ast_type = node['ast_type']
        if ast_type == 'Name':
            self.visit_Name_for_value(node)
        elif ast_type == 'Call':
            self.visit_Call(node)
        elif ast_type == 'BinOp':
            self.visit_BinOp_as_Call_arg(node, func_flow_category)
        elif ast_type == 'Str':
            self.visit_Str(node)
        elif ast_type == 'Num':
            self.visit_Num(node)


    def visit_BinOp_as_Call_arg(self, node, func_flow_category):
        self.visit_BinOp_operand_as_Call_arg(node['left'], func_flow_category)
        self.visit_BinOp_operand_as_Call_arg(node['right'], func_flow_category)


    def visit_Call_args(self, nodes, func_name, func_flow_category):
        for i, node in enumerate(nodes):
            arg = f"{func_name}_arg{i}"
            node[CallArgKeys.Call_arg] = arg
            node[CallArgKeys.Call_arg_CallFlowCategory] = func_flow_category
            node_ast_type = node['ast_type']
            if node_ast_type == 'Name':
                self.visit_Name_for_value(node)
            elif node_ast_type == 'Call':
                self.visit_Call(node)
            elif node_ast_type == 'BinOp':
                self.visit_BinOp_as_Call_arg(node, func_flow_category)
            elif node_ast_type == 'Str':
                self.visit_Str(node)
            elif node_ast_type == 'Num':
                self.visit_Num(node)

    def visit_Call_func(self, node):
        name = self.visit_Name(node)
        flow_category = self.assign_FlowCategory(node, name)
        return name, flow_category


    def visit_Call(self, node):
        name, flow_category = self.visit_Call_func(node['func'])
        self.visit_Call_args(node['args'], name, flow_category)


    def visit_Str(self, node):
        node[FlowCategory.__name__] = FlowCategory.REGULAR


    def visit_Num(self, node):
        node[FlowCategory.__name__] = FlowCategory.REGULAR