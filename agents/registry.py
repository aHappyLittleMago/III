"""智能体注册表，用于可插拔算法的切换。"""

from __future__ import annotations

from typing import Callable, Type

from agents.base import AgentCore
from agents.q_learning import QLearningAgent
from agents.rule_based import RuleBasedAgent

_REGISTRY: dict[str, Callable[[], AgentCore]] = {
    QLearningAgent.name: QLearningAgent,
    RuleBasedAgent.name: RuleBasedAgent,
}


def register_agent(name: str, factory: Type[AgentCore]) -> None:
    _REGISTRY[name] = factory


def get_agent(name: str) -> AgentCore:
    if name not in _REGISTRY:
        raise ValueError(f"未知智能体：{name}。可用：{list(_REGISTRY.keys())}")
    return _REGISTRY[name]()


def list_agents() -> list[str]:
    return list(_REGISTRY.keys())
