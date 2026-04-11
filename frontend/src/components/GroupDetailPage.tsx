import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft, Crown, Copy, Plus, Trash2, Check, Loader2,
  Users, Settings, LogOut, Sparkles, X, ChevronDown,
} from 'lucide-react'
import { useAppStore } from '../store/useAppStore'
import { toast } from 'sonner'

interface Props {
  groupId: number
}

const listVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
}
const rowVariants = {
  hidden: { opacity: 0, x: -16 },
  visible: { opacity: 1, x: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } },
  exit: { opacity: 0, x: 16, transition: { duration: 0.15 } },
}

export default function GroupDetailPage({ groupId }: Props) {
  const setView = useAppStore((s) => s.setView)
  const currentUser = useAppStore((s) => s.currentUser)
  const groups = useAppStore((s) => s.groups)
  const groupItems = useAppStore((s) => s.groupItems)
  const groupItemsLoading = useAppStore((s) => s.groupItemsLoading)
  const groupMembers = useAppStore((s) => s.groupMembers)
  const fetchGroupDetail = useAppStore((s) => s.fetchGroupDetail)
  const fetchGroupItemsList = useAppStore((s) => s.fetchGroupItemsList)
  const fetchGroupMembers = useAppStore((s) => s.fetchGroupMembers)
  const addGroupItemAction = useAppStore((s) => s.addGroupItemAction)
  const toggleGroupItemAction = useAppStore((s) => s.toggleGroupItemAction)
  const deleteGroupItemAction = useAppStore((s) => s.deleteGroupItemAction)
  const clearGroupChecked = useAppStore((s) => s.clearGroupChecked)
  const kickGroupMember = useAppStore((s) => s.kickGroupMember)
  const renameExistingGroup = useAppStore((s) => s.renameExistingGroup)
  const deleteExistingGroup = useAppStore((s) => s.deleteExistingGroup)
  const leaveExistingGroup = useAppStore((s) => s.leaveExistingGroup)

  const group = groups.find((g) => g.id === groupId)
  const items = groupItems[groupId] || []
  const members = groupMembers[groupId] || []
  const isOwner = group?.owner_id === currentUser?.user_id

  const [showSheet, setShowSheet] = useState(false)
  const [itemInput, setItemInput] = useState('')
  const [qtyInput, setQtyInput] = useState('')
  const [adding, setAdding] = useState(false)

  const [showMembers, setShowMembers] = useState(false)
  const [showAdmin, setShowAdmin] = useState(false)

  const [renameInput, setRenameInput] = useState('')
  const [renaming, setRenaming] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)

  useEffect(() => {
    fetchGroupDetail(groupId)
    fetchGroupItemsList(groupId)
    fetchGroupMembers(groupId)
  }, [groupId, fetchGroupDetail, fetchGroupItemsList, fetchGroupMembers])

  useEffect(() => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      tg.BackButton.show()
      tg.BackButton.onClick(() => setView({ type: 'groups-list' }))
      return () => { tg.BackButton.hide(); tg.BackButton.offClick(() => setView({ type: 'groups-list' })) }
    }
  }, [setView])

  const checkedCount = items.filter((i) => i.checked).length
  const total = items.length
  const progress = total > 0 ? (checkedCount / total) * 100 : 0

  function copyCode() {
    if (!group) return
    navigator.clipboard.writeText(group.invite_code).then(() => toast.success('Copiat!')).catch(() => {})
  }

  async function handleAdd() {
    const item = itemInput.trim()
    if (!item) return
    setAdding(true)
    try {
      await addGroupItemAction(groupId, item, qtyInput.trim() || '1')
      setItemInput('')
      setQtyInput('')
      setShowSheet(false)
    } finally {
      setAdding(false)
    }
  }

  async function handleRename() {
    const name = renameInput.trim()
    if (!name || !group) return
    setRenaming(true)
    try {
      await renameExistingGroup(groupId, name)
      setRenameInput('')
    } finally {
      setRenaming(false)
    }
  }

  async function handleDeleteGroup() {
    try {
      await deleteExistingGroup(groupId)
      setView({ type: 'groups-list' })
    } catch { /* handled in store */ }
  }

  async function handleLeave() {
    try {
      await leaveExistingGroup(groupId)
      setView({ type: 'groups-list' })
    } catch { /* handled in store */ }
  }

  function getInitials(member: { first_name: string | null; username: string | null }) {
    const name = member.first_name || member.username || '?'
    return name.charAt(0).toUpperCase()
  }

  return (
    <div className="flex min-h-full flex-col">
      {/* Header */}
      <div
        className="sticky top-0 z-10 px-4 pb-3 pt-6"
        style={{ backdropFilter: 'blur(24px)', WebkitBackdropFilter: 'blur(24px)' }}
      >
        <div className="flex items-center gap-3">
          <button
            onClick={() => setView({ type: 'groups-list' })}
            className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-muted-foreground transition-colors hover:text-foreground"
            style={{ background: 'hsl(0 0% 100% / 0.06)' }}
          >
            <ArrowLeft size={16} />
          </button>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <h1 className="truncate text-lg font-bold text-foreground">
                {group?.name || 'Grup'}
              </h1>
              {isOwner && <Crown size={14} className="flex-shrink-0 text-accent" />}
            </div>
          </div>
        </div>

        {/* Invite code */}
        {group && (
          <div className="mt-2 flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Cod:</span>
            <button
              onClick={copyCode}
              className="flex items-center gap-1.5 rounded-lg px-2 py-1 font-mono text-xs transition-colors hover:text-primary"
              style={{ background: 'hsl(var(--muted))', color: 'hsl(var(--muted-foreground))' }}
            >
              <Copy size={11} />
              {group.invite_code}
            </button>
          </div>
        )}

        {/* Progress bar */}
        {total > 0 && (
          <div className="mt-3">
            <div className="mb-1 flex justify-between text-xs text-muted-foreground">
              <span>{checkedCount} din {total}</span>
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
              onClick={() => clearGroupChecked(groupId)}
              className="flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-medium text-muted-foreground"
              style={{ background: 'hsl(0 0% 100% / 0.06)', border: '1px solid hsl(0 0% 100% / 0.08)' }}
            >
              <Sparkles size={13} />
              Curăță
            </button>
          )}
          <button
            onClick={() => setShowSheet(true)}
            className="ml-auto flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-semibold text-background"
            style={{ background: 'hsl(var(--primary))', boxShadow: '0 0 12px hsl(185 100% 50% / 0.4)' }}
          >
            <Plus size={14} />
            Adaugă
          </button>
        </div>
      </div>

      {/* Items list */}
      <div className="flex-1 px-4">
        {groupItemsLoading[groupId] && items.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 size={28} className="animate-spin text-primary" />
          </div>
        ) : items.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center py-12 text-center"
          >
            <div className="mb-3 text-3xl">🛒</div>
            <p className="text-sm font-medium text-muted-foreground">Lista grupului e goală</p>
          </motion.div>
        ) : (
          <motion.ul variants={listVariants} initial="hidden" animate="visible" className="flex flex-col gap-2">
            <AnimatePresence mode="popLayout">
              {items.map((item) => (
                <motion.li
                  key={item.id}
                  variants={rowVariants}
                  exit="exit"
                  layout
                  className="glass-card group flex items-center gap-3 rounded-2xl p-4"
                >
                  <button
                    onClick={() => toggleGroupItemAction(groupId, item.id)}
                    className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full border-2 transition-all duration-200"
                    style={{
                      borderColor: item.checked ? 'hsl(var(--primary))' : 'hsl(var(--border))',
                      background: item.checked ? 'hsl(var(--primary))' : 'transparent',
                    }}
                  >
                    {item.checked && <Check size={12} className="text-background" strokeWidth={3} />}
                  </button>

                  <div className={`flex-1 min-w-0 transition-opacity duration-200 ${item.checked ? 'opacity-40' : ''}`}>
                    <span className={`block truncate font-medium text-foreground ${item.checked ? 'line-through' : ''}`}>
                      {item.item}
                    </span>
                    <div className="mt-0.5 flex items-center gap-2">
                      {item.quantity && item.quantity !== '1' && (
                        <span
                          className="inline-block rounded-md px-1.5 py-0.5 text-xs font-medium"
                          style={{ background: 'hsl(var(--muted))', color: 'hsl(var(--muted-foreground))' }}
                        >
                          ×{item.quantity}
                        </span>
                      )}
                      <span className="text-xs text-muted-foreground opacity-60">{item.added_by_name}</span>
                    </div>
                  </div>

                  <button
                    onClick={() => deleteGroupItemAction(groupId, item.id)}
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

        {/* Members panel */}
        <div className="mt-4">
          <button
            onClick={() => setShowMembers((v) => !v)}
            className="glass-card flex w-full items-center justify-between rounded-2xl p-4 transition-colors"
          >
            <div className="flex items-center gap-2 text-sm font-medium text-foreground">
              <Users size={16} className="text-secondary" />
              Membri ({members.length})
            </div>
            <motion.div animate={{ rotate: showMembers ? 180 : 0 }} transition={{ duration: 0.2 }}>
              <ChevronDown size={16} className="text-muted-foreground" />
            </motion.div>
          </button>

          <AnimatePresence>
            {showMembers && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.25 }}
                className="overflow-hidden"
              >
                <div className="flex flex-col gap-2 pt-2">
                  {members.map((member) => {
                    const isMe = member.user_id === currentUser?.user_id
                    const isMemberOwner = group?.owner_id === member.user_id
                    const displayName = member.first_name || member.username || `User ${member.user_id}`
                    return (
                      <div
                        key={member.user_id}
                        className="glass-card flex items-center gap-3 rounded-2xl px-4 py-3"
                      >
                        {/* Avatar */}
                        <div
                          className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full text-sm font-bold text-background"
                          style={{ background: isMemberOwner ? 'hsl(40 100% 50%)' : 'hsl(275 99% 53%)' }}
                        >
                          {getInitials(member)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <span className="truncate text-sm font-medium text-foreground">
                            {displayName}
                            {isMe && <span className="ml-1 text-muted-foreground">(tu)</span>}
                          </span>
                          {isMemberOwner && (
                            <div className="flex items-center gap-1 text-xs text-accent">
                              <Crown size={10} />
                              Admin
                            </div>
                          )}
                        </div>
                        {isOwner && !isMe && (
                          <button
                            onClick={() => kickGroupMember(groupId, member.user_id)}
                            className="rounded-lg px-2.5 py-1 text-xs font-medium text-destructive transition-colors hover:bg-destructive/10"
                            style={{ border: '1px solid hsl(var(--destructive) / 0.3)' }}
                          >
                            Elimină
                          </button>
                        )}
                      </div>
                    )
                  })}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Admin panel (owner only) */}
        {isOwner && (
          <div className="mt-3">
            <button
              onClick={() => setShowAdmin((v) => !v)}
              className="glass-card flex w-full items-center justify-between rounded-2xl p-4 transition-colors"
            >
              <div className="flex items-center gap-2 text-sm font-medium text-foreground">
                <Settings size={16} className="text-accent" />
                Admin grup
              </div>
              <motion.div animate={{ rotate: showAdmin ? 180 : 0 }} transition={{ duration: 0.2 }}>
                <ChevronDown size={16} className="text-muted-foreground" />
              </motion.div>
            </button>

            <AnimatePresence>
              {showAdmin && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.25 }}
                  className="overflow-hidden"
                >
                  <div className="flex flex-col gap-3 pt-2">
                    {/* Rename */}
                    <div className="glass-card rounded-2xl p-4">
                      <p className="mb-2 text-xs font-medium text-muted-foreground">Redenumire grup</p>
                      <div className="flex gap-2">
                        <input
                          placeholder={group?.name}
                          value={renameInput}
                          onChange={(e) => setRenameInput(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && handleRename()}
                          className="flex-1 rounded-xl border px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground"
                          style={{ background: 'hsl(0 0% 100% / 0.05)', borderColor: 'hsl(var(--border))' }}
                        />
                        <button
                          onClick={handleRename}
                          disabled={!renameInput.trim() || renaming}
                          className="rounded-xl px-3 py-2 text-sm font-medium text-background disabled:opacity-50"
                          style={{ background: 'hsl(var(--primary))' }}
                        >
                          {renaming ? <Loader2 size={14} className="animate-spin" /> : 'OK'}
                        </button>
                      </div>
                    </div>

                    {/* Delete group */}
                    {!confirmDelete ? (
                      <button
                        onClick={() => setConfirmDelete(true)}
                        className="flex items-center gap-2 rounded-2xl p-4 text-sm font-medium text-destructive transition-colors"
                        style={{ background: 'hsl(0 84% 60% / 0.08)', border: '1px solid hsl(0 84% 60% / 0.2)' }}
                      >
                        <Trash2 size={15} />
                        Șterge grupul
                      </button>
                    ) : (
                      <div className="rounded-2xl p-4" style={{ background: 'hsl(0 84% 60% / 0.08)', border: '1px solid hsl(0 84% 60% / 0.2)' }}>
                        <p className="mb-3 text-sm text-foreground">Ești sigur că vrei să ștergi grupul?</p>
                        <div className="flex gap-2">
                          <button
                            onClick={handleDeleteGroup}
                            className="flex-1 rounded-xl py-2 text-sm font-semibold text-white"
                            style={{ background: 'hsl(var(--destructive))' }}
                          >
                            Da, șterge
                          </button>
                          <button
                            onClick={() => setConfirmDelete(false)}
                            className="flex-1 rounded-xl py-2 text-sm font-medium text-muted-foreground"
                            style={{ background: 'hsl(0 0% 100% / 0.06)' }}
                          >
                            Anulează
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        {/* Leave group (non-owner) */}
        {!isOwner && (
          <div className="mt-3 pb-4">
            <button
              onClick={handleLeave}
              className="flex w-full items-center justify-center gap-2 rounded-2xl p-4 text-sm font-medium text-muted-foreground transition-colors"
              style={{ background: 'hsl(0 0% 100% / 0.04)', border: '1px solid hsl(0 0% 100% / 0.08)' }}
            >
              <LogOut size={15} />
              Ieși din grup
            </button>
          </div>
        )}

        <div className="h-4" />
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
                  placeholder="Nume produs"
                  value={itemInput}
                  onChange={(e) => setItemInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
                  className="w-full rounded-xl border px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground"
                  style={{ background: 'hsl(0 0% 100% / 0.05)', borderColor: 'hsl(var(--border))' }}
                />
                <input
                  placeholder="Cantitate (opțional)"
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
                  style={{ background: 'hsl(var(--primary))', boxShadow: '0 0 16px hsl(185 100% 50% / 0.35)' }}
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
