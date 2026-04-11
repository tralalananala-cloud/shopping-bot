export default function Spinner({ className = '' }) {
  return (
    <div className={`flex justify-center items-center py-12 ${className}`}>
      <div className="spinner w-8 h-8 rounded-full border-2 border-tg-bg2 border-t-[var(--tg-btn)]" />
    </div>
  )
}
