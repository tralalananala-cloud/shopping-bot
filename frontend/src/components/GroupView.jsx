import { useState, useEffect, useCallback } from 'react'
import Header       from './Header.jsx'
import ProgressBar  from './ProgressBar.jsx'
import Spinner      from './Spinner.jsx'
import AddItemSheet from './AddItemSheet.jsx'
import * as api     from '../api.js'

export default function GroupView({ nav, group: groupInit }) {
  const [data,      setData]      = useState(null)   // { group, items, total, done }
  const [loading,   setLoading]   = useState(true)
  const [adding,    setAdding]    = useState(false)
  const [showAdd,   setShowAdd]   = useState(false)
  const [showAdmin, setShowAdmin] = useState(false)
  const [renaming,  setRenaming]  = useState(false)
  const [newName,   setNewName]   = useState('')
  const [meId,      setMeId]      = useState(null)

  const groupId = groupInit?.id

  const fetchData = useCallback(async () => {
    try {
      const [groupData, me] = await Promise.all([
        api.getGroup(groupId),
        api.getMe(),
      ])
      setData(groupData)
      setMeId(me.user_id)
    } catch (e) {
      nav.toast(e.message, 'error')
    } finally {
      setLoading(false)
    }
  }, [groupId, nav])

  useEffect(() => { fetchData() }, [fetchData])

  async function handleAdd(item, quantity) {
    setAdding(true)
    try {
      const newItem = await api.addGroupItem(groupId, item, quantity)
      setData(prev => ({
        ...prev,
        items: [newItem, ...prev.items],
        total: prev.total + 1,
      }))
      setShowAdd(false)
      nav.toast('Produs adăugat')
    } catch (e) {
      nav.toast(e.message, 'error')
    } finally {
      setAdding(false)
    }
  }

  async function handleToggle(itemId) {
    try {
      const updated = await api.toggleGroupItem(groupId, itemId)
      setData(prev => {
        const items = prev.items.map(i => i.id === itemId ? updated : i)
        const done  = items.filter(i => i.checked).length
        return { ...prev, items, done }
      })
    } catch (e) {
      nav.toast(e.message, 'error')
    }
  }

  async function handleDelete(itemId) {
    try {
      await api.deleteGroupItem(groupId, itemId)
      setData(prev => {
        const items = prev.items.filter(i => i.id !== itemId)
        const done  = items.filter(i => i.checked).length
        return { ...prev, items, total: items.length, done }
      })
    } catch (e) {
      nav.toast(e.message, 'error')
    }
  }

  async function handleClear() {
    try {
      const res = await api.clearGroupDone(groupId)
      setData(prev => {
        const items = prev.items.filter(i => !i.checked)
        return { ...prev, items, total: items.length, done: 0 }
      })
      nav.toast(`${res.count} produse șterse`)
    } catch (e) {
      nav.toast(e.message, 'error')
    }
  }

  async function handleLeave() {
    if (!confirm('Ești sigur că vrei să ieși din acest grup?')) return
    try {
      await api.leaveGroup(groupId)
      nav.toast('Ai ieșit din grup')
      nav.pop()
    } catch (e) {
      nav.toast(e.message, 'error')
    }
  }

  async function handleRename(e) {
    e.preventDefault()
    if (!newName.trim()) return
    try {
      const updated = await api.renameGroup(groupId, newName.trim())
      setData(prev => ({ ...prev, group: updated }))
      setRenaming(false)
      nav.toast('Grup redenumit')
    } catch (e) {
      nav.toast(e.message, 'error')
    }
  }

  async function handleDeleteGroup() {
    if (!confirm(`Ștergi grupul "${data.group.name}"? Acțiunea este ireversibilă.`)) return
    try {
      await api.deleteGroup(groupId)
      nav.toast('Grup șters')
      nav.pop()
    } catch (e) {
      nav.toast(e.message, 'error')
    }
  }

  if (loading) return <div className="min-h-screen flex flex-col"><Header title="Grup" onBack={nav.pop} /><Spinner /></div>
  if (!data)   return null

  const { group, items, done } = data
  const isOwner   = meId === group.owner_id
  const hasDone   = done > 0
  const unchecked = items.filter(i => !i.checked)
  const checked   = items.filter(i =>  i.checked)

  return (
    <div className="flex flex-col min-h-screen animate-fade-in">
      <Header
        title={`👥 ${group.name}`}
        onBack={nav.pop}
        action={
          <div className="flex gap-1">
            {hasDone && (
              <button onClick={handleClear} className="text-xs text-red-500 font-medium px-2 py-1">
                Șterge bifate
              </button>
            )}
            <button
              onClick={() => nav.push('members', group)}
              className="text-tg-hint text-sm px-2 py-1"
              title="Membri"
            >
              👤
            </button>
            {isOwner && (
              <button
                onClick={() => setShowAdmin(s => !s)}
                className="text-tg-hint text-sm px-2 py-1"
                title="Admin"
              >
                ⚙️
              </button>
            )}
          </div>
        }
      />

      {/* Banner admin */}
      {isOwner && showAdmin && (
        <div className="mx-4 mt-3 bg-tg-bg2 rounded-2xl p-4 flex flex-col gap-3 animate-slide-up">
          <p className="text-xs font-semibold text-tg-hint uppercase tracking-wide">Administrare grup</p>

          {/* Cod invitație */}
          <div className="flex items-center justify-between">
            <span className="text-sm">Cod invitație:</span>
            <span
              className="font-mono bg-tg-bg px-3 py-1 rounded-lg text-sm cursor-pointer active:opacity-70"
              onClick={() => { navigator.clipboard?.writeText(group.invite_code); nav.toast('Cod copiat!') }}
            >
              {group.invite_code} 📋
            </span>
          </div>

          {/* Redenumire */}
          {renaming ? (
            <form onSubmit={handleRename} className="flex gap-2">
              <input
                autoFocus
                value={newName}
                onChange={e => setNewName(e.target.value)}
                placeholder="Nume nou"
                maxLength={50}
                className="flex-1 bg-tg-bg rounded-xl px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[var(--tg-btn)]"
              />
              <button type="submit" className="text-sm font-semibold text-[var(--tg-btn)] px-2">Salvează</button>
              <button type="button" onClick={() => setRenaming(false)} className="text-sm text-tg-hint px-2">Anulează</button>
            </form>
          ) : (
            <button
              onClick={() => { setNewName(group.name); setRenaming(true) }}
              className="text-left text-sm text-[var(--tg-btn)] font-medium"
            >
              ✏️ Redenumește grupul
            </button>
          )}

          {/* Ștergere grup */}
          <button onClick={handleDeleteGroup} className="text-left text-sm text-red-500 font-medium">
            🗑 Șterge grupul
          </button>
        </div>
      )}

      <div className="flex-1 overflow-y-auto scroll-hidden px-4 pb-28">
        {/* Progress bar */}
        {items.length > 0 && (
          <div className="py-3">
            <ProgressBar done={done} total={items.length} />
          </div>
        )}

        {/* Empty state */}
        {items.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="text-5xl mb-4">📭</div>
            <p className="font-semibold">Lista grupului e goală</p>
            <p className="text-sm text-tg-hint mt-1">Apasă + pentru a adăuga primul produs</p>
          </div>
        )}

        {/* Produse necumpărate */}
        {unchecked.length > 0 && (
          <div className="flex flex-col gap-1 mt-1">
            {unchecked.map(item => (
              <GroupItemRow
                key={item.id}
                item={item}
                meId={meId}
                isOwner={isOwner}
                onToggle={() => handleToggle(item.id)}
                onDelete={() => handleDelete(item.id)}
              />
            ))}
          </div>
        )}

        {/* Separator */}
        {unchecked.length > 0 && checked.length > 0 && (
          <p className="text-xs text-tg-hint mt-4 mb-1 px-1">Cumpărate</p>
        )}

        {/* Produse cumpărate */}
        {checked.length > 0 && (
          <div className="flex flex-col gap-1">
            {checked.map(item => (
              <GroupItemRow
                key={item.id}
                item={item}
                meId={meId}
                isOwner={isOwner}
                onToggle={() => handleToggle(item.id)}
                onDelete={() => handleDelete(item.id)}
              />
            ))}
          </div>
        )}
      </div>

      {/* FAB Adaugă */}
      <button
        onClick={() => setShowAdd(true)}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-[var(--tg-btn)] text-[var(--tg-btn-text)] text-3xl shadow-lg flex items-center justify-center active:scale-95 transition-transform z-30"
      >
        +
      </button>

      {/* Buton ieșire (non-owner) */}
      {!isOwner && (
        <button
          onClick={handleLeave}
          className="fixed bottom-6 left-6 text-xs text-tg-hint font-medium py-2 px-3 bg-tg-bg2 rounded-xl"
        >
          Ieși din grup
        </button>
      )}

      {showAdd && (
        <AddItemSheet
          loading={adding}
          onAdd={handleAdd}
          onClose={() => setShowAdd(false)}
        />
      )}
    </div>
  )
}

