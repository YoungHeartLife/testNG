import { useEffect, useState } from 'react'
import { StatCard } from '../components/StatCard'
import { DailyTradingReport, useRealtimeDashboard, apiBase } from '../websocket/useRealtime'

const actionTone: Record<string, string> = {
  buy_allowed: 'from-emerald-500 to-sky-500',
  no_buy: 'from-amber-500 to-orange-500',
  half_position: 'from-orange-500 to-red-500',
  clear_all: 'from-red-600 to-rose-700',
}

export default function Home() {
  const { data, connected } = useRealtimeDashboard()
  const [report, setReport] = useState<DailyTradingReport | null>(null)
  const [pushState, setPushState] = useState<string>('')
  const market = data?.market

  useEffect(() => {
    fetch(`${apiBase}/api/report/today`)
      .then((response) => response.json())
      .then(setReport)
      .catch(() => setReport(null))
  }, [])

  async function pushReport() {
    setPushState('正在推送...')
    try {
      const response = await fetch(`${apiBase}/api/report/push`, { method: 'POST' })
      const payload = await response.json()
      setPushState(payload.pushplus?.msg || payload.pushplus?.message || '报告已提交 PushPlus')
    } catch {
      setPushState('推送失败：请检查后端网络与 PUSHPLUS_TOKEN')
    }
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,#0ea5e933,transparent_38%),linear-gradient(135deg,#020617,#0f172a_45%,#082f49)] px-6 py-8 md:px-10">
      <section className="mx-auto max-w-7xl">
        <div className="mb-8 flex flex-col justify-between gap-4 md:flex-row md:items-end">
          <div>
            <p className="text-sm font-semibold text-sky-300">环境 &gt; 个股 &gt; 情绪 &gt; 技术</p>
            <h1 className="mt-2 text-4xl font-black tracking-tight md:text-5xl">AI 交易系统执行台</h1>
            <p className="mt-3 max-w-3xl text-slate-300">集成大盘涨跌家数硬风控、Tushare/演示数据选股、消息面风险、持仓交易提示与 PushPlus 微信报告。</p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <div className={`rounded-full px-4 py-2 text-sm ${connected ? 'bg-emerald-500/20 text-emerald-200' : 'bg-amber-500/20 text-amber-200'}`}>
              {connected ? 'WebSocket 已连接' : '使用 HTTP 快照 / 等待连接'}
            </div>
            <button onClick={pushReport} className="rounded-full bg-white px-5 py-2 text-sm font-bold text-slate-950 shadow-lg shadow-sky-950/30 hover:bg-sky-100">
              推送微信报告
            </button>
          </div>
        </div>
        {pushState ? <div className="mb-5 rounded-2xl border border-sky-300/30 bg-sky-500/10 p-4 text-sky-100">{pushState}</div> : null}

        {!data || !market ? (
          <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-slate-300">正在加载本地交易辅助数据...</div>
        ) : (
          <div className="grid gap-6">
            {report ? (
              <section className={`overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-r ${actionTone[report.strategy.action_level] || 'from-sky-500 to-cyan-500'} p-[1px] shadow-2xl`}>
                <div className="rounded-3xl bg-slate-950/85 p-6 backdrop-blur">
                  <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
                    <div>
                      <p className="text-sm font-bold uppercase tracking-[0.3em] text-white/60">今日操作提示</p>
                      <h2 className="mt-2 text-3xl font-black">{report.strategy.action_title}</h2>
                      <p className="mt-3 text-slate-200">{report.strategy.position_hint}</p>
                    </div>
                    <div className="rounded-3xl bg-white/10 p-5 text-right">
                      <p className="text-sm text-slate-300">买入窗口</p>
                      <p className="mt-1 text-xl font-bold">{report.strategy.buy_window}</p>
                    </div>
                  </div>
                  <div className="mt-5 grid gap-3 md:grid-cols-3">
                    {report.strategy.risk_warnings.slice(0, 3).map((warning) => (
                      <div key={warning} className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-amber-100">{warning}</div>
                    ))}
                  </div>
                </div>
              </section>
            ) : null}

            <section className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur">
              <div className="mb-5 flex items-center justify-between">
                <h2 className="text-2xl font-bold">市场环境</h2>
                <span className="rounded-full bg-sky-500/20 px-3 py-1 text-sky-200">{market.market_status}</span>
              </div>
              <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
                <StatCard label="上涨家数" value={market.up_count} tone="green" />
                <StatCard label="下跌家数" value={market.down_count} tone="red" />
                <StatCard label="涨停数量" value={market.limit_up} tone="green" />
                <StatCard label="跌停数量" value={market.limit_down} tone="red" />
                <StatCard label="炸板率" value={`${(market.broken_limit_rate * 100).toFixed(1)}%`} tone="yellow" />
                <StatCard label="允许开仓" value={market.allow_buy ? '是' : '否'} tone={market.allow_buy ? 'green' : 'red'} />
              </div>
            </section>

            <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
              <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur">
                <h2 className="mb-5 text-2xl font-bold">重点股票池</h2>
                <div className="space-y-4">
                  {data.selector.map((signal) => (
                    <article key={signal.stock} className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <h3 className="text-xl font-bold">{signal.name} <span className="text-slate-400">{signal.stock}</span></h3>
                          <p className="mt-2 text-sm text-slate-300">{signal.explanation}</p>
                        </div>
                        <div className="rounded-2xl bg-emerald-500/20 px-4 py-2 text-2xl font-black text-emerald-200">{signal.score}</div>
                      </div>
                      <div className="mt-4 flex flex-wrap gap-2">
                        {signal.factors.map((factor) => (
                          <span key={factor} className="rounded-full bg-sky-500/20 px-3 py-1 text-sm text-sky-100">{factor}</span>
                        ))}
                      </div>
                    </article>
                  ))}
                </div>
              </div>

              <aside className="space-y-6">
                <section className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur">
                  <h2 className="mb-5 text-2xl font-bold">AI 实时提示</h2>
                  <div className="whitespace-pre-line rounded-2xl bg-slate-950/70 p-5 leading-8 text-slate-100">{data.ai.message}</div>
                  <div className="mt-5 rounded-2xl border border-amber-400/30 bg-amber-500/10 p-5 text-amber-100">
                    风控优先级：4000 家下跌清仓 / 3000 家下跌砍半 / 3000 家上涨才买 / 禁止追高。
                  </div>
                </section>

                {report ? (
                  <section className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur">
                    <h2 className="mb-4 text-2xl font-bold">消息面 & 持仓</h2>
                    <p className="rounded-2xl bg-sky-500/10 p-4 text-sky-100">{report.news.summary}</p>
                    <div className="mt-4 space-y-3">
                      {report.holdings.items.length ? report.holdings.items.map((item) => (
                        <div key={item.stock} className="rounded-2xl bg-slate-950/60 p-4 text-sm">
                          <b>{item.name} {item.stock}</b>：{item.action}（{item.pnl_pct}%）
                        </div>
                      )) : <div className="rounded-2xl bg-slate-950/60 p-4 text-sm text-slate-300">未配置持仓，设置 HOLDINGS_JSON 后可生成持仓交易信息。</div>}
                    </div>
                  </section>
                ) : null}
              </aside>
            </section>
          </div>
        )}
      </section>
    </main>
  )
}
