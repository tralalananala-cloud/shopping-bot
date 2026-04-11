export default function Toast({ msg, type = 'success' }) {
  const colors = {
    success: 'bg-emerald-600',
    error:   'bg-red-500',
    info:    'bg-[var(--tg-btn)]',
  }
  return (
    <div className={`animate-slide-up ${colors[type] || colors.info} text-white text-sm font-medium px-4 py-2.5 rounded-xl shadow-lg max-w-xs text-center`}>
      {msg}
    </div>
  )
}
