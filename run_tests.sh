#!/bin/bash
set -e

#check syntax
printf "CHECKING SYNTAX\n"
flake8 src/*.py
flake8 unit_tests/*.py
flake8 smoke_tests/*.py

#run unit tests
printf "RUNNING UNIT TESTS\n"
python -m unittest discover

#now find all smoke tests and run them
printf "RUNNING SMOKE TESTS\n"
python -m unittest discover smoke_tests

printf "\nOK\n"
set +e

exit 0

