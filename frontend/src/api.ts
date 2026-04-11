/**
 * Client API pentru Shopping Bot REST API.
 *
 * Autentificare:
 *  - Producție (Telegram Mini App): trimite X-Telegram-Init-Data
 *  - Development (browser): trimite X-Dev-User-Id: 123456789
 */

export interface PersonalItem {
  id: number;
  user_id: number;
  item: string;
  quantity: string;
  checked: boolean;
  created_at: string;
}

export interface Group {
  id: number;
  name: string;
  owner_id: number;
  invite_code: string;
  created_at: string;
  member_count?: number;
}

export interface GroupItem {
  id: number;
  group_id: number;
  item: string;
  quantity: string;
  checked: boolean;
  added_by: number;
  added_by_name: string;
  created_at: string;
}

export interface GroupMember {
  user_id: number;
  username: string | null;
  first_name: string | null;
  joined_at: string;
  is_owner: boolean;
}

export interface User {
  user_id: number;
  username: string | null;
  first_name: string | null;
  created_at: string;
}

const BASE_URL = import.meta.env.VITE_API_URL || ''

function getHeaders(): Record<string, string> {
  const h: Record<string, string> = { 'Content-Type': 'application/json' }
  const tg = window.Telegram?.WebApp
  if (tg?.initData) {
    h['X-Telegram-Init-Data'] = tg.initData
  } else {
    const devId = localStorage.getItem('dev_user_id') || '123456789'
    h['X-Dev-User-Id'] = devId
  }
  return h
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: getHeaders(),
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({})) as { detail?: string }
    throw new Error(err.detail || `Eroare ${res.status}`)
  }
  return res.json() as Promise<T>
}

// ── Utilizator ──────────────────────────────────────────────────────────────
export const getMe = () => request<User>('GET', '/api/users/me')

// ── Lista personală ─────────────────────────────────────────────────────────
export const getPersonalList    = ()                    => request<PersonalItem[]>('GET',    '/api/personal/')
export const addPersonalItem    = (item: string, qty: string) => request<PersonalItem>('POST',   '/api/personal/', { item, quantity: qty || '1' })
export const togglePersonalItem = (id: number)          => request<PersonalItem>('PATCH',  `/api/personal/${id}/toggle`)
export const deletePersonalItem = (id: number)          => request<void>('DELETE', `/api/personal/${id}`)
export const clearPersonalDone  = ()                    => request<void>('DELETE', '/api/personal/clear/checked')

// ── Grupuri ─────────────────────────────────────────────────────────────────
export const getGroups   = ()              => request<Group[]>('GET',  '/api/groups/')
export const createGroup = (name: string)  => request<Group>('POST', '/api/groups/', { name })
export const joinGroup   = (code: string)  => request<Group>('POST', '/api/groups/join', { invite_code: code })

export const getGroup    = (gid: number)              => request<Group>('GET',    `/api/groups/${gid}`)
export const renameGroup = (gid: number, name: string) => request<Group>('PATCH',  `/api/groups/${gid}/rename`, { name })
export const deleteGroup = (gid: number)              => request<void>('DELETE', `/api/groups/${gid}`)
export const leaveGroup  = (gid: number)              => request<void>('DELETE', `/api/groups/${gid}/leave`)

export const getGroupItems   = (gid: number)                            => request<GroupItem[]>('GET',    `/api/groups/${gid}/items`)
export const addGroupItem    = (gid: number, item: string, qty: string) => request<GroupItem>('POST',   `/api/groups/${gid}/items`, { item, quantity: qty || '1' })
export const toggleGroupItem = (gid: number, iid: number)               => request<GroupItem>('PATCH',  `/api/groups/${gid}/items/${iid}/toggle`)
export const deleteGroupItem = (gid: number, iid: number)               => request<void>('DELETE', `/api/groups/${gid}/items/${iid}`)
export const clearGroupDone  = (gid: number)                            => request<void>('DELETE', `/api/groups/${gid}/items/clear/checked`)

export const getMembers = (gid: number)              => request<GroupMember[]>('GET',    `/api/groups/${gid}/members`)
export const kickMember = (gid: number, uid: number) => request<void>('DELETE', `/api/groups/${gid}/members/${uid}`)
