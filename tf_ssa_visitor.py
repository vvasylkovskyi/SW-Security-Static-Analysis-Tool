from tf_visitor import TaintedFlowVisitor, TaintQualifer
from ssa_visitor import Keys as SSAKeys


class TaintedFlowSSAVisitor(TaintedFlowVisitor):


    def visit_Name(self, node):
        name = node[SSAKeys.SSA_NAME]
        self.assign_taint_qualifier(node, name)