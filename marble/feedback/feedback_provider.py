import json
import re
from typing import Dict, Any, Tuple

from marble.evaluator.evaluator import Evaluator
from marble.utils import get_logger
from marble.llms.model_prompting import model_prompting

# 奖励函数权重配置（对应需求：规划、沟通、个体贡献）
REWARD_WEIGHTS = {
    "planning": 0.4,
    "communication": 0.3,
    "contribution": 0.3
}

# 奖励等级划分阈值
REWARD_THRESHOLDS = {
    "high": 0.6,  # 高奖励（正向强化）
    "low": 0.3  # 低奖励（惩罚纠正）
}


class FeedbackProvider:
    def __init__(self, task: str, agent_profiles: Dict[str, str], evaluator: Evaluator, is_feedback: bool = True):
        """
        初始化反馈提供者，关联评估器实例，加载反馈提示词模板

        Args:
            evaluator (Evaluator): 已完成评估的Evaluator实例
        """
        self.logger = get_logger(self.__class__.__name__)
        # 基本信息
        self.task = task
        self.agent_profiles = agent_profiles
        self.is_feedback = is_feedback
        self.evaluator = evaluator
        self.llm = self._init_llm()

        # 加载反馈提示词模板
        try:
            with open('marble/feedback/feedback_prompts.json', 'r', encoding='utf-8') as f:
                self.feedback_prompts = json.load(f)
        except FileNotFoundError:
            self.logger.error("The feedback prompt file is not found：marble/feedback/feedback_prompts.json")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"The file format of the feedback prompt is incorrect and the JSON cannot be parsed: {str(e)}")
            raise

        # 存储生成的反馈结果
        self.individual_feedbacks: Dict[str, str] = {}  # 智能体个体反馈
        self.team_feedback: str = ""  # 团队整体反馈
        self.agent_rewards: Dict[str, float] = {}  # 智能体个体奖励值

    def _init_llm(self) -> str:
        """
        从评估器中提取LLM配置，初始化反馈使用的模型
        """
        evaluate_llm_config = self.evaluator.metrics_config.get('evaluate_llm', {})
        if isinstance(evaluate_llm_config, dict):
            return evaluate_llm_config.get('model', 'gpt-3.5-turbo')
        else:
            return evaluate_llm_config or 'gpt-3.5-turbo'

    def _calculate_agent_contribution_ratio(self, agent_id: str) -> float:
        """
        计算单个智能体的贡献占比（个体里程碑数 / 总里程碑数）

        Args:
            agent_id (str): 智能体ID

        Returns:
            float: 贡献占比（0-1之间）
        """
        agent_kpis = self.evaluator.metrics.get("agent_kpis", {})
        agent_milestones = agent_kpis.get(agent_id, 0)
        total_milestones = self.evaluator.metrics.get("total_milestones", agent_milestones)
        return agent_milestones / total_milestones if total_milestones > 0 else 0.0

    def _get_latest_scores(self) -> Tuple[float, float]:
        """
        获取最新的规划得分与沟通得分（取列表最后一个值，无数据返回默认3.0）

        Returns:
            Tuple[float, float]: (最新规划得分, 最新沟通得分)
        """
        planning_scores = self.evaluator.metrics.get("planning_score", [])
        communication_scores = self.evaluator.metrics.get("communication_score", [])

        latest_planning = planning_scores[-1] if planning_scores else 3.0
        latest_communication = communication_scores[-1] if communication_scores else 3.0
        if latest_planning == -1:
            latest_planning = 0.0
        if latest_communication == -1:
            latest_communication = 0.0
        return float(latest_planning), float(latest_communication)

    def calculate_agent_rewards(self) -> Dict[str, float]:
        """
        计算每个智能体的个体奖励值，实现奖励函数：
        R = α·规划得分 + β·沟通得分 + γ·贡献占比
        （注：规划/沟通得分归一化到 0-1 区间，再参与计算，最终奖励值也在0-1之间）

        Returns:
            Dict[str, float]: 智能体ID到奖励值的映射
        """
        latest_planning, latest_communication = self._get_latest_scores()
        agent_kpis = self.evaluator.metrics.get("agent_kpis", {})
        self.logger.debug(f"Start calculating agent rewards and planning scores：{latest_planning}，Communication score：{latest_communication}")

        # 归一化系数（将1-5分映射到0-1）
        score_normalize_factor = 1.0 / 5.0
        # 遍历基准改为 agent_profiles，确保所有智能体都被计算
        for agent_id in self.agent_profiles:
            # 1. 获取个体数据并归一化, 无KPI数据的智能体，贡献占比默认0.0
            if agent_id in agent_kpis:
                contribution_ratio = self._calculate_agent_contribution_ratio(agent_id)
            else:
                contribution_ratio = 0.0
                self.logger.debug(f"Agent {agent_id} has no effective KPI data, and the contribution ratio is set to 0.0 by default")

            normalized_planning = latest_planning * score_normalize_factor
            normalized_communication = latest_communication * score_normalize_factor

            # 2. 计算奖励值
            agent_reward = (
                    REWARD_WEIGHTS["planning"] * normalized_planning
                    + REWARD_WEIGHTS["communication"] * normalized_communication
                    + REWARD_WEIGHTS["contribution"] * contribution_ratio
            )

            # 3. 裁剪到 0-1 区间
            agent_reward = max(0.0, min(1.0, agent_reward))
            self.agent_rewards[agent_id] = agent_reward
            self.logger.debug(f"Agent {agent_id} reward calculation completed: {agent_reward:.4f} (Contribution ratio: {contribution_ratio:.2%})")
        return self.agent_rewards

    def sorted_agent_contribution(self):
        agent_contribution = {
            agent_id: self._calculate_agent_contribution_ratio(agent_id)
            for agent_id in self.evaluator.metrics.get("agent_kpis", {})
        }
        return sorted(agent_contribution.items(), key=lambda x: x[1], reverse=True)

    def generate_individual_feedback(self, iteration_task_data: Dict[str, Any]) -> Dict[str, str]:
        """
        为每个智能体生成个性化强化学习反馈（奖励/惩罚+行为指导）

        Args:
            iteration_task_data (str): 任务完成情况

        Returns:
            Dict[str, str]: 智能体ID到个性化反馈的映射
        """
        if not self.agent_rewards:
            self.logger.warning("If the agent reward is not calculated, the reward value is automatically calculated first")
            self.calculate_agent_rewards()

        latest_planning, latest_communication = self._get_latest_scores()
        total_milestones = self.evaluator.metrics.get("total_milestones", 0)
        prompt_template = self.feedback_prompts["agent_individual_feedback"]["prompt"]

        for agent_id, agent_reward in self.agent_rewards.items():
            # 1. 收集智能体个体数据
            agent_profile = self.agent_profiles.get(agent_id, "未配置角色简介")
            agent_milestones = self.evaluator.metrics.get("agent_kpis", {}).get(agent_id, 0)
            contribution_ratio = self._calculate_agent_contribution_ratio(agent_id)

            # 2. 填充提示词模板
            filled_prompt = prompt_template.format(
                task=self.task,
                agent_id=agent_id,
                agent_profile=agent_profile,
                planning_score=latest_planning,
                communication_score=latest_communication,
                # 上一轮任务的 情况data 来优化反馈以及建议准确性和有效性
                iteration_task_data=iteration_task_data,
                contribution_ratio=contribution_ratio,
                agent_reward=agent_reward,
                agent_milestones=agent_milestones,
                total_milestones=total_milestones
            )

            # 3. 调用LLM生成反馈
            try:
                result = model_prompting(
                    llm_model=self.llm,
                    messages=[{"role": "user", "content": filled_prompt}],
                    return_num=1,
                    max_token_num=1024,
                    temperature=0.1,
                    top_p=None,
                    stream=None,
                )[0]

                assert isinstance(result.content, str)
                self.individual_feedbacks[agent_id] = result.content
                self.logger.debug(f"Agent {agent_id} personalized feedback generation completes")

            except Exception as e:
                self.logger.error(f"generativeAgents: {agent_id} feedbackFailed:{e}")
                self.individual_feedbacks[agent_id] = f"feedbackGenerationFailed:{str(e)}"

        return self.individual_feedbacks

    def generate_team_feedback(self, iteration_task_data: Dict[str, Any]) -> str:
        """
        生成团队整体反馈与关系图优化建议

        Args:
            iteration_task_data (str): 任务情况

        Returns:
            str: 团队整体反馈内容
        """
        latest_planning, latest_communication = self._get_latest_scores()
        total_milestones = self.evaluator.metrics.get("total_milestones", 0)

        # 1. 生成智能体贡献排名
        sorted_contribution = self.sorted_agent_contribution()
        contribution_ranking = "\n".join([
            f"{i + 1}. {agent_id}: {ratio:.2%}"
            for i, (agent_id, ratio) in enumerate(sorted_contribution)
        ]) or "无有效贡献数据"

        # 2. 填充提示词模板
        prompt_template = self.feedback_prompts["team_collective_feedback"]["prompt"]
        filled_prompt = prompt_template.format(
            task=self.task,
            planning_score=latest_planning,
            communication_score=latest_communication,
            # 上一轮任务的 情况data 来优化反馈以及建议准确性和有效性
            iteration_task_data=iteration_task_data,
            total_milestones=total_milestones,
            agent_contribution_ranking=contribution_ranking,
        )

        # 3. 调用LLM生成团队反馈
        try:
            result = model_prompting(
                llm_model=self.llm,
                messages=[{"role": "user", "content": filled_prompt}],
                return_num=1,
                max_token_num=1024,
                temperature=0.1,
                top_p=None,
                stream=None,
            )[0]

            assert isinstance(result.content, str)
            self.team_feedback = result.content
            self.logger.debug("The overall feedback of the team and the optimization suggestions of the relationship diagram are generated")

        except Exception as e:
            self.logger.error(f"generateTeamFeedbackFailed：{e}")
            self.team_feedback = f"teamFeedbackGenerationFailed：{str(e)}"

        return self.team_feedback

    def generate_reward_explanation(self, agent_id: str) -> str:
        """
        为单个智能体解释奖励计算逻辑，建立行为-奖励关联

        Args:
            agent_id (str): 智能体ID

        Returns:
            str: 奖励解释内容
        """
        if agent_id not in self.agent_rewards:
            self.logger.warning(f"Agent {agent_id} If there is no reward data, the reward value will be automatically calculated first")
            self.calculate_agent_rewards()

        if agent_id not in self.agent_rewards:
            error_msg = f"Agent {agent_id} No or valid data"
            self.logger.error(error_msg)
            return error_msg

        # 1. 收集智能体数据
        latest_planning, latest_communication = self._get_latest_scores()
        agent_reward = self.agent_rewards[agent_id]
        contribution_ratio = self._calculate_agent_contribution_ratio(agent_id)

        # 2. 填充提示词模板
        prompt_template = self.feedback_prompts["reward_explanation"]["prompt"]
        filled_prompt = prompt_template.format(
            planning_score=latest_planning,
            communication_score=latest_communication,
            contribution_ratio=contribution_ratio,
            agent_reward=agent_reward
        )

        # 3. 调用LLM生成解释
        try:
            result = model_prompting(
                llm_model=self.llm,
                messages=[{"role": "user", "content": filled_prompt}],
                return_num=1,
                max_token_num=512,
                temperature=0.1,
                top_p=None,
                stream=None,
            )[0]

            assert isinstance(result.content, str)
            self.logger.debug(f"agent {agent_id} The reward interpretation is generated")
            return result.content

        except Exception as e:
            self.logger.error(f"Generative agents {agent_id} Reward explanation failed：{e}")
            return f"Reward explanation generation failed：{str(e)}"

    def get_full_feedback_package(self, iteration_task_data: Dict[str, Any]) -> Dict[str, Any] | None:
        """
        生成完整的反馈包（个体反馈+团队反馈+奖励解释），形成闭环优化数据

        Args:
            iteration_task_data (str): 任务完成情况

        Returns:
            Dict[str, Any]: 完整反馈包
        """
        if not self.is_feedback:
            self.logger.info("The feedback function is not enabled and does not generate feedback information")
            return None
        # 1. 生成所有反馈内容
        self.generate_individual_feedback(iteration_task_data)
        self.generate_team_feedback(iteration_task_data)
        latest_planning_score, latest_communication_score = self._get_latest_scores()
        # 2. 构建完整反馈包
        full_feedback = {
            "team_feedback": self.team_feedback,
            "individual_feedbacks": self.individual_feedbacks,
            "agent_rewards": self.agent_rewards,
            "reward_weights": REWARD_WEIGHTS,
            "metrics_summary": {
                "latest_planning_score": latest_planning_score,
                "latest_communication_score": latest_communication_score,
                "total_milestones": self.evaluator.metrics.get("total_milestones", 0),
                "agent_kpis": self.evaluator.metrics.get("agent_kpis"),
                "sorted_agent_contribution": self.sorted_agent_contribution()
            },
            "agent_reward_explanations": {
                agent_id: self.generate_reward_explanation(agent_id) for agent_id in self.agent_rewards
            }
        }

        self.logger.info(f"The full feedback package is built and can be used for the next round of agent policy optimization: {full_feedback}")
        return full_feedback