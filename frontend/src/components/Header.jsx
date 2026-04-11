/**
 * Header reutilizabil cu titlu și buton opțional de back.
 * Butonul back e afișat doar dacă Telegram BackButton nu e disponibil
 * (ex.: preview în browser).
 */
const tg = window.Telegram?.WebApp

export default function Header({ title, onBack, action }) {
  const showBack = onBack && !tg?.BackButton

  return (
    <div className="flex items-center gap-3 px-4 py-3 bg-tg-bg sticky top-0 z-10 border-b border-tg-bg2">
      {showBack && (
        <button
          onClick={onBack}
          className="w-8 h-8 flex items-center justify-center rounded-full text-tg-hint hover:bg-tg-bg2 transition"
          aria-label="Înapoi"
        >
          ‹
        </button>
      )}
      <h1 className="flex-1 font-semibold text-base truncate">{title}</h1>
      {action}
    </div>
  )
}
