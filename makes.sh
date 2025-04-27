#!/bin/bash

set -e  # Detiene la ejecución si ocurre un error

echo "Cleaning project..."
make clean

echo "Building project with 12 threads..."
make -j 12

echo "Running project..."
./project
