#!/usr/bin/env bash

set -e

# Ensure current path is project root
cd "$(dirname "$0")/../"

git clone https://github.com/nevernorbo/mean-flashcards.git /tmp/mean-flashcards


REPO_PATH=/tmp/mean-flashcards bash -x tools/index_qdrant.sh /tmp/mean-flashcards

rm -rf /tmp/mean-flashcards
