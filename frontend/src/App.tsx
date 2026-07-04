import { Grid } from './Grid'
import { LearningPanel } from './LearningPanel'
import { useSimulation } from './useSimulation'
import type { Direction } from './types'

const AGENT_LABELS: Record<string, string> = {
  q_learning: 'Q-learning（强化学习）',
  rule_based: '规则基线',
}

export default function App() {
  const { state, connected, send } = useSimulation()

  if (!state) {
    return (
      <div className="app loading">
        <div className="loader" />
        <p>{connected ? '正在加载仿真…' : '正在连接服务器…'}</p>
      </div>
    )
  }

  const sim = state.simulation

  const hint = (dir: Direction) => send({ cmd: 'hint', direction: dir })

  return (
    <div className="app">
      <header>
        <div>
          <h1>III · 数字智能体演示</h1>
          <p className="subtitle">基于环境反馈的无监督导航，支持可选的人工弱监督指引</p>
        </div>
        <div className={`status ${connected ? 'online' : 'offline'}`}>
          {connected ? '● 在线' : '○ 离线'}
        </div>
      </header>

      <main>
        <section className="sandbox-section">
          <Grid state={state} />

          <div className="feedback-strip">
            <span className={sim.last_reward >= 0 ? 'pos' : 'neg'}>
              {sim.last_reward >= 0 ? '+' : ''}{sim.last_reward.toFixed(2)}
            </span>
            <span>{sim.last_feedback}</span>
            <span className="meta">回合 {sim.episode} · 步数 {sim.step}</span>
          </div>
        </section>

        <aside className="controls">
          <div className="panel">
            <h3>控制</h3>
            <div className="btn-row">
              <button className="primary" onClick={() => send({ cmd: sim.running ? 'stop' : 'start' })}>
                {sim.running ? '暂停' : '开始'}
              </button>
              <button onClick={() => send({ cmd: 'step' })} disabled={sim.running}>
                单步
              </button>
              <button onClick={() => send({ cmd: 'reset' })}>重置</button>
            </div>

            <label className="speed-label">
              速度
              <input
                type="range"
                min={50}
                max={800}
                step={50}
                value={sim.tick_ms}
                onChange={(e) => send({ cmd: 'speed', tick_ms: Number(e.target.value) })}
              />
              <span className="mono">{sim.tick_ms}ms</span>
            </label>

            <h4>智能体核心</h4>
            <select
              value={sim.agent_name}
              onChange={(e) => send({ cmd: 'swap_agent', name: e.target.value })}
            >
              {state.available_agents.map((a) => (
                <option key={a} value={a}>{AGENT_LABELS[a] ?? a}</option>
              ))}
            </select>
          </div>

          <div className="panel">
            <h3>人工指引</h3>
            <p className="hint-desc">可选弱监督 — 智能体可能跟随你给出的方向</p>
            <div className="dpad">
              <button onClick={() => hint('up')} title="向上指引">↑</button>
              <div className="dpad-mid">
                <button onClick={() => hint('left')}>←</button>
                <button className="clear" onClick={() => send({ cmd: 'clear_hint' })}>✕</button>
                <button onClick={() => hint('right')}>→</button>
              </div>
              <button onClick={() => hint('down')}>↓</button>
            </div>
          </div>

          <LearningPanel agent={state.agent} />
        </aside>
      </main>

      <footer>
        <span>🟫 墙体</span>
        <span>★ 奖励</span>
        <span>🤖 智能体</span>
      </footer>
    </div>
  )
}
