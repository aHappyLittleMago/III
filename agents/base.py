"""统一智能体接口 — 任意算法均可在此接入。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from sandbox.environment import Action


@dataclass
class AgentObservation:
    """转换后的环境信息，供智能体使用。"""

    position: tuple[int, int]
    grid_size: tuple[int, int]
    walls: set[tuple[int, int]]
    rewards: set[tuple[int, int]]
    human_hint: Optional[Action]
    step: int
    episode: int


@dataclass
class AgentFeedback:
    """执行动作后来自环境的反馈。"""

    event: str
    reward: float
    message: str
    prev_position: tuple[int, int]
    new_position: tuple[int, int]
    action: Action


class AgentCore(ABC):
    """可替换数字智能体的抽象基类。"""

    name: str = "base"

    @abstractmethod
    def reset(self, observation: AgentObservation) -> None:
        """回合开始时调用。"""

    @abstractmethod
    def select_action(self, observation: AgentObservation) -> Action:
        """根据当前观测选择下一步动作。"""

    @abstractmethod
    def learn(self, feedback: AgentFeedback, observation: AgentObservation) -> None:
        """根据环境反馈更新内部模型。"""

    @abstractmethod
    def get_visual_state(self) -> dict[str, Any]:
        """返回智能体内部状态，供前端可视化。"""

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "AgentCore":
        return cls(**{k: v for k, v in config.items() if k in cls.__init__.__annotations__})


def env_to_agent_obs(env_obs) -> AgentObservation:
    """适配器：沙箱观测 → 智能体观测。"""
    return AgentObservation(
        position=env_obs.agent_pos,
        grid_size=env_obs.grid_size,
        walls=set(env_obs.walls),
        rewards=set(env_obs.rewards),
        human_hint=env_obs.human_hint,
        step=env_obs.step,
        episode=env_obs.episode,
    )
