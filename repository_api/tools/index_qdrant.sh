#!/usr/bin/env bash

set -e

REPO_PATH=$1

REPO_PATH=$(realpath $REPO_PATH)

# Get path to this script
SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
ROOT_PATH=$SCRIPT_PATH/..


python3 -m code_search.index.files_to_json

python3 -m code_search.index.parser_for_code $REPO_PATH

python3 -m code_search.index.upload_code

python3 -m code_search.index.parser_for_nl $REPO_PATH

python3 -m code_search.index.upload_signatures
