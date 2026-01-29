from marble.memory import BaseMemory

def generate_agent_task_planning_prompt(
    agent_id: str,
    persona: str,
    task_history_str: str,
    memory_str: str,
    full_feedback: dict
) -> str:
    """
    嵌入完整反馈包的任务规划提示词（处理full_feedback为{}或None的边界情况）
    """
    # 1. 判空处理：设置默认值，避免KeyError或AttributeError
    if not full_feedback:
        default_individual_feedback = """
### 反馈等级
优化
### 本轮表现总结
暂无历史表现数据，需首次探索高效完成任务的方式，聚焦自身角色核心职责。
### 下一轮行为指导
1.  优先完成与自身角色强相关的核心任务，争取首个里程碑贡献；
2.  主动了解团队其他智能体职责，为后续协作打下基础；
3.  记录任务执行中的有效方法，形成个人经验记忆。
"""
        default_team_feedback = """
### 团队整体表现总结
暂无团队历史协作数据，需建立初始协作机制，共同推进任务目标。
### 关系图(交流)优化建议
1.  主动与核心任务相关智能体建立沟通，传递有效任务信息；
2.  避免无效信息干扰，聚焦任务本身的协作推进；
3.  优先配合任务负责人，共同完成团队首个里程碑。
### 团队下一轮协作策略
1.  明确各智能体角色分工，避免任务重叠或遗漏；
2.  建立简单的任务同步机制，及时更新任务进度；
3.  共同聚焦核心目标，争取完成团队首轮里程碑任务。
"""
        individual_feedback = default_individual_feedback
        team_feedback = default_team_feedback
        agent_reward = 0.0  # 无反馈时默认奖励值为0.0
        full_feedback = {
            "individual_feedbacks": {agent_id: individual_feedback},
            "team_feedback": team_feedback,
            "agent_rewards": {agent_id: agent_reward}
        }
    else:
        # 2. 从完整反馈包中提取关键内容（即使字典非空，也做get容错，避免缺键报错）
        agent_id = agent_id
        individual_feedback = full_feedback.get("individual_feedbacks", {}).get(agent_id, """
### 反馈等级
优化
### 本轮表现总结
暂无有效个人表现数据，需聚焦自身角色，提升任务完成质量。
### 下一轮行为指导
1.  优先完成核心任务，争取获得里程碑贡献；
2.  优化任务执行流程，提升个人工作效率；
3.  积极配合团队协作，助力团队整体评分提升。
""")
        team_feedback = full_feedback.get("team_feedback", """
### 团队整体表现总结
暂无有效团队协作数据，需积极探索高效协作模式。
### 关系图(交流)优化建议
1.  保持与相关智能体的正常沟通，提升协作效率；
2.  优先配合核心任务推进，避免拖慢团队进度；
3.  建立简单的进度同步机制，确保信息畅通。
### 团队下一轮协作策略
1.  明确团队核心目标，共同聚焦任务推进；
2.  弥补团队协作短板，提升整体执行效率；
3.  争取完成更多团队里程碑，提升整体评分。
""")
        # 提取奖励值，缺省时默认0.0
        agent_reward = full_feedback.get("agent_rewards", {}).get(agent_id, 0.0)

    # 3. 构建反馈嵌入模块（突出奖惩机制，简洁直观）
    feedback_module = f"""
### 强化学习反馈指导（本轮个人奖励值：{agent_reward:.4f}）
#### 个人表现反馈
{individual_feedback}
#### 团队协作反馈
{team_feedback}
#### 完整反馈信息
{full_feedback}
#### 奖惩核心提醒
1.  优先选择符合「下一轮行为指导」的任务，将提升个人奖励值与团队评分；
2.  优先选择能完成里程碑、提升贡献占比的任务，将获得额外奖励加分；
3.  避免选择与自身不足相关的任务，防止奖励值下降与团队进度拖慢。
"""

    # 4. 嵌入原有提示词（保留核心逻辑，新增反馈模块）
    final_prompt = f"""
Agent '{agent_id}' should prioritize tasks that align with their role: {persona}.
{feedback_module}
Based on the task history: {task_history_str}, and memory: {memory_str}, what should be the next task?
"""
    return final_prompt


