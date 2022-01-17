from tf_visitor import TypeQualifers


def resolve_equation(resolution, new_constraint):

    resolution_lhs = resolution[1]
    resolution_rhs = resolution[3]

    new_constraint_lhs = new_constraint[1]
    new_constraint_rhs = new_constraint[3]

    # Reduce the equation by removing common parts
    if new_constraint_lhs == resolution_rhs:
        return (new_constraint[0], resolution_lhs, '<=', new_constraint_rhs)
    elif new_constraint_rhs == resolution_lhs:
        return (new_constraint[0], new_constraint_lhs, '<=', resolution_rhs)


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


def has_vulnerability(source, sink, src_with_type_qualifiers, constraints):
    tained_source_index = find_pattern_index(
        source, src_with_type_qualifiers)
    sink_index = find_pattern_index(
        sink, src_with_type_qualifiers)

    first_constraint = constraints[tained_source_index]

    constraints_height = len(constraints)
    # debug_print_lhs_and_rhs(first_constraint) # Starts with tained

    # last_constraint = constraints[sink_index]
    # debug_print_lhs_and_rhs(last_constraint)

    source_greek_letter = find_greek_letter_in_constraint(
        first_constraint)

    print("Source greek letter: ", source_greek_letter)
    resolution = first_constraint
    constraint_index = tained_source_index
    while constraints_height > constraint_index:
        greek_letter = find_greek_letter_in_constraint(
            constraints[constraint_index])

        # if greek_letter == source_greek_letter:
        # print("Do something. Reassignment?")

        if greek_letter == source_greek_letter and constraint_index == sink_index:
            resolution = resolve_equation(
                resolution, constraints[constraint_index])

        if is_illegal_flow(resolution):
            return True

        constraint_index += 1
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
