from tf_visitor import TaintQualifer
from tf_src_visitor import TaintedFlowSrcVisitor
from ssa_visitor import Keys

class TaintedFlowSSASrcVisitor(TaintedFlowSrcVisitor):

    def visit_Name(self, node):
        return f"{node[TaintQualifer.__name__]} {node[Keys.SSA_NAME]}"