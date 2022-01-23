from tf_visitor import TaintQualifer, CallArgKeys
from visitors import Visitor, AstTypes


class TaintedFlowSrcVisitor(Visitor):

    def __init__(self, ast):
        super(TaintedFlowSrcVisitor, self).__init__(ast)
        self.super = super(TaintedFlowSrcVisitor, self)
        self.indentation_level=0


    def visit_Module(self, node):
        return "\n".join(self.visit_body(node['body']))


    def visit_Assign_target(self, node):
        return self.visit_Name(node)


    def visit_Assign(self, node):
        targets, value = self.super.visit_Assign(node)
        return f"{node[AstTypes.Generic.lineno]:>2}: {self.indentation_level * Visitor.INDENTATION}{', '.join(targets)} = {value}"


    def visit_Compare(self, node):
        left = self.visit_Compare_operand(node[AstTypes.Compare.left])
        comparators = list(self.visit_Compare_operand(node) for node in node[AstTypes.Compare.comparators])
        ops = self.visit_Compare_ops(node[AstTypes.Compare.ops])
        return f"{left} {', '.join(ops)} {','.join(comparators)}"


    def visit_Call_arg(self, node):
        arg = self.super.visit_Call_arg(node)
        return f"{node[CallArgKeys.Call_arg_TaintQualifer]} {node[CallArgKeys.Call_arg]} {arg}"


    def visit_Call_args(self, nodes):
        return ', '.join(self.visit_Call_arg(node) for node in nodes)


    def visit_Call_func(self, node):
        return self.visit_Name(node)


    def visit_Call(self, node):
        return f"{self.visit_Call_func(node[AstTypes.Call.func])}({self.visit_Call_args(node[AstTypes.Call.args])})"


    def visit_While(self, node):

        indentation = self.indentation_level * Visitor.INDENTATION
        self.indentation_level += 1
        (test, body) = self.super.visit_While(node)
        self.indentation_level -= 1

        representation = f"{node[AstTypes.Generic.lineno]:>2}: {indentation}while ({test}):\n"
        representation += "\n".join(body)
        return representation


    def visit_If(self, node):

        indentation = self.indentation_level * Visitor.INDENTATION
        self.indentation_level += 1
        (test, body, orelse) = self.super.visit_If(node)
        self.indentation_level -= 1

        representation = f"{node[AstTypes.Generic.lineno]:>2}: {indentation}if({test}):\n"
        representation += "\n".join(body)
        if orelse:
            representation += f"\n{node[AstTypes.Generic.lineno]+len(body):>2}: {indentation}else:\n"
            representation += "\n".join(orelse)
        return representation


    def visit_Expr(self, node):
        value = self.super.visit_Expr(node)
        return f"{node[AstTypes.Generic.lineno]:>2}: {self.indentation_level * Visitor.INDENTATION}{value}"


    def visit_BinOp(self, node):
        (left, op, right) = self.super.visit_BinOp(node)
        return f"{left} {op} {right}"


    def visit_Name(self, node):
        return f"{node[TaintQualifer.__name__]} {self.super.visit_Name(node)}"

    def visit_Constant(self, node):
        return f"{node[TaintQualifer.__name__]} {self.super.visit_Constant(node)}"


    def visit_Break(self, node):
        return f"{self.indentation_level * Visitor.INDENTATION}{self.super.visit_Break(node)}"