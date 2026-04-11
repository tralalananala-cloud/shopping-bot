import { useState } from 'react'

const HELP_TEXT = [
  {
    title: '📝 Lista personală',
    body: 'Lista ta privată. Adaugă, bifează și șterge produse. Partajează-o rapid într-un grup.',
  },
  {
    title: '👥 Grupuri',
    body: 'Creează un grup, invită familia sau prietenii cu un cod de 6 caractere. Lista e vizibilă tuturor membrilor.',
  },
  {
    title: '⚙️ Admin grup',
    body: 'Proprietarul poate redenumi grupul, elimina membri și șterge grupul.',
  },
  {
    title: '💡 Sfat cantitate',
    body: 'Scrie cantitatea la finalul numelui: "lapte 2" → lapte ×2',
  },
]

function HelpModal({ onClose }) {
  return (
    <>
      <div className="fixed inset-0 bg-black/40 z-40 animate-fade-in" onClick={onClose} />
      <div className="fixed inset-x-4 top-1/2 -translate-y-1/2 z-50 bg-tg-bg rounded-2xl p-5 shadow-2xl animate-slide-up max-h-[80vh] overflow-y-auto scroll-hidden">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-bold text-lg">ℹ️ Ajutor</h2>
          <button onClick={onClose} className="text-tg-hint text-2xl leading-none">×</button>
        </div>
        <div className="flex flex-col gap-4">
          {HELP_TEXT.map(h => (
            <div key={h.title}>
              <p className="font-semibold text-sm mb-1">{h.title}</p>
              <p className="text-sm text-tg-hint">{h.body}</p>
            </div>
          ))}
        </div>
      </div>
    </>
  )
}

export default function MainMenu({ nav }) {
  const [showHelp, setShowHelp] = useState(false)

  const cards = [
    {
      emoji: '📝',
      label: 'Lista mea',
      sub:   'Produse personale',
      color: 'from-blue-500 to-cyan-400',
      onClick: () => nav.push('personal'),
    },
    {
      emoji: '👥',
      label: 'Grupuri',
      sub:   'Liste partajate',
      color: 'from-violet-500 to-purple-400',
      onClick: () => nav.push('groups'),
    },
    {
      emoji: 'ℹ️',
      label: 'Ajutor',
      sub:   'Cum funcționează',
      color: 'from-amber-500 to-yellow-400',
      onClick: () => setShowHelp(true),
    },
  ]

  return (
    <div className="min-h-screen flex flex-col px-4 pt-10 pb-6 animate-fade-in">
      {/* Hero */}
      <div className="text-center mb-10">
        <div className="text-5xl mb-3">🛒</div>
        <h1 className="text-2xl font-bold">Lista de Cumpărături</h1>
        <p className="text-tg-hint text-sm mt-1">Organizează cumpărăturile cu familia</p>
      </div>

      {/* Carduri */}
      <div className="flex flex-col gap-3">
        {cards.map(c => (
          <button
            key={c.label}
            onClick={c.onClick}
            className="flex items-center gap-4 bg-tg-bg2 rounded-2xl p-4 text-left active:scale-[0.98] transition-transform"
          >
            <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${c.color} flex items-center justify-center text-2xl shadow-md`}>
              {c.emoji}
            </div>
            <div className="flex-1">
              <p className="font-semibold">{c.label}</p>
              <p className="text-xs text-tg-hint">{c.sub}</p>
            </div>
            <span className="text-tg-hint text-lg">›</span>
          </button>
        ))}
      </div>

      {showHelp && <HelpModal onClose={() => setShowHelp(false)} />}
    </div>
  )
}
