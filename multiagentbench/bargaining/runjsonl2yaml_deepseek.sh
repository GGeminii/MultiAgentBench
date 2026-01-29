#!/bin/bash
# Bash script to run jsonl_to_yaml.py with parameters defined as variables

# Define variables for the parameters
INPUT_FILE="./bargaining/bargaining_deepseek.jsonl"
OUTPUT_FOLDER="./bargaining/dataset/bargaining-deepseek"
DEFAULT_COORDINATE_MODE="graph"
DEFAULT_ENVIRONMENT='{"max_iterations": 5, "name": "WorldSimulation Competition Environment", "type": "WorldSimulation"}'
DEFAULT_LLM="deepseek/deepseek-chat"
DEFAULT_MEMORY='{"type": "BaseMemory"}'
DEFAULT_METRICS_EVALUATE_LLM="deepseek/deepseek-chat"
DEFAULT_OUTPUT='{"file_path": "result/bargaining/bargaining_deepseek_output.jsonl"}'

# Run the jsonl_to_yaml.py script with the parameters
python3 jsonl2yaml.py \
  --input_file "$INPUT_FILE" \
  --output_folder "$OUTPUT_FOLDER" \
  --default_coordinate_mode "$DEFAULT_COORDINATE_MODE" \
  --default_environment "$DEFAULT_ENVIRONMENT" \
  --default_llm "$DEFAULT_LLM" \
  --default_memory "$DEFAULT_MEMORY" \
  --default_metrics_evaluate_llm "$DEFAULT_METRICS_EVALUATE_LLM" \
  --default_output "$DEFAULT_OUTPUT"