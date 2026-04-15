import { useEffect } from 'react'
import { Loader2, Trash2 } from 'lucide-react'
import { useAppStore } from '../store/useAppStore'
import { FeedCard } from './FeedCard'
import { toast } from 'sonner'
import { clearPersonalDone, clearGroupDone } from '../api'

export default function CompletedPage() {
  const feedItems   = useAppStore((s) => s.feedItems)
  const feedLoading = useAppStore((s) => s.feedLoading)
  const fetchFeed   = useAppStore((s) => s.fetchFeed)
  const setView     = useAppStore((s) => s.setView)

  useEffect(() => {
    const tg = window.Telegram?.WebApp
    if (!tg) return
    const goBack = () => setView({ type: 'feed' })
    tg.BackButton.show()
    tg.BackButton.onClick(goBack)
    return () => { tg.BackButton.hide(); tg.BackButton.offClick(goBack) }
  }, [setView])

  const completed = feedItems.filter((i) => i.checked)

  // Grupăm după sursă pentru afișare
  const personal = completed.filter((i) => i.source === 'personal')
  const byGroup = completed
    .filter((i) => i.source === 'group')
    .reduce<Record<string, typeof completed>>((acc, item) => {
      const key = `${item.group_id}::${item.group_name}`
      acc[key] = acc[key] ? [...acc[key], item] : [item]
      return acc
    }, {})

  async function clearAll() {
    try {
      // Șterge toate bifatele din personal
      if (personal.length > 0) await clearPersonalDone()

      // Șterge bifatele din fiecare grup
      const groupIds = [...new Set(
        completed.filter((i) => i.source === 'group' && i.group_id).map((i) => i.group_id!)
      )]
      for (const gid of groupIds) await clearGroupDone(gid)

      toast.success('Toate îndeplinitele au fost șterse!')
      fetchFeed()
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare la ștergere')
    }
  }

  return (
    <div className="flex min-h-full flex-col">
      {/* Header */}
      <div
        className="sticky top-0 z-10 px-4 pb-3 pt-6"
        style={{ backdropFilter: 'blur(24px)', WebkitBackdropFilter: 'blur(24px)' }}
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-foreground">✅ Completate</h1>
            <p className="text-sm text-muted-foreground">{completed.length} produse îndeplinite</p>
          </div>
          {completed.length > 0 && (
            <button
              onClick={clearAll}
              className="flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:text-destructive"
              style={{ background: 'hsl(0 0% 100% / 0.06)' }}
            >
              <Trash2 size={13} />
              Curăță tot
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 px-4 pb-4">
        {feedLoading && completed.length === 0 ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 size={28} className="animate-spin text-primary" />
          </div>
        ) : completed.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="mb-3 text-5xl">✅</div>
            <p className="font-semibold text-foreground">Nimic completat încă</p>
            <p className="mt-1 text-sm text-muted-foreground">Bifează produse din feed sau liste</p>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {/* Personal */}
            {personal.length > 0 && (
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Lista personală · {personal.length}
                </p>
                <div className="flex flex-col gap-2">
                  {personal.map((item, i) => (
                    <FeedCard key={`p-${item.id}`} item={item} index={i} />
                  ))}
                </div>
              </div>
            )}

            {/* Per group */}
            {Object.entries(byGroup).map(([key, items]) => {
              const groupName = items[0].group_name || 'Grup'
              return (
                <div key={key}>
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    👥 {groupName} · {items.length}
                  </p>
                  <div className="flex flex-col gap-2">
                    {items.map((item, i) => (
                      <FeedCard key={`g-${item.id}`} item={item} index={i} />
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
