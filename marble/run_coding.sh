#!/bin/bash

# Define the path to the configuration file
CONFIG_FILE="marble/configs/coding_config/coding_config.yaml"

# Execute the simulation engine with the specified configuration
LOG_FILE="logs/coding/log_coding_$(date +%Y%m%d_%H%M%S).log"
python marble/main.py --config "$CONFIG_FILE" > >(tee $LOG_FILE) 2>&1