function GroupItemRow({ item, meId, isOwner, onToggle, onDelete }) {
  const canDelete = isOwner || item.added_by === meId

  return (
    <div className="flex items-center gap-3 bg-tg-bg2 rounded-xl px-3 py-3 group">
      {/* Checkbox */}
      <button
        onClick={onToggle}
        className={`w-6 h-6 rounded-full border-2 flex items-center justify-center shrink-0 transition ${
          item.checked ? 'bg-[var(--tg-btn)] border-[var(--tg-btn)]' : 'border-tg-hint'
        }`}
      >
        {item.checked && (
          <svg className="w-3 h-3 text-[var(--tg-btn-text)]" viewBox="0 0 12 12" fill="none">
            <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        )}
      </button>

      {/* Nume + cantitate + adăugător */}
      <div className="flex-1 min-w-0">
        <span className={`text-sm font-medium ${item.checked ? 'line-through text-tg-hint' : ''}`}>
          {item.item}
        </span>
        {item.quantity !== '1' && (
          <span className="ml-1.5 text-xs text-tg-hint">×{item.quantity}</span>
        )}
        <p className="text-xs text-tg-hint mt-0.5 truncate">{item.added_by_name}</p>
      </div>

      {/* Buton ștergere */}
      {canDelete && (
        <button
          onClick={onDelete}
          className="text-tg-hint hover:text-red-500 transition p-1 opacity-0 group-hover:opacity-100 focus:opacity-100"
        >
          <svg className="w-4 h-4" viewBox="0 0 16 16" fill="none">
            <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </button>
      )}
    </div>
  )
}
