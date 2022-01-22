from collections import defaultdict

from visitors import Visitor
from ps_visitor import Keys as PathSensitivityKeys, default_conditions


class Keys(PathSensitivityKeys):
    SSA_NAME = "ssa_name"

DEBUG = 1
DEBUG = 0


class ScopedSingleStaticAssignmentVisitor(Visitor):

    def __init__(self, ast):
        super(ScopedSingleStaticAssignmentVisitor, self).__init__(ast)
        self.super = super(ScopedSingleStaticAssignmentVisitor, self)

        self._ssa_variable_map = dict() #map ssa back to original name
        self._variable_ssa_map = {tuple(default_conditions):defaultdict(list)} #for every scope access ssa from name
        self._scope = None
        self._scope_ssa_set = defaultdict(set)  # do not duplicate ssa variables

    # TODO FIX
# TODO FIX
# TODO FIX

    @property
    def ssa_variable_map(self):
        return self._ssa_variable_map


    @property
    def variable_ssa_map(self):
        return self._variable_ssa_map


    def initialize_scope(self):

        def p(s):
            if DEBUG:
                print("initialize_scope ", s)
                print(self._variable_ssa_map)

        p("begin")

        self._variable_ssa_map[self._scope] = defaultdict(list)
        inscope = set()
        scopes = len(self._scope)
        i = 1
        while i < scopes:
            for k,v in self._variable_ssa_map[self._scope[:i]].items():
                for n in v:
                    if n not in inscope:
                        self._variable_ssa_map[self._scope][k].append(n)
                inscope.update(v)
            i+=1

        p("end")


    def make_non_scope_overlaping_ssa_name(self, name):
        i = len(self._variable_ssa_map[self._scope][name]) #creates empty list for name in self._variable_ssa_map[self._scope]
        ssa_name = f"{name}_{i}"
        while ssa_name in self._ssa_variable_map:
            i += 1
            ssa_name = f"{name}_{i}"
        return ssa_name


    def make_ssa_name(self, name):

        def p(s):
            if DEBUG:
                print("make_ssa_name ", s, name)
                print(self._variable_ssa_map)

        p("begin")

        ssa_name = self.make_non_scope_overlaping_ssa_name(name)
        self._ssa_variable_map[ssa_name] = name

        self._variable_ssa_map[self._scope][name].append(ssa_name)
        self._scope_ssa_set[self._scope].add(ssa_name)

        p("end")

        return ssa_name


    def visit_body_line(self, node):
        def p():
            if DEBUG:
                print()
                print()
                print("visit_body_line")
                print(node['lineno'])
                print()
        p()
        self._scope = tuple(node[Keys.CONDITIONS])
        if not self._scope in self._variable_ssa_map:
            self.initialize_scope()
        return self.super.visit_body_line(node)


    def visit_Assign_target(self, node):
        # print("visit_Assign_target")
        # print(node['lineno'], self._scope)
        # print()

        target_id = self.super.visit_Name(node)

        node[Keys.SSA_NAME] = self.make_ssa_name(target_id)

        return target_id


    def visit_Name(self, node):
        """
if(c > 0):
    a = b()
    if(c < 3):
        a = f(a)
    else:
        c = d(a)
e(a,c)
        """
        # print(node['lineno'], self._scope)
        # print()

        name = self.super.visit_Name(node)

        if DEBUG:
            print("visit_Name")
            print(name, self._variable_ssa_map)
            print()

        if name in self._variable_ssa_map[self._scope]:
            node[Keys.SSA_NAME] = self._variable_ssa_map[self._scope][name][-1]
        else:
            node[Keys.SSA_NAME] = self.make_ssa_name(name)

        return name