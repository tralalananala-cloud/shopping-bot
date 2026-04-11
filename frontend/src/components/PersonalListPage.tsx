import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Plus, Trash2, Sparkles, Check, Loader2 } from 'lucide-react'
import { useAppStore } from '../store/useAppStore'

const listVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
}

const rowVariants = {
  hidden: { opacity: 0, x: -16 },
  visible: { opacity: 1, x: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } },
  exit: { opacity: 0, x: 16, transition: { duration: 0.15 } },
}

export default function PersonalListPage() {
  const setView = useAppStore((s) => s.setView)
  const personalItems = useAppStore((s) => s.personalItems)
  const personalLoading = useAppStore((s) => s.personalLoading)
  const fetchPersonalList = useAppStore((s) => s.fetchPersonalList)
  const addPersonal = useAppStore((s) => s.addPersonal)
  const togglePersonal = useAppStore((s) => s.togglePersonal)
  const deletePersonal = useAppStore((s) => s.deletePersonal)
  const clearPersonalChecked = useAppStore((s) => s.clearPersonalChecked)

  const [showSheet, setShowSheet] = useState(false)
  const [itemInput, setItemInput] = useState('')
  const [qtyInput, setQtyInput] = useState('')
  const [adding, setAdding] = useState(false)

  useEffect(() => {
    fetchPersonalList()
  }, [fetchPersonalList])

  useEffect(() => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      tg.BackButton.show()
      tg.BackButton.onClick(() => setView({ type: 'home' }))
      return () => { tg.BackButton.hide(); tg.BackButton.offClick(() => setView({ type: 'home' })) }
    }
  }, [setView])

  const checkedCount = personalItems.filter((i) => i.checked).length
  const total = personalItems.length
  const progress = total > 0 ? (checkedCount / total) * 100 : 0

  async function handleAdd() {
    const item = itemInput.trim()
    if (!item) return
    setAdding(true)
    try {
      await addPersonal(item, qtyInput.trim() || '1')
      setItemInput('')
      setQtyInput('')
      setShowSheet(false)
    } finally {
      setAdding(false)
    }
  }

  return (
    <div className="flex min-h-full flex-col">
      {/* Header */}
      <div className="sticky top-0 z-10 px-4 pb-3 pt-6" style={{ backdropFilter: 'blur(24px)', WebkitBackdropFilter: 'blur(24px)' }}>
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-foreground">📝 Lista mea</h1>
          <button
            onClick={() => setView({ type: 'home' })}
            className="flex h-8 w-8 items-center justify-center rounded-full text-muted-foreground transition-colors hover:text-foreground"
            style={{ background: 'hsl(0 0% 100% / 0.06)' }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Progress bar */}
        {total > 0 && (
          <div className="mt-3">
            <div className="mb-1 flex justify-between text-xs text-muted-foreground">
              <span>{checkedCount} din {total} produse</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full" style={{ background: 'hsl(var(--border))' }}>
              <motion.div
                className="h-full rounded-full"
                style={{ background: 'hsl(var(--primary))' }}
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.4, ease: 'easeOut' }}
              />
            </div>
          </div>
        )}

        {/* Toolbar */}
        <div className="mt-3 flex gap-2">
          {checkedCount > 0 && (
            <button
              onClick={clearPersonalChecked}
              className="flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors"
              style={{ background: 'hsl(0 0% 100% / 0.06)', border: '1px solid hsl(0 0% 100% / 0.08)' }}
            >
              <Sparkles size={13} />
              Curăță bifate
            </button>
          )}
          <button
            onClick={() => setShowSheet(true)}
            className="ml-auto flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-semibold text-background transition-all"
            style={{
              background: 'hsl(var(--primary))',
              boxShadow: '0 0 12px hsl(185 100% 50% / 0.4)',
            }}
          >
            <Plus size={14} />
            Adaugă
          </button>
        </div>
      </div>

      {/* List */}
      <div className="flex-1 px-4 pb-4">
        {personalLoading && personalItems.length === 0 ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 size={28} className="animate-spin text-primary" />
          </div>
        ) : personalItems.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center py-16 text-center"
          >
            <div className="mb-3 text-4xl">🛒</div>
            <p className="font-medium text-muted-foreground">Lista ta e goală</p>
            <p className="mt-1 text-sm text-muted-foreground opacity-60">Apasă + pentru a adăuga</p>
          </motion.div>
        ) : (
          <motion.ul variants={listVariants} initial="hidden" animate="visible" className="flex flex-col gap-2">
            <AnimatePresence mode="popLayout">
              {personalItems.map((item) => (
                <motion.li
                  key={item.id}
                  variants={rowVariants}
                  exit="exit"
                  layout
                  className="glass-card group flex items-center gap-3 rounded-2xl p-4"
                >
                  {/* Checkbox */}
                  <button
                    onClick={() => togglePersonal(item.id)}
                    className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full border-2 transition-all duration-200"
                    style={{
                      borderColor: item.checked ? 'hsl(var(--primary))' : 'hsl(var(--border))',
                      background: item.checked ? 'hsl(var(--primary))' : 'transparent',
                    }}
                  >
                    {item.checked && <Check size={12} className="text-background" strokeWidth={3} />}
                  </button>

                  {/* Item name + qty */}
                  <div className={`flex-1 min-w-0 transition-opacity duration-200 ${item.checked ? 'opacity-40' : ''}`}>
                    <span className={`block truncate font-medium text-foreground ${item.checked ? 'line-through' : ''}`}>
                      {item.item}
                    </span>
                    {item.quantity && item.quantity !== '1' && (
                      <span
                        className="mt-0.5 inline-block rounded-md px-1.5 py-0.5 text-xs font-medium"
                        style={{ background: 'hsl(var(--muted))', color: 'hsl(var(--muted-foreground))' }}
                      >
                        ×{item.quantity}
                      </span>
                    )}
                  </div>

                  {/* Delete button */}
                  <button
                    onClick={() => deletePersonal(item.id)}
                    className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full text-muted-foreground opacity-0 transition-all duration-200 group-hover:opacity-100 hover:text-destructive"
                    style={{ background: 'hsl(0 0% 100% / 0.06)' }}
                  >
                    <Trash2 size={13} />
                  </button>
                </motion.li>
              ))}
            </AnimatePresence>
          </motion.ul>
        )}
      </div>

      {/* Add item sheet */}
      <AnimatePresence>
        {showSheet && (
          <>
            <motion.div
              className="fixed inset-0 z-40 bg-black/50"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowSheet(false)}
            />
            <motion.div
              className="fixed bottom-0 left-0 right-0 z-50 mx-auto max-w-[440px] rounded-t-3xl p-6"
              style={{ background: 'hsl(240 10% 6%)', border: '1px solid hsl(0 0% 100% / 0.08)' }}
              initial={{ y: '100%' }}
              animate={{ y: 0 }}
              exit={{ y: '100%' }}
              transition={{ type: 'spring', stiffness: 400, damping: 35 }}
            >
              <div className="mb-4 flex items-center justify-between">
                <h3 className="text-base font-semibold text-foreground">Adaugă produs</h3>
                <button onClick={() => setShowSheet(false)} className="text-muted-foreground">
                  <X size={18} />
                </button>
              </div>
              <div className="flex flex-col gap-3">
                <input
                  autoFocus
                  placeholder="Nume produs (ex: lapte)"
                  value={itemInput}
                  onChange={(e) => setItemInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
                  className="w-full rounded-xl border px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground"
                  style={{ background: 'hsl(0 0% 100% / 0.05)', borderColor: 'hsl(var(--border))' }}
                />
                <input
                  placeholder="Cantitate (opțional, ex: 2)"
                  value={qtyInput}
                  onChange={(e) => setQtyInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
                  className="w-full rounded-xl border px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground"
                  style={{ background: 'hsl(0 0% 100% / 0.05)', borderColor: 'hsl(var(--border))' }}
                />
                <button
                  onClick={handleAdd}
                  disabled={!itemInput.trim() || adding}
                  className="flex items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold text-background transition-all disabled:opacity-50"
                  style={{
                    background: 'hsl(var(--primary))',
                    boxShadow: '0 0 16px hsl(185 100% 50% / 0.35)',
                  }}
                >
                  {adding ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
                  Adaugă
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
