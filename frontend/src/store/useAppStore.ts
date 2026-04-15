import { create } from 'zustand'
import { toast } from 'sonner'
import type { Priority } from '../api'
import {
  getMe, getFeed,
  getPersonalList, addPersonalItem, togglePersonalItem, deletePersonalItem, clearPersonalDone,
  getGroups, createGroup, joinGroup, getGroup, renameGroup, deleteGroup, leaveGroup,
  getGroupItems, addGroupItem, toggleGroupItem, deleteGroupItem, clearGroupDone,
  getMembers, kickMember,
} from '../api'
import type { User, PersonalItem, Group, GroupItem, GroupMember, FeedItem } from '../api'

export type View =
  | { type: 'feed' }
  | { type: 'personal-list' }
  | { type: 'groups-list' }
  | { type: 'group-detail'; groupId: number }
  | { type: 'completed' }
  | { type: 'help' }

interface AppState {
  // Navigation
  view: View
  setView: (view: View) => void

  // Current user
  currentUser: User | null
  fetchCurrentUser: () => Promise<void>

  // Feed
  feedItems: FeedItem[]
  feedLoading: boolean
  fetchFeed: () => Promise<void>
  toggleFeedItem: (item: FeedItem) => Promise<void>

  // Personal list
  personalItems: PersonalItem[]
  personalLoading: boolean
  fetchPersonalList: () => Promise<void>
  addPersonal: (item: string, qty: string, priority: Priority) => Promise<void>
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
  addGroupItemAction: (gid: number, item: string, qty: string, priority: Priority) => Promise<void>
  toggleGroupItemAction: (gid: number, iid: number) => Promise<void>
  deleteGroupItemAction: (gid: number, iid: number) => Promise<void>
  clearGroupChecked: (gid: number) => Promise<void>

  // Group members
  groupMembers: Record<number, GroupMember[]>
  fetchGroupMembers: (gid: number) => Promise<void>
  kickGroupMember: (gid: number, uid: number) => Promise<void>
}

