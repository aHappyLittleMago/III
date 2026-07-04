"""二维网格沙箱环境，包含墙体、奖励与反馈。"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Action(str, Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class CellType(str, Enum):
    EMPTY = "empty"
    WALL = "wall"
    REWARD = "reward"
    AGENT = "agent"


@dataclass
class Feedback:
    event: str  # "step", "collision", "reward", "done"
    reward: float
    message: str


@dataclass
class Observation:
    grid_size: tuple[int, int]
    agent_pos: tuple[int, int]
    walls: list[tuple[int, int]]
    rewards: list[tuple[int, int]]
    human_hint: Optional[Action] = None
    step: int = 0
    episode: int = 0


@dataclass
class SandboxEnvironment:
    width: int = 12
    height: int = 10
    agent_pos: tuple[int, int] = field(default=(1, 1))
    walls: set[tuple[int, int]] = field(default_factory=set)
    rewards: set[tuple[int, int]] = field(default_factory=set)
    human_hint: Optional[Action] = None
    step_count: int = 0
    episode_count: int = 0
    max_steps: int = 200

    def __post_init__(self) -> None:
        if not self.walls and not self.rewards:
            self._build_default_map()

    def _build_default_map(self) -> None:
        """创建带墙体与奖励的演示地图。"""
        self.walls = {
            (3, 2), (3, 3), (3, 4), (3, 5), (3, 6),
            (6, 4), (6, 5), (6, 6), (6, 7), (6, 8),
            (8, 1), (8, 2), (8, 3),
            (1, 7), (2, 7), (4, 7), (5, 7),
        }
        self.rewards = {(9, 8), (5, 1)}
        self.agent_pos = (1, 1)

    def reset(self, random_start: bool = False) -> Observation:
        self.step_count = 0
        self.episode_count += 1
        self.human_hint = None
        if random_start:
            self.agent_pos = self._random_empty_cell()
        else:
            self.agent_pos = (1, 1)
        return self.get_observation()

    def _random_empty_cell(self) -> tuple[int, int]:
        candidates = [
            (r, c)
            for r in range(self.height)
            for c in range(self.width)
            if (r, c) not in self.walls and (r, c) not in self.rewards
        ]
        return random.choice(candidates) if candidates else (1, 1)

    def set_human_hint(self, hint: Optional[Action]) -> None:
        self.human_hint = hint

    def get_observation(self) -> Observation:
        return Observation(
            grid_size=(self.height, self.width),
            agent_pos=self.agent_pos,
            walls=sorted(self.walls),
            rewards=sorted(self.rewards),
            human_hint=self.human_hint,
            step=self.step_count,
            episode=self.episode_count,
        )

    def _delta(self, action: Action) -> tuple[int, int]:
        return {
            Action.UP: (-1, 0),
            Action.DOWN: (1, 0),
            Action.LEFT: (0, -1),
            Action.RIGHT: (0, 1),
        }[action]

    def step(self, action: Action) -> tuple[Observation, Feedback]:
        self.step_count += 1
        dr, dc = self._delta(action)
        nr, nc = self.agent_pos[0] + dr, self.agent_pos[1] + dc

        if not (0 <= nr < self.height and 0 <= nc < self.width):
            return self.get_observation(), Feedback(
                event="collision",
                reward=-1.0,
                message="撞到边界墙",
            )

        if (nr, nc) in self.walls:
            return self.get_observation(), Feedback(
                event="collision",
                reward=-1.0,
                message="撞到障碍物",
            )

        self.agent_pos = (nr, nc)

        if (nr, nc) in self.rewards:
            self.rewards.discard((nr, nc))
            done = len(self.rewards) == 0
            return self.get_observation(), Feedback(
                event="done" if done else "reward",
                reward=10.0,
                message="获得奖励！" if not done else "已收集全部奖励！",
            )

        if self.step_count >= self.max_steps:
            return self.get_observation(), Feedback(
                event="done",
                reward=-0.5,
                message="达到最大步数",
            )

        return self.get_observation(), Feedback(
            event="step",
            reward=-0.04,
            message="已移动",
        )

    def to_grid(self) -> list[list[str]]:
        """返回用于可视化的网格。"""
        grid = [[CellType.EMPTY.value for _ in range(self.width)] for _ in range(self.height)]
        for r, c in self.walls:
            grid[r][c] = CellType.WALL.value
        for r, c in self.rewards:
            grid[r][c] = CellType.REWARD.value
        ar, ac = self.agent_pos
        grid[ar][ac] = CellType.AGENT.value
        return grid
