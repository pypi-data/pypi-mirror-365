Inventory Explorer
==================

Inventory Explorer helps you efficiently explore the hosts, groups and
variables in an Ansible inventory.

![Illustrated inventory-explorer interactions](./docs/demo.png)

Features:

* Fuzzy search hosts and groups (using [fzf](https://github.com/junegunn/fzf))
* Quickly see what groups a host is in
* Quickly see what hosts are in a group
* Quickly jump between related hosts and groups
* Display and [fuzzy search YAML](https://github.com/bbc/fzy) group and host data
* Quickly edit host or group variables
* See fully evaluated variables (e.g. with all template substitutions applied)


Warning: Experimental
---------------------

This project is currently in an experimental/exploratory phase to try and
understand how an Inventory exploring tool might function and be used. It may
change radically or become abandoned depending on feedback.


Installation
------------

Install from [PyPI](https://pypi.org/) using `pip`:

    $ pip install inventory-explorer


Usage
-----

    $ inventory-explorer

Or

    $ inventory-explorer -i path/to/inventory

Follow the prompts! Press ctrl+C to exit, or return to earlier parts of the UI.
You may need to press this multiple times to exit.


Inventory aliases
-----------------

In some cases it can be helpful to define short-forms for the full path(s) to a
given inventory which you frequently use.

On startup, `inventory-explorer` tries to read the file
`inventory-explorer-aliases.yml` from the working directory. This should be a
YAML file with values in one of the three forms demonstrated below:

    simple: path/to/some/simple/inventory.py
    
    several:
      - paths/to/one/inventory.py
      - paths/to/another/inventory.ini
    
    vars_too:
      inventory_files:
        - path/to/an/inventory.yml
      extra_vars:
        - foo=bar
        - @path/to/vars.yml

`--inventory simple` becomes a shorthand for `--inventory
path/to/some/simple/inventory.py`.

`--inventory several` becomes a shorthand for `--inventory
paths/to/one/inventory.py --inventory paths/to/another/inventory.ini`.

`--inventory vars_too` becomes a shorthand for `--inventory
path/to/an/inventory.py --extra-vars foo=bar --extra-vars @path/to/vars.yml`.

As with the `--extra-vars` argument, `inventory-explorer` extends the Ansible
syntax for extra variables by supporting shell-style glob patterns in
filenames.


Development
-----------

You can run the test suite using:

    $ pip install -r requirements-test.txt
    $ pytest

