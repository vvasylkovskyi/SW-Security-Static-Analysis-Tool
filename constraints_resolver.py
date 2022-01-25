

from curses.ascii import TAB
from queue import Empty
from tf_visitor import TaintQualifer
from constraints_visitor import Constraint
from collections import namedtuple

Vulnerabilty = namedtuple("Vulnerability", ("name", "source", "sink"))


class ConstraintsResolver:
    queue_of_equations = list()

    def add_to_queue_of_equations(self, equation):
        self.queue_of_equations.append(equation)

    def remove_equation_from_the_queue(self, equation):
        self.queue_of_equations.remove(equation)

    def is_illegal_flow(self, constraint):
        # if tainted <= untainted
        # means it is illegal flow
        left_hand_side = constraint.lhs_tq
        right_hand_side = constraint.rhs_tq

        if left_hand_side == TaintQualifer.TAINTED and right_hand_side == TaintQualifer.UNTAINTED:
            return True
        return False

    def is_idempotent_equation(self, constraint):
        if (constraint[1] == TaintQualifer.UNTAINTED and constraint[3] == TaintQualifer.TAINTED
                or constraint[1] == TaintQualifer.UNTAINTED and constraint[3] == TaintQualifer.UNTAINTED
                or constraint[1] == TaintQualifer.TAINTED and constraint[3] == TaintQualifer.TAINTED):
            return True
        return False

    def get_next_best_constraint(self, resolution, new_constraint):
        if self.is_idempotent_equation(new_constraint):
            return resolution
        if not self.is_idempotent_equation(new_constraint) and new_constraint not in self.queue_of_equations:
            self.add_to_queue_of_equations(new_constraint)

        return resolution

    def is_sink(self, qualifier, sink_qualifiers):
        for sink_qualifier in sink_qualifiers:
            if qualifier == sink_qualifier:
                return True
        return False

    def try_simplify_equation(self, resolution, new_constraint, sink_qualifiers):
        resolution_lhs = resolution.lhs_tq
        resolution_rhs = resolution.rhs_tq

        new_constraint_lhs = new_constraint.lhs_tq
        new_constraint_rhs = new_constraint.rhs_tq

        if new_constraint_lhs == resolution_rhs and not self.is_sink(new_constraint_lhs, sink_qualifiers) and not self.is_sink(resolution_rhs, sink_qualifiers):
            return Constraint(new_constraint.line, resolution.lhs_tq, resolution.lhs_id, new_constraint.rhs_tq, new_constraint.rhs_id)
        elif new_constraint_rhs == resolution_lhs and not self.is_sink(new_constraint_rhs, sink_qualifiers) and not self.is_sink(resolution_lhs, sink_qualifiers):
            return Constraint(new_constraint.line, new_constraint.lhs_tq, new_constraint.lhs_id, resolution.rhs_tq, resolution.rhs_id)
        else:
            return False

    def resolve_equation(self, resolution, new_constraint, sink_qualifiers):
        if self.is_idempotent_equation(new_constraint):
            return resolution

        if self.try_simplify_equation(resolution, new_constraint, sink_qualifiers):
            return self.try_simplify_equation(resolution, new_constraint, sink_qualifiers)
        else:
            return self.get_next_best_constraint(resolution, new_constraint)

    def debug_print_compare_constraints(self, resolution, new_constraint):
        print("---------------")
        print("Resolution: ", resolution)
        print("New Constraint: ", new_constraint)

    def reduce_constraints(self, resolution, new_constraint, sink_qualifiers):
        # self.debug_print_compare_constraints(resolution, new_constraint)
        return self.resolve_equation(resolution, new_constraint,  sink_qualifiers)

    def is_constraints_contain_illegal_flow(self, constraints):
        for constraint in constraints:
            if self.is_illegal_flow(constraint):
                print("Is illegal flow!")
                return True
        return False

    def replace_qualifiers_with_sinks_and_sources(self, resolution, source_qualifiers, sink_qualifiers):
        lhs = resolution.lhs_tq
        rhs = resolution.rhs_tq

        for source_qualifier in source_qualifiers:
            if source_qualifier == lhs:
                lhs = TaintQualifer.TAINTED
            elif source_qualifier == rhs:
                rhs = TaintQualifer.TAINTED

        for sink_qualifier in sink_qualifiers:
            if sink_qualifier == lhs:
                lhs = TaintQualifer.UNTAINTED
            elif sink_qualifier == rhs:
                rhs = TaintQualifer.UNTAINTED

        return Constraint(resolution.line, lhs, resolution.lhs_id, rhs, resolution.rhs_id)

    def contains_target(self, constraint, qualifiers):
        lhs = constraint.lhs_tq
        rhs = constraint.rhs_tq
        for source_qualifier in qualifiers:
            if lhs == source_qualifier or rhs == source_qualifier:
                return True
        return False

    def try_illegal_flow(self, resolution, source_qualifiers, sink_qualifiers):
        resolution = self.replace_qualifiers_with_sinks_and_sources(
            resolution, source_qualifiers, sink_qualifiers)

        if self.is_illegal_flow(resolution):
            print("Is illegal flow!")
            return True

        return False

    def has_vulnerability(self, constraints, source_qualifiers, sink_qualifiers, tf_labels):
        constraint_index = 0

        resolution = constraints[constraint_index]  # Starting always from zero

        while not self.contains_target(resolution, sink_qualifiers) and constraint_index < len(constraints) - 1:
            constraint_index += 1
            resolution = constraints[constraint_index]
            self.add_to_queue_of_equations(resolution)

        if self.try_illegal_flow(resolution, source_qualifiers, sink_qualifiers):
            print("Is illegal flow!")
            return True

        while len(constraints) - 1 > constraint_index:
            constraint_index += 1
            print("[Index:", constraint_index, "] Constraint: ",
                  constraints[constraint_index])

            if self.try_illegal_flow(constraints[constraint_index], source_qualifiers, sink_qualifiers):
                print("Is illegal flow!")
                return True

            resolution = self.reduce_constraints(
                resolution, constraints[constraint_index],  sink_qualifiers)

            if self.contains_target(resolution, sink_qualifiers):
                print("Contains sink")
                resolution = self.replace_qualifiers_with_sinks_and_sources(
                    resolution, source_qualifiers, sink_qualifiers)

            if self.is_illegal_flow(resolution):
                print("Is illegal flow!")
                return True

        print("QUEUE contents: ", self.queue_of_equations)

        # Empty the queue
        copy_queue = self.queue_of_equations

        if self.queue_of_equations is Empty:
            return False

        while not self.queue_of_equations is Empty:
            can_reduce = False
            for constraint in self.queue_of_equations:
                new_resolution = self.reduce_constraints(
                    resolution, constraint, sink_qualifiers)
                if new_resolution != resolution:
                    can_reduce = True
                    resolution = new_resolution
                    self.remove_equation_from_the_queue(constraint)
                    is_illegal_flow = self.try_illegal_flow(
                        resolution, source_qualifiers, sink_qualifiers)
                    if is_illegal_flow:
                        return True

            if can_reduce == False:
                break  # Cannot reduce equations anymore

            if self.is_illegal_flow(resolution):
                print("Is illegal flow!")
                return True

        print("RESOLUTION SO FAR: ", resolution)
        print("SINKS VARS: ", sink_qualifiers)
        print("TF_LABELS: ", tf_labels)

        return self.try_illegal_flow(resolution, source_qualifiers, sink_qualifiers)

    def get_qualifiers(self, targets, tf_labels):
        qualifiers = list()
        for target in targets:
            for key in tf_labels:
                if target in key:
                    qualifiers.append(tf_labels[key])
        return qualifiers

    def resolve_constraints_and_find_vulnerabilties(self, constraints, pattern, sources_ssa, sinks_ssa, tf_labels):
        sources = pattern['sources']
        sinks = pattern['sinks']
        name = pattern['vulnerability']
        vulnerabilities = list()
        for source in sources:
            for sink in sinks:
                print("SINK: ", sink)
                sink_qualifiers = self.get_qualifiers(
                    [sink], tf_labels)
                source_qualifiers = self.get_qualifiers(
                    sources, tf_labels)
                print("SINK QUALIFIERS: ", sink_qualifiers)
                print("Source QUALIFIERS: ", source_qualifiers)
                if self.has_vulnerability(constraints, source_qualifiers, sink_qualifiers, tf_labels):
                    vulnerabilities_index = len(vulnerabilities) + 1
                    vulnerability_name = name + "_" + vulnerabilities_index.__str__()
                    vulnerability = Vulnerabilty(
                        vulnerability_name, source, sink)
                    vulnerabilities.append(vulnerability)
        return vulnerabilities
