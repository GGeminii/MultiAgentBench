WORKSPACE_DIR="workspace"
UPDATE_SCRIPT="scripts/coding/utils/update_coding_config.py"
RUN_DEMO_SCRIPT="marble/run_coding.sh"

model_name="deepseek-v3.2"
safe_model_name=$(echo ${model_name} | tr '/' '_')
LOG_DIR="logs/coding_solution/${safe_model_name}"

mkdir -p ${LOG_DIR}

for id in {2..2}; do
    echo "Processing task with ID=$id..."
    rm -rf ${WORKSPACE_DIR}/*
    python ${UPDATE_SCRIPT} --benchmark_id ${id}
    echo "Running the demo script..."
    bash ${RUN_DEMO_SCRIPT}
    echo "Saving solution file..."
    cp ${WORKSPACE_DIR}/solution.py ${LOG_DIR}/solution_${id}.py
    echo "Task with ID=$id completed."
    echo "==============================="
done

echo "All tasks have been processed!"
