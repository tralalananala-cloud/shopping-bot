import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { Toaster } from 'sonner'
import { useAppStore } from '../store/useAppStore'
import BottomNav from '../components/BottomNav'
import HomePage from '../components/HomePage'
import PersonalListPage from '../components/PersonalListPage'
import GroupsListPage from '../components/GroupsListPage'
import GroupDetailPage from '../components/GroupDetailPage'
import HelpPage from '../components/HelpPage'

function ViewRouter() {
  const view = useAppStore((s) => s.view)

  switch (view.type) {
    case 'home':
      return <HomePage />
    case 'personal-list':
      return <PersonalListPage />
    case 'groups-list':
      return <GroupsListPage />
    case 'group-detail':
      return <GroupDetailPage groupId={view.groupId} />
    case 'help':
      return <HelpPage />
    default:
      return <HomePage />
  }
}

export default function Index() {
  const fetchCurrentUser = useAppStore((s) => s.fetchCurrentUser)

  useEffect(() => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      tg.ready()
      tg.expand()
    }
    fetchCurrentUser()
  }, [fetchCurrentUser])

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-background">
      {/* Decorative background blobs */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <motion.div
          className="absolute -left-20 -top-20 h-80 w-80 rounded-full"
          style={{
            background: 'hsl(185 100% 50% / 0.15)',
            filter: 'blur(80px)',
          }}
          animate={{
            x: [0, 30, 0],
            y: [0, 20, 0],
          }}
          transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute -right-20 top-1/3 h-96 w-96 rounded-full"
          style={{
            background: 'hsl(275 99% 53% / 0.15)',
            filter: 'blur(80px)',
          }}
          animate={{
            x: [0, -25, 0],
            y: [0, 35, 0],
          }}
          transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut', delay: 2 }}
        />
        <motion.div
          className="absolute bottom-20 left-1/3 h-72 w-72 rounded-full"
          style={{
            background: 'hsl(40 100% 50% / 0.12)',
            filter: 'blur(80px)',
          }}
          animate={{
            x: [0, 20, -10, 0],
            y: [0, -20, 10, 0],
          }}
          transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut', delay: 4 }}
        />
      </div>

      {/* Main content */}
      <div className="relative mx-auto flex min-h-screen max-w-[440px] flex-col">
        <main className="flex-1 overflow-y-auto pb-28 scrollbar-hide">
          <ViewRouter />
        </main>
        <BottomNav />
      </div>

      <Toaster
        position="top-center"
        toastOptions={{
          style: {
            background: 'hsl(240 10% 5% / 0.95)',
            backdropFilter: 'blur(24px)',
            border: '1px solid hsl(0 0% 100% / 0.08)',
            color: 'hsl(0 0% 100%)',
            fontFamily: 'Space Grotesk, sans-serif',
          },
        }}
      />
    </div>
  )
}
