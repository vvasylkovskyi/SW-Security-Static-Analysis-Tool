
import ast
from cfg.right_hand_side_visitor import RightHandSideVisitor
from cfg.label_visitor import LabelVisitor
from cfg.node import AssignmentNode, IgnoredNode, Node, EntryExitNode, ControlFlowNode, FunctionNode, ConnectStatements


class Visitor(ast.NodeVisitor):
    """A Control Flow Graph containing a list of nodes."""

    def __init__(self, tree):
        super().__init__()
        """Create an empty CFG."""
        self.nodes = list()
        self.undecided = False
        self.init_cfg(tree)

    # def visit_Module(self, node):
    #     print("HEYdsdfsdfdsfsd")
    #     print("Node: ", node.body)

    #     # Magically, this happens after we call super().__init__()
    #     return self.handle_initialize_statements(node.body)

    def init_cfg(self, tree):
        print("Starting visitor")

        entry_node = self.append_node(EntryExitNode("Entry node"))

        # print("Node: ", tree.body)

        # print("Self nodes: ", self.nodes)
        statements = self.handle_initialize_statements(tree.body)

        # print("THE END STATEMENTS")
        first_node = statements.first_statement

        entry_node.connect(first_node)
        # print("First! ", first_node)
        exit_node = self.append_node(EntryExitNode("Exit node"))

        last_nodes = statements.last_statements
        # print("Last Nodes: ", last_nodes)
        exit_node.connect_predecessors(last_nodes)
        # print("Last! ", last_nodes)
        # print("-----NODES -----")
        # print(self.nodes)
        # print("----------------")

        # visit_result = self.visit(tree)
        # print(visit_result)

    def append_node(self, node):
        """Append a node to the CFG and return it."""
        self.nodes.append(node)
        return node

    def connect_control_flow_node(self, control_flow_node, next_node):
        """Connect a ControlFlowNode properly to the next_node."""
        for last in control_flow_node[1]:                         # list of last nodes in ifs and elifs
            if isinstance(next_node, ControlFlowNode):
                # connect to next if test case
                last.connect(next_node.test)
            else:
                last.connect(next_node)

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

    def connect_nodes(self, nodes):
        """Connect the nodes in a list linearly."""
        for n, next_node in zip(nodes, nodes[1:]):
            if isinstance(n, ControlFlowNode):             # case for if
                self.connect_control_flow_node(n, next_node)
            elif isinstance(next_node, ControlFlowNode):  # case for if
                n.connect(next_node[0])
            else:
                n.connect(next_node)

    def add_if_label(self, CFG_node):
        """Prepend 'if ' and append ':' to the label of a Node."""
        CFG_node.label = 'if ' + CFG_node.label + ':'

    def add_elif_label(self, CFG_node):
        """Add the el to an already add_if_label'ed Node."""
        CFG_node.label = 'el' + CFG_node.label

    def handle_initialize_statements(self, statements):
        cfg_statements = list()
        break_nodes = list()

        for statement in statements:
            print("--------Statement-------")
            print("Stmt: ", statement)
            node = self.visit(statement)
            print("------------------------")
            if self.should_connect_node(node):
                cfg_statements.append(node)

        print("Final cfg statements: ", cfg_statements)
        self.connect_nodes(cfg_statements)
        if cfg_statements:  # When body of module only contains ignored nodes
            first_statement = self.get_first_statement(cfg_statements[0])
            last_statements = self.get_last_statements(cfg_statements)
            return ConnectStatements(first_statement=first_statement, last_statements=last_statements, break_statements=break_nodes)

    def assignment_call_node(self, left_hand_label, ast_node):
        # print("HERE")
        """Handle assignments that contain a function call on its right side."""
        self.undecided = True  # Used for handling functions in assignments
        rhs_visitor = RightHandSideVisitor()
        rhs_visitor.visit(ast_node.value)
        # print("VALUE: ", ast_node.value)
        call = self.visit(ast_node.value)
        print("CALL: ", call)
        call_label = ''
        call_assignment = None
        # call_label = call.label
        # call_assignment = AssignmentNode(left_hand_label + ' = ' + call_label, left_hand_label,
        #  ast_node, rhs_visitor.result, line_number = ast_node.lineno, path = "")
        call_label = call.label
        call_assignment = AssignmentNode(left_hand_label + ' = ' + call_label, left_hand_label,
                                         ast_node, rhs_visitor.result, line_number=ast_node.lineno, path="")

        self.nodes.append(call_assignment)
        return call_assignment

    def get_names(self, node, result):
        """Recursively finds all names."""
        if isinstance(node, ast.Name):
            return node.id + result
        elif isinstance(node, ast.Subscript):
            return result
        else:
            return self.get_names(node.value, result + '.' + node.attr)

    def extract_left_hand_side(self, target):
        """Extract the left hand side varialbe from a target.
        Removes list indexes, stars and other left hand side elements.
        """
        left_hand_side = self.get_names(target, '')

        left_hand_side.replace('*', '')
        if '[' in left_hand_side:
            index = left_hand_side.index('[')
            left_hand_side = target[0:index]

        return left_hand_side

    def handle_or_else(self, orelse, test):
        if isinstance(orelse[0], ast.If):
            control_flow_node = self.visit(orelse[0])
            self.add_elif_label(control_flow_node.test)
            test.connect(control_flow_node.test)
            return control_flow_node.last_nodes
        else:
            else_connect_statements = self.handle_initialize_statements(orelse)
            test.connect(else_connect_statements.first_statement)
            return else_connect_statements.last_statements

    def visit_Call(self, node):
        print("Visit Call")
        label_visitor = LabelVisitor()
        label_visitor.visit(node)
        # if
        print("label: ", label_visitor.result)
        func_call_node = Node(label_visitor.result, node,
                              line_number=node.lineno, path="")
        if not self.undecided:
            self.nodes.append(func_call_node)
        self.undecided = False

        return func_call_node

    def visit_Assign(self, node):
        print("Visit Assign")
        rhs_visitor = RightHandSideVisitor()
        # print("Node value: ", node.value)
        rhs_visitor.visit(node.value)
        # print("Targets: ", node.targets)
        if isinstance(node.value, ast.Call):  # x = call()
            print("TESTESTSE")
            label_visitor = LabelVisitor()
            label_visitor.visit(node.targets[0])
            # print("Targets: ", node.targets[0])
            # print("WHAT IS THE RESULT : ", label_visitor.result)
            return self.assignment_call_node(label_visitor.result, node)
        else:
            label_visitor = LabelVisitor()
            print("HEREdsdsd")
            label_visitor.visit(node)
            return self.append_node(AssignmentNode(label_visitor.result, self.extract_left_hand_side(node.targets[0]), node, rhs_visitor.result, line_number=node.lineno, path=""))

    def visit_Expr(self, node):
        print("Visit expr:", node.value)
        return self.visit(node.value)

    def visit_If(self, node):
        print("Node TEST: ", node.test)
        label_visitor = LabelVisitor()
        label_visitor.visit(node.test)
        test = self.append_node(
            Node(label_visitor.result, node, line_number=node.lineno, path=""))
        self.add_if_label(test)
        body_connect_statements = self.handle_initialize_statements(node.body)
        test.connect(body_connect_statements.first_statement)

        if node.orelse:
            print("IS HERE")
            oresle_last_nodes = self.handle_or_else(node.orelse, test)
            body_connect_statements.last_statements.extend(oresle_last_nodes)
        else:
            body_connect_statements.last_statements.append(test)
        last_statements = body_connect_statements.last_statements
        return ControlFlowNode(test, last_statements)
