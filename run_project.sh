#!/usr/bin/env bash
# CPUF001 Student Marks Data Processor macOS and Linux runner.
# The input CSV filename is passed to the Python program as an argument.
set -eu
python3 student_data_processor.py input_data.csv
