from tf_visitor import TypeQualifers


class ConstraintsResolver:
    queue_of_equations = list()

    def add_to_queue_of_equations(self, equation):
        self.queue_of_equations.append(equation)
        print("ADD QUEUE: ", self.queue_of_equations)

    def remove_equation_from_the_queue(self, equation):
        print("REMOVE QUEUE: ", self.queue_of_equations)
        self.queue_of_equations.remove(equation)

    def is_one_of_the_type_qualifiers(self, value):
        return value == TypeQualifers.TAINTED or value == TypeQualifers.UNTAINTED

    def find_greek_letter_in_constraint(self, constraint):
        left_hand_side = constraint[1]
        right_hand_side = constraint[3]
        if self.is_one_of_the_type_qualifiers(left_hand_side):
            return right_hand_side
        elif self.is_one_of_the_type_qualifiers(right_hand_side):
            return left_hand_side

    def find_pattern_index(self, source, src_with_type_qualifiers, constraints):
        taint_type_qualifier = TypeQualifers.TAINTED
        tainted_source = taint_type_qualifier + ' ' + source
        for index, src in enumerate(src_with_type_qualifiers):
            if tainted_source in src:
                index_in_src = index + 1
                break
        last_constraint_containing_the_tained_source_index = 0
        for index, constraint in enumerate(constraints):
            if constraint.line == index_in_src:
                last_constraint_containing_the_tained_source_index = index
        return last_constraint_containing_the_tained_source_index

    def is_illegal_flow(self, constraint):
        # if tainted <= untainted
        # means it is illegal flow
        left_hand_side = constraint[1]
        right_hand_side = constraint[3]

        if left_hand_side == TypeQualifers.TAINTED and right_hand_side == TypeQualifers.UNTAINTED:
            return True
        return False

    def debug_print_lhs_and_rhs(constraint):
        print("constraint: ", constraint)
        print("Left hand side: ", constraint[1])
        print("Right hand side: ", constraint[3])

    def is_idempotent_equation(self, constraint):
        if (constraint[1] == TypeQualifers.UNTAINTED and constraint[3] == TypeQualifers.TAINTED
                or constraint[1] == TypeQualifers.UNTAINTED and constraint[3] == TypeQualifers.UNTAINTED
                or constraint[1] == TypeQualifers.TAINTED and constraint[3] == TypeQualifers.TAINTED):
            return True
        return False

    def get_next_best_constraint(self, resolution, new_constraint, source_greek_letter):
        # No reduction. return the constraint with the source, if any
        if self.contains_source(resolution, source_greek_letter) and self.contains_source(new_constraint, source_greek_letter):
            # Both constraints contain source. Choose one that is tainted, if any
            print("HERE")
            if self.is_tainted(resolution) and self.is_tainted(new_constraint):
                # if both are tainted, choose the new one (to respect the order of executions)
                return new_constraint
            elif self.is_tainted(resolution) and not self.is_tainted(new_constraint):
                return resolution
            elif not self.is_tainted(resolution) and self.is_tainted(new_constraint):
                return new_constraint
            # If none is tained, then move on to the next constraint
            return new_constraint
        elif self.contains_source(resolution, source_greek_letter) and not self.contains_source(new_constraint, source_greek_letter):
            print("Yo-1")
            if not self.is_idempotent_equation(new_constraint) and new_constraint not in self.queue_of_equations:
                print("IT IS YEE")
                self.add_to_queue_of_equations(new_constraint)

            # Could not reduce, but maybe there is an equation in the queue that can be resolved
            # resolution = self.try_to_reduce_equation_with_queued_equations(
            #     resolution, source_greek_letter)
            return resolution
        elif not self.contains_source(resolution, source_greek_letter) and self.contains_source(new_constraint, source_greek_letter):
            print("Yo-2")
            return new_constraint
        else:
            # If none is tained and none is source, then just move on to the next constraint
            print("Yo-3")
            return new_constraint

    def try_to_reduce_equation_with_queued_equations(self, prev_resolution, source_greek_letter):
        print("Attempting reduction")
        resolution = prev_resolution
        for constraint in self.queue_of_equations:
            print("YO")
            resolution = self.reduce_constraints(
                resolution, constraint, source_greek_letter)
            if resolution != prev_resolution:
                self.remove_equation_from_the_queue(constraint)
        return resolution

    def check_if_source_is_being_sanitized(self, constraint, source_greek_letter):
        print("y")
        constraint_rhs = constraint[3]
        if constraint_rhs == TypeQualifers.TAINTED:
            print("Sanitizing?")
            return True
        return False

    def try_simplify_equation(self, resolution, new_constraint):
        resolution_lhs = resolution[1]
        resolution_rhs = resolution[3]

        new_constraint_lhs = new_constraint[1]
        new_constraint_rhs = new_constraint[3]

        if new_constraint_lhs == resolution_rhs:
            return (new_constraint[0], resolution_lhs, '<=', new_constraint_rhs)
        elif new_constraint_rhs == resolution_lhs:
            return (new_constraint[0], new_constraint_lhs, '<=', resolution_rhs)
        else:
            return False

    def resolve_equation(self, resolution, new_constraint, source_greek_letter):

        resolution_lhs = resolution[1]
        resolution_rhs = resolution[3]

        new_constraint_lhs = new_constraint[1]
        new_constraint_rhs = new_constraint[3]

        if self.is_idempotent_equation(new_constraint):
            print("HERE")
            return resolution

        # Reduce the equation by removing common parts

        if self.contains_source(resolution, source_greek_letter) and self.contains_source(new_constraint, source_greek_letter):
            print("Sanitizing?")
            if resolution_lhs == TypeQualifers.TAINTED and new_constraint_rhs == TypeQualifers.UNTAINTED:
                return self.try_simplify_equation(resolution, new_constraint)
            return resolution

        if self.try_simplify_equation(resolution, new_constraint):
            return self.try_simplify_equation(resolution, new_constraint)
        else:
            return self.get_next_best_constraint(resolution, new_constraint, source_greek_letter)

    def contains_source(self, constraint, source_greek_letter):
        lhs = constraint[1]
        rhs = constraint[3]
        return lhs == source_greek_letter or rhs == source_greek_letter

    def debug_print_compare_constraints(self, resolution, new_constraint):
        print("---------------")
        print("Resolution: ", resolution)
        print("New Constraint: ", new_constraint)

    def reduce_constraints(self, resolution, new_constraint, source_greek_letter):
        self.debug_print_compare_constraints(resolution, new_constraint)
        return self.resolve_equation(resolution, new_constraint, source_greek_letter)

    def is_tainted(self, greek_letter_constraint):
        lhs = greek_letter_constraint[1]
        return lhs == TypeQualifers.TAINTED

    def has_vulnerability(self, source, sink, src_with_type_qualifiers, constraints):
        tained_source_index = self.find_pattern_index(
            source, src_with_type_qualifiers, constraints)
        sink_index = self.find_pattern_index(
            sink, src_with_type_qualifiers, constraints)

        first_constraint = constraints[0]  # Starting always from zero
        # print("[Index: 0 ]", "Constraint: ",
        #       first_constraint)
        source_constraint = constraints[tained_source_index]
        # The Height is always equal to the index of the sink
        constraints_height = sink_index
        # debug_print_lhs_and_rhs(first_constraint)  # Starts with tained

        # print("sink index: ", sink_index)
        # debug_print_lhs_and_rhs(first_constraint)

        source_greek_letter = self.find_greek_letter_in_constraint(
            source_constraint)

        print("Source greek letter: ", source_greek_letter)
        resolution = first_constraint

        # First Check
        if self.is_illegal_flow(resolution):
            print("Is illegal flow!")
            return True

        # Run the constraints and reduce them until we reach the illegal flow,
        # or until we finish the algorithm. If at the end of the algorithm there is no illegal flow, then no vulnerability exists
        constraint_index = 0
        while constraints_height > constraint_index:
            constraint_index += 1
            print("[Index:", constraint_index, "] Constraint: ",
                  constraints[constraint_index])

            if self.is_illegal_flow(constraints[constraint_index]):
                print("Is illegal flow!")
                return True

            resolution = self.reduce_constraints(
                resolution, constraints[constraint_index], source_greek_letter)

            if self.is_illegal_flow(resolution):
                print("Is illegal flow!")
                return True

        return False

    def resolve_constraints_and_find_vulnerabilties(self, constraints, src_with_type_qualifiers, pattern):
        sources = pattern['sources']
        sinks = pattern['sinks']
        name = pattern['vulnerability']
        vulnerabilities = list()
        for source in sources:
            for sink in sinks:
                if self.has_vulnerability(
                        source, sink, src_with_type_qualifiers, constraints):
                    vulnerabilities_index = len(vulnerabilities) + 1
                    vulnerability_name = name + "_" + vulnerabilities_index.__str__()
                    vulnerability = (vulnerability_name, source, sink)
                    vulnerabilities.append(vulnerability)
        return vulnerabilities
