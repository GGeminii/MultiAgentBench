from marble.memory import BaseMemory

def generate_agent_task_planning_prompt(
    agent_id: str,
    persona: str,
    task_history_str: str,
    memory_str: str,
    full_feedback: dict
) -> str:
    """
    嵌入完整反馈包的任务规划提示词
    """
    # 判空处理
    if not full_feedback:
        default_individual_feedback = """
### Feedback Level
Optimization
### Current Round Performance Summary
No historical performance data available. You need to explore efficient task completion methods for the first time and focus on the core responsibilities of your role.
### Next Round Action Guidelines
1.  Prioritize completing core tasks closely related to your role to strive for the first milestone contribution;
2.  Proactively understand the responsibilities of other agents in the team to lay a foundation for subsequent collaboration;
3.  Record effective methods during task execution to form personal experiential memory.
"""
        default_team_feedback = """
### Team Overall Performance Summary
No historical team collaboration data available. It is necessary to establish an initial collaboration mechanism to jointly advance task objectives.
### Relationship Graph (Communication) Optimization Suggestions
1.  Proactively establish communication with agents related to core tasks and transmit effective task information;
2.  Avoid interference from invalid information and focus on the collaborative advancement of the task itself;
3.  Prioritize cooperating with the task leader to jointly complete the team's first milestone.
### Team Next Round Collaboration Strategy
1.  Clarify the role division of each agent to avoid task overlap or omission;
2.  Establish a simple task synchronization mechanism to update task progress in a timely manner;
3.  Jointly focus on core objectives to strive for completing the team's first round of milestone tasks.
"""
        individual_feedback = default_individual_feedback
        team_feedback = default_team_feedback
        agent_reward = 0.0
        full_feedback = {
            "individual_feedbacks": {agent_id: individual_feedback},
            "team_feedback": team_feedback,
            "agent_rewards": {agent_id: agent_reward}
        }
    else:
        # 从完整反馈包中提取关键内容
        agent_id = agent_id
        individual_feedback = full_feedback.get("individual_feedbacks", {}).get(agent_id, """
### Feedback Level
Optimization
### Current Round Performance Summary
No valid personal performance data available. Focus on your role and improve the quality of task completion.
### Next Round Action Guidelines
1.  Prioritize completing core tasks to strive for milestone contributions;
2.  Optimize the task execution process to improve personal work efficiency;
3.  Actively cooperate with team collaboration to help improve the overall team score.
""")
        team_feedback = full_feedback.get("team_feedback", """
### Team Overall Performance Summary
No valid team collaboration data available. It is necessary to actively explore efficient collaboration modes.
### Relationship Graph (Communication) Optimization Suggestions
1.  Maintain normal communication with relevant agents to improve collaboration efficiency;
2.  Prioritize cooperating with the advancement of core tasks to avoid delaying the overall team progress;
3.  Establish a simple progress synchronization mechanism to ensure smooth information flow.
### Team Next Round Collaboration Strategy
1.  Clarify the team's core objectives and jointly focus on task advancement;
2.  Make up for the shortcomings of team collaboration to improve overall execution efficiency;
3.  Strive to complete more team milestones to improve the overall score.
""")
        # 提取奖励值，缺省时默认0.0
        agent_reward = full_feedback.get("agent_rewards", {}).get(agent_id, 0.0)

    # 3. 构建反馈嵌入模块
    feedback_module = f"""
### Reinforcement Learning Feedback Guidance (Current Round Personal Reward Value: {agent_reward:.4f})
#### Personal Performance Feedback
{individual_feedback}
#### Team Collaboration Feedback
{team_feedback}
#### Complete Feedback Information
{full_feedback}
#### Core Reward and Punishment Reminders
1.  Prioritize tasks that align with the "Next Round Action Guidelines" to improve your personal reward value and the team's overall score;
2.  Prioritize tasks that can complete milestones and increase your contribution ratio to obtain additional reward points;
3.  Avoid tasks related to your shortcomings to prevent a decline in reward value and delays in the overall team progress.
"""

    # 4. 嵌入原有提示词
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
    # 判空处理
    if not full_feedback:
        default_individual_feedback = """
### Feedback Level
Optimization
### Current Round Performance Summary
No historical execution data available. You need to standardize task execution for the first time to ensure that the task quality meets requirements.
### Next Round Action Guidelines
1.  Strictly perform tasks in accordance with the responsibilities of your role to ensure that the results are verifiable and implementable;
2.  Proactively record problems and solutions during task execution to form personal memory;
3.  If collaboration is needed, proactively communicate with relevant agents and transmit clear and effective information.
"""
        default_team_feedback = """
### Team Overall Performance Summary
No historical team execution data available. It is necessary to establish initial collaboration norms to jointly improve the task completion rate.
### Relationship Graph (Communication) Optimization Suggestions
1.  Focus on the core of the task when communicating with other agents and avoid transmitting invalid information;
2.  Prioritize cooperating to complete the team's core tasks to help the team's first milestone land;
3.  Synchronize task execution progress in a timely manner to keep the team informed of the overall advancement.
### Team Next Round Collaboration Strategy
1.  Clarify the task boundaries of each agent to avoid task overlap or lack of responsibility;
2.  Establish a simple problem feedback mechanism to solve obstacles in collaboration in a timely manner;
3.  Jointly optimize the task execution process to improve the overall team execution efficiency.
"""
        individual_feedback = default_individual_feedback
        team_feedback = default_team_feedback
        agent_reward = 0.0
        full_feedback = {
            "individual_feedbacks": {agent_id: individual_feedback},
            "team_feedback": team_feedback,
            "agent_rewards": {agent_id: agent_reward}
        }
    else:
        # 从完整反馈包中提取关键内容
        agent_id = agent_id
        individual_feedback = full_feedback.get("individual_feedbacks", {}).get(agent_id, """
### Feedback Level
Optimization
### Current Round Performance Summary
No valid personal execution data available. Strictly standardize the execution process to improve the quality of task completion.
### Next Round Action Guidelines
1.  Focus on the core objectives of the task to ensure that the execution results can support team milestones;
2.  Optimize personal execution efficiency to avoid delaying the overall team progress;
3.  Proactively cooperate with team collaboration and follow the established team collaboration rules.
""")
        team_feedback = full_feedback.get("team_feedback", """
### Team Overall Performance Summary
No valid team execution data available. Explore efficient collaboration modes to improve the overall score.
### Relationship Graph (Communication) Optimization Suggestions
1.  Maintain smooth communication with relevant agents to improve collaboration efficiency;
2.  Prioritize supporting agents with low contributions to complete tasks to make up for the team's capability gaps;
3.  Avoid invalid communication to ensure accurate and efficient information transmission.
### Team Next Round Collaboration Strategy
1.  Jointly focus on the team's core objectives to promote the landing of milestone tasks;
2.  Summarize effective methods in collaboration to form team collaboration norms;
3.  Make up for the shortcomings of team execution to improve the overall task completion rate and score.
""")
        # 提取奖励值，缺省时默认0.0
        agent_reward = full_feedback.get("agent_rewards", {}).get(agent_id, 0.0)

    # 构建反馈嵌入模块
    feedback_module = f"""
### Reinforcement Learning Feedback Execution Constraints (Current Round Personal Reward Value: {agent_reward:.4f})
#### Personal Execution Feedback
{individual_feedback}
#### Team Collaboration Constraints
{team_feedback}
#### Complete Feedback Information
{full_feedback}
#### Reward and Punishment Result Correlation
1.  Strictly follow the "Next Round Action Guidelines" to execute tasks. Completing milestones will significantly improve your personal reward value;
2.  Follow the team's "Relationship Graph (Communication) Optimization Suggestions" and collaboration strategies to improve the team score and obtain additional rewards;
3.  Repeating personal shortcomings or violating team collaboration requirements will lead to a decline in reward value and affect the team's overall task completion rate.
"""

    # 嵌入原有提示词
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