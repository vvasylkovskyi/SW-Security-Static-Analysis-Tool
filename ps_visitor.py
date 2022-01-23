"""
"""

from visitors import Visitor, AstTypes


class Keys:
    CONDITIONS = "conditions"


default_conditions = [(True, True)]


class PathSensitivityVisitor(Visitor):


    def __init__(self, ast):
        super(PathSensitivityVisitor, self).__init__(ast)
        self.super = super(PathSensitivityVisitor, self)

        self._current_conditions = default_conditions.copy()
        self._conditions = default_conditions.copy()


    @property
    def conditions(self):
        return self._conditions


    def visit_body_line(self, node):
        node[Keys.CONDITIONS] = self._current_conditions.copy()
        return self.super.visit_body_line(node)


    def visit_Compare(self, node):
        (left, ops, comparators) = self.super.visit_Compare(node)
        return f"{left} {','.join(ops)} {','.join(comparators)}"


    def visit_While(self, node):

        test = self.visit_If_test(node[AstTypes.While.test])
        condition = (test, True)

        self._conditions.append(condition)

        self._current_conditions.append(condition)

        body = self.visit_body(node[AstTypes.While.body])

        self._current_conditions.pop()

        return test, body


    def visit_If(self, node):

        test = self.visit_If_test(node[AstTypes.If.test])

        condition = (test, True)
        self._conditions.append(condition)

        self._current_conditions.append(condition)

        body = self.visit_body(node[AstTypes.If.body])

        condition = (test, False)
        self._conditions.append(condition)

        self._current_conditions[-1] = condition

        orelse = self.visit_body(node[AstTypes.If.orelse])

        self._current_conditions.pop()

        return test, body, orelse