#!/bin/bash

# Define the path to the configuration file
CONFIG_FILE="multiagentbench/bargaining/task.yaml" #config path for the research scenario

# Execute the simulation engine with the specified configuration
LOG_FILE="logs/bargaining/log_bargaining_$(date +%Y%m%d_%H%M%S).log"
python marble/main.py --config "$CONFIG_FILE" > >(tee $LOG_FILE) 2>&1
