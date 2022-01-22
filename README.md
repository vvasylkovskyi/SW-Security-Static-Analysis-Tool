# SW-Security-Static-Analysis-Tool

## A tool for static (tainted flows?) analysis of software vulnerability

`python3 tf_analyser.py -h`

###Start by extracting the archive provided by the teachers

`python3 test.py --extract`


`python3 test.py --help`


usage: test.py [-h] [--extract] [--pprint_asts] [--pprint_outputs]
               [--pprint_patterns] [--tests TESTS [TESTS ...]]

optional arguments:
-h, --help            show this help message and exit

--extract             flag to extract slices from zip archive
  
--pprint_asts         pretty print abstract syntax trees

--pprint_outputs      pretty print output objects

--pprint_patterns     pretty print patterns objects

--tests TESTS [TESTS ...]   expression to id tests (example 1a 2)

### To generate a visitor pattern skeleton

`python3 generate_visitors.py tf_visitor slices/*.py.json --framework`

## To check current state of development of the solution

`python3 test.py | less`

Note that the representation of the constraint is a string but the constraint itself is a tuple of 5 elements consisting of a line number and two pairs of type qualifiers and ids