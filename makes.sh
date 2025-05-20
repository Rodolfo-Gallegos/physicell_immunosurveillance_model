#!/bin/bash

set -e  # Detiene la ejecución si ocurre un error

echo "Cleaning project..."
make clean

echo "Building project with 8 threads..."
make -j 8

#echo "Running project..."
#./project
