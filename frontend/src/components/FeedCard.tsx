import { motion } from 'framer-motion'
import { Check } from 'lucide-react'
import { useAppStore } from '../store/useAppStore'
import type { FeedItem } from '../api'

const PRIORITY_COLOR: Record<number, string> = {
  3: 'hsl(0 84% 60%)',       // mare — roșu
  2: 'hsl(185 100% 50%)',    // normală — cyan
  1: 'hsl(240 5% 50%)',      // mică — gri
}

const PRIORITY_LABEL: Record<number, string> = {
  3: '🔴 Mare',
  2: '',
  1: '🔵 Mică',
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins  = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days  = Math.floor(diff / 86400000)
  if (mins  < 1)  return 'acum'
  if (mins  < 60) return `${mins}m`
  if (hours < 24) return `${hours}h`
  return `${days}z`
}

interface Props {
  item: FeedItem
  index?: number
}

export function FeedCard({ item, index = 0 }: Props) {
  const toggleFeedItem = useAppStore((s) => s.toggleFeedItem)
  const setView        = useAppStore((s) => s.setView)

  const color = PRIORITY_COLOR[item.priority] ?? PRIORITY_COLOR[2]
  const prioLabel = PRIORITY_LABEL[item.priority] ?? ''

  const sourceLabel = item.source === 'personal'
    ? '🛒 Lista personală'
    : `👥 ${item.group_name}`

  function handleSourceClick() {
    if (item.source === 'personal') {
      setView({ type: 'personal-list' })
    } else if (item.group_id) {
      setView({ type: 'group-detail', groupId: item.group_id })
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04, type: 'spring', stiffness: 300, damping: 26 }}
      className="glass-card overflow-hidden rounded-2xl"
      style={{ borderLeft: `3px solid ${color}` }}
    >
      <div className="flex items-center gap-3 p-4">
        {/* Content */}
        <div className="min-w-0 flex-1">
          {/* Source + priority */}
          <div className="mb-1 flex flex-wrap items-center gap-2">
            <button
              onClick={handleSourceClick}
              className="text-xs font-medium text-muted-foreground hover:text-primary transition-colors"
            >
              {sourceLabel}
            </button>
            {prioLabel && (
              <span className="text-xs" style={{ color }}>
                {prioLabel}
              </span>
            )}
          </div>

          {/* Item name */}
          <p
            className={`font-semibold transition-all ${
              item.checked ? 'line-through text-muted-foreground opacity-50' : 'text-foreground'
            }`}
          >
            {item.item}
            {item.quantity && item.quantity !== '1' && (
              <span
                className="ml-2 inline-block rounded px-1.5 py-0.5 text-xs font-medium"
                style={{ background: 'hsl(var(--muted))', color: 'hsl(var(--muted-foreground))' }}
              >
                ×{item.quantity}
              </span>
            )}
          </p>

          {/* Meta */}
          <p className="mt-1 text-xs text-muted-foreground">
            {item.source === 'group' && item.added_by_name
              ? `${item.added_by_name} · `
              : ''}
            {timeAgo(item.created_at)}
          </p>
        </div>

        {/* Check button */}
        <button
          onClick={() => toggleFeedItem(item)}
          className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full border-2 transition-all duration-200 active:scale-90"
          style={{
            borderColor: item.checked ? color : 'hsl(var(--border))',
            background:  item.checked ? color : 'transparent',
          }}
        >
          {item.checked && <Check size={14} className="text-background" strokeWidth={3} />}
        </button>
      </div>
    </motion.div>
  )
}
