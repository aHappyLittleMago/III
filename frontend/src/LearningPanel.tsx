import type { AgentVisualState } from './types'

interface Props {
  agent: AgentVisualState
}

const ACTION_LABELS: Record<string, string> = {
  up: '上',
  down: '下',
  left: '左',
  right: '右',
}

export function LearningPanel({ agent }: Props) {
  const rewards = agent.episode_rewards ?? []

  return (
    <div className="panel learning-panel">
      <h3>智能体思维</h3>
      <div className="thinking-box">{agent.thinking ?? '…'}</div>

      {agent.type === 'q_learning' && (
        <>
          <div className="stat-row">
            <span>探索率 ε</span>
            <span className="mono">{agent.epsilon?.toFixed(3)}</span>
          </div>
          <div className="stat-row">
            <span>Q 表条目</span>
            <span className="mono">{agent.q_entries}</span>
          </div>
          <div className="stat-row">
            <span>已学习碰撞</span>
            <span className="mono">{agent.collisions}</span>
          </div>
          <div className="stat-row">
            <span>已收集奖励</span>
            <span className="mono">{agent.rewards_collected}</span>
          </div>
          <div className="stat-row">
            <span>本回合奖励</span>
            <span className="mono">{agent.current_episode_reward?.toFixed(2)}</span>
          </div>

          {rewards.length > 0 && (
            <div className="chart-wrap">
              <div className="chart-label">近期回合奖励</div>
              <div className="bar-chart">
                {rewards.map((v, i) => {
                  const h = Math.max(4, Math.min(100, ((v + 5) / 25) * 100))
                  return (
                    <div
                      key={i}
                      className="bar"
                      style={{ height: `${h}%` }}
                      title={`回合 ${i + 1}：${v}`}
                    />
                  )
                })}
              </div>
            </div>
          )}
        </>
      )}

      {agent.type === 'rule_based' && (
        <>
          <div className="stat-row">
            <span>碰撞记忆</span>
            <span className="mono">{agent.memory_entries}</span>
          </div>
          <div className="stat-row">
            <span>本回合步数</span>
            <span className="mono">{agent.steps}</span>
          </div>
        </>
      )}

      {agent.last_action && (
        <div className="last-action">
          上一步动作：<strong>{ACTION_LABELS[agent.last_action] ?? agent.last_action}</strong>
        </div>
      )}
    </div>
  )
}
