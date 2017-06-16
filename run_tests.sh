#!/bin/bash
set -e

#check syntax
printf "CHECKING SYNTAX\n"
pyflakes src/*.py
pyflakes unit_tests/*.py
pyflakes smoke_tests/*.py

#run unit tests
printf "RUNNING UNIT TESTS\n"
python -m unittest discover

#now find all smoke tests and run them
printf "RUNNING SMOKE TESTS\n"
cd smoke_tests
python -m unittest test_smoke.RunSmokeTests

printf "\nOK\n"
set +e

exit 0

