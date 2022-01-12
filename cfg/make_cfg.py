from cfg.visitor import Visitor
from .expr_visitor import ExprVisitor


class CFG():
    def __init__(
        self,
        nodes,
    ):
        self.nodes = nodes

    def __repr__(self):
        output = ''
        for x, n in enumerate(self.nodes):
            output = ''.join(
                (output, 'Node: ' + str(x) + ' ' + repr(n), '\n\n'))
        return output

    def __str__(self):
        output = ''
        for x, n in enumerate(self.nodes):
            output = ''.join(
                (output, 'Node: ' + str(x) + ' ' + str(n), '\n\n'))
        return output


def make_cfg(tree):
    visitor = Visitor(tree)

    return CFG(visitor.nodes)
