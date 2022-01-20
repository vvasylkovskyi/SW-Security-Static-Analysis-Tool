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
        # print(name, node[FlowCategory.__name__], node)
        return node[FlowCategory.__name__]


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


    def visit_Assign_value(self, node):
        ast_type = node['ast_type']
        if ast_type == 'Name':
            self.visit_Name_for_value(node)
        elif ast_type == 'Call':
            self.visit_Call(node)
        elif ast_type == 'BinOp':
            self.visit_BinOp(node)


    def visit_Assign_targets(self, nodes):
        for node in nodes:
            self.visit_Name_for_target(node)


    def visit_Assign(self, node):
        self.visit_Assign_value(node['value'])
        self.visit_Assign_targets(node['targets'])


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

#TODO needed?
    # def visit_binop_operand_as_Call_arg(self, node, func_flow_category):
    #     node[CallArgKeys.Call_arg_CallFlowCategory] = func_flow_category
    #     self.visit_binop_operand(node)
    #
    #
    # def visit_BinOp_as_Call_arg(self, node, func_flow_category):
    #     self.visit_binop_operand_as_Call_arg(node['left'], func_flow_category)
    #     self.visit_binop_operand_as_Call_arg(node['right'], func_flow_category)


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
                self.visit_BinOp(node)
                # self.visit_BinOp_as_Call_arg(node, func_flow_category) #possibly recursive


    def visit_Call_func(self, node):
        name = self.visit_Name(node)
        flow_category = self.assign_FlowCategory(node, name)
        return name, flow_category


    def visit_Call(self, node):
        name, flow_category = self.visit_Call_func(node['func'])
        self.visit_Call_args(node['args'], name, flow_category)