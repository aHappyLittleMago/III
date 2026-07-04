# III — 数字智能体演示

在二维沙箱环境中探索**无监督 / 弱监督数字智能体**的原型项目，附带浏览器实时可视化界面。

## 架构

```
┌─────────────────────────────────────────────────────────┐
│  浏览器（React + Vite）                                  │
│  网格视图 · 学习曲线 · 人工指引控件                        │
└────────────────────────┬────────────────────────────────┘
                         │ WebSocket /ws
┌────────────────────────▼────────────────────────────────┐
│  FastAPI 服务端（server/）                               │
│  仿真循环 · 智能体切换 · 指引注入                         │
└────────────┬───────────────────────────┬────────────────┘
             │                           │
┌────────────▼──────────┐   ┌────────────▼────────────────┐
│  沙箱（sandbox/）      │   │  智能体（agents/）           │
│  网格 · 墙体 ·        │   │  AgentCore 统一接口          │
│  奖励 · 反馈          │◄──│  Q-learning · 规则基线       │
└───────────────────────┘   └─────────────────────────────┘
```

### 核心组件

1. **沙箱** — 带墙体与奖励的二维网格。智能体可上下左右移动，碰撞、步进与收集奖励时返回反馈。

2. **可插拔智能体核心** — `AgentCore` 抽象接口，配合 `env_to_agent_obs()` 适配器使用。通过注册表（`q_learning`、`rule_based`）切换算法。继承 `AgentCore` 并在 `agents/registry.py` 中注册即可添加新智能体。

3. **可视化** — React 前端通过 WebSocket 实时展示网格、学习统计、回合奖励曲线及人工方向指引。

## 文档

- [核心架构与学习原理](docs/核心架构与学习原理.md) — 系统构成、仿真循环与学习机制（含 Mermaid 图解）

## 分支

- `main` — 稳定发布
- `dev` — 日常开发迭代（默认在此分支开发新功能）

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+

### 1. 启动后端

```bash
cd D:\Projects\III
pip install -r requirements.txt
python run.py
```

服务运行于 **http://localhost:8000**

### 2. 启动前端（开发模式）

另开终端：

```bash
cd D:\Projects\III\frontend
npm install
npm run dev
```

打开 **http://localhost:5173** — Vite 会将 WebSocket/API 代理到后端。

### 3. 生产模式（单服务）

```bash
cd frontend && npm install && npm run build
cd .. && python run.py
```

打开 **http://localhost:8000** — 同时提供构建后的前端与 API。

## 使用说明

- **开始** — 启动自主仿真循环
- **单步** — 暂停时执行一步
- **重置** — 开始新回合
- **速度** — 调整 tick 间隔
- **智能体核心** — 在 `q_learning` 与 `rule_based` 之间切换
- **人工指引** — 方向键发送可选的弱监督提示

## 添加新智能体

```python
# agents/my_agent.py
from agents.base import AgentCore, AgentObservation, AgentFeedback
from sandbox.environment import Action

class MyAgent(AgentCore):
    name = "my_agent"

    def reset(self, observation): ...
    def select_action(self, observation) -> Action: ...
    def learn(self, feedback, observation): ...
    def get_visual_state(self) -> dict: ...

# agents/registry.py
from agents.my_agent import MyAgent
_REGISTRY[MyAgent.name] = MyAgent
```

## 演示场景

默认地图包含墙体障碍与两颗奖励星。Q-learning 智能体通过 ε-贪心策略探索，从碰撞惩罚（-1）与奖励加成（+10）中学习，逐步改善导航能力。人工指引会偏置动作选择，实现弱监督。
