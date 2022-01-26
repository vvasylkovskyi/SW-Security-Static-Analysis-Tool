from visitors import Visitor
from utilities import GreekLetters
from instantiation_visitor import FlowCategory, CallArgKeys as InstantiationCallArgKeys


class TaintQualifer:
    TAINTED = "tainted"
    UNTAINTED = "untainted"
    labels = GreekLetters.greek_letters_lowercase


class CallArgKeys(InstantiationCallArgKeys):
    Call_arg_TaintQualifer = "Call_arg_TaintQualifier"


class TaintedFlowVisitor(Visitor):

    def __init__(self, ast):
        super(TaintedFlowVisitor, self).__init__(ast)
        self.super = super(TaintedFlowVisitor, self)
        self._labels = filter(None, TaintQualifer.labels)
        self._labels_map = dict()
        self.sources = list()
        self.sinks = list()
        self.sanitizers = list()

    @property
    def labels(self):
        return self._labels_map

    def next_label(self):
        next_greek_letter = next(self._labels)
        greek_letters_list = list(GreekLetters.greek_letters_lowercase)
        greek_letters_list.remove(next_greek_letter)
        GreekLetters.greek_letters_lowercase = tuple(greek_letters_list)
        return next_greek_letter

    def check_for_Call_arg(self, node):
        if CallArgKeys.Call_arg in node and CallArgKeys.Call_arg_CallFlowCategory in node:
            arg_flow_category = node.pop(CallArgKeys.Call_arg_CallFlowCategory)
            node[CallArgKeys.Call_arg_TaintQualifer] = {
                FlowCategory.SOURCE: TaintQualifer.TAINTED,
                FlowCategory.SANITIZER: TaintQualifer.TAINTED,
                FlowCategory.REGULAR: TaintQualifer.TAINTED,
                FlowCategory.SINK: TaintQualifer.UNTAINTED
            }[arg_flow_category]
            taint_qualifier = self.next_label()

            self._labels_map[node[CallArgKeys.Call_arg]
                             ] = taint_qualifier

    def assign_taint_qualifier(self, node, name):
        if not name in self._labels_map:
            node_flow_category = node[FlowCategory.__name__]

            if node_flow_category == FlowCategory.SOURCE:
                self.sources.append(name)
            #     taint_qualifier = TaintQualifer.TAINTED

            elif node_flow_category == FlowCategory.SANITIZER:
                self.sanitizers.append(name)
            #     taint_qualifier = TaintQualifer.UNTAINTED

            elif node_flow_category == FlowCategory.SINK:
                self.sinks.append(name)
            #     taint_qualifier = TaintQualifer.UNTAINTED

            # elif node_flow_category == FlowCategory.REGULAR:
            taint_qualifier = self.next_label()

            self._labels_map[name] = taint_qualifier

        node[TaintQualifer.__name__] = self._labels_map[name]

    def visit_Name(self, node):
        name = self.super.visit_Name(node)
        self.assign_taint_qualifier(node, name)

    def visit_Call_args(self, nodes):
        for node in nodes:
            self.check_for_Call_arg(node)
        self.super.visit_Call_args(nodes)

    def visit_BinOp(self, node):
        self.check_for_Call_arg(node)
        self.super.visit_BinOp(node)

    def check_for_Call_arg_CallFlowCategory(self, node):
        if CallArgKeys.Call_arg_CallFlowCategory in node:
            del node[CallArgKeys.Call_arg_CallFlowCategory]

    def visit_Constant(self, node):
        node[TaintQualifer.__name__] = TaintQualifer.UNTAINTED
        self.check_for_Call_arg(node)
        self.check_for_Call_arg_CallFlowCategory(node)
