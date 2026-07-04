"""连接沙箱与可插拔智能体的仿真循环。"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from agents.base import AgentCore, AgentFeedback, env_to_agent_obs
from agents.registry import get_agent, list_agents
from sandbox.environment import Action, SandboxEnvironment


@dataclass
class SimulationState:
    running: bool = False
    tick_ms: int = 300
    agent_name: str = "q_learning"
    episode: int = 0
    step: int = 0
    last_feedback: str = ""
    last_reward: float = 0.0


class SimulationEngine:
    def __init__(self) -> None:
        self.env = SandboxEnvironment()
        self.agent: AgentCore = get_agent("q_learning")
        self.state = SimulationState()
        self._listeners: list[Callable[[dict], Any]] = []
        self._task: Optional[asyncio.Task] = None
        self._prev_pos = self.env.agent_pos

    def subscribe(self, callback: Callable[[dict], Any]) -> None:
        self._listeners.append(callback)

    async def _broadcast(self, payload: dict) -> None:
        for cb in self._listeners:
            result = cb(payload)
            if asyncio.iscoroutine(result):
                await result

    def swap_agent(self, name: str) -> None:
        self.state.agent_name = name
        self.agent = get_agent(name)
        obs = self.env.get_observation()
        self.agent.reset(env_to_agent_obs(obs))

    def set_human_hint(self, hint: Optional[str]) -> None:
        if hint is None:
            self.env.set_human_hint(None)
        else:
            self.env.set_human_hint(Action(hint))

    def reset_episode(self) -> None:
        obs = self.env.reset()
        self._prev_pos = obs.agent_pos
        self.agent.reset(env_to_agent_obs(obs))
        self.state.step = obs.step
        self.state.episode = obs.episode

    def get_snapshot(self) -> dict:
        return {
            "grid": self.env.to_grid(),
            "width": self.env.width,
            "height": self.env.height,
            "agent_pos": self.env.agent_pos,
            "human_hint": self.env.human_hint.value if self.env.human_hint else None,
            "simulation": {
                "running": self.state.running,
                "tick_ms": self.state.tick_ms,
                "agent_name": self.state.agent_name,
                "episode": self.state.episode,
                "step": self.state.step,
                "last_feedback": self.state.last_feedback,
                "last_reward": self.state.last_reward,
            },
            "agent": self.agent.get_visual_state(),
            "available_agents": list_agents(),
        }

    async def _tick(self) -> None:
        env_obs = self.env.get_observation()
        agent_obs = env_to_agent_obs(env_obs)
        action = self.agent.select_action(agent_obs)
        prev_pos = self.env.agent_pos

        new_env_obs, feedback = self.env.step(action)
        agent_feedback = AgentFeedback(
            event=feedback.event,
            reward=feedback.reward,
            message=feedback.message,
            prev_position=prev_pos,
            new_position=new_env_obs.agent_pos,
            action=action,
        )
        self.agent.learn(agent_feedback, env_to_agent_obs(new_env_obs))

        self.state.step = new_env_obs.step
        self.state.episode = new_env_obs.episode
        self.state.last_feedback = feedback.message
        self.state.last_reward = feedback.reward
        self._prev_pos = new_env_obs.agent_pos

        if feedback.event == "done":
            await asyncio.sleep(0.5)
            self.reset_episode()

        await self._broadcast(self.get_snapshot())

    async def _run_loop(self) -> None:
        while self.state.running:
            await self._tick()
            await asyncio.sleep(self.state.tick_ms / 1000.0)

    def start(self) -> None:
        if not self.state.running:
            self.state.running = True
            if self.state.episode == 0:
                self.reset_episode()
            self._task = asyncio.create_task(self._run_loop())

    def stop(self) -> None:
        self.state.running = False
        if self._task:
            self._task.cancel()
            self._task = None

    def set_speed(self, tick_ms: int) -> None:
        self.state.tick_ms = max(50, min(2000, tick_ms))
