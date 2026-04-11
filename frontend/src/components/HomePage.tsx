import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { ShoppingCart, Users, HelpCircle, Package, Group } from 'lucide-react'
import { useAppStore } from '../store/useAppStore'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } },
}

export default function HomePage() {
  const currentUser = useAppStore((s) => s.currentUser)
  const personalItems = useAppStore((s) => s.personalItems)
  const groups = useAppStore((s) => s.groups)
  const fetchPersonalList = useAppStore((s) => s.fetchPersonalList)
  const fetchGroups = useAppStore((s) => s.fetchGroups)
  const setView = useAppStore((s) => s.setView)

  useEffect(() => {
    fetchPersonalList()
    fetchGroups()
  }, [fetchPersonalList, fetchGroups])

  const firstName = currentUser?.first_name || currentUser?.username || 'utilizator'
  const uncheckedCount = personalItems.filter((i) => !i.checked).length

  return (
    <motion.div
      className="px-4 pt-8"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Greeting */}
      <motion.div variants={itemVariants} className="mb-6">
        <h1 className="text-2xl font-bold text-foreground">
          Bună, {firstName}! 👋
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Ce cumpărăm azi?
        </p>
      </motion.div>

      {/* Stats row */}
      <motion.div variants={itemVariants} className="mb-6 grid grid-cols-2 gap-3">
        <div className="glass-card rounded-2xl p-4">
          <div className="mb-1 flex items-center gap-2">
            <Package size={16} className="text-primary" />
            <span className="text-xs font-medium text-muted-foreground">Produse rămase</span>
          </div>
          <p className="text-2xl font-bold text-foreground">{uncheckedCount}</p>
        </div>
        <div className="glass-card rounded-2xl p-4">
          <div className="mb-1 flex items-center gap-2">
            <Group size={16} className="text-secondary" />
            <span className="text-xs font-medium text-muted-foreground">Grupuri</span>
          </div>
          <p className="text-2xl font-bold text-foreground">{groups.length}</p>
        </div>
      </motion.div>

      {/* Action cards */}
      <motion.div variants={itemVariants} className="mb-3">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Acțiuni rapide
        </p>
      </motion.div>

      <div className="flex flex-col gap-3">
        {/* Personal list */}
        <motion.button
          variants={itemVariants}
          onClick={() => setView({ type: 'personal-list' })}
          className="glass-card glass-hover group relative w-full overflow-hidden rounded-2xl p-5 text-left transition-all duration-200 active:scale-[0.98]"
          whileTap={{ scale: 0.98 }}
        >
          <div className="flex items-center gap-4">
            <div
              className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl text-xl"
              style={{
                background: 'linear-gradient(135deg, hsl(185 100% 50% / 0.2), hsl(185 100% 50% / 0.05))',
                border: '1px solid hsl(185 100% 50% / 0.3)',
              }}
            >
              <ShoppingCart size={22} className="text-primary" />
            </div>
            <div>
              <p className="font-semibold text-foreground">Lista mea</p>
              <p className="text-sm text-muted-foreground">
                {uncheckedCount > 0 ? `${uncheckedCount} produse de cumpărat` : 'Lista e goală'}
              </p>
            </div>
          </div>
          <div
            className="pointer-events-none absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100"
            style={{ background: 'linear-gradient(135deg, hsl(185 100% 50% / 0.04), transparent)' }}
          />
        </motion.button>

        {/* Groups */}
        <motion.button
          variants={itemVariants}
          onClick={() => setView({ type: 'groups-list' })}
          className="glass-card glass-hover group relative w-full overflow-hidden rounded-2xl p-5 text-left transition-all duration-200 active:scale-[0.98]"
          whileTap={{ scale: 0.98 }}
        >
          <div className="flex items-center gap-4">
            <div
              className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl text-xl"
              style={{
                background: 'linear-gradient(135deg, hsl(275 99% 53% / 0.2), hsl(275 99% 53% / 0.05))',
                border: '1px solid hsl(275 99% 53% / 0.3)',
              }}
            >
              <Users size={22} className="text-secondary" />
            </div>
            <div>
              <p className="font-semibold text-foreground">Grupuri</p>
              <p className="text-sm text-muted-foreground">
                {groups.length > 0 ? `${groups.length} grupuri active` : 'Niciun grup'}
              </p>
            </div>
          </div>
          <div
            className="pointer-events-none absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100"
            style={{ background: 'linear-gradient(135deg, hsl(275 99% 53% / 0.04), transparent)' }}
          />
        </motion.button>

        {/* Help */}
        <motion.button
          variants={itemVariants}
          onClick={() => setView({ type: 'help' })}
          className="glass-card glass-hover group relative w-full overflow-hidden rounded-2xl p-5 text-left transition-all duration-200 active:scale-[0.98]"
          whileTap={{ scale: 0.98 }}
        >
          <div className="flex items-center gap-4">
            <div
              className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl text-xl"
              style={{
                background: 'linear-gradient(135deg, hsl(40 100% 50% / 0.2), hsl(40 100% 50% / 0.05))',
                border: '1px solid hsl(40 100% 50% / 0.3)',
              }}
            >
              <HelpCircle size={22} className="text-accent" />
            </div>
            <div>
              <p className="font-semibold text-foreground">Ajutor</p>
              <p className="text-sm text-muted-foreground">Ghid de utilizare</p>
            </div>
          </div>
          <div
            className="pointer-events-none absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100"
            style={{ background: 'linear-gradient(135deg, hsl(40 100% 50% / 0.04), transparent)' }}
          />
        </motion.button>
      </div>
    </motion.div>
  )
}
