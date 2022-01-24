

from queue import Empty
from tf_visitor import TaintQualifer
from constraints_visitor import Constraint
from collections import namedtuple

Vulnerabilty = namedtuple("Vulnerability", ("name", "source", "sink"))


class ConstraintsResolver:
    queue_of_equations = list()

    def add_to_queue_of_equations(self, equation):
        self.queue_of_equations.append(equation)
        print("ADD QUEUE: ", self.queue_of_equations)

    def remove_equation_from_the_queue(self, equation):
        print("REMOVE QUEUE: ", self.queue_of_equations)
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
            print("IT IS YEE")
            self.add_to_queue_of_equations(new_constraint)

        return resolution

    # TODO. Not working yet.
    def check_if_source_is_being_sanitized(self, constraint):
        print("y")
        constraint_rhs = constraint.rhs_tq
        if constraint_rhs == TaintQualifer.TAINTED:
            print("Sanitizing?")
            return True
        return False

    def try_simplify_equation(self, resolution, new_constraint):
        resolution_lhs = resolution.lhs_tq
        resolution_rhs = resolution.rhs_tq

        new_constraint_lhs = new_constraint.lhs_tq
        new_constraint_rhs = new_constraint.rhs_tq

        if new_constraint_lhs == resolution_rhs:
            return Constraint(new_constraint.line, resolution.lhs_tq, resolution.lhs_id, new_constraint.rhs_tq, new_constraint.rhs_id)
        elif new_constraint_rhs == resolution_lhs:
            return Constraint(new_constraint.line, new_constraint.lhs_tq, new_constraint.lhs_id, resolution.rhs_tq, resolution.rhs_id)
        else:
            return False

    def resolve_equation(self, resolution, new_constraint):
        if self.is_idempotent_equation(new_constraint):
            print("HERE")
            return resolution

        if self.try_simplify_equation(resolution, new_constraint):
            return self.try_simplify_equation(resolution, new_constraint)
        else:
            return self.get_next_best_constraint(resolution, new_constraint)

    def debug_print_compare_constraints(self, resolution, new_constraint):
        print("---------------")
        print("Resolution: ", resolution)
        print("New Constraint: ", new_constraint)

    def reduce_constraints(self, resolution, new_constraint):
        self.debug_print_compare_constraints(resolution, new_constraint)
        return self.resolve_equation(resolution, new_constraint)

    def is_constraints_contain_illegal_flow(self, constraints):
        for constraint in constraints:
            if self.is_illegal_flow(constraint):
                print("Is illegal flow!")
                return True
        return False

    def has_vulnerability(self, constraints):

        # Run and check if contains vulnerability without resolving constraints
        if self.is_constraints_contain_illegal_flow(constraints):
            return True

        first_constraint = constraints[0]  # Starting always from zero

        resolution = first_constraint

        # First Check
        if self.is_illegal_flow(resolution):
            print("Is illegal flow!")
            return True

        # Run the constraints and reduce them until we reach the illegal flow,
        # or until we finish the algorithm. If at the end of the algorithm there is no illegal flow, then no vulnerability exists
        constraint_index = 0
        while len(constraints) - 1 > constraint_index:
            constraint_index += 1
            print("[Index:", constraint_index, "] Constraint: ",
                  constraints[constraint_index])

            if self.is_illegal_flow(constraints[constraint_index]):
                print("Is illegal flow!")
                return True

            resolution = self.reduce_constraints(
                resolution, constraints[constraint_index])

            if self.is_illegal_flow(resolution):
                print("Is illegal flow!")
                return True

        print("QUEUE contents: ", self.queue_of_equations)

        # Empty the queue
        copy_queue = self.queue_of_equations

        if self.queue_of_equations is Empty:
            return False

        for constraint in copy_queue:
            if self.queue_of_equations is Empty:
                break

            if constraint in self.queue_of_equations:
                resolution = self.reduce_constraints(resolution, constraint)
                self.remove_equation_from_the_queue(constraint)

            if self.is_illegal_flow(resolution):
                print("Is illegal flow!")
                return True
        return False

    # def filter_vulnerabilities_by_sinks(self, vulnerabilities, sinks):
    #     print("Filtering")
    #     print("Sinks: ", sinks)
    #     return filter(lambda vulnerability: vulnerability.sink in sinks, vulnerabilities)

    def resolve_constraints_and_find_vulnerabilties(self, constraints, pattern):
        sources = pattern['sources']
        sinks = pattern['sinks']
        name = pattern['vulnerability']
        vulnerabilities = list()
        for source in sources:
            for sink in sinks:
                if self.has_vulnerability(constraints):
                    vulnerabilities_index = len(vulnerabilities) + 1
                    vulnerability_name = name + "_" + vulnerabilities_index.__str__()
                    vulnerability = Vulnerabilty(
                        vulnerability_name, source, sink)
                    vulnerabilities.append(vulnerability)

        # relevant_vulnerabilties = self.filter_vulnerabilities_by_sinks(
        #     vulnerabilities, sinks)
        return vulnerabilities
