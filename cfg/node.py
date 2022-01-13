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

    def connect(self, successor):
        """Connect this node to its successor node by setting its outgoing and the successors ingoing."""
        if isinstance(self, ConnectToExitNode) and not type(successor) is EntryExitNode:
            return
        self.outgoing.append(successor)
        successor.ingoing.append(self)

    def connect_predecessors(self, predecessors):
        """Connect all nodes in predecessors to this node."""
        for n in predecessors:
            self.ingoing.append(n)
            n.outgoing.append(self)

    def __str__(self):
        """Print the label of the node."""
        return ' '.join(('Label: ', self.label))

    # def __repr__(self):
    #     """Print a representation of the node."""
    #     label = ' '.join(('Label: ', self.label))
    #     line_number = 'Line number: ' + str(self.line_number)
    #     outgoing = ''
    #     ingoing = ''
    #     if self.ingoing is not None:
    #         ingoing = ' '.join(
    #             ('ingoing:\t', str([x.label for x in self.ingoing])))
    #     else:
    #         ingoing = ' '.join(('ingoing:\t', '[]'))

    #     if self.outgoing is not None:
    #         outgoing = ' '.join(
    #             ('outgoing:\t', str([x.label for x in self.outgoing])))
    #     else:
    #         outgoing = ' '.join(('outgoing:\t', '[]'))

    #     if self.old_constraint is not None:
    #         old_constraint = 'Old constraint:\t ' + \
    #             ', '.join([x.label for x in self.old_constraint])
    #     else:
    #         old_constraint = 'Old constraint:\t '

    #     if self.new_constraint is not None:
    #         new_constraint = 'New constraint: ' + \
    #             ', '.join([x.label for x in self.new_constraint])
    #     else:
    #         new_constraint = 'New constraint:'
    #     return '\n' + '\n'.join((label, line_number, ingoing, outgoing, old_constraint, new_constraint))


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


class ConnectToExitNode():
    pass


class AssignmentNode(Node):
    """CFG Node that represents an assignment."""

    def __init__(self, label, left_hand_side, ast_node, right_hand_side_variables, *, line_number, path):
        """Create an Assignment node.
        Args:
            label (str): The label of the node, describing the expression it represents.
            left_hand_side(str): The variable on the left hand side of the assignment. Used for analysis.
            right_hand_side_variables(list[str]): A list of variables on the right hand side.
            line_number(Optional[int]): The line of the expression the Node represents.
        """
        super(AssignmentNode, self).__init__(
            label, ast_node, line_number=line_number, path=path)
        self.left_hand_side = left_hand_side
        self.right_hand_side_variables = right_hand_side_variables

    def __repr__(self):
        output_string = super(AssignmentNode, self).__repr__()
        output_string += '\n'
        return ''.join((output_string, 'left_hand_side:\t', str(self.left_hand_side), '\n', 'right_hand_side_variables:\t', str(self.right_hand_side_variables)))
