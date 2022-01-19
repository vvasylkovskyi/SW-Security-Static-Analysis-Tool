from tf_visitor import TypeQualifers


def is_one_of_the_type_qualifiers(value):
    return value == TypeQualifers.TAINTED or value == TypeQualifers.UNTAINTED


def find_greek_letter_in_constraint(constraint):
    left_hand_side = constraint[1]
    right_hand_side = constraint[3]
    if is_one_of_the_type_qualifiers(left_hand_side):
        return right_hand_side
    elif is_one_of_the_type_qualifiers(right_hand_side):
        return left_hand_side


def find_pattern_index(source, src_with_type_qualifiers):
    taint_type_qualifier = TypeQualifers.TAINTED
    tainted_source = taint_type_qualifier + ' ' + source
    for index, src in enumerate(src_with_type_qualifiers):
        if tainted_source in src:
            return index


def is_illegal_flow(constraint):
    # untainted < tainted
    # Else, it is illegal flow
    left_hand_side = constraint[1]
    right_hand_side = constraint[3]

    if left_hand_side == TypeQualifers.TAINTED and right_hand_side == TypeQualifers.UNTAINTED:
        return True
    return False


def debug_print_lhs_and_rhs(constraint):
    print("constraint: ", constraint)
    print("Left hand side: ", constraint[1])
    print("Right hand side: ", constraint[3])


def resolve_equation(resolution, new_constraint, source_greek_letter):

    resolution_lhs = resolution[1]
    resolution_rhs = resolution[3]

    new_constraint_lhs = new_constraint[1]
    new_constraint_rhs = new_constraint[3]

    # Reduce the equation by removing common parts
    if new_constraint_lhs == resolution_rhs:
        return (new_constraint[0], resolution_lhs, '<=', new_constraint_rhs)
    elif new_constraint_rhs == resolution_lhs:
        return (new_constraint[0], new_constraint_lhs, '<=', resolution_rhs)
    else:
        # No reduction. return the constraint with the source, if any
        if contains_source(resolution, source_greek_letter) and contains_source(new_constraint, source_greek_letter):
            # Both constraints contain source. Choose one that is tainted, if any
            print("HERE")
            if is_tainted(resolution) and is_tainted(new_constraint):
                # if both are tainted, choose the new one (to respect the order of executions)
                return new_constraint
            elif is_tainted(resolution) and not is_tainted(new_constraint):
                return resolution
            elif not is_tainted(resolution) and is_tainted(new_constraint):
                return new_constraint
            # If none is tained, then move on to the next constraint
            return new_constraint
        elif contains_source(resolution, source_greek_letter) and not contains_source(new_constraint, source_greek_letter):
            return resolution
        elif not contains_source(resolution, source_greek_letter) and contains_source(new_constraint, source_greek_letter):
            return new_constraint

    # If none is tained and none is source, then just move on to the next constraint
    return new_constraint


def contains_source(constraint, source_greek_letter):
    lhs = constraint[1]
    rhs = constraint[3]
    return lhs == source_greek_letter or rhs == source_greek_letter


def debug_print_compare_constraints(resolution, new_constraint):
    print("---------------")
    print("Resolution: ", resolution)
    print("New Constraint: ", new_constraint)


def reduce_constraints(resolution, new_constraint, source_greek_letter):
    # debug_print_compare_constraints(resolution, new_constraint)
    return resolve_equation(resolution, new_constraint, source_greek_letter)


def is_tainted(greek_letter_constraint):
    lhs = greek_letter_constraint[1]
    return lhs == TypeQualifers.TAINTED


def has_vulnerability(source, sink, src_with_type_qualifiers, constraints):
    tained_source_index = find_pattern_index(
        source, src_with_type_qualifiers)
    sink_index = find_pattern_index(
        sink, src_with_type_qualifiers)

    first_constraint = constraints[0]  # Starting always from zero
    # print("[Index: 0 ]", "Constraint: ",
    #       first_constraint)
    source_constraint = constraints[tained_source_index]
    # The Height is always equal to the index of the sink
    constraints_height = sink_index
    # debug_print_lhs_and_rhs(first_constraint)  # Starts with tained

    # print("sink index: ", sink_index)
    # debug_print_lhs_and_rhs(last_constraint)

    source_greek_letter = find_greek_letter_in_constraint(
        source_constraint)

    print("Source greek letter: ", source_greek_letter)
    resolution = first_constraint
    constraint_index = 0
    while constraints_height > constraint_index:
        constraint_index += 1

        # print("[Index:", constraint_index, "] Constraint: ",
        #       constraints[constraint_index])

        resolution = reduce_constraints(
            resolution, constraints[constraint_index], source_greek_letter)

        if is_illegal_flow(resolution):
            print("Is illegal flow!")
            return True

    return False


def resolve_constraints_and_find_vulnerabilties(constraints, src_with_type_qualifiers, pattern):
    sources = pattern['sources']
    sinks = pattern['sinks']
    name = pattern['vulnerability']
    vulnerabilities = list()
    for source in sources:
        for sink in sinks:
            if has_vulnerability(
                    source, sink, src_with_type_qualifiers, constraints):
                vulnerabilities_index = len(vulnerabilities) + 1
                vulnerability_name = name + "_" + vulnerabilities_index.__str__()
                vulnerability = (vulnerability_name, source, sink)
                vulnerabilities.append(vulnerability)
    return vulnerabilities
