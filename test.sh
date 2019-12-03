#! /bin/bash
source ./venv/bin/activate
unset SCALING_SPOON_PRODUCTION
python -m unittest tests
pytest forgery/tests.py