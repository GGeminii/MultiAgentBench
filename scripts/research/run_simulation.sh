#!/bin/bash

# Define the path to the configuration file
CONFIG_FILE="/home/ubuntu/xp/app/MultiAgentBench/multiagentbench/output_yaml_files_main/task_1.yaml" #config path for the research scenario

# Execute the simulation engine with the specified configuration
python /home/ubuntu/xp/app/MultiAgentBench/marble/main.py --config "$CONFIG_FILE"
