import json
import sys
from collections import defaultdict


def calculate_ts_cs(data):
    """计算TS和CS"""
    # 1. 计算TS
    agent_kpis = data.get('agent_kpis', {})
    total_milestones = data.get('total_milestones', 0)

    ts = 0.0
    if agent_kpis and total_milestones > 0:
        kpis_sum = sum(agent_kpis.values())
        kpis_count = len(agent_kpis)
        denominator = total_milestones * kpis_count
        ts = kpis_sum / denominator if denominator > 0 else 0

    # 2. 计算CS
    planning_scores = data.get('planning_scores', [])
    communication_scores = data.get('communication_scores', [])

    def safe_avg(scores):
        len = 0
        if not scores:
            return 0.0
        safe_scores = []
        # 将-1替换为0
        for i, score in enumerate(scores):
            safe_score = max(score, 0)
            safe_scores.append(safe_score)
            if safe_score > 0:
                len += 1
        if len == 0:
            return sum(safe_scores)
        elif len > 0:
            return sum(safe_scores) / len

    planning_avg = safe_avg(planning_scores)
    comm_avg = safe_avg(communication_scores)
    if comm_avg == 0:
        cs = planning_avg
    elif comm_avg > 0:
        cs = (planning_avg + comm_avg) / 2

    return round(ts, 4), round(cs, 4)


def flatten_dict(d, parent_key='', separator='.'):
    """将嵌套字典展平"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{separator}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, separator).items())
        else:
            items.append((new_key, v))
    return dict(items)


def process_jsonl_file(file_path, evaluation_param):
    """处理JSONL文件"""
    ts_list = []
    cs_list = []
    line_count = 0

    # 用于收集所有评估字段的值
    evaluation_stats = defaultdict(list)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            print("行号\tTS\tCS\tEvaluation Fields")
            print("-" * 70)
            total_token_usage = 0
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    token_usage = data.get('token_usage', 0)
                    print(f"token_usage: {token_usage}")
                    total_token_usage += token_usage
                    # 计算TS和CS
                    ts, cs = calculate_ts_cs(data)

                    # 获取评估字段
                    evaluation_data = data.get(evaluation_param, {})

                    # 展平嵌套字典以便处理
                    flattened_eval = flatten_dict(evaluation_data)

                    # 收集每个字段的值
                    for field, value in flattened_eval.items():
                        if isinstance(value, (int, float)):
                            evaluation_stats[field].append(value)

                    # 输出结果
                    print(f"{line_num}\t{ts}\t{cs}\t{flattened_eval}")

                    # 收集数据用于计算平均值
                    ts_list.append(ts)
                    cs_list.append(cs)
                    line_count += 1

                except json.JSONDecodeError:
                    print(f"{line_num}\tERROR\tERROR\tInvalid JSON format")
                except Exception as e:
                    print(f"{line_num}\tERROR\tERROR\tError: {str(e)}")
            # 计算并输出TS和CS的平均值
            if ts_list and cs_list:
                print("-" * 70)
                print(f"总token: {total_token_usage}, 平均token:{total_token_usage / line_count}")
                avg_ts = round(sum(ts_list) / len(ts_list), 4)
                avg_cs = round(sum(cs_list) / len(cs_list), 4)
                print(f"平均值\t{avg_ts}\t{avg_cs}({avg_cs * 20})\t(基于 {line_count} 行数据)")

                # 输出评估字段的平均值
                if evaluation_stats:
                    print("\n" + "=" * 70)
                    print(f"{evaluation_param} 字段平均值:")
                    print("-" * 70)

                    for field, values in sorted(evaluation_stats.items()):
                        if values:
                            avg_value = round(sum(values) / len(values), 4)
                            print(f"{field}: {avg_value} (基于 {len(values)} 个值)")

                    # 计算整体平均值（所有字段的平均）
                    all_values = []
                    for values in evaluation_stats.values():
                        all_values.extend(values)

                    if all_values:
                        overall_avg = round(sum(all_values) / len(all_values), 4)
                        print("-" * 70)
                        print(f"整体平均值: {overall_avg}({overall_avg * 20}) (基于 {len(all_values)} 个评估值)")
            else:
                print("没有有效的数据行")

    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 不存在")
        sys.exit(1)
    except Exception as e:
        print(f"处理文件时发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # 使用示例
    process_jsonl_file(
        "result/research/ablation/research_qwen3_30b_output.jsonl",
        # "result/bargaining/ablation/bargaining_qwen3_30b_output.jsonl",
        # "result/coding/ablation/coding_qwen3_30b_output.jsonl",
        'task_evaluation'  # 可以改为 'code_quality' / 'task_evaluation'
    )