export const useAppStore = create<AppState>((set, get) => ({
  // ── Navigation ──────────────────────────────────────────────────────────────
  view: { type: 'feed' },
  setView: (view) => set({ view }),

  // ── Current User ────────────────────────────────────────────────────────────
  currentUser: null,
  fetchCurrentUser: async () => {
    try {
      const user = await getMe()
      set({ currentUser: user })
    } catch {
      // Silently fail
    }
  },

  // ── Feed ─────────────────────────────────────────────────────────────────────
  feedItems: [],
  feedLoading: false,
  fetchFeed: async () => {
    set({ feedLoading: true })
    try {
      const items = await getFeed()
      set({ feedItems: Array.isArray(items) ? items : [] })
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare la încărcarea feed-ului')
    } finally {
      set({ feedLoading: false })
    }
  },
  toggleFeedItem: async (item: FeedItem) => {
    // Optimistic update
    set((s) => ({
      feedItems: s.feedItems.map((fi) =>
        fi.source === item.source && fi.id === item.id
          ? { ...fi, checked: !fi.checked }
          : fi
      ),
    }))
    try {
      if (item.source === 'personal') {
        await togglePersonalItem(item.id)
        // Sync personalItems too
        const updated = get().personalItems.map((pi) =>
          pi.id === item.id ? { ...pi, checked: !pi.checked } : pi
        )
        set({ personalItems: updated })
      } else if (item.source === 'group' && item.group_id) {
        await toggleGroupItem(item.group_id, item.id)
        // Sync groupItems too
        const gid = item.group_id
        const updated = (get().groupItems[gid] || []).map((gi) =>
          gi.id === item.id ? { ...gi, checked: !gi.checked } : gi
        )
        set((s) => ({ groupItems: { ...s.groupItems, [gid]: updated } }))
      }
    } catch (e) {
      // Revert optimistic update
      set((s) => ({
        feedItems: s.feedItems.map((fi) =>
          fi.source === item.source && fi.id === item.id
            ? { ...fi, checked: !fi.checked }
            : fi
        ),
      }))
      toast.error(e instanceof Error ? e.message : 'Eroare')
    }
  },

  // ── Personal List ────────────────────────────────────────────────────────────
  personalItems: [],
  personalLoading: false,
  fetchPersonalList: async () => {
    set({ personalLoading: true })
    try {
      const items = await getPersonalList()
      set({ personalItems: Array.isArray(items) ? items : [] })
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare la încărcarea listei')
    } finally {
      set({ personalLoading: false })
    }
  },
  addPersonal: async (item, qty, priority) => {
    try {
      const newItem = await addPersonalItem(item, qty, priority)
      set((s) => ({ personalItems: [newItem, ...s.personalItems] }))
      // Refresh feed
      get().fetchFeed()
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
        feedItems: s.feedItems.map((fi) =>
          fi.source === 'personal' && fi.id === id ? { ...fi, checked: updated.checked } : fi
        ),
      }))
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare')
    }
  },
  deletePersonal: async (id) => {
    try {
      await deletePersonalItem(id)
      set((s) => ({
        personalItems: s.personalItems.filter((i) => i.id !== id),
        feedItems: s.feedItems.filter((fi) => !(fi.source === 'personal' && fi.id === id)),
      }))
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare la ștergere')
    }
  },
  clearPersonalChecked: async () => {
    try {
      await clearPersonalDone()
      set((s) => ({
        personalItems: s.personalItems.filter((i) => !i.checked),
        feedItems: s.feedItems.filter((fi) => !(fi.source === 'personal' && fi.checked)),
      }))
      toast.success('Produsele bifate au fost șterse!')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare')
    }
  },

  // ── Groups ───────────────────────────────────────────────────────────────────
  groups: [],
  groupsLoading: false,
  fetchGroups: async () => {
    set({ groupsLoading: true })
    try {
      const groups = await getGroups()
      set({ groups: Array.isArray(groups) ? groups : [] })
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
      set((s) => ({
        groups: s.groups.filter((g) => g.id !== gid),
        feedItems: s.feedItems.filter((fi) => fi.group_id !== gid),
      }))
      toast.success('Grupul a fost șters!')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare la ștergere')
      throw e
    }
  },
  leaveExistingGroup: async (gid) => {
    try {
      await leaveGroup(gid)
      set((s) => ({
        groups: s.groups.filter((g) => g.id !== gid),
        feedItems: s.feedItems.filter((fi) => fi.group_id !== gid),
      }))
      toast.success('Ai ieșit din grup!')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare')
      throw e
    }
  },

  // ── Group Items ───────────────────────────────────────────────────────────────
  groupItems: {},
  groupItemsLoading: {},
  fetchGroupItemsList: async (gid) => {
    set((s) => ({ groupItemsLoading: { ...s.groupItemsLoading, [gid]: true } }))
    try {
      const items = await getGroupItems(gid)
      set((s) => ({ groupItems: { ...s.groupItems, [gid]: Array.isArray(items) ? items : [] } }))
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare la încărcarea produselor')
    } finally {
      set((s) => ({ groupItemsLoading: { ...s.groupItemsLoading, [gid]: false } }))
    }
  },
  addGroupItemAction: async (gid, item, qty, priority) => {
    try {
      const newItem = await addGroupItem(gid, item, qty, priority)
      set((s) => ({
        groupItems: {
          ...s.groupItems,
          [gid]: [newItem, ...(s.groupItems[gid] || [])],
        },
      }))
      get().fetchFeed()
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
        feedItems: s.feedItems.map((fi) =>
          fi.source === 'group' && fi.group_id === gid && fi.id === iid
            ? { ...fi, checked: updated.checked }
            : fi
        ),
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
        feedItems: s.feedItems.filter(
          (fi) => !(fi.source === 'group' && fi.group_id === gid && fi.id === iid)
        ),
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
        feedItems: s.feedItems.filter(
          (fi) => !(fi.source === 'group' && fi.group_id === gid && fi.checked)
        ),
      }))
      toast.success('Produsele bifate au fost șterse!')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Eroare')
    }
  },

  // ── Group Members ─────────────────────────────────────────────────────────────
  groupMembers: {},
  fetchGroupMembers: async (gid) => {
    try {
      const members = await getMembers(gid)
      set((s) => ({ groupMembers: { ...s.groupMembers, [gid]: Array.isArray(members) ? members : [] } }))
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
