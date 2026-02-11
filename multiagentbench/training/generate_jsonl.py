import json
import os
import copy  # 引入深拷贝，避免字典引用导致的错误


def get_existing_task_count(output_file_path):
    """
    读取输出文件的已有行数（仅统计合法的JSON行），用于确定续写的起始task_id

    Args:
        output_file_path (str): 输出文件路径

    Returns:
        int: 输出文件中已有的有效JSON行数，若无文件则返回0
    """
    if not os.path.exists(output_file_path):
        return 0

    valid_lines = 0
    try:
        with open(output_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:  # 跳过空行
                    continue
                # 验证是否为合法JSON（仅统计有效JSON行）
                try:
                    json.loads(line)
                    valid_lines += 1
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"读取输出文件已有行数时警告: {e}，默认按0行处理")
        return 0
    return valid_lines


def replace_task_in_json_template(input_file_path, output_file_path,
                                  start_task_id=None, start_line=None, end_line=None):
    """
    读取输入文件的指定行范围，替换JSON模板中的{task}，并**续写**到输出文件（jsonl格式）
    - 不传start_task_id时，自动读取输出文件已有行数，从 已有行数+1 开始
    - task_id默认对应输出文件的行号（第N行的task_id=N）
    - 每个JSON输出严格占一行，JSON间无空行
    - 确保输入文件每行文本精准替换模板中的{task}占位符

    Args:
        input_file_path (str): 输入文件路径（每行是要替换{task}的文本）
        output_file_path (str): 输出文件路径（jsonl格式，续写模式）
        start_task_id (int/None): task_id起始值，None则自动计算（已有行数+1）
        start_line (int/None): 输入文件起始行号（包含，从1开始），None=第一行
        end_line (int/None): 输入文件结束行号（包含，从1开始），None=最后一行
    """
    # 定义JSON模板字典（基础结构）
    json_template_dict = {
        "scenario": "training",
        "task_id": 0,  # 占位，后续替换为实际数值
        "agents": [
            {
                "agent_id": "agent1",
                "profile": "I am a Training Requirements Extraction Specialist, dedicated to precisely extracting training requirements, target job competency requirements, core theoretical knowledge points, typical operational scenarios, and training objectives from industrial knowledge bases (regulations, cases, operation manuals, etc.). With profound industrial domain knowledge and training system design experience, I can identify key training elements from unstructured text, ensuring extracted content is highly aligned with actual job needs and laying a foundation for the precise generation of training content.",
                "type": "BaseAgent"
            },
            {
                "agent_id": "agent2",
                "profile": "I am an AI-driven Training Package Generation Process Analyst, specializing in organizing the generation process of modular training packages. I excel at transforming complex AI workflows into clear step sequences, including input-output relationships, flow logic, and execution conditions for core links such as knowledge base data parsing, intelligent extraction of theoretical knowledge points, combination of standardized operational steps, and training package data encapsulation. My work ensures the accuracy and executability of process models, providing a solid process foundation for the formulation of operational specifications.",
                "type": "BaseAgent"
            },
            {
                "agent_id": "agent3",
                "profile": "I am an Operational Specification Engineer for Training Package Generation, focusing on defining operational specifications during the AI-driven training package generation process. I can distill data parsing standards, knowledge point extraction rules, operational step combination logic, data encapsulation formats, quality verification requirements, exception handling mechanisms, and compliance constraints from processes and requirements. My work ensures the standardization, repeatability, and accuracy of training content throughout the process, providing clear behavioral guidelines for the standardization of modular training packages.",
                "type": "BaseAgent"
            },
            {
                "agent_id": "agent4",
                "profile": "I am a Technical Documentation and Localization Specialist for Training Systems, dedicated to transforming training package generation processes and operational specifications into professional, formal English technical documentation. I am proficient in the format and terminology of training system documents and System Requirements Specifications (SRS), capable of unifying professional terminology, optimizing sentence structures, maintaining consistent style, and structuring layout in accordance with international standards, ensuring that the final output document is clear, rigorous, and meets international engineering and training practice requirements.",
                "type": "BaseAgent"
            }
        ],
        "coordinate_mode": "",
        "engine_planner": {
            "initial_progress": "Initiating the scenario-driven modular training system research task, leveraging AI to automatically parse knowledge base data, extract and combine knowledge points and operational steps, and form standardized training package encapsulation processes and specifications."
        },
        "environment": {
            "max_iterations": "",
            "name": "",
            "type": ""
        },
        "llm": "",
        "memory": {
            "type": ""
        },
        "metrics": {
            "content_accuracy": True,
            "structural_completeness": True,
            "specification_compliance": True,
            "practical_operability": True,
            "evaluate_llm": ""
        },
        "output": {
            "file_path": "",
            "format": "jsonl"
        },
        "relationships": [
            ["agent1", "agent2", "collaborate with"],
            ["agent1", "agent3", "collaborate with"],
            ["agent1", "agent4", "collaborate with"],
            ["agent2", "agent3", "collaborate with"],
            ["agent2", "agent4", "collaborate with"],
            ["agent3", "agent4", "collaborate with"]
        ],
        "task": {
            "content": "\n            Dear Expert Team:\n\n            You will collaborate on a scenario-driven modular training system research task, aiming to address the problem of rigid training content disconnected from practical application by studying how to use AI to automatically parse data such as regulations and cases in the knowledge base, intelligently extract and combine relevant theoretical knowledge points and standardized operational steps, and form a standardized data encapsulation process and specification for modular training packages.\n\n            **Task Instance**:\n            {task}\n\n            **Your Task**:\n\n            1. **Training Requirements Extraction**: Extract basic information such as training requirements, target competencies, core knowledge points, and operational scenarios from the knowledge base (e.g., the conveyor belt case above) to provide a data source for subsequent tasks.\n            2. **Process Organization**: Organize the AI-driven training package generation process, including steps, sequences, input/output, flow logic, and execution conditions for links such as data parsing, knowledge point extraction, operational step combination, and data encapsulation.\n            3. **Operational Specification Definition**: Define operational specifications during AI parsing, extraction, combination, and encapsulation, including standards, rules, quality requirements, exception handling, and compliance constraints.\n            4. **English and Format Integration**: Translate processes and specifications into professional English, unify terminology, format according to SRS or training system document standards, and output a complete, standardized English technical document.\n\n            Please collaborate to complete the above tasks, ensuring that the final output processes and specifications are accurate, clear, and in line with industrial training practice standards.\n\n            Good luck!\n            ",
            "output_format": "You need to output the final results in the following format:\n                **[Training Requirements Extraction Results]**\n                List core training requirements, target competencies, knowledge points, and operational scenarios extracted from the knowledge base.\n\n                **[Process Organization Results]**\n                Present the AI-driven training package generation process as a step sequence, clearly defining the input, output, execution conditions, and flow logic of each link.\n\n                **[Operational Specification Definition Results]**\n                Define operational specifications, standards, rules, and exception handling mechanisms for data parsing, extraction, combination, and encapsulation.\n\n                **[English Integrated Document]**\n                Output a complete English technical document formatted according to SRS or training system document standards, with unified terminology and professional style."
        }
    }

    try:
        # 1. 确定起始task_id
        if start_task_id is None:
            existing_count = get_existing_task_count(output_file_path)
            start_task_id = existing_count + 1
            print(
                f"未指定start_task_id，自动计算起始值：输出文件已有{existing_count}行有效数据 → 起始task_id={start_task_id}")
        current_task_id = start_task_id

        # 2. 读取输入文件并处理行范围
        with open(input_file_path, 'r', encoding='utf-8') as infile:
            all_lines = infile.readlines()
        total_input_lines = len(all_lines)

        # 处理行号参数合法性
        start_line = 1 if start_line is None else max(1, start_line)
        end_line = total_input_lines if end_line is None else min(total_input_lines, end_line)

        if start_line > end_line:
            print(f"错误：输入文件起始行({start_line})大于结束行({end_line})，无数据可处理！")
            return

        target_lines = all_lines[start_line - 1: end_line]
        print(
            f"输入文件总行数：{total_input_lines}，待处理行范围：{start_line}-{end_line}，实际待处理行数：{len(target_lines)}")

        # 3. 续写模式打开输出文件
        with open(output_file_path, 'a', encoding='utf-8') as outfile:
            for line_idx_in_target, raw_line in enumerate(target_lines):
                original_line_num = start_line + line_idx_in_target
                # 清理输入行（仅去除首尾空白，保留内部换行/空格）
                task_content = raw_line.strip()

                # 跳过空行
                if not task_content:
                    print(f"跳过输入文件第{original_line_num}行（空行），task_id保持为: {current_task_id}")
                    continue

                # 关键：深拷贝模板字典，避免引用导致的批量替换错误
                temp_dict = copy.deepcopy(json_template_dict)

                # 1. 替换task_id（数字类型，符合JSON规范）
                temp_dict["task_id"] = current_task_id

                # 2. 精准替换{task}占位符（核心修正：确保100%替换）
                if "{task}" in temp_dict["task"]["content"]:
                    temp_dict["task"]["content"] = temp_dict["task"]["content"].replace("{task}", task_content)
                else:
                    print(f"警告：输入文件第{original_line_num}行处理时，模板中未找到{{task}}占位符")
                    continue

                # 转为单行紧凑JSON字符串
                new_json_str = json.dumps(temp_dict, ensure_ascii=False, separators=(',', ':'))

                # 续写（仅加换行符分隔，无空行）
                outfile.write(new_json_str + '\n')
                print(
                    f"成功处理：输入文件第{original_line_num}行 → 输出task_id={current_task_id}，替换内容：{task_content[:50]}...")

                # task_id递增
                current_task_id += 1

        # 最终统计
        final_task_id = current_task_id - 1
        print(f"\n处理完成！输出文件：{output_file_path}")
        if start_task_id > final_task_id:
            print("本次无有效数据写入（全部为空行/错误行）")
        else:
            print(
                f"本次续写的task_id范围：{start_task_id} ~ {final_task_id}（共{final_task_id - start_task_id + 1}行有效数据）")

    except FileNotFoundError as e:
        print(f"错误：文件不存在 - {e}")
    except PermissionError as e:
        print(f"错误：文件权限不足 - {e}")
    except Exception as e:
        print(f"错误：处理过程异常 - {e}")


# -------------------------- 主程序入口 --------------------------
if __name__ == "__main__":
    # 自定义配置
    INPUT_FILE = "./dataset/03_specs.txt"  # 输入文件（每行是要替换{task}的文本）
    OUTPUT_FILE = "./training_main.jsonl"  # 输出JSONL文件
    START_TASK_ID = None  # 自动计算起始task_id
    START_LINE = 50  # 从第1行开始处理
    END_LINE = 79  # 处理到第2行结束

    # 执行替换任务
    replace_task_in_json_template(
        input_file_path=INPUT_FILE,
        output_file_path=OUTPUT_FILE,
        start_task_id=START_TASK_ID,
        start_line=START_LINE,
        end_line=END_LINE
    )