import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Plus, Key, Crown, Users, ChevronRight, Copy, Loader2 } from 'lucide-react'
import { useAppStore } from '../store/useAppStore'
import { toast } from 'sonner'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.06 } },
}

const rowVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } },
}

export default function GroupsListPage() {
  const setView = useAppStore((s) => s.setView)
  const groups = useAppStore((s) => s.groups)
  const groupsLoading = useAppStore((s) => s.groupsLoading)
  const currentUser = useAppStore((s) => s.currentUser)
  const fetchGroups = useAppStore((s) => s.fetchGroups)
  const createNewGroup = useAppStore((s) => s.createNewGroup)
  const joinExistingGroup = useAppStore((s) => s.joinExistingGroup)

  const [showCreate, setShowCreate] = useState(false)
  const [showJoin, setShowJoin] = useState(false)
  const [nameInput, setNameInput] = useState('')
  const [codeInput, setCodeInput] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchGroups()
  }, [fetchGroups])

  useEffect(() => {
    const tg = window.Telegram?.WebApp
    if (!tg) return
    const goHome = () => setView({ type: 'feed' })
    tg.BackButton.show()
    tg.BackButton.onClick(goHome)
    return () => { tg.BackButton.hide(); tg.BackButton.offClick(goHome) }
  }, [setView])

  async function handleCreate() {
    const name = nameInput.trim()
    if (!name) return
    setLoading(true)
    try {
      await createNewGroup(name)
      setNameInput('')
      setShowCreate(false)
    } finally {
      setLoading(false)
    }
  }

  async function handleJoin() {
    const code = codeInput.trim().toUpperCase()
    if (code.length < 4) return
    setLoading(true)
    try {
      await joinExistingGroup(code)
      setCodeInput('')
      setShowJoin(false)
    } finally {
      setLoading(false)
    }
  }

  function copyCode(code: string) {
    navigator.clipboard.writeText(code).then(() => toast.success('Cod copiat!')).catch(() => {})
  }

  return (
    <div className="flex min-h-full flex-col">
      {/* Header */}
      <div
        className="sticky top-0 z-10 px-4 pb-3 pt-6"
        style={{ backdropFilter: 'blur(24px)', WebkitBackdropFilter: 'blur(24px)' }}
      >
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-foreground">👥 Grupuri</h1>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowJoin(true)}
              className="flex h-8 w-8 items-center justify-center rounded-full text-muted-foreground transition-colors hover:text-foreground"
              style={{ background: 'hsl(0 0% 100% / 0.06)' }}
              title="Alătură-te unui grup"
            >
              <Key size={15} />
            </button>
            <button
              onClick={() => setShowCreate(true)}
              className="flex h-8 w-8 items-center justify-center rounded-full text-background transition-all"
              style={{
                background: 'hsl(var(--primary))',
                boxShadow: '0 0 12px hsl(185 100% 50% / 0.4)',
              }}
              title="Creează grup"
            >
              <Plus size={16} />
            </button>
            <button
              onClick={() => setView({ type: 'feed' })}
              className="flex h-8 w-8 items-center justify-center rounded-full text-muted-foreground transition-colors hover:text-foreground"
              style={{ background: 'hsl(0 0% 100% / 0.06)' }}
            >
              <X size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* List */}
      <div className="flex-1 px-4 pb-4">
        {groupsLoading && groups.length === 0 ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 size={28} className="animate-spin text-primary" />
          </div>
        ) : groups.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center py-16 text-center"
          >
            <div className="mb-3 text-4xl">👥</div>
            <p className="font-medium text-muted-foreground">Niciun grup</p>
            <p className="mt-1 text-sm text-muted-foreground opacity-60">
              Creează sau alătură-te unui grup
            </p>
          </motion.div>
        ) : (
          <motion.ul
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="flex flex-col gap-3"
          >
            {groups.map((group) => {
              const isOwner = group.owner_id === currentUser?.user_id
              return (
                <motion.li key={group.id} variants={rowVariants}>
                  <button
                    className="glass-card glass-hover group w-full rounded-2xl p-4 text-left transition-all duration-200"
                    onClick={() => setView({ type: 'group-detail', groupId: group.id })}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0 flex-1">
                        {/* Name + crown */}
                        <div className="flex items-center gap-2">
                          <span className="truncate font-semibold text-foreground">{group.name}</span>
                          {isOwner && (
                            <Crown size={14} className="flex-shrink-0 text-accent" />
                          )}
                        </div>

                        {/* Invite code badge */}
                        <div className="mt-2 flex flex-wrap items-center gap-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              copyCode(group.invite_code)
                            }}
                            className="flex items-center gap-1.5 rounded-lg px-2 py-1 font-mono text-xs transition-colors hover:text-primary"
                            style={{
                              background: 'hsl(var(--muted))',
                              color: 'hsl(var(--muted-foreground))',
                            }}
                          >
                            <Copy size={11} />
                            {group.invite_code}
                          </button>

                          {group.member_count !== undefined && (
                            <span className="flex items-center gap-1 text-xs text-muted-foreground">
                              <Users size={11} />
                              {group.member_count}
                            </span>
                          )}
                        </div>
                      </div>

                      <ChevronRight
                        size={18}
                        className="mt-1 flex-shrink-0 text-muted-foreground transition-transform duration-200 group-hover:translate-x-0.5"
                      />
                    </div>
                  </button>
                </motion.li>
              )
            })}
          </motion.ul>
        )}
      </div>

      {/* Create sheet */}
      <AnimatePresence>
        {showCreate && (
          <>
            <motion.div
              className="fixed inset-0 z-40 bg-black/50"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowCreate(false)}
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
                <h3 className="text-base font-semibold text-foreground">Creează grup</h3>
                <button onClick={() => setShowCreate(false)} className="text-muted-foreground">
                  <X size={18} />
                </button>
              </div>
              <div className="flex flex-col gap-3">
                <input
                  autoFocus
                  placeholder="Numele grupului"
                  value={nameInput}
                  onChange={(e) => setNameInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
                  className="w-full rounded-xl border px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground"
                  style={{ background: 'hsl(0 0% 100% / 0.05)', borderColor: 'hsl(var(--border))' }}
                />
                <button
                  onClick={handleCreate}
                  disabled={!nameInput.trim() || loading}
                  className="flex items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold text-background transition-all disabled:opacity-50"
                  style={{ background: 'hsl(var(--primary))', boxShadow: '0 0 16px hsl(185 100% 50% / 0.35)' }}
                >
                  {loading ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
                  Creează
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Join sheet */}
      <AnimatePresence>
        {showJoin && (
          <>
            <motion.div
              className="fixed inset-0 z-40 bg-black/50"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowJoin(false)}
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
                <h3 className="text-base font-semibold text-foreground">Alătură-te unui grup</h3>
                <button onClick={() => setShowJoin(false)} className="text-muted-foreground">
                  <X size={18} />
                </button>
              </div>
              <div className="flex flex-col gap-3">
                <input
                  autoFocus
                  placeholder="Cod invitație (ex: ABC123)"
                  value={codeInput}
                  onChange={(e) => setCodeInput(e.target.value.toUpperCase())}
                  onKeyDown={(e) => e.key === 'Enter' && handleJoin()}
                  maxLength={12}
                  className="w-full rounded-xl border px-4 py-3 font-mono text-sm uppercase tracking-wider text-foreground placeholder:text-muted-foreground"
                  style={{ background: 'hsl(0 0% 100% / 0.05)', borderColor: 'hsl(var(--border))' }}
                />
                <button
                  onClick={handleJoin}
                  disabled={codeInput.trim().length < 4 || loading}
                  className="flex items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold text-background transition-all disabled:opacity-50"
                  style={{ background: 'hsl(var(--secondary))', boxShadow: '0 0 16px hsl(275 99% 53% / 0.35)' }}
                >
                  {loading ? <Loader2 size={16} className="animate-spin" /> : <Key size={16} />}
                  Intră în grup
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
