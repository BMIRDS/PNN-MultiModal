#!/bin/bash

DATA_DIR="/datasets/PNN_study"

INPUT_CSV="${DATA_DIR}/TMA1054 hWTA_20230817T1508_LabWorksheet.csv"
OUTPUT_DIR="outputs/test01"
ROI_INDEX=3

python testpt2.py \
-i "${INPUT_CSV}" \
-o "${OUTPUT_DIR}" \
-d "${DATA_DIR}" \
--roi ${ROI_INDEX} \
--test-case
