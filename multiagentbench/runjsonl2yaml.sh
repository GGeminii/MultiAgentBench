#!/bin/bash
# Bash script to run jsonl_to_yaml.py with parameters defined as variables

# Define variables for the parameters
INPUT_FILE="./bargaining/bargaining_main.jsonl"
#OUTPUT_FOLDER="output_yaml_files_main"
OUTPUT_FOLDER="bargaining-xiaomi"
DEFAULT_COORDINATE_MODE="graph"
#DEFAULT_ENVIRONMENT='{"max_iterations": 5, "name": "Research Collaboration Environment", "type": "Research"}'
DEFAULT_ENVIRONMENT='{"max_iterations": 5, "name": "WorldSimulation Competition Environment", "type": "WorldSimulation"}'
#DEFAULT_LLM="gpt-3.5-turbo"
#DEFAULT_LLM="deepseek/deepseek-chat"
#DEFAULT_LLM="openrouter/meta-llama/llama-3.3-70b-instruct:free"
DEFAULT_LLM="openrouter/xiaomi/mimo-v2-flash:free"
DEFAULT_MEMORY='{"type": "BaseMemory"}'
#DEFAULT_METRICS_EVALUATE_LLM="gpt-4o"
#DEFAULT_METRICS_EVALUATE_LLM="deepseek/deepseek-chat"
#DEFAULT_METRICS_EVALUATE_LLM="openrouter/meta-llama/llama-3.3-70b-instruct:free"
DEFAULT_METRICS_EVALUATE_LLM="openrouter/xiaomi/mimo-v2-flash:free"
DEFAULT_OUTPUT='{"file_path": "result/discussion_output.jsonl"}'

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
