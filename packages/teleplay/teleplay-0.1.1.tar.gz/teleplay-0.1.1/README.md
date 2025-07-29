# Teleplay

Test a single or series of Python CLI programs all at once!

## Features

Ever needed to test a series of command line scripts with flexible YAML-based arguments? Me neither -- until I did!

Provide a list of Python CLI invocations along with their associated command line arguments in a `teleplay.yaml` file, and go to it!

## Example

The following example tests a module known as [PaperPC](https://github.com/paperdyne/paperpc) using
a program that allows for simple addition (`main.ppc`). The YAML represents the command line for this
module: `paperpc main.ppc --inputs [2,3]`.
```yaml
modules:
    paperpc:
        args:
            - main.ppc
            - --inputs [2,3]
        outcome: 5
```
