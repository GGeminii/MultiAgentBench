import json
from typing import List, Dict, Any


def handle_bargaining(
        input_path: str,
        seller_llm: str,
        buyer_llm: str,
        output_path: str
) -> List[Dict[str, Any]]:
    """
    处理价格商议数据集，替换agents中不同角色的llm字段，并将结果写入指定文件
    Args:
        input_path: 输入JSON数据集文件路径（每行一个JSON对象）
        seller_llm: 卖方模型名称，用于替换seller角色agent的llm字段
        buyer_llm: 买方模型名称，用于替换buyer角色agent的llm字段
        output_path: 处理后数据的输出文件路径
    Returns:
        List[Dict[str, Any]]: 处理后的所有数据列表
    """
    processed_data = []

    # 1. 读取并处理输入文件
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # 去除行首尾空白字符，跳过空行
                line = line.strip()
                if not line:
                    continue

                try:
                    # 解析单行JSON数据
                    data = json.loads(line)

                    # 替换agents中的llm字段
                    if 'agents' in data and isinstance(data['agents'], list):
                        for agent in data['agents']:
                            # 确保agent是字典且包含role和llm字段
                            if isinstance(agent, dict) and 'role' in agent and 'llm' in agent:
                                role = agent['role'].lower()  # 统一小写避免大小写问题
                                if role == 'seller':
                                    agent['llm'] = seller_llm
                                elif role == 'buyer':
                                    agent['llm'] = buyer_llm

                    processed_data.append(data)

                except json.JSONDecodeError as e:
                    print(f"警告：第 {line_num} 行JSON解析失败，跳过该行。错误信息：{e}")
                except Exception as e:
                    print(f"警告：第 {line_num} 行处理出错，跳过该行。错误信息：{e}")

    except FileNotFoundError:
        raise FileNotFoundError(f"错误：输入文件不存在 - {input_path}")
    except PermissionError:
        raise PermissionError(f"错误：没有权限读取输入文件 - {input_path}")
    except Exception as e:
        raise Exception(f"读取输入文件时发生未知错误：{e}")

    # 2. 将处理后的数据写入输出文件
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in processed_data:
                # 确保JSON序列化时保留中文，且格式紧凑
                json_line = json.dumps(item, ensure_ascii=False)
                f.write(json_line + '\n')  # 每行一个JSON对象，符合JSONL格式
        print(f"成功！处理后的数据已写入：{output_path}")

    except PermissionError:
        raise PermissionError(f"错误：没有权限写入输出文件 - {output_path}")
    except Exception as e:
        raise Exception(f"写入输出文件时发生未知错误：{e}")

    return processed_data


# 测试示例
if __name__ == "__main__":
    # 配置参数
    INPUT_FILE = "bargaining_main.jsonl"  # 输入文件路径
    OUTPUT_FILE = "bargaining_gpt.jsonl"  # 输出文件路径
    SELLER_LLM = "gpt-4o-mini"  # 卖方要替换的LLM名称
    BUYER_LLM = "gpt-4o-mini"  # 买方要替换的LLM名称

    try:
        # 调用函数处理数据
        result = handle_bargaining(INPUT_FILE, SELLER_LLM, BUYER_LLM, OUTPUT_FILE)
        print(f"\n总计成功处理 {len(result)} 条数据")

        # 验证第一条数据的替换结果
        if result:
            print("\n第一条数据的agents llm字段替换结果：")
            for agent in result[0]['agents']:
                print(f"- Agent {agent['agent_id']} (role: {agent['role']}) → llm: {agent['llm']}")

    except Exception as e:
        print(f"处理失败：{str(e)}")
