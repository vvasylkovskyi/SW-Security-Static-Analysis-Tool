
import os
from collections import namedtuple
import json

SOURCES_KEYWORD = 'sources'
SINKS_KEYWORD = 'sinks'

Definitions = namedtuple('Definitions', 'sources sinks')

default_trigger_word_file = os.path.join(os.path.dirname(
    __file__), 'tests', 'experiences', 'vulnerable_input_vs_eval', 'dummy_trigger_words.json')


def parse(trigger_word_file=default_trigger_word_file):
    sources = list()
    sinks = list()

    file_contents_in_string = ''
    with open(trigger_word_file, 'r') as fd:
        for line in fd:
            line = line.rstrip()
            file_contents_in_string += line + '\n'

    json_object = json.loads(file_contents_in_string)
    try:
        sources = json_object[SOURCES_KEYWORD]
        sinks = json_object[SINKS_KEYWORD]
    except KeyError:
        print("No such key. The trigger words file is malformed. yolo")
        return
    return Definitions(sources, sinks)


def find_vulnerabilities(trigger_word_file=default_trigger_word_file):
    definitions = parse(trigger_word_file)
    print("Trigger path: ", trigger_word_file)
    print("definitions: ", definitions)

    vulnerabilities = '[{}]'
    return vulnerabilities
