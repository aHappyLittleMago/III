import type { GameState } from './types'

const CELL_COLORS: Record<string, string> = {
  empty: '#1a1f2e',
  wall: '#3d4f6f',
  reward: '#f0c040',
  agent: '#4ade80',
}

interface GridProps {
  state: GameState
}

export function Grid({ state }: GridProps) {
  const { grid, agent_pos, human_hint } = state
  const cellSize = Math.min(42, Math.floor(520 / Math.max(grid[0]?.length ?? 12, grid.length)))

  return (
    <div className="grid-wrap">
      <div
        className="grid"
        style={{
          gridTemplateColumns: `repeat(${grid[0]?.length ?? 1}, ${cellSize}px)`,
          gridTemplateRows: `repeat(${grid.length}, ${cellSize}px)`,
        }}
      >
        {grid.map((row, r) =>
          row.map((cell, c) => {
            const isAgent = r === agent_pos[0] && c === agent_pos[1]
            const key = `${r}-${c}`
            return (
              <div
                key={key}
                className={`cell ${cell} ${isAgent ? 'agent-cell' : ''}`}
                style={{ background: isAgent ? CELL_COLORS.agent : CELL_COLORS[cell] ?? CELL_COLORS.empty }}
              >
                {cell === 'reward' && !isAgent && '★'}
                {isAgent && '🤖'}
                {cell === 'wall' && ''}
              </div>
            )
          }),
        )}
      </div>
      {human_hint && (
        <div className="hint-badge">人工指引：{human_hint === 'up' ? '上' : human_hint === 'down' ? '下' : human_hint === 'left' ? '左' : '右'}</div>
      )}
    </div>
  )
}
