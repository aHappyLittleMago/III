"""Q-learning 智能体 — 仅通过反馈学习导航。"""

from __future__ import annotations

import random
from typing import Any

from agents.base import AgentCore, AgentFeedback, AgentObservation
from sandbox.environment import Action


class QLearningAgent(AgentCore):
    name = "q_learning"

    def __init__(
        self,
        alpha: float = 0.3,
        gamma: float = 0.95,
        epsilon: float = 0.25,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.05,
    ) -> None:
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.q_table: dict[tuple[int, int], dict[Action, float]] = {}
        self.last_state: tuple[int, int] | None = None
        self.last_action: Action | None = None
        self.total_reward: float = 0.0
        self.episode_rewards: list[float] = []
        self.collision_count: int = 0
        self.reward_count: int = 0
        self._current_episode_reward: float = 0.0

    def _get_q(self, state: tuple[int, int], action: Action) -> float:
        return self.q_table.setdefault(state, {}).get(action, 0.0)

    def _set_q(self, state: tuple[int, int], action: Action, value: float) -> None:
        self.q_table.setdefault(state, {})[action] = value

    def reset(self, observation: AgentObservation) -> None:
        if observation.episode > 1:
            self.episode_rewards.append(self._current_episode_reward)
        self._current_episode_reward = 0.0
        self.last_state = observation.position
        self.last_action = None
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def _best_action(self, state: tuple[int, int]) -> Action:
        actions = list(Action)
        q_vals = [self._get_q(state, a) for a in actions]
        max_q = max(q_vals)
        best = [a for a, q in zip(actions, q_vals) if q == max_q]
        return random.choice(best)

    def select_action(self, observation: AgentObservation) -> Action:
        state = observation.position
        hint = observation.human_hint

        # 弱监督：以一定概率采纳人工指引
        if hint is not None and random.random() < 0.6:
            self.last_state = state
            self.last_action = hint
            return hint

        if random.random() < self.epsilon:
            action = random.choice(list(Action))
        else:
            action = self._best_action(state)

        self.last_state = state
        self.last_action = action
        return action

    def learn(self, feedback: AgentFeedback, observation: AgentObservation) -> None:
        if self.last_state is None or self.last_action is None:
            return

        self.total_reward += feedback.reward
        self._current_episode_reward += feedback.reward

        if feedback.event == "collision":
            self.collision_count += 1
        elif feedback.event in ("reward", "done") and feedback.reward > 0:
            self.reward_count += 1

        state = self.last_state
        action = self.last_action
        reward = feedback.reward
        next_state = observation.position

        old_q = self._get_q(state, action)
        next_max = max(self._get_q(next_state, a) for a in Action)
        new_q = old_q + self.alpha * (reward + self.gamma * next_max - old_q)
        self._set_q(state, action, new_q)

        self.last_state = next_state

    def get_visual_state(self) -> dict[str, Any]:
        recent = self.episode_rewards[-20:] if self.episode_rewards else []
        return {
            "type": self.name,
            "epsilon": round(self.epsilon, 4),
            "q_entries": len(self.q_table),
            "total_reward": round(self.total_reward, 2),
            "current_episode_reward": round(self._current_episode_reward, 2),
            "episode_rewards": [round(r, 2) for r in recent],
            "collisions": self.collision_count,
            "rewards_collected": self.reward_count,
            "last_action": self.last_action.value if self.last_action else None,
            "thinking": self._format_thinking(),
        }

    def _format_thinking(self) -> str:
        if self.last_state is None:
            return "正在观察环境…"
        qs = self.q_table.get(self.last_state, {})
        if not qs:
            return f"从 {self.last_state} 探索中（尚无 Q 值）"
        best = max(qs, key=qs.get)
        return f"位于 {self.last_state}：最优→{best.value}（Q={qs[best]:.2f}，ε={self.epsilon:.2f}）"
