import { useEffect, useState } from 'react'

export type MarketStatus = {
  market_status: string
  up_count: number
  down_count: number
  limit_up: number
  limit_down: number
  broken_limit_rate: number
  risk_level: 'low' | 'medium' | 'high'
  allow_buy: boolean
  prompt: string
}

export type StockSignal = {
  stock: string
  name: string
  score: number
  factors: string[]
  explanation: string
}

export type DashboardPayload = {
  market: MarketStatus
  selector: StockSignal[]
  ai: {
    market_status: string
    risk_level: string
    allow_buy: boolean
    message: string
  }
}

export type DailyTradingReport = {
  title: string
  market: MarketStatus
  strategy: {
    action_level: 'buy_allowed' | 'no_buy' | 'half_position' | 'clear_all'
    action_title: string
    position_hint: string
    buy_window: string
    hard_rules: string[]
    risk_warnings: string[]
    execution_checklist: string[]
  }
  news: {
    summary: string
    risk_level: string
    official_sources: string[]
    items: Array<{
      title: string
      source: string
      published_at: string
      risk_hint: string
      url?: string | null
    }>
  }
  selector: StockSignal[]
  stock_trade_notes: Array<Record<string, unknown>>
  holdings: {
    items: Array<{
      stock: string
      name: string
      pnl_pct: number
      action: string
      reason: string
      stop_loss: string
    }>
  }
  html: string
}

export const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'
const wsBase = process.env.NEXT_PUBLIC_WS_BASE || 'ws://localhost:8000'

export function useRealtimeDashboard() {
  const [data, setData] = useState<DashboardPayload | null>(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    fetch(`${apiBase}/api/dashboard`)
      .then((response) => response.json())
      .then(setData)
      .catch(() => setConnected(false))

    const socket = new WebSocket(`${wsBase}/ws/realtime`)
    socket.onopen = () => setConnected(true)
    socket.onclose = () => setConnected(false)
    socket.onerror = () => setConnected(false)
    socket.onmessage = (event) => setData(JSON.parse(event.data))

    return () => socket.close()
  }, [])

  return { data, connected }
}
