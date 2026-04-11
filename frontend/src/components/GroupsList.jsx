import { useState, useEffect, useCallback } from 'react'
import Header  from './Header.jsx'
import Spinner from './Spinner.jsx'
import * as api from '../api.js'

export default function GroupsList({ nav }) {
  const [groups,  setGroups]  = useState([])
  const [loading, setLoading] = useState(true)
  const [modal,   setModal]   = useState(null) // null | 'create' | 'join'
  const [text,    setText]    = useState('')
  const [saving,  setSaving]  = useState(false)

  const fetchGroups = useCallback(async () => {
    try {
      const data = await api.getGroups()
      setGroups(data.groups)
    } catch (e) {
      nav.toast(e.message, 'error')
    } finally {
      setLoading(false)
    }
  }, [nav])

  useEffect(() => { fetchGroups() }, [fetchGroups])

  async function handleCreate(e) {
    e.preventDefault()
    if (!text.trim()) return
    setSaving(true)
    try {
      const group = await api.createGroup(text.trim())
      setGroups(prev => [group, ...prev])
      setModal(null)
      setText('')
      nav.toast('Grup creat!')
    } catch (err) {
      nav.toast(err.message, 'error')
    } finally {
      setSaving(false)
    }
  }

  async function handleJoin(e) {
    e.preventDefault()
    if (!text.trim()) return
    setSaving(true)
    try {
      const group = await api.joinGroup(text.trim().toUpperCase())
      setGroups(prev => prev.find(g => g.id === group.id) ? prev : [group, ...prev])
      setModal(null)
      setText('')
      nav.toast(`Te-ai alăturat grupului "${group.name}"`)
    } catch (err) {
      nav.toast(err.message, 'error')
    } finally {
      setSaving(false)
    }
  }

  function openGroup(group) {
    nav.push('group', group)
  }

  return (
    <div className="flex flex-col min-h-screen animate-fade-in">
      <Header title="👥 Grupuri" onBack={nav.pop} />

      {loading ? (
        <Spinner />
      ) : (
        <div className="flex-1 overflow-y-auto scroll-hidden px-4 pb-28">

          {/* Empty state */}
          {groups.length === 0 && (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <div className="text-5xl mb-4">👥</div>
              <p className="font-semibold">Niciun grup</p>
              <p className="text-sm text-tg-hint mt-1">Creează unul sau alătură-te cu un cod</p>
            </div>
          )}

          {/* Lista grupuri */}
          <div className="flex flex-col gap-2 mt-3">
            {groups.map(g => (
              <button
                key={g.id}
                onClick={() => openGroup(g)}
                className="flex items-center gap-4 bg-tg-bg2 rounded-2xl px-4 py-3.5 text-left active:scale-[0.98] transition-transform"
              >
                <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-violet-500 to-purple-400 flex items-center justify-center text-xl text-white shadow">
                  👥
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-sm truncate">{g.name}</p>
                  <p className="text-xs text-tg-hint mt-0.5">{g.member_count} membri</p>
                </div>
                <div className="text-xs font-mono text-tg-hint bg-tg-bg px-2 py-1 rounded-lg">
                  {g.invite_code}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Butoane fixe jos */}
      <div className="fixed bottom-0 left-0 right-0 p-4 flex gap-3 bg-tg-bg border-t border-tg-bg2">
        <button
          onClick={() => { setModal('join'); setText('') }}
          className="flex-1 py-3 rounded-xl bg-tg-bg2 text-sm font-semibold active:scale-95 transition-transform"
        >
          🔗 Alătură-te
        </button>
        <button
          onClick={() => { setModal('create'); setText('') }}
          className="flex-1 py-3 rounded-xl bg-[var(--tg-btn)] text-[var(--tg-btn-text)] text-sm font-semibold active:scale-95 transition-transform"
        >
          ➕ Grup nou
        </button>
      </div>

      {/* Modal creare / alăturare */}
      {modal && (
        <>
          <div className="fixed inset-0 bg-black/40 z-40 animate-fade-in" onClick={() => setModal(null)} />
          <div className="fixed bottom-0 left-0 right-0 z-50 bg-tg-bg rounded-t-2xl p-5 pb-10 animate-slide-up shadow-2xl">
            <div className="w-10 h-1 bg-tg-bg2 rounded-full mx-auto mb-5" />
            <h2 className="font-bold text-base mb-4">
              {modal === 'create' ? '➕ Grup nou' : '🔗 Alătură-te la un grup'}
            </h2>
            <form onSubmit={modal === 'create' ? handleCreate : handleJoin} className="flex gap-2">
              <input
                autoFocus
                value={text}
                onChange={e => setText(e.target.value)}
                placeholder={modal === 'create' ? 'Numele grupului' : 'Cod invitație (ex: AB3X7Z)'}
                maxLength={modal === 'create' ? 50 : 6}
                className="flex-1 bg-tg-bg2 rounded-xl px-4 py-3 text-sm text-tg-text placeholder:text-tg-hint outline-none focus:ring-2 focus:ring-[var(--tg-btn)]"
                disabled={saving}
              />
              <button
                type="submit"
                disabled={!text.trim() || saving}
                className="bg-[var(--tg-btn)] text-[var(--tg-btn-text)] px-5 rounded-xl font-semibold text-sm disabled:opacity-40 transition"
              >
                {saving ? '...' : '›'}
              </button>
            </form>
          </div>
        </>
      )}
    </div>
  )
}
