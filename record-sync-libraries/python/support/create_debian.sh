#!/bin/bash

startPath = $(pwd)
startDir = $(basename $startPath)

if [ $startDir = "support" ]; then
    cd ..
elif [ $startDir != "jh-recsynclib" ]; then
    echo "You should be running this from within the base of the project"
    echo "bailing..."
    exit 1
fi

