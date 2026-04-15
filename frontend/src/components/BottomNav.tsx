import { motion } from 'framer-motion'
import { LayoutList, ShoppingCart, Users, CheckCircle2, HelpCircle, type LucideProps } from 'lucide-react'
import { useAppStore } from '../store/useAppStore'
import type { View } from '../store/useAppStore'
import { clsx } from 'clsx'
import type { ForwardRefExoticComponent, RefAttributes } from 'react'

type LucideIcon = ForwardRefExoticComponent<Omit<LucideProps, 'ref'> & RefAttributes<SVGSVGElement>>

const tabs: Array<{ label: string; icon: LucideIcon; view: View }> = [
  { label: 'Feed',       icon: LayoutList,    view: { type: 'feed' } },
  { label: 'Lista',      icon: ShoppingCart,  view: { type: 'personal-list' } },
  { label: 'Grupuri',    icon: Users,         view: { type: 'groups-list' } },
  { label: 'Completate', icon: CheckCircle2,  view: { type: 'completed' } },
  { label: 'Ajutor',     icon: HelpCircle,    view: { type: 'help' } },
]

export default function BottomNav() {
  const view    = useAppStore((s) => s.view)
  const setView = useAppStore((s) => s.setView)

  const activeType =
    view.type === 'group-detail' ? 'groups-list' : view.type

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 flex justify-center px-3 pb-5">
      <div className="mx-auto w-full max-w-[440px]">
        <nav className="glass-card relative flex items-center justify-around rounded-3xl px-1 py-2.5">
          {tabs.map((tab) => {
            const isActive = tab.view.type === activeType
            const Icon: LucideIcon = tab.icon
            return (
              <button
                key={tab.view.type}
                onClick={() => setView(tab.view)}
                className="relative flex flex-col items-center gap-0.5 px-3 py-1"
              >
                {isActive && (
                  <motion.div
                    layoutId="nav-indicator"
                    className="absolute inset-0 rounded-2xl"
                    style={{
                      background: 'hsl(185 100% 50% / 0.12)',
                      border: '1px solid hsl(185 100% 50% / 0.2)',
                    }}
                    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                  />
                )}
                <Icon
                  size={19}
                  className={clsx(
                    'relative z-10 transition-colors duration-200',
                    isActive ? 'text-primary' : 'text-muted-foreground',
                  )}
                />
                <span
                  className={clsx(
                    'relative z-10 text-[10px] font-medium transition-colors duration-200',
                    isActive ? 'text-primary' : 'text-muted-foreground',
                  )}
                >
                  {tab.label}
                </span>
              </button>
            )
          })}
        </nav>
      </div>
    </div>
  )
}
