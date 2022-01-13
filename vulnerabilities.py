
import os
from collections import namedtuple
import json

from cfg.node import AssignmentNode

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


def parse(trigger_word_file=default_trigger_word_file):
    file_contents_in_string = ''
    with open(trigger_word_file, 'r') as fd:
        for line in fd:
            line = line.rstrip()
            file_contents_in_string += line + '\n'

    list_of_vulnerability_patterns = json.loads(file_contents_in_string)
    vulnerability_definitions = list()
    print("JSON: ", list_of_vulnerability_patterns)
    for vulnerability_pattern in list_of_vulnerability_patterns:
        print("Vulnerabilty: ", vulnerability_pattern)
        sources = list()
        sinks = list()
        vulnerability = vulnerability_pattern[VULNERABILITY_NAME_KEYWORD]
        sources = vulnerability_pattern[SOURCES_KEYWORD]
        sinks = vulnerability_pattern[SINKS_KEYWORD]
        new_vulnerability_definition = VulnerabilityDefinition(
            vulnerability, sources, sinks)
        vulnerability_definitions.append(new_vulnerability_definition)
    return vulnerability_definitions


def filter_cfg_nodes(cfg, cfg_node_type):
    return [node for node in cfg.nodes if isinstance(node, cfg_node_type)]


def source_node_contains_label(node, sources):
    for source in sources:
        if source[0] in node.label:
            trigger_word = source[0]
            return TriggerNode(trigger_word, node)


def get_trigger_node_that_contains_label(node, triggers):
    for trigger in triggers:
        # print("TRIGGERRRERE: ", trigger)
        # print("Node Label: ", node.label)
        print("Trigger: ", trigger)
        if trigger in node.label:
            print("TRIGGER WORD: ", trigger)
            return TriggerNode(trigger, node)


def find_triggers(nodes, triggers):
    trigger_nodes = list()
    for node in nodes:
        # print("Node: ", node)
        trigger_that_contains_label = get_trigger_node_that_contains_label(
            node, triggers)
        # print("Trigger that contains label: ", trigger_that_contains_label)
        if trigger_that_contains_label is not None:
            print("Is not None: ", trigger_that_contains_label)
            trigger_nodes.append(trigger_that_contains_label)
    return trigger_nodes


def get_vulnerability(source, sink):
    print("Getting vulnerability based on:\n")
    print("Source: ", source)
    print("Sink: ", sink)


def find_vulnerabilities_in_cfg(cfg, vulnerability_definition):
    print("Looking for vulnerability")

    sources_definition = vulnerability_definition.sources
    sinks_definition = vulnerability_definition.sinks
    assignment_nodes = filter_cfg_nodes(cfg, AssignmentNode)
    # print("Sources: ", sources_definition)
    # print("Sinks: ", sinks_definition)
    sources = find_triggers(assignment_nodes, sources_definition)
    sinks = find_triggers(cfg.nodes, sinks_definition)

    # print("SOurces in the file: ", sources[0])
    # print("Sinks in the file: ", sinks[1])

    for sink in sinks:
        for source in sources:
            vulnerability = get_vulnerability(source, sink)


def find_vulnerabilities(cfg, trigger_word_file=default_trigger_word_file):
    vulnerability_definitions = parse(trigger_word_file)
    # print("Trigger path: ", trigger_word_file)
    # print("definitions: ", vulnerability_definitions)

    list_of_potential_vulnerabilities = '[{}]'
    for vulnerability_definition in vulnerability_definitions:
        find_vulnerabilities_in_cfg(cfg, vulnerability_definition)
        print("Definition: ", vulnerability_definition)
    return list_of_potential_vulnerabilities
