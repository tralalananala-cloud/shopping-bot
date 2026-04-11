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

// ── Tipuri interne pentru răspunsurile API ──────────────────────────────────
interface PersonalListResponse { items: PersonalItem[]; total: number; done: number }
interface GroupsListResponse   { groups: Group[] }
interface GroupDetailResponse  { group: Group; items: GroupItem[]; total: number; done: number }
interface MembersResponse      { group_id: number; members: GroupMember[] }

// ── Utilizator ──────────────────────────────────────────────────────────────
export const getMe = () => request<User>('GET', '/api/users/me')

// ── Lista personală ─────────────────────────────────────────────────────────
// API returnează {items, total, done} — extragem doar items
export const getPersonalList    = ()                          => request<PersonalListResponse>('GET', '/api/personal/').then(r => r.items)
export const addPersonalItem    = (item: string, qty: string) => request<PersonalItem>('POST',   '/api/personal/', { item, quantity: qty || '1' })
export const togglePersonalItem = (id: number)                => request<PersonalItem>('PATCH',  `/api/personal/${id}/toggle`)
export const deletePersonalItem = (id: number)                => request<void>('DELETE', `/api/personal/${id}`)
export const clearPersonalDone  = ()                          => request<void>('DELETE', '/api/personal/clear/checked')

// ── Grupuri ─────────────────────────────────────────────────────────────────
// GET /api/groups/ returnează {groups} — extragem array-ul
export const getGroups   = ()              => request<GroupsListResponse>('GET',  '/api/groups/').then(r => r.groups)
export const createGroup = (name: string)  => request<Group>('POST', '/api/groups/', { name })
export const joinGroup   = (code: string)  => request<Group>('POST', '/api/groups/join', { invite_code: code })

// GET /api/groups/{gid} returnează {group, items, total, done}
export const getGroup      = (gid: number)               => request<GroupDetailResponse>('GET', `/api/groups/${gid}`).then(r => r.group)
export const getGroupItems = (gid: number)               => request<GroupDetailResponse>('GET', `/api/groups/${gid}`).then(r => r.items)
export const renameGroup   = (gid: number, name: string) => request<Group>('PATCH',  `/api/groups/${gid}/rename`, { name })
export const deleteGroup   = (gid: number)               => request<void>('DELETE', `/api/groups/${gid}`)
export const leaveGroup    = (gid: number)               => request<void>('DELETE', `/api/groups/${gid}/leave`)

export const addGroupItem    = (gid: number, item: string, qty: string) => request<GroupItem>('POST',   `/api/groups/${gid}/items`, { item, quantity: qty || '1' })
export const toggleGroupItem = (gid: number, iid: number)               => request<GroupItem>('PATCH',  `/api/groups/${gid}/items/${iid}/toggle`)
export const deleteGroupItem = (gid: number, iid: number)               => request<void>('DELETE', `/api/groups/${gid}/items/${iid}`)
export const clearGroupDone  = (gid: number)                            => request<void>('DELETE', `/api/groups/${gid}/items/clear/checked`)

// GET /api/groups/{gid}/members returnează {group_id, members}
export const getMembers = (gid: number)              => request<MembersResponse>('GET', `/api/groups/${gid}/members`).then(r => r.members)
export const kickMember = (gid: number, uid: number) => request<void>('DELETE', `/api/groups/${gid}/members/${uid}`)
