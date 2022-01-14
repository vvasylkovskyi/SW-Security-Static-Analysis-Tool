# SW-Security-Static-Analysis-Tool

A tool for static (tainted flows?) analysis of software vulnerability

`python3 tf_analyser.py -h`

positional arguments:

  program     path of a JSON file containing the program slice to analyse,
              represented in the form of an Abstract Syntax Tree

  patterns    path of a JSON file containing the list of vulnerability
              patterns to consider

optional arguments:
  -h, --help  show this help message and exit

`python3 test.py -h`

usage: test.py [-h] [--extract] [--fix_outputs]

optional arguments:

  -h, --help     show this help message and exit

  --extract      flag to extract slices from zip archive (https://fenix.tecnico.ulisboa.pt/downloadFile/563568428829723/slices.zip)

  --fix_outputs  flag to fix output files by replacing single quotes by double
                 quotes

To see the proof of concept for visiting the ast as json given as input to the main tool run
`python3 test.py --test_visitor`
