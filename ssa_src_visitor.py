from src_visitor import SrcVisitor
from ssa_visitor import Keys

class SSASrcVisitor(SrcVisitor):

    def visit_Name(self, node):
        return node[Keys.SSA_NAME]