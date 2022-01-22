from collections import defaultdict

from visitors import Visitor


class Keys:
    SSA_NAME = "ssa_name"


class SingleStaticAssignmentVisitor(Visitor):

    def __init__(self, ast):
        super(SingleStaticAssignmentVisitor, self).__init__(ast)
        self.super = super(SingleStaticAssignmentVisitor, self)

        self._variable_ssa_map = defaultdict(list)
        self._ssa_variable_map = dict()
        self._scope = None
        self._scoped_variable_ssa_map = defaultdict(dict)

#TODO scope map {cond1 : {a_0: a}}

    @property
    def variable_ssa_map(self):
        return self._variable_ssa_map


    @property
    def ssa_variable_map(self):
        return self._ssa_variable_map


    def make_ssa_name(self, name):
        ssa_name = f"{name}_{len(self._variable_ssa_map[name])}"
        self._variable_ssa_map[name].append(ssa_name)
        self._ssa_variable_map[ssa_name] = name
        return ssa_name


    def visit_Assign_target(self, node):

        target_id = self.super.visit_Name(node)
        node[Keys.SSA_NAME] = self.make_ssa_name(target_id)

        return target_id


    def visit_Name(self, node):

        name = self.super.visit_Name(node)

        if name not in self._variable_ssa_map:
            node[Keys.SSA_NAME] = self.make_ssa_name(name)
        else:
            node[Keys.SSA_NAME] = self._variable_ssa_map[name][-1]

        return name