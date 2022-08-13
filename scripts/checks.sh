#!/usr/bin/env bash

# Reformating the code using black
black --check $(git ls-files './kharma/*.py')
# Check for unused imports
pylint --disable=all --enable=unused-import $(git ls-files './kharma/*.py')
# Validate types using mymy
mypy ./kharma