type StatCardProps = {
  label: string
  value: string | number
  tone?: 'red' | 'green' | 'yellow' | 'blue'
}

const toneClass = {
  red: 'border-red-500/40 bg-red-500/10 text-red-100',
  green: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-100',
  yellow: 'border-amber-500/40 bg-amber-500/10 text-amber-100',
  blue: 'border-sky-500/40 bg-sky-500/10 text-sky-100',
}

export function StatCard({ label, value, tone = 'blue' }: StatCardProps) {
  return (
    <div className={`rounded-2xl border p-5 shadow-lg ${toneClass[tone]}`}>
      <p className="text-sm opacity-70">{label}</p>
      <p className="mt-3 text-3xl font-bold">{value}</p>
    </div>
  )
}
