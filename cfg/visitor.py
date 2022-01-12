
import ast
from cfg.right_hand_side_visitor import RightHandSideVisitor
from cfg.node import IgnoredNode, Node, EntryExitNode, ControlFlowNode, FunctionNode, ConnectStatements


class Visitor(ast.NodeVisitor):
    """A Control Flow Graph containing a list of nodes."""

    def __init__(self, tree):
        super().__init__()
        """Create an empty CFG."""
        self.nodes = list()
        self.init_cfg(tree)

    # def visit_Module(self, node):
    #     print("HEYdsdfsdfdsfsd")
    #     print("Node: ", node.body)

    #     # Magically, this happens after we call super().__init__()
    #     return self.handle_initialize_statements(node.body)

    def init_cfg(self, tree):
        print("Starting visitor")

        self.append_node(EntryExitNode("Entry node"))

        print("Node: ", tree.body)

        print("Self nodes: ", self.nodes)
        statements = self.handle_initialize_statements(tree.body)

        first_node = statements.first_statement

        print("First! ", first_node)
        self.append_node(EntryExitNode("Exit node"))

        # last_nodes = statements.last_statements
        # print("Last! ", last_nodes)

        visit_result = self.visit(tree)
        # print(visit_result)

    def append_node(self, Node):
        """Append a node to the CFG and return it."""
        self.nodes.append(Node)
        return Node

    def should_connect_node(self, node):
        if isinstance(node, IgnoredNode):
            return False
        elif isinstance(node, ControlFlowNode):
            return True
        elif type(node) is FunctionNode:
            return False
        else:
            return True

    def get_first_statement(self, node_or_tuple):
        """Find the first statement of the provided object.
        Returns:
            The node if is is a node.
            The first element in the tuple if it is a tuple.
        """
        if isinstance(node_or_tuple, tuple):
            return node_or_tuple[0]
        else:
            return node_or_tuple

    def get_last_statements(self, cfg_statements):
        """Retrieve the last statements from a cfg_statments list."""
        if isinstance(cfg_statements[-1], ControlFlowNode):
            return cfg_statements[-1].last_nodes
        else:
            return [cfg_statements[-1]]

    def handle_initialize_statements(self, statements):
        cfg_statements = list()
        break_nodes = list()

        # print("Statements: ", statements)
        for statement in statements:
            print("--------Statement-------")
            print("Stmt: ", statement)
            node = self.visit(statement)
            print("Node: ", node)
            print("------------------------")
            # print("Node ? :", node)
            if self.should_connect_node(node):
                cfg_statements.append(node)

        # self.connect_nodes(cfg_statements)
        print("Final cfg statements: ", cfg_statements)
        if cfg_statements:  # When body of module only contains ignored nodes
            # print("HERE")
            first_statement = self.get_first_statement(cfg_statements[0])
            print("First: ", first_statement)
            last_statements = self.get_last_statements(cfg_statements)
            print("Last: ", last_statements)
            return ConnectStatements(first_statement=first_statement, last_statements=last_statements, break_statements=break_nodes)

    def visit_Call(self, node):
        print("Visit Call")

    def visit_Assign(self, node):
        print("Visit Assign")
        rhs_visitor = RightHandSideVisitor()

    def visit_Expr(self, node):
        print("Visit expr:", node.value)
        return self.visit(node.value)
