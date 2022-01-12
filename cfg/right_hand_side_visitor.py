"""Contains a class that finds all names.
Used to find all variables on a right hand side(RHS) of assignment.
"""
from ast import NodeVisitor


class RightHandSideVisitor(NodeVisitor):
    """Visitor collecting all names."""

    def __init__(self):
        """Initialize result as list."""
        self.result = list()

    def visit_Name(self, node):
        self.result.append(node.id)

    def visit_Call(self, node):
        if node.args:
            for arg in node.args:
                self.visit(arg)
        if node.keywords:
            for keyword in node.keywords:
                self.visit(keyword)
