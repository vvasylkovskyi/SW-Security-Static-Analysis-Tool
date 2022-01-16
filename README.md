# SW-Security-Static-Analysis-Tool

A tool for static (tainted flows?) analysis of software vulnerability

`python3 tf_analyser.py -h`

Start by extracting the archive provided by the teachers

`python3 test.py --extract`


To generate a visitor pattern skeleton

`python3 generate_visitors.py tf_visitor slices/*.py.json --framework`


To check current state of development of the solution

`python3 test.py | less`

Note that the representation of the constraint is a string but the constraint itself is a tuple of 5 elements consisting of a line number and two pairs of type qualifiers and ids


