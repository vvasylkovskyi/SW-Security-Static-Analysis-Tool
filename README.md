# SW-Security-Static-Analysis-Tool

A tool for static analysis of software vulnerability

## Testing the dummy example - Vulnerable Source: (input) && Vulnerable Sink: (eval)

Run the following:

### Basic Input + Eval

`$ python tool.py run tests/data/vulnerable_programs/dummy_vulnerable_program.py tests/experiences/vulnerable_input_vs_eval/dummy_trigger_words.json`

### XSS

`$ python tool.py run tests/data/vulnerable_programs/XSS_call.py tests/experiences/vulnerable_input_vs_eval/dummy_trigger_words.json`

## Using online CFG tool - staticfg

https://github.com/coetaur0/staticfg
