import { useCallback, useEffect, useRef, useState } from 'react'
import type { GameState, WsCommand } from './types'

const WS_URL =
  import.meta.env.DEV
    ? `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws`
    : `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws`

export function useSimulation() {
  const [state, setState] = useState<GameState | null>(null)
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  const send = useCallback((cmd: WsCommand) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(cmd))
    }
  }, [])

  useEffect(() => {
    const connect = () => {
      const ws = new WebSocket(WS_URL)
      wsRef.current = ws

      ws.onopen = () => setConnected(true)
      ws.onclose = () => {
        setConnected(false)
        setTimeout(connect, 1500)
      }
      ws.onmessage = (ev) => {
        setState(JSON.parse(ev.data) as GameState)
      }
    }
    connect()
    return () => wsRef.current?.close()
  }, [])

  return { state, connected, send }
}
