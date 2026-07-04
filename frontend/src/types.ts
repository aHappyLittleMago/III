export interface SimulationMeta {
  running: boolean
  tick_ms: number
  agent_name: string
  episode: number
  step: number
  last_feedback: string
  last_reward: number
}

export interface AgentVisualState {
  type: string
  epsilon?: number
  q_entries?: number
  total_reward?: number
  current_episode_reward?: number
  episode_rewards?: number[]
  collisions?: number
  rewards_collected?: number
  last_action?: string | null
  thinking?: string
  memory_entries?: number
  steps?: number
}

export interface GameState {
  grid: string[][]
  width: number
  height: number
  agent_pos: [number, number]
  human_hint: string | null
  simulation: SimulationMeta
  agent: AgentVisualState
  available_agents: string[]
}

export type Direction = 'up' | 'down' | 'left' | 'right'

export type WsCommand =
  | { cmd: 'start' }
  | { cmd: 'stop' }
  | { cmd: 'reset' }
  | { cmd: 'hint'; direction: Direction }
  | { cmd: 'clear_hint' }
  | { cmd: 'swap_agent'; name: string }
  | { cmd: 'speed'; tick_ms: number }
  | { cmd: 'step' }
