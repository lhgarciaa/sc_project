#!/bin/bash
set -e

#check syntax
printf "CHECKING SYNTAX\n"
flake8 src/*.py
flake8 unit_tests/*.py
flake8 smoke_tests/*.py
echo "OK"

#run unit tests
cmd='python -m unittest discover'
printf "RUNNING UNIT TESTS with $cmd\n"
$cmd

#now find all smoke tests and run them
cmd='python -m unittest discover smoke_tests'
printf "RUNNING SMOKE TESTS with $cmd\n"
$cmd

printf "\nOK\n"
set +e

exit 0

