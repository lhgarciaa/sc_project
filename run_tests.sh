#!/bin/bash
set -e

#check syntax
printf "CHECKING SYNTAX\n"
flake8 src/*.py
flake8 smoke_tests/*.py
echo "OK"

#now find all smoke tests and run them
cmd='python -m unittest discover smoke_tests'
printf "RUNNING SMOKE TESTS with $cmd\n"
$cmd

set +e

exit 0
