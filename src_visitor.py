import visitors

class SrcVisitor(visitors.Visitor):

    def visit_Module(self, node):
        self.indentation_level=0
        return "\n".join(self.visit_body(node['body']))

    def visit_Assign(self, node):
        targets, value = super(SrcVisitor, self).visit_Assign(node)
        return f"{self.indentation_level * SrcVisitor.INDENTATION}{','.join(targets)}={value}"

    def visit_Call(self, node):
        func, args = super(SrcVisitor, self).visit_Call(node)
        return f"{func}({','.join(args)})"

    def visit_Expr(self, node):
        value = super(SrcVisitor, self).visit_Expr(node)
        return f"{self.indentation_level * SrcVisitor.INDENTATION}{value}"

    def visit_BinOp(self, node):
        (left, op, right) = super(SrcVisitor, self).visit_BinOp(node)
        return f"{left}{op}{right}"

    def visit_Compare(self, node):
        (left, ops, comparators) = super(SrcVisitor, self).visit_Compare(node)
        return f"{left}{','.join(ops)}{','.join(comparators)}"

    def visit_While(self, node):

        indentation = self.indentation_level * SrcVisitor.INDENTATION
        self.indentation_level += 1
        (test, body) = super(SrcVisitor, self).visit_While(node)
        self.indentation_level -= 1

        representation = f"{indentation}while ({test}):\n"
        representation += "\n".join(body)
        return representation

    def visit_If(self, node):

        indentation = self.indentation_level * SrcVisitor.INDENTATION
        self.indentation_level += 1
        (test, body, orelse) = super(SrcVisitor, self).visit_If(node)
        self.indentation_level -= 1

        representation = f"{indentation}if({test}):\n"

        representation += "\n".join(body)

        if orelse:
            representation += f"\n{indentation}else:\n"
            representation += "\n".join(orelse)

        return representation

    def visit_Break(self, node):
        return f"{self.indentation_level * SrcVisitor.INDENTATION}{super(SrcVisitor, self).visit_Break(node)}"

    def visit_Continue(self, node):
        return f"{self.indentation_level * SrcVisitor.INDENTATION}{super(SrcVisitor, self).visit_Continue(node)}"



if __name__ == '__main__':
    visitors.Driver.drive(SrcVisitor)