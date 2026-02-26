#!/bin/bash

# Activate virtual environment and run pipeline
source venv/bin/activate
python pipeline.py "$@"
