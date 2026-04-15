import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { RefreshCw, Loader2 } from 'lucide-react'
import { useAppStore } from '../store/useAppStore'
import type { FeedItem } from '../api'
import { FeedCard } from './FeedCard'

export default function FeedPage() {
  const feedItems   = useAppStore((s) => s.feedItems)
  const feedLoading = useAppStore((s) => s.feedLoading)
  const fetchFeed   = useAppStore((s) => s.fetchFeed)
  const currentUser = useAppStore((s) => s.currentUser)

  useEffect(() => { fetchFeed() }, [fetchFeed])

  const active    = feedItems.filter((i) => !i.checked)
  const completed = feedItems.filter((i) => i.checked)
  const firstName = currentUser?.first_name || currentUser?.username || 'utilizator'

  return (
    <div className="px-4 pt-6">
      {/* Header */}
      <div className="mb-5 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Bună, {firstName}! 👋</h1>
          <p className="mt-0.5 text-sm text-muted-foreground">
            {active.length > 0 ? `${active.length} produse de cumpărat` : 'Totul e gata!'}
          </p>
        </div>
        <button
          onClick={fetchFeed}
          disabled={feedLoading}
          className="flex h-9 w-9 items-center justify-center rounded-full text-muted-foreground transition-colors hover:text-foreground disabled:opacity-40"
          style={{ background: 'hsl(0 0% 100% / 0.06)' }}
        >
          {feedLoading
            ? <Loader2 size={16} className="animate-spin" />
            : <RefreshCw size={16} />
          }
        </button>
      </div>

      {/* Feed */}
      {feedLoading && feedItems.length === 0 ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 size={32} className="animate-spin text-primary" />
        </div>
      ) : feedItems.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-center justify-center py-20 text-center"
        >
          <div className="mb-3 text-5xl">🛒</div>
          <p className="font-semibold text-foreground">Feed-ul e gol</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Adaugă produse în lista personală sau grupuri
          </p>
        </motion.div>
      ) : (
        <div className="flex flex-col gap-3">
          {active.length > 0 && (
            <>
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                De cumpărat · {active.length}
              </p>
              {active.map((item, i) => (
                <FeedCard key={`${item.source}-${item.id}`} item={item} index={i} />
              ))}
            </>
          )}
          {completed.length > 0 && (
            <>
              <p className="mt-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Îndeplinite · {completed.length}
              </p>
              {completed.slice(0, 10).map((item, i) => (
                <FeedCard key={`${item.source}-${item.id}`} item={item} index={i} />
              ))}
              {completed.length > 10 && (
                <p className="pb-2 text-center text-xs text-muted-foreground">
                  + {completed.length - 10} mai multe în secțiunea Completate
                </p>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}
