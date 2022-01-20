from visitors import Visitor
from utilities import greek_letters_lowercase
from instantiation_visitor import FlowCategory


class TaintQualifer:
    TAINTED = "tainted"
    UNTAINTED = "untainted"
    labels = greek_letters_lowercase


class TaintedFlowVisitor(Visitor):

    def __init__(self, ast):
        super(TaintedFlowVisitor, self).__init__(ast)
        self._labels = filter(None, TaintQualifer.labels)
        self._labels_map = dict()

    def next_label(self):
        return next(self._labels)

    def visit_Name(self, node):
        name = super(TaintedFlowVisitor, self).visit_Name(node)
        if not name in self._labels_map:

            if FlowCategory.__name__ not in node:
                print(node)
                raise RuntimeError("no flow category")

            if node[FlowCategory.__name__] == FlowCategory.SOURCE:
                taint_qualifier = TaintQualifer.TAINTED

            elif node[FlowCategory.__name__] == FlowCategory.SINK:
                taint_qualifier = TaintQualifer.UNTAINTED

            elif node[FlowCategory.__name__] == FlowCategory.SANITIZER:
                taint_qualifier = TaintQualifer.UNTAINTED

            elif node[FlowCategory.__name__] == FlowCategory.REGULAR:
                taint_qualifier = self.next_label()

            self._labels_map[name] = taint_qualifier

        node[TaintQualifer.__name__] = self._labels_map[name]

