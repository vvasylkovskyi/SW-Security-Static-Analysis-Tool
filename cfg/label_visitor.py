from ast import NodeVisitor


class LabelVisitor(NodeVisitor):
    def __init__(self):
        self.result = ''

    def visit_Str(self, node):
        # print("YEYEYsEYEY")
        self.result += "'" + node.s + "'"

    def visit_Name(self, node):
        # print("VISIT NAME?")
        self.result += node.id
