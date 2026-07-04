"""简单规则智能体，用于对比或兜底。"""

from __future__ import annotations

from typing import Any

from agents.base import AgentCore, AgentFeedback, AgentObservation
from sandbox.environment import Action


class RuleBasedAgent(AgentCore):
    name = "rule_based"

    def __init__(self) -> None:
        self.collision_memory: set[tuple[int, int, Action]] = set()
        self.last_action: Action | None = None
        self.steps: int = 0

    def reset(self, observation: AgentObservation) -> None:
        self.steps = 0

    def _is_blocked(self, pos: tuple[int, int], action: Action, obs: AgentObservation) -> bool:
        dr, dc = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}[action.value]
        nr, nc = pos[0] + dr, pos[1] + dc
        h, w = obs.grid_size
        if not (0 <= nr < h and 0 <= nc < w):
            return True
        if (nr, nc) in obs.walls:
            return True
        if (pos[0], pos[1], action) in self.collision_memory:
            return True
        return False

    def _toward_nearest_reward(self, pos: tuple[int, int], obs: AgentObservation) -> Action | None:
        if not obs.rewards:
            return None
        target = min(obs.rewards, key=lambda r: abs(r[0] - pos[0]) + abs(r[1] - pos[1]))
        tr, tc = target
        pr, pc = pos
        candidates: list[Action] = []
        if tr < pr:
            candidates.append(Action.UP)
        elif tr > pr:
            candidates.append(Action.DOWN)
        if tc < pc:
            candidates.append(Action.LEFT)
        elif tc > pc:
            candidates.append(Action.RIGHT)
        for action in candidates:
            if not self._is_blocked(pos, action, obs):
                return action
        return None

    def select_action(self, observation: AgentObservation) -> Action:
        self.steps += 1
        pos = observation.position

        if observation.human_hint and not self._is_blocked(pos, observation.human_hint, observation):
            self.last_action = observation.human_hint
            return observation.human_hint

        preferred = self._toward_nearest_reward(pos, observation)
        if preferred:
            self.last_action = preferred
            return preferred

        for action in Action:
            if not self._is_blocked(pos, action, observation):
                self.last_action = action
                return action

        self.last_action = Action.UP
        return Action.UP

    def learn(self, feedback: AgentFeedback, observation: AgentObservation) -> None:
        if feedback.event == "collision" and self.last_action:
            self.collision_memory.add(
                (feedback.prev_position[0], feedback.prev_position[1], self.last_action)
            )

    def get_visual_state(self) -> dict[str, Any]:
        return {
            "type": self.name,
            "memory_entries": len(self.collision_memory),
            "steps": self.steps,
            "last_action": self.last_action.value if self.last_action else None,
            "thinking": "贪心朝最近奖励移动，并避开已知碰撞",
        }
