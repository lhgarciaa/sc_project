#!/bin/bash
set -e

#check syntax
printf "CHECKING SYNTAX\n"
pyflakes src/*.py
pyflakes tests/*.py

#run unit tests
printf "RUNNING UNIT TESTS\n"
python -m unittest discover

#now find all smoke tests and run them
printf "RUNNING SMOKE TESTS\n"
cd tests
python -m unittest test_smoke.RunSmokeTests

printf "\nOK\n"
set +e

exit 0

