#!/bin/bash
# Launches KeyCast. Default: interpret KeyCast.swift directly (no build step).
# --build: compile to build/keycast with swiftc -O, then run the binary.
# Any other args (e.g. --check-mappings) are forwarded to KeyCast.
set -e

# cd to this script's own directory so relative "mappings" resolution works
# regardless of where run.sh was invoked from.
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$1" == "--build" ]]; then
    shift
    mkdir -p build
    swiftc -O -o build/keycast KeyCast.swift
    exec ./build/keycast "$@"
else
    exec swift KeyCast.swift "$@"
fi
