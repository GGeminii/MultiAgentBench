#!/bin/bash

# 定义配置文件的基础路径
CONFIG_BASE_PATH="multiagentbench/bargaining/dataset/bargaining-llama33-70b/task_"
# 定义日志文件的基础路径
LOG_BASE_PATH="logs/bargaining/llama33-70b/log_bargaining_"
LOG_DIR=$(dirname "$LOG_BASE_PATH")
# 递归创建日志目录
mkdir -p "$LOG_DIR"

# 循环100次（从1到100）
for ((i=12; i<=12; i++))
do
    # 拼接当前次数对应的配置文件完整路径
    CONFIG_FILE="${CONFIG_BASE_PATH}${i}.yaml"

    # 检查配置文件是否存在
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "错误：配置文件 $CONFIG_FILE 不存在，跳过本次循环"
        continue
    fi

    # 拼接当前次数对应的日志文件完整路径
    CURRENT_DATETIME=$(date +%Y%m%d_%H%M%S)
    LOG_FILE="${LOG_BASE_PATH}${i}_${CURRENT_DATETIME}.log"

    # 打印当前执行信息
    echo "======================================"
    echo "正在执行第 $i 次运行，配置文件：$CONFIG_FILE"
    echo "日志文件将保存为：$LOG_FILE"
    echo "======================================"

    # 执行仿真引擎
    python marble/main.py --config "$CONFIG_FILE" --feedback_mode > >(tee "$LOG_FILE") 2>&1

    # 打印本次执行完成信息
    echo "第 $i 次运行执行完成"
    echo ""
done

# 循环结束提示
echo "100次循环全部执行完毕！"