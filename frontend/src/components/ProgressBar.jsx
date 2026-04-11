export default function ProgressBar({ done, total }) {
  const pct = total > 0 ? Math.round((done / total) * 100) : 0
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-1.5 bg-tg-bg2 rounded-full overflow-hidden">
        <div
          className="h-full bg-[var(--tg-btn)] rounded-full transition-all duration-300"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs text-tg-hint whitespace-nowrap font-medium">
        {done}/{total}
      </span>
    </div>
  )
}
