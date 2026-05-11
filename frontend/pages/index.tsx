import { StatCard } from '../components/StatCard'
import { useRealtimeDashboard } from '../websocket/useRealtime'

export default function Home() {
  const { data, connected } = useRealtimeDashboard()
  const market = data?.market

  return (
    <main className="min-h-screen px-6 py-8 md:px-10">
      <section className="mx-auto max-w-7xl">
        <div className="mb-8 flex flex-col justify-between gap-4 md:flex-row md:items-end">
          <div>
            <p className="text-sm font-semibold text-sky-300">环境 &gt; 情绪 &gt; 个股 &gt; 技术</p>
            <h1 className="mt-2 text-4xl font-black tracking-tight">AI 情绪交易系统 MVP</h1>
            <p className="mt-3 text-slate-300">实时监控市场环境、AI 选股池、风险提示与情绪状态。</p>
          </div>
          <div className={`rounded-full px-4 py-2 text-sm ${connected ? 'bg-emerald-500/20 text-emerald-200' : 'bg-amber-500/20 text-amber-200'}`}>
            {connected ? 'WebSocket 已连接' : '使用 HTTP 快照 / 等待连接'}
          </div>
        </div>

        {!data || !market ? (
          <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-slate-300">正在加载本地交易辅助数据...</div>
        ) : (
          <div className="grid gap-6">
            <section className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl">
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
              <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl">
                <h2 className="mb-5 text-2xl font-bold">AI 选股池</h2>
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

              <aside className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl">
                <h2 className="mb-5 text-2xl font-bold">AI 实时提示</h2>
                <div className="rounded-2xl bg-slate-950/70 p-5 whitespace-pre-line leading-8 text-slate-100">{data.ai.message}</div>
                <div className="mt-5 rounded-2xl border border-amber-400/30 bg-amber-500/10 p-5 text-amber-100">
                  风控优先级：4000 家下跌清仓 / 高风险禁止开仓 / 禁止追高 / 止损提醒。
                </div>
              </aside>
            </section>
          </div>
        )}
      </section>
    </main>
  )
}