def generate_agent_task_execution_prompt(
    agent_id: str,
    profile: str,
    memory: BaseMemory,
    reasoning_prompt: str,
    task: str,
    agent_descriptions: list[str],
    full_feedback: dict
) -> str:
    """
    嵌入完整反馈包的任务执行提示词（处理full_feedback为{}或None的边界情况）
    """
    # 1. 判空处理：设置默认值，避免KeyError或AttributeError
    if not full_feedback:  # 同时匹配None、{}（空字典）两种情况
        default_individual_feedback = """
### 反馈等级
优化
### 本轮表现总结
暂无历史执行数据，需首次规范执行任务，确保任务质量符合要求。
### 下一轮行为指导
1.  严格按照自身角色职责执行任务，确保成果可验证、可落地；
2.  主动记录任务执行中的问题与解决方案，形成个人记忆；
3.  若需要协作，主动与相关智能体沟通，传递清晰有效的信息。
"""
        default_team_feedback = """
### 团队整体表现总结
暂无团队历史执行数据，需建立初始协作规范，共同提升任务完成率。
### 关系图(交流)优化建议
1.  与其他智能体沟通时，聚焦任务核心，避免传递无效信息；
2.  优先配合完成团队核心任务，助力团队首个里程碑落地；
3.  及时同步任务执行进度，让团队掌握整体推进情况。
### 团队下一轮协作策略
1.  明确各智能体任务边界，避免任务重叠或责任缺失；
2.  建立简单的问题反馈机制，及时解决协作中的障碍；
3.  共同优化任务执行流程，提升团队整体执行效率。
"""
        individual_feedback = default_individual_feedback
        team_feedback = default_team_feedback
        agent_reward = 0.0  # 无反馈时默认奖励值为0.0
        full_feedback = {
            "individual_feedbacks": {agent_id: individual_feedback},
            "team_feedback": team_feedback,
            "agent_rewards": {agent_id: agent_reward}
        }
    else:
        # 2. 从完整反馈包中提取关键内容（即使字典非空，也做get容错，避免缺键报错）
        agent_id = agent_id
        individual_feedback = full_feedback.get("individual_feedbacks", {}).get(agent_id, """
### 反馈等级
优化
### 本轮表现总结
暂无有效个人执行数据，需严格规范执行流程，提升任务完成质量。
### 下一轮行为指导
1.  聚焦任务核心目标，确保执行成果能支撑团队里程碑；
2.  优化个人执行效率，避免拖延影响团队整体进度；
3.  主动配合团队协作，遵循团队既定的协作规则。
""")
        team_feedback = full_feedback.get("team_feedback", """
### 团队整体表现总结
暂无有效团队执行数据，需探索高效协作模式，提升整体评分。
### 关系图(交流)优化建议
1.  保持与相关智能体的顺畅沟通，提升协作效率；
2.  优先支撑低贡献智能体完成任务，弥补团队能力缺口；
3.  避免无效沟通，确保信息传递准确、高效。
### 团队下一轮协作策略
1.  共同聚焦团队核心目标，推进里程碑任务落地；
2.  总结协作中的有效方法，形成团队协作规范；
3.  弥补团队执行短板，提升整体任务完成率与评分。
""")
        # 提取奖励值，缺省时默认0.0
        agent_reward = full_feedback.get("agent_rewards", {}).get(agent_id, 0.0)

    # 3. 构建反馈嵌入模块（突出执行阶段的奖惩约束）
    feedback_module = f"""
### 强化学习反馈执行约束（本轮个人奖励值：{agent_reward:.4f}）
#### 个人执行反馈
{individual_feedback}
#### 团队协作约束
{team_feedback}
#### 完整反馈信息
{full_feedback}
#### 奖惩结果关联
1.  严格遵循「下一轮行为指导」执行任务，完成里程碑将显著提升个人奖励值；
2.  遵循团队「关系图优化建议」与协作策略，将提升团队评分并获得额外奖励；
3.  若重复出现个人不足、违反团队协作要求，将导致奖励值下降并影响团队任务完成率。
"""

    # 4. 嵌入原有提示词（保留核心逻辑，新增反馈模块，修正拼写错误）
    final_prompt = f"""
You are {agent_id}: {profile}
{reasoning_prompt}
{feedback_module}
This is your task: {task}
These are the ids and profiles of other agents you can interact with:
{agent_descriptions}
But you do not have to communicate with other agents.
You can also solve the task by calling other functions to solve it by yourself.
These are your memory: {memory.get_memory_str()}
"""
    return final_prompt