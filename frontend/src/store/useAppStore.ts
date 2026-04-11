import { create } from 'zustand'
import { toast } from 'sonner'
import {
  getMe,
  getPersonalList, addPersonalItem, togglePersonalItem, deletePersonalItem, clearPersonalDone,
  getGroups, createGroup, joinGroup, getGroup, renameGroup, deleteGroup, leaveGroup,
  getGroupItems, addGroupItem, toggleGroupItem, deleteGroupItem, clearGroupDone,
  getMembers, kickMember,
} from '../api'
import type { User, PersonalItem, Group, GroupItem, GroupMember } from '../api'

export type View =
  | { type: 'home' }
  | { type: 'personal-list' }
  | { type: 'groups-list' }
  | { type: 'group-detail'; groupId: number }
  | { type: 'help' }

interface AppState {
  // Navigation
  view: View
  setView: (view: View) => void

  // Current user
  currentUser: User | null
  fetchCurrentUser: () => Promise<void>

  // Personal list
  personalItems: PersonalItem[]
  personalLoading: boolean
  fetchPersonalList: () => Promise<void>
  addPersonal: (item: string, qty: string) => Promise<void>
  togglePersonal: (id: number) => Promise<void>
  deletePersonal: (id: number) => Promise<void>
  clearPersonalChecked: () => Promise<void>

  // Groups
  groups: Group[]
  groupsLoading: boolean
  fetchGroups: () => Promise<void>
  createNewGroup: (name: string) => Promise<void>
  joinExistingGroup: (code: string) => Promise<void>
  fetchGroupDetail: (gid: number) => Promise<Group | null>
  renameExistingGroup: (gid: number, name: string) => Promise<void>
  deleteExistingGroup: (gid: number) => Promise<void>
  leaveExistingGroup: (gid: number) => Promise<void>

  // Group items
  groupItems: Record<number, GroupItem[]>
  groupItemsLoading: Record<number, boolean>
  fetchGroupItemsList: (gid: number) => Promise<void>
  addGroupItemAction: (gid: number, item: string, qty: string) => Promise<void>
  toggleGroupItemAction: (gid: number, iid: number) => Promise<void>
  deleteGroupItemAction: (gid: number, iid: number) => Promise<void>
  clearGroupChecked: (gid: number) => Promise<void>

  // Group members
  groupMembers: Record<number, GroupMember[]>
  fetchGroupMembers: (gid: number) => Promise<void>
  kickGroupMember: (gid: number, uid: number) => Promise<void>
}

