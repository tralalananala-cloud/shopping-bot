import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { X } from 'lucide-react'
import { useAppStore } from '../store/useAppStore'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.05 },
  },
}

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 280, damping: 22 } },
}

const sections = [
  {
    emoji: '📝',
    title: 'Lista personală',
    color: 'hsl(185 100% 50%)',
    bgColor: 'hsl(185 100% 50% / 0.08)',
    borderColor: 'hsl(185 100% 50% / 0.2)',
    content: 'Lista ta personală este vizibilă doar ție. Adaugă produse cu butonul +, bifează-le când le cumperi, și șterge-le pe toate cu "Curăță bifate". Poți adăuga și cantitate opțional.',
  },
  {
    emoji: '👥',
    title: 'Grupuri',
    color: 'hsl(275 99% 53%)',
    bgColor: 'hsl(275 99% 53% / 0.08)',
    borderColor: 'hsl(275 99% 53% / 0.2)',
    content: 'Grupurile îți permit să colaborezi cu familia sau prietenii. Creează un grup nou sau alătură-te unui grup existent folosind codul de invitație. Toți membrii pot adăuga și bifa produse.',
  },
  {
    emoji: '⚙️',
    title: 'Admin grup',
    color: 'hsl(40 100% 50%)',
    bgColor: 'hsl(40 100% 50% / 0.08)',
    borderColor: 'hsl(40 100% 50% / 0.2)',
    content: 'Dacă ești proprietarul unui grup, poți redenumi grupul, elimina membri și șterge grupul. Membrii non-admin pot ieși din grup oricând din pagina grupului.',
  },
  {
    emoji: '💡',
    title: 'Sfat pentru cantitate',
    color: 'hsl(185 100% 50%)',
    bgColor: 'hsl(185 100% 50% / 0.08)',
    borderColor: 'hsl(185 100% 50% / 0.2)',
    content: 'Poți specifica cantitatea direct în câmpul de cantitate (ex: "2", "500g", "1 pachet"). Cantitatea apare ca un badge mic lângă produs. Dacă nu specifici cantitate, se salvează "1" implicit.',
  },
  {
    emoji: '🔗',
    title: 'Partajare grup',
    color: 'hsl(275 99% 53%)',
    bgColor: 'hsl(275 99% 53% / 0.08)',
    borderColor: 'hsl(275 99% 53% / 0.2)',
    content: 'Fiecare grup are un cod unic de invitație (ex: ABC123). Partajează codul cu persoanele pe care vrei să le adaugi în grup. Ele îl pot introduce în secțiunea "Grupuri" → butonul cu cheița.',
  },
]

export default function HelpPage() {
  const setView = useAppStore((s) => s.setView)

  useEffect(() => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      tg.BackButton.show()
      tg.BackButton.onClick(() => setView({ type: 'home' }))
      return () => { tg.BackButton.hide(); tg.BackButton.offClick(() => setView({ type: 'home' })) }
    }
  }, [setView])

  return (
    <div className="flex min-h-full flex-col">
      {/* Header */}
      <div
        className="sticky top-0 z-10 px-4 pb-3 pt-6"
        style={{ backdropFilter: 'blur(24px)', WebkitBackdropFilter: 'blur(24px)' }}
      >
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-foreground">ℹ️ Ajutor</h1>
          <button
            onClick={() => setView({ type: 'home' })}
            className="flex h-8 w-8 items-center justify-center rounded-full text-muted-foreground transition-colors hover:text-foreground"
            style={{ background: 'hsl(0 0% 100% / 0.06)' }}
          >
            <X size={16} />
          </button>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Ghid de utilizare pentru Shopping Bot
        </p>
      </div>

      {/* Sections */}
      <motion.div
        className="flex flex-col gap-3 px-4 pb-6"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {sections.map((section) => (
          <motion.div
            key={section.title}
            variants={cardVariants}
            className="rounded-2xl p-4"
            style={{
              background: section.bgColor,
              border: `1px solid ${section.borderColor}`,
            }}
          >
            <div className="mb-2 flex items-center gap-2">
              <span className="text-xl">{section.emoji}</span>
              <h3 className="font-semibold" style={{ color: section.color }}>
                {section.title}
              </h3>
            </div>
            <p className="text-sm leading-relaxed text-muted-foreground">
              {section.content}
            </p>
          </motion.div>
        ))}

        {/* Footer note */}
        <motion.div variants={cardVariants} className="glass-card rounded-2xl p-4 text-center">
          <p className="text-xs text-muted-foreground">
            Shopping Bot v2.0 · Telegram Mini App
          </p>
          <p className="mt-1 text-xs text-muted-foreground opacity-60">
            API: shopping-bot-w69n.onrender.com
          </p>
        </motion.div>
      </motion.div>
    </div>
  )
}
