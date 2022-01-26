

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

    def extract_next_equation_from_queue(self):
        next_equation = self.queue_of_equations[0]
        self.queue_of_equations.remove(next_equation)
        return next_equation

    def reset_queue(self):
        self.queue_of_equations = list()

    def is_illegal_flow(self, constraint):
        # if tainted <= untainted
        # means it is illegal flow
        left_hand_side = constraint.lhs_tq
        right_hand_side = constraint.rhs_tq

        if left_hand_side == TaintQualifer.TAINTED and right_hand_side == TaintQualifer.UNTAINTED:
            return True
        return False

    def is_idempotent_equation(self, constraint):
        if (constraint.lhs_tq == TaintQualifer.UNTAINTED or constraint.lhs_tq == TaintQualifer.TAINTED and constraint.rhs_tq == TaintQualifer.TAINTED):
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

    def try_simplify_equation_in_queue(self, resolution, new_constraint):
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
        if self.is_idempotent_equation(resolution):
            return new_constraint
        elif self.is_idempotent_equation(new_constraint):
            return resolution

        print("[RESOLVING EQUATION] - Resolution: ", resolution,
              "| Constraint: ", new_constraint)
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
        for qualifier in qualifiers:
            if lhs == qualifier or rhs == qualifier:
                return True
        return False

    def is_rhs(self, constraint, qualifiers):
        rhs = constraint.rhs_tq
        for qualifier in qualifiers:
            if rhs == qualifier:
                return True
        return False

    def is_lhs(self, constraint, qualifiers):
        lhs = constraint.lhs_tq
        for qualifier in qualifiers:
            if lhs == qualifier:
                return True
        return False

    def try_illegal_flow(self, resolution, source_qualifiers, sink_qualifiers):
        resolution = self.replace_qualifiers_with_sinks_and_sources(
            resolution, source_qualifiers, sink_qualifiers)

        if self.is_illegal_flow(resolution):
            print("Is illegal flow!")
            return True

        return False

    def try_are_sink_and_source_params_of_the_same_func(self, sink_qualifiers, source_qualifiers):
        sink_flows_to = None
        source_flows_to = None
        for equation in self.queue_of_equations:
            if self.contains_target(equation, sink_qualifiers) and self.is_lhs(equation, sink_qualifiers):
                sink_flows_to = equation.rhs_tq
        for equation in self.queue_of_equations:
            if self.contains_target(equation, source_qualifiers) and self.is_lhs(equation, source_qualifiers):
                source_flows_to = equation.rhs_tq

        if sink_flows_to == source_flows_to:
            return True

    def reduce_queue_equations_locally(self):
        print("QUEUE: ", self.queue_of_equations)
        print("Is empty? : ", self.queue_of_equations is Empty)
        if len(self.queue_of_equations) == 0 or self.queue_of_equations is Empty:
            return

        local_resolution = self.extract_next_equation_from_queue()
        print("-----In the queue----")
        while True:
            can_reduce = False
            for constraint in self.queue_of_equations:
                if self.try_simplify_equation_in_queue(local_resolution, constraint):
                    new_resolution = self.try_simplify_equation_in_queue(
                        local_resolution, constraint)
                    if new_resolution != local_resolution:
                        can_reduce = True
                        self.remove_equation_from_the_queue(constraint)
                        local_resolution = new_resolution
            if can_reduce:
                self.add_to_queue_of_equations(local_resolution)

            if can_reduce == False:
                break

    def reduce_equations_in_queue(self, resolution, sink_qualifiers, source_qualifiers):
        print("QUEUE contents: ", self.queue_of_equations)

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
                print("Is illegal flow! in the queue")
                return True

    def get_qualifiers(self, targets, tf_labels):
        qualifiers = list()
        for target in targets:
            for key in tf_labels:
                if target in key:
                    qualifiers.append(tf_labels[key])
        return qualifiers

    def map_ssa_to_variable(self, ssa_variable_map, ssa_variables_list):
        variables = list()
        for ssa_variable in ssa_variables_list:
            if ssa_variable in ssa_variable_map:
                variables.append(ssa_variable_map[ssa_variable])
        return variables

    def get_uninstantiated_variables(self, constraints, path_feasibility_constraints_item, ssa_variable_map, sources):
        instantiated_variables = path_feasibility_constraints_item._instantiated_variables
        defined_functions = path_feasibility_constraints_item._functions
        all_variables = list()
        # print("Checking")
        # print("Instantiated variables: ", instantiated_variables)
        # print("Defined functions: ", defined_functions)
        for constraint in constraints:
            lhs = constraint.lhs_id
            rhs = constraint.rhs_id
            all_variables.append(lhs)
            all_variables.append(rhs)

        all_instantiated_variables = [
            *instantiated_variables, *defined_functions]
        uninstantiated_variables_ssa = [
            item for item in all_variables if item not in all_instantiated_variables]

        # print("All instantia: ", all_instantiated_variables)
        # print("All Variables: ", all_variables)
        # defined_
        # TODO Remove functions
        uninstantiated_variables = self.map_ssa_to_variable(
            ssa_variable_map, uninstantiated_variables_ssa)
        uninstantiated_variables = [
            item for item in uninstantiated_variables if item not in sources]
        print("uninstatiated FINAL: ", uninstantiated_variables)
        return list(set(sorted(uninstantiated_variables)))

    def is_new_vulnerability(self, vulnerabilities, name, source, sink):
        for vulnerability in vulnerabilities:
            if vulnerability.name == name and vulnerability.source == source and vulnerability.sink == sink:
                print("Is not new")
                return False
        print("Is new")
        return True

    def add_vulnerability(self, vulnerabilities, name, source, sink):
        if self.is_new_vulnerability(vulnerabilities, name, source, sink):
            vulnerabilities.append(Vulnerabilty(name, source, sink))
        return vulnerabilities

    def try_add_vulnerability(self, vulnerabilities, name, current_source, path_feasibility_constraints_item, sources, sink, tf_labels):
        constraints = path_feasibility_constraints_item._scoped_constraints
        # print("Constraints: ", constraints)
        # print("HERE ARE SEVERAL OR WHAT")

        # print("SOURCES: ", sources)
        sink_qualifiers = self.get_qualifiers(
            [sink], tf_labels)
        source_qualifiers = self.get_qualifiers(
            sources, tf_labels)
        # print("Sources: ", sources)
        # print("Sink: ", sink)
        # print("SINK QUALIFIERS: ", sink_qualifiers)
        # print("Source QUALIFIERS: ", source_qualifiers)

        if self.has_vulnerability(constraints, source_qualifiers, sink_qualifiers, tf_labels):
            print("Has vulnerability")
            vulnerabilities = self.add_vulnerability(
                vulnerabilities, name, current_source, sink)
        return vulnerabilities

    def format_constraints_to_allow_multiple_reduction(self, constraints):
        print("Formatting")
        formatted_constraints = constraints.copy()
        copy_constraints = constraints.copy()
        for constraint in constraints:
            original_rhs = constraint.rhs_tq
            number_of_possible_flows = 0
            for copy_constraint in copy_constraints:
                if copy_constraint == constraint:
                    continue
                copy_lhs = copy_constraint.lhs_tq
                if copy_lhs == original_rhs:
                    number_of_possible_flows += 1
            while number_of_possible_flows > 1:
                formatted_constraints.append(constraint)
                number_of_possible_flows -= 1

        # for constraint in constraints:
        #     original_lhs = constraint.lhs_tq
        #     number_of_possible_flows = 0
        #     for copy_constraint in copy_constraints:
        #         if copy_constraint == constraint:
        #             continue
        #         copy_rhs = copy_constraint.rhs_tq
        #         if copy_rhs == original_lhs:
        #             number_of_possible_flows += 1
        #     while number_of_possible_flows > 1:
        #         formatted_constraints.append(constraint)
        #         number_of_possible_flows -= 1

            # rhs = constraint.rhs_id
        return sorted(formatted_constraints)

    def has_vulnerability(self, constraints, source_qualifiers, sink_qualifiers, tf_labels):
        constraints = self.format_constraints_to_allow_multiple_reduction(
            constraints)
        constraint_index = 0
        resolution = constraints[constraint_index]  # Starting always from zero
        self.reset_queue()

        print("Final constraints: ", constraints)
        # while not self.contains_target(resolution, sink_qualifiers) and constraint_index < len(constraints) - 1:
        #     constraint_index += 1
        #     resolution = constraints[constraint_index]
        #     self.add_to_queue_of_equations(resolution)

        # if self.try_illegal_flow(resolution, source_qualifiers, sink_qualifiers):
        #     print("Is illegal flow! First")
        #     return True

        while constraint_index < len(constraints) - 1:
            constraint_index += 1
            print("[Index:", constraint_index, "] Resolution: ", resolution, "| Constraint: ",
                  constraints[constraint_index])

            if self.try_illegal_flow(constraints[constraint_index], source_qualifiers, sink_qualifiers):
                print("Is illegal flow!")
                return True

            resolution = self.reduce_constraints(
                resolution, constraints[constraint_index], sink_qualifiers)

            if self.contains_target(resolution, sink_qualifiers):
                # print("Contains sink")
                resolution = self.replace_qualifiers_with_sinks_and_sources(
                    resolution, source_qualifiers, sink_qualifiers)

            if self.is_illegal_flow(resolution):
                print("Is illegal flow!")
                return True

        if self.try_illegal_flow(resolution, source_qualifiers, sink_qualifiers):
            return True

        is_illegal_flow = self.reduce_equations_in_queue(
            resolution, sink_qualifiers, source_qualifiers)

        if is_illegal_flow:
            return True

        # print("HERE NOT REDUCING ANYMORE")

        self.reduce_queue_equations_locally()

        print("OK; reduced. Now the queue: ", self.queue_of_equations)

        for resolution in self.queue_of_equations:
            is_illegal_flow = self.reduce_equations_in_queue(
                resolution, sink_qualifiers, source_qualifiers)
            if is_illegal_flow:
                return True

        # if self.try_are_sink_and_source_params_of_the_same_func(sink_qualifiers, source_qualifiers):
        #     print("Is illegal flow!")
        #     return True

        # print("QUEUE: ", self.queue_of_equations)
        # print("RESOLUTION SO FAR: ", resolution)
        # print("SINKS VARS: ", sink_qualifiers)
        # print("TF_LABELS: ", tf_labels)

        return self.try_illegal_flow(resolution, source_qualifiers, sink_qualifiers)

    def resolve_constraints_and_find_vulnerabilties(self, ssa_variable_map, path_feasibility_constraints, pattern, sources_ssa, sinks_ssa, tf_labels):
        vulnerabilities = list()
        uninstantiated_variables = list()
        sources = pattern['sources']
        sinks = pattern['sinks']
        name = pattern['vulnerability']
        for sink in sinks:
            for source in sources:
                for _, path_feasibility_constraints_item in path_feasibility_constraints.items():
                    vulnerabilities = self.try_add_vulnerability(
                        vulnerabilities, name, source, path_feasibility_constraints_item, sources, sink, tf_labels)
                    break  # only need 1 flow to state that there is a vulnerability. We could say in which flow we found it, but it is not required for the analysis.

                for _, path_feasibility_constraints_item in path_feasibility_constraints.items():
                    constraints = path_feasibility_constraints_item._scoped_constraints
                    uninstantiated_variables = self.get_uninstantiated_variables(
                        constraints, path_feasibility_constraints_item, ssa_variable_map, sources)

                    for uninstantiated_variable in uninstantiated_variables:
                        vulnerabilities = self.try_add_vulnerability(
                            vulnerabilities, name, uninstantiated_variable, path_feasibility_constraints_item, uninstantiated_variables, sink, tf_labels)
        return vulnerabilities
