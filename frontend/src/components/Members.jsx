import { useState, useEffect, useCallback } from 'react'
import Header  from './Header.jsx'
import Spinner from './Spinner.jsx'
import * as api from '../api.js'

export default function Members({ nav, group }) {
  const [members, setMembers] = useState([])
  const [loading, setLoading] = useState(true)
  const [meId,    setMeId]    = useState(null)

  const fetchMembers = useCallback(async () => {
    try {
      const [data, me] = await Promise.all([
        api.getMembers(group.id),
        api.getMe(),
      ])
      setMembers(data.members)
      setMeId(me.user_id)
    } catch (e) {
      nav.toast(e.message, 'error')
    } finally {
      setLoading(false)
    }
  }, [group.id, nav])

  useEffect(() => { fetchMembers() }, [fetchMembers])

  async function handleKick(userId, name) {
    if (!confirm(`Elimini "${name}" din grup?`)) return
    try {
      await api.kickMember(group.id, userId)
      setMembers(prev => prev.filter(m => m.user_id !== userId))
      nav.toast(`${name} a fost eliminat`)
    } catch (e) {
      nav.toast(e.message, 'error')
    }
  }

  const isOwner = meId === group.owner_id

  return (
    <div className="flex flex-col min-h-screen animate-fade-in">
      <Header title={`Membri — ${group.name}`} onBack={nav.pop} />

      {loading ? (
        <Spinner />
      ) : (
        <div className="flex-1 overflow-y-auto scroll-hidden px-4 pb-8 mt-3">
          {/* Cod invitație */}
          <div
            className="flex items-center justify-between bg-tg-bg2 rounded-2xl px-4 py-3 mb-4 cursor-pointer active:opacity-70"
            onClick={() => {
              navigator.clipboard?.writeText(group.invite_code)
              nav.toast('Cod de invitație copiat!')
            }}
          >
            <div>
              <p className="text-xs text-tg-hint">Cod invitație</p>
              <p className="font-mono font-bold text-lg tracking-widest">{group.invite_code}</p>
            </div>
            <span className="text-2xl">📋</span>
          </div>

          {/* Lista membri */}
          <p className="text-xs text-tg-hint uppercase tracking-wide font-semibold mb-2 px-1">
            {members.length} membri
          </p>
          <div className="flex flex-col gap-2">
            {members.map(m => {
              const name = m.first_name || m.username || `User #${m.user_id}`
              const isMe = m.user_id === meId
              return (
                <div
                  key={m.user_id}
                  className="flex items-center gap-3 bg-tg-bg2 rounded-xl px-4 py-3"
                >
                  {/* Avatar */}
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-violet-500 flex items-center justify-center text-white font-bold text-sm shrink-0">
                    {name[0]?.toUpperCase() || '?'}
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-sm truncate">
                      {name}
                      {isMe && <span className="text-xs text-tg-hint font-normal ml-1">(tu)</span>}
                    </p>
                    {m.username && (
                      <p className="text-xs text-tg-hint">@{m.username}</p>
                    )}
                  </div>

                  {/* Embleme + kick */}
                  <div className="flex items-center gap-2 shrink-0">
                    {m.is_owner && <span className="text-base" title="Owner">👑</span>}
                    {isOwner && !m.is_owner && !isMe && (
                      <button
                        onClick={() => handleKick(m.user_id, name)}
                        className="text-xs text-red-500 font-medium bg-red-500/10 px-2 py-1 rounded-lg active:opacity-70"
                      >
                        Elimină
                      </button>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
