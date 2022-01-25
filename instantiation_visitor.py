from visitors import Visitor, AstTypes


class FlowCategory:
    SOURCE = "sources"
    SANITIZER = "sanitizers"
    SINK = "sinks"
    REGULAR = None  # instantiated and no source, sink or sanitizer


class CallArgKeys:
    Call_arg = "Call_arg"
    Call_arg_CallFlowCategory = "Call_arg_CallFlowCategory"


class InstantiationVisitor(Visitor):

    def __init__(self, ast, **kwargs):
        super(InstantiationVisitor, self).__init__(ast)

        self.pattern = kwargs
        self.sources = self.pattern[FlowCategory.SOURCE]
        self.sinks = self.pattern[FlowCategory.SINK]
        self.sanitizers = self.pattern[FlowCategory.SANITIZER]

        self.instantiated = set(self.sources).union(
            self.sinks)  # variables only

        print("after instantiated: ", self.instantiated)

    def remove_unisntantiated_vars_from_sink(self, name):
        if name in self.pattern[FlowCategory.SINK]:
            self.pattern[FlowCategory.SINK].remove(name)

    def visit_ast(self):
        module = self.visit_Module(self.ast)

    def assign_FlowCategory(self, node, name):
        if name in self.sources:
            node[FlowCategory.__name__] = FlowCategory.SOURCE
        elif name in self.sinks:
            node[FlowCategory.__name__] = FlowCategory.SINK
        # elif name in self.sanitizers:
        #     node[FlowCategory.__name__] = FlowCategory.SANITIZER
        else:
            node[FlowCategory.__name__] = FlowCategory.REGULAR
        return node[FlowCategory.__name__]

    def visit_Name_for_target(self, node):
        print("HERE VISITING NAME TARGET")
        name = self.visit_Name(node)
        print("HERE YOLO VISITING NAME TARGET")
        print("yoyo NAME: ", name)
        self.instantiated.add(name)
        print("New instantiateds: ", self.instantiated)
        self.assign_FlowCategory(node, name)

    def visit_Assign_targets(self, nodes):
        for node in nodes:
            self.visit_Name_for_target(node)

    def visit_Name_for_value(self, node):
        name = self.visit_Name(node)
        print("Sources: ", self.sources)
        print("Name: ", name)
        print("HERE VISITING NAME just")
        if not name in self.instantiated:
            node[FlowCategory.__name__] = FlowCategory.SOURCE
            self.sources.append(name)
            print("HERE VISITING")
            print("Sources: ", self.sources)
            print("Name: ", name)
            self.instantiated.add(name)
            # self.remove_unisntantiated_vars_from_sink(name)
            # print("PATTERN: ", self.pattern)
        else:
            self.assign_FlowCategory(node, name)

    def visit_Compare_operand(self, node):
        ast_type = node[AstTypes.Generic.ast_type]
        if ast_type == AstTypes.Name.Key:
            return self.visit_Name_for_value(node)
        elif ast_type == AstTypes.Call.Key:
            return self.visit_Call(node)
        elif ast_type == AstTypes.BinOp.Key:
            return self.visit_BinOp(node)

    def visit_Compare_comparators(self, nodes):
        for node in nodes:
            self.visit_Compare_operand(node)

    def visit_Compare(self, node):

        self.visit_Compare_operand(node[AstTypes.Compare.left])
        self.visit_Compare_comparators(node[AstTypes.Compare.comparators])

    def visit_If_test(self, node):
        ast_type = node[AstTypes.Generic.ast_type]
        if ast_type == AstTypes.Name.Key:
            return self.visit_Name_for_value(node)
        elif ast_type == AstTypes.Compare.Key:
            return self.visit_Compare(node)

    def visit_BinOp_operand_as_Call_arg(self, node, func_flow_category):
        node[CallArgKeys.Call_arg_CallFlowCategory] = func_flow_category
        ast_type = node[AstTypes.Generic.ast_type]
        if ast_type == AstTypes.Name.Key:
            return self.visit_Name_for_value(node)
        elif ast_type == AstTypes.BinOp.Key:
            return self.visit_BinOp_as_Call_arg(node, func_flow_category)
        elif ast_type == AstTypes.Call.Key:
            return self.visit_Call(node)
        elif ast_type == AstTypes.Constant.Key:
            return self.visit_Constant(node)

    def visit_BinOp_as_Call_arg(self, node, func_flow_category):
        self.visit_BinOp_operand_as_Call_arg(
            node[AstTypes.BinOp.left], func_flow_category)
        self.visit_BinOp_operand_as_Call_arg(
            node[AstTypes.BinOp.right], func_flow_category)

    def visit_Call_arg(self, node, arg_name, func_flow_category):

        node[CallArgKeys.Call_arg] = arg_name
        node[CallArgKeys.Call_arg_CallFlowCategory] = func_flow_category

        ast_type = node[AstTypes.Generic.ast_type]
        if ast_type == AstTypes.Name.Key:
            return self.visit_Name_for_value(node)
        elif ast_type == AstTypes.BinOp.Key:
            return self.visit_BinOp_as_Call_arg(node, func_flow_category)
        elif ast_type == AstTypes.Call.Key:
            return self.visit_Call(node)
        elif ast_type == AstTypes.Constant.Key:
            return self.visit_Constant(node)

    def visit_Call_args(self, nodes, func_name, func_flow_category):
        for i, node in enumerate(nodes):
            self.visit_Call_arg(
                node, f"{func_name}_arg{i}", func_flow_category)

    def visit_Call_func(self, node):
        name = self.visit_Name(node)
        flow_category = self.assign_FlowCategory(node, name)
        return name, flow_category

    def visit_Call(self, node):
        name, flow_category = self.visit_Call_func(node[AstTypes.Call.func])
        self.visit_Call_args(node[AstTypes.Call.args], name, flow_category)

    def visit_Constant(self, node):
        node[FlowCategory.__name__] = FlowCategory.REGULAR
