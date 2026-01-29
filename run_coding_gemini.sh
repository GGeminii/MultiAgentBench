WORKSPACE_DIR="workspace"
UPDATE_SCRIPT="scripts/coding/utils/update_coding_config.py"
# 配置文件的基础路径
CONFIG_BASE_PATH="marble/configs/coding_config/coding_config_gemini.yaml"
# 执行日志文件的基础路径
LOG_BASE_PATH="logs/coding/gemini/log_coding_"
# 代码方案日志目录名称
model_name="gemini"
safe_model_name=$(echo ${model_name} | tr '/' '_')
SOLUTION_LOG_DIR="logs/coding_solution/${safe_model_name}"

mkdir -p ${SOLUTION_LOG_DIR}

for id in {4..10}; do
    echo "Processing task with ID=$id..."
    rm -rf ${WORKSPACE_DIR}/*
    python ${UPDATE_SCRIPT} --benchmark_id ${id}
    echo "Running the demo script..."

    # 配置文件完整路径
    CONFIG_FILE="${CONFIG_BASE_PATH}"

    # 检查配置文件是否存在
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "错误：配置文件 $CONFIG_FILE 不存在，跳过本次循环"
        continue
    fi

    # 日志文件完整路径
    CURRENT_DATETIME=$(date +%Y%m%d_%H%M%S)
    LOG_FILE="${LOG_BASE_PATH}${id}_${CURRENT_DATETIME}.log"

    # 打印当前执行信息
    echo "======================================"
    echo "正在执行第 $id 次运行，配置文件：$CONFIG_FILE"
    echo "日志文件将保存为：$LOG_FILE"
    echo "======================================"

    # 执行仿真引擎
    python marble/main.py --config "$CONFIG_FILE" --feedback_mode > >(tee "$LOG_FILE") 2>&1

    echo "Saving solution file..."
    cp ${WORKSPACE_DIR}/solution.py ${SOLUTION_LOG_DIR}/solution_${id}.py
    echo "Task with ID=$id completed."
    echo "==============================="
done

echo "All tasks have been processed!"