export const useAppStore = create<AppState>((set) => ({
  // ── Navigation ──────────────────────────────────────────────────────────
  view: { type: 'home' },
  setView: (view) => set({ view }),

  // ── Current User ────────────────────────────────────────────────────────
  currentUser: null,
  fetchCurrentUser: async () => {
    try {
      const user = await getMe()
      set({ currentUser: user })
    } catch {
      // Silently fail - not critical for startup
    }
  },

  // ── Personal List ────────────────────────────────────────────────────────
  personalItems: [],
  personalLoading: false,
  fetchPersonalList: async () => {
    set({ personalLoading: true })
    try {
      const items = await getPersonalList()
      set({ personalItems: items })
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare la încărcarea listei')
    } finally {
      set({ personalLoading: false })
    }
  },
  addPersonal: async (item, qty) => {
    try {
      const newItem = await addPersonalItem(item, qty)
      set((s) => ({ personalItems: [newItem, ...s.personalItems] }))
      toast.success('Produs adăugat!')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare la adăugare')
      throw e
    }
  },
  togglePersonal: async (id) => {
    try {
      const updated = await togglePersonalItem(id)
      set((s) => ({
        personalItems: s.personalItems.map((i) => (i.id === id ? updated : i)),
      }))
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare')
    }
  },
  deletePersonal: async (id) => {
    try {
      await deletePersonalItem(id)
      set((s) => ({ personalItems: s.personalItems.filter((i) => i.id !== id) }))
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare la ștergere')
    }
  },
  clearPersonalChecked: async () => {
    try {
      await clearPersonalDone()
      set((s) => ({ personalItems: s.personalItems.filter((i) => !i.checked) }))
      toast.success('Produsele bifate au fost șterse!')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare')
    }
  },

  // ── Groups ───────────────────────────────────────────────────────────────
  groups: [],
  groupsLoading: false,
  fetchGroups: async () => {
    set({ groupsLoading: true })
    try {
      const groups = await getGroups()
      set({ groups })
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare la încărcarea grupurilor')
    } finally {
      set({ groupsLoading: false })
    }
  },
  createNewGroup: async (name) => {
    try {
      const group = await createGroup(name)
      set((s) => ({ groups: [group, ...s.groups] }))
      toast.success(`Grupul "${name}" a fost creat!`)
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare la creare')
      throw e
    }
  },
  joinExistingGroup: async (code) => {
    try {
      const group = await joinGroup(code)
      set((s) => ({ groups: [...s.groups, group] }))
      toast.success(`Ai intrat în grupul "${group.name}"!`)
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Cod invalid')
      throw e
    }
  },
  fetchGroupDetail: async (gid) => {
    try {
      const group = await getGroup(gid)
      set((s) => ({
        groups: s.groups.some((g) => g.id === gid)
          ? s.groups.map((g) => (g.id === gid ? group : g))
          : [...s.groups, group],
      }))
      return group
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare')
      return null
    }
  },
  renameExistingGroup: async (gid, name) => {
    try {
      const updated = await renameGroup(gid, name)
      set((s) => ({ groups: s.groups.map((g) => (g.id === gid ? updated : g)) }))
      toast.success('Grupul a fost redenumit!')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare la redenumire')
      throw e
    }
  },
  deleteExistingGroup: async (gid) => {
    try {
      await deleteGroup(gid)
      set((s) => ({ groups: s.groups.filter((g) => g.id !== gid) }))
      toast.success('Grupul a fost șters!')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare la ștergere')
      throw e
    }
  },
  leaveExistingGroup: async (gid) => {
    try {
      await leaveGroup(gid)
      set((s) => ({ groups: s.groups.filter((g) => g.id !== gid) }))
      toast.success('Ai ieșit din grup!')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare')
      throw e
    }
  },

  // ── Group Items ───────────────────────────────────────────────────────────
  groupItems: {},
  groupItemsLoading: {},
  fetchGroupItemsList: async (gid) => {
    set((s) => ({ groupItemsLoading: { ...s.groupItemsLoading, [gid]: true } }))
    try {
      const items = await getGroupItems(gid)
      set((s) => ({ groupItems: { ...s.groupItems, [gid]: items } }))
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare la încărcarea produselor')
    } finally {
      set((s) => ({ groupItemsLoading: { ...s.groupItemsLoading, [gid]: false } }))
    }
  },
  addGroupItemAction: async (gid, item, qty) => {
    try {
      const newItem = await addGroupItem(gid, item, qty)
      set((s) => ({
        groupItems: {
          ...s.groupItems,
          [gid]: [newItem, ...(s.groupItems[gid] || [])],
        },
      }))
      toast.success('Produs adăugat!')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare la adăugare')
      throw e
    }
  },
  toggleGroupItemAction: async (gid, iid) => {
    try {
      const updated = await toggleGroupItem(gid, iid)
      set((s) => ({
        groupItems: {
          ...s.groupItems,
          [gid]: (s.groupItems[gid] || []).map((i) => (i.id === iid ? updated : i)),
        },
      }))
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare')
    }
  },
  deleteGroupItemAction: async (gid, iid) => {
    try {
      await deleteGroupItem(gid, iid)
      set((s) => ({
        groupItems: {
          ...s.groupItems,
          [gid]: (s.groupItems[gid] || []).filter((i) => i.id !== iid),
        },
      }))
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare la ștergere')
    }
  },
  clearGroupChecked: async (gid) => {
    try {
      await clearGroupDone(gid)
      set((s) => ({
        groupItems: {
          ...s.groupItems,
          [gid]: (s.groupItems[gid] || []).filter((i) => !i.checked),
        },
      }))
      toast.success('Produsele bifate au fost șterse!')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare')
    }
  },

  // ── Group Members ─────────────────────────────────────────────────────────
  groupMembers: {},
  fetchGroupMembers: async (gid) => {
    try {
      const members = await getMembers(gid)
      set((s) => ({ groupMembers: { ...s.groupMembers, [gid]: members } }))
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare la încărcarea membrilor')
    }
  },
  kickGroupMember: async (gid, uid) => {
    try {
      await kickMember(gid, uid)
      set((s) => ({
        groupMembers: {
          ...s.groupMembers,
          [gid]: (s.groupMembers[gid] || []).filter((m) => m.user_id !== uid),
        },
      }))
      toast.success('Membrul a fost eliminat!')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare la eliminare')
      throw e
    }
  },
}))
