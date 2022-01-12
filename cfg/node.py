from collections import namedtuple


class Node(object):
    """A Control Flow Graph node that contains a list of ingoing and outgoing nodes and a list of its variables."""

    def __init__(self, label, ast_node, *, line_number, path):
        """Create a Node that can be used in a CFG.
        Args:
            label (str): The label of the node, describing the expression it represents.
            line_number(Optional[int]): The line of the expression the Node represents.
        """
        self.ingoing = list()
        self.outgoing = list()

        self.label = label
        self.ast_node = ast_node
        self.line_number = line_number
        self.path = path

        # Used by the Fixedpoint algorithm
        self.old_constraint = set()
        self.new_constraint = set()


ControlFlowNode = namedtuple(
    'ControlFlowNode',
    (
        'test',
        'last_nodes',
        'break_statements'
    )
)

ConnectStatements = namedtuple(
    'ConnectStatements', 'first_statement last_statements break_statements')


class FunctionNode(Node):
    """CFG Node that represents a function definition.

    Used as a dummy for creating a list of function definitions.    
    """

    def __init__(self, ast_node):
        """Create a function node.

        This node is a dummy node representing a function definition
        """
        super(FunctionNode, self).__init__(self.__class__.__name__, ast_node)


class IgnoredNode(object):
    """Ignored Node sent from a ast node that is not yet implemented."""
    pass


class EntryExitNode(Node):
    """CFG Node that represents a Exit or an Entry node."""

    def __init__(self, label):
        super(EntryExitNode, self).__init__(
            label, None, line_number=None, path=None)
