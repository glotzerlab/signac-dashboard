#!/bin/bash

# This file creates a new signac project with a few statepoints and launches
# a signac-dashboard server all in bash.

signac init default

for a in {1..5}; do
    statepoint="{\"a\": $a}"
    echo "Creating statepoint: $statepoint"
    signac job -c "$statepoint"
done

signac-dashboard run
