
from visitors import Visitor


class Keys:
    POINTER = "p"


class PointersVisitor(Visitor):

    def __init__(self, ast):
        super(PointersVisitor, self).__init__(ast)
        self.super = super(PointersVisitor, self)
        self._pointers = dict()


    @property
    def pointers(self):
        return self._pointers


    def visit_Assign(self, node):
        value = self.super.visit_Assign(node)
        node[Keys.POINTER] = id(node)
        self._pointers[node[Keys.POINTER]] = node


    def visit_While(self, node):
        value = self.super.visit_While(node)
        node[Keys.POINTER] = id(node)
        self._pointers[node[Keys.POINTER]] = node


    def visit_Break(self, node):
        value = self.super.visit_Break(node)
        node[Keys.POINTER] = id(node)
        self._pointers[node[Keys.POINTER]] = node


    def visit_Compare(self, node):
        value = self.super.visit_Compare(node)
        node[Keys.POINTER] = id(node)
        self._pointers[node[Keys.POINTER]] = node


    def visit_Load(self, node):
        value = self.super.visit_Load(node)
        node[Keys.POINTER] = id(node)
        self._pointers[node[Keys.POINTER]] = node


    def visit_Name(self, node):
        value = self.super.visit_Name(node)
        node[Keys.POINTER] = id(node)
        self._pointers[node[Keys.POINTER]] = node


    def visit_Add(self, node):
        value = self.super.visit_Add(node)
        node[Keys.POINTER] = id(node)
        self._pointers[node[Keys.POINTER]] = node


    def visit_Store(self, node):
        value = self.super.visit_Store(node)
        node[Keys.POINTER] = id(node)
        self._pointers[node[Keys.POINTER]] = node


    def visit_Module(self, node):
        value = self.super.visit_Module(node)
        node[Keys.POINTER] = id(node)
        self._pointers[node[Keys.POINTER]] = node


    def visit_Expr(self, node):
        value = self.super.visit_Expr(node)
        node[Keys.POINTER] = id(node)
        self._pointers[node[Keys.POINTER]] = node


    def visit_If(self, node):
        value = self.super.visit_If(node)
        node[Keys.POINTER] = id(node)
        self._pointers[node[Keys.POINTER]] = node


    def visit_Lt(self, node):
        value = self.super.visit_Lt(node)
        node[Keys.POINTER] = id(node)
        self._pointers[node[Keys.POINTER]] = node


    def visit_Constant(self, node):
        value = self.super.visit_Constant(node)
        node[Keys.POINTER] = id(node)
        self._pointers[node[Keys.POINTER]] = node


    def visit_NotEq(self, node):
        value = self.super.visit_NotEq(node)
        node[Keys.POINTER] = id(node)
        self._pointers[node[Keys.POINTER]] = node


    def visit_BinOp(self, node):
        value = self.super.visit_BinOp(node)
        node[Keys.POINTER] = id(node)
        self._pointers[node[Keys.POINTER]] = node


    def visit_Call(self, node):
        value = self.super.visit_Call(node)
        node[Keys.POINTER] = id(node)
        self._pointers[node[Keys.POINTER]] = node


    def visit_Eq(self, node):
        value = self.super.visit_Eq(node)
        node[Keys.POINTER] = id(node)
        self._pointers[node[Keys.POINTER]] = node


    def visit_Gt(self, node):
        value = self.super.visit_Gt(node)
        node[Keys.POINTER] = id(node)
        self._pointers[node[Keys.POINTER]] = node

