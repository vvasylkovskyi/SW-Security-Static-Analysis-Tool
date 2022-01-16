
import os
from collections import namedtuple
import json
import ast
from cfg.node import AssignmentNode, EntryExitNode, Node

SOURCES_KEYWORD = 'sources'
SINKS_KEYWORD = 'sinks'
VULNERABILITY_NAME_KEYWORD = 'vulnerability'

VulnerabilityDefinition = namedtuple(
    'VulnerabilityDefinition', 'vulnerability sources sinks')

default_trigger_word_file = os.path.join(os.path.dirname(
    __file__), 'tests', 'experiences', 'vulnerable_input_vs_eval', 'dummy_trigger_words.json')


class TriggerNode():
    def __init__(self, trigger_word, cfg_node):
        self.trigger_word = trigger_word
        self.cfg_node = cfg_node

    def __str__(self):
        """Print the label of the node."""
        return 'Trigger Word: ' + self.trigger_word


class Vulnerability():
    def __init__(self, name, source, sink, unsanitized_flows=True):
        self.name = name
        self.source = source
        self.sink = sink
        self.unsanitized_flows = unsanitized_flows


def parse(trigger_word_file=default_trigger_word_file):
    file_contents_in_string = ''
    with open(trigger_word_file, 'r') as fd:
        for line in fd:
            line = line.rstrip()
            file_contents_in_string += line + '\n'

    list_of_vulnerability_patterns = json.loads(file_contents_in_string)
    vulnerability_definitions = list()
    for vulnerability_pattern in list_of_vulnerability_patterns:
        sources = list()
        sinks = list()
        vulnerability = vulnerability_pattern[VULNERABILITY_NAME_KEYWORD]
        sources = vulnerability_pattern[SOURCES_KEYWORD]
        sinks = vulnerability_pattern[SINKS_KEYWORD]
        new_vulnerability_definition = VulnerabilityDefinition(
            vulnerability, sources, sinks)
        vulnerability_definitions.append(new_vulnerability_definition)
    return vulnerability_definitions


def filter_cfg_nodes(nodes, cfg_node_type):
    return [node for node in nodes if isinstance(node, cfg_node_type)]


def source_node_contains_label(node, sources):
    for source in sources:
        if source[0] in node.label:
            trigger_word = source[0]
            return TriggerNode(trigger_word, node)


def get_trigger_node_that_contains_label(node, trigger):
    if trigger in node.label:
        return TriggerNode(trigger, node)


def find_triggers(nodes, triggers):
    trigger_nodes = list()
    for trigger in triggers:
        for node in nodes:
            trigger_that_contains_label = get_trigger_node_that_contains_label(
                node, trigger)
            if trigger_that_contains_label is not None:
                trigger_nodes.append(trigger_that_contains_label)
    return trigger_nodes


def get_sink_args(cfg_node):
    if type(cfg_node) == AssignmentNode:
        return get_sink_args(cfg_node.ast_node.value)
    elif isinstance(cfg_node, Node):
        return get_sink_args(cfg_node.ast_node)
    elif isinstance(cfg_node, ast.Call):
        args = list()
        for arg in cfg_node.args + cfg_node.keywords:
            if isinstance(arg, ast.Name):
                args.append(arg.id)
            elif isinstance(arg, ast.Str):
                args.append(arg.s)
            elif isinstance(arg, ast.Call):
                args.extend(get_sink_args(arg))
            elif isinstance(arg, ast.keyword):
                args.append(arg.value)
            elif isinstance(arg, ast.Attribute):
                import ast_helper
                args.append(ast_helper.get_call_names_as_string(arg))
            else:
                raise Exception('Unexpected argument type:', type(arg))
        return args
    elif isinstance(cfg_node, ast.Str):
        return None
    else:
        raise Exception('Unexpected node type:', type(cfg_node))


def get_vulnerability(name, source, sink):
    source_in_sink = source.cfg_node in sink.cfg_node.new_constraint
    if source_in_sink:
        return Vulnerability(name, source.trigger_word, sink.trigger_word)


def filter_out_entry_and_exit_nodes(nodes):
    filtered_list = list()
    for node in nodes:
        if not isinstance(node, EntryExitNode):
            filtered_list.append(node)
    return filtered_list


def find_vulnerability_for_pair(name, source_def, sink_def, sources_in_nodes, sinks_in_nodes):
    for i, source in enumerate(sources_in_nodes):
        for j, sink in enumerate(sinks_in_nodes):
            vulnerability_name = name + "_" + (1 + i + j).__str__()
            vulnerability = get_vulnerability(vulnerability_name, source, sink)
            if vulnerability is not None:
                return Vulnerability(name, source_def, sink_def)
    return None


def find_vulnerabilities_in_cfg(cfg, vulnerability_definition):
    name = vulnerability_definition.vulnerability
    nodes = filter_out_entry_and_exit_nodes(cfg.nodes)
    sources_definition = vulnerability_definition.sources
    sinks_definition = vulnerability_definition.sinks
    assignment_nodes = filter_cfg_nodes(nodes, AssignmentNode)
    sources_in_nodes = find_triggers(assignment_nodes, sources_definition)
    sinks_in_nodes = find_triggers(nodes, sinks_definition)
    vulnerabilities = list()

    for i, source_def in enumerate(sources_definition):
        for j, sink_def in enumerate(sinks_definition):
            vulnerability_name = name + "_" + (1 + i + j).__str__()
            vulnerability = find_vulnerability_for_pair(
                vulnerability_name, source_def, sink_def, sources_in_nodes, sinks_in_nodes)
            if vulnerability is not None:
                vulnerabilities.append(vulnerability)

    return vulnerabilities


def find_vulnerabilities(cfg, trigger_word_file=default_trigger_word_file):
    vulnerability_definitions = parse(trigger_word_file)
    list_of_vulnerabilities = list()
    for vulnerability_definition in vulnerability_definitions:
        vulnerabilities = find_vulnerabilities_in_cfg(
            cfg, vulnerability_definition)
        if vulnerabilities:
            list_of_vulnerabilities.extend(vulnerabilities)
    return list_of_vulnerabilities
