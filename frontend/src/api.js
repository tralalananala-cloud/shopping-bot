/**
 * Client API pentru Shopping Bot REST API.
 *
 * Autentificare:
 *  - Producție (Telegram Mini App): trimite X-Telegram-Init-Data
 *  - Development (browser): trimite X-Dev-User-Id din localStorage
 */

const BASE = import.meta.env.VITE_API_URL || ''

function headers() {
  const h = { 'Content-Type': 'application/json' }
  const tg = window.Telegram?.WebApp
  if (tg?.initData) {
    h['X-Telegram-Init-Data'] = tg.initData
  } else {
    const devId = localStorage.getItem('dev_user_id') || '123456789'
    h['X-Dev-User-Id'] = devId
  }
  return h
}

async function req(method, path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: headers(),
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Eroare ${res.status}`)
  }
  return res.json()
}

// ── Utilizator ──────────────────────────────────────────────────────────────
export const getMe = () => req('GET', '/api/users/me')

// ── Lista personală ─────────────────────────────────────────────────────────
export const getPersonalList    = ()           => req('GET',    '/api/personal/')
export const addPersonalItem    = (item, qty)  => req('POST',   '/api/personal/', { item, quantity: qty || '1' })
export const togglePersonalItem = (id)         => req('PATCH',  `/api/personal/${id}/toggle`)
export const deletePersonalItem = (id)         => req('DELETE', `/api/personal/${id}`)
export const clearPersonalDone  = ()           => req('DELETE', '/api/personal/clear/checked')

// ── Grupuri ─────────────────────────────────────────────────────────────────
export const getGroups   = ()     => req('GET',  '/api/groups/')
export const createGroup = (name) => req('POST', '/api/groups/', { name })
export const joinGroup   = (code) => req('POST', '/api/groups/join', { invite_code: code })

export const getGroup         = (gid)       => req('GET',    `/api/groups/${gid}`)
export const renameGroup      = (gid, name) => req('PATCH',  `/api/groups/${gid}/rename`, { name })
export const deleteGroup      = (gid)       => req('DELETE', `/api/groups/${gid}`)
export const leaveGroup       = (gid)       => req('DELETE', `/api/groups/${gid}/leave`)

export const addGroupItem     = (gid, item, qty) => req('POST',   `/api/groups/${gid}/items`, { item, quantity: qty || '1' })
export const toggleGroupItem  = (gid, iid)       => req('PATCH',  `/api/groups/${gid}/items/${iid}/toggle`)
export const deleteGroupItem  = (gid, iid)       => req('DELETE', `/api/groups/${gid}/items/${iid}`)
export const clearGroupDone   = (gid)            => req('DELETE', `/api/groups/${gid}/items/clear/checked`)

export const getMembers  = (gid)        => req('GET',    `/api/groups/${gid}/members`)
export const kickMember  = (gid, uid)   => req('DELETE', `/api/groups/${gid}/members/${uid}`)
