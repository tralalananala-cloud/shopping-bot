import { useState, useEffect, useCallback } from 'react'
import Toast      from './components/Toast.jsx'
import MainMenu   from './components/MainMenu.jsx'
import PersonalList from './components/PersonalList.jsx'
import GroupsList   from './components/GroupsList.jsx'
import GroupView    from './components/GroupView.jsx'
import Members      from './components/Members.jsx'

const tg = window.Telegram?.WebApp

// Stiva de navigare: fiecare element e { screen, data }
export default function App() {
  const [stack,  setStack]  = useState([{ screen: 'menu', data: null }])
  const [toasts, setToasts] = useState([])

  const current = stack[stack.length - 1]

  // ── Inițializare Telegram ────────────────────────────────────────────────
  useEffect(() => {
    tg?.ready()
    tg?.expand()
  }, [])

  // ── Toast ────────────────────────────────────────────────────────────────
  const toast = useCallback((msg, type = 'success') => {
    const id = Date.now()
    setToasts(t => [...t, { id, msg, type }])
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 3200)
  }, [])

  // ── Navigare ─────────────────────────────────────────────────────────────
  const push = useCallback((screen, data = null) => {
    setStack(s => [...s, { screen, data }])
  }, [])

  const pop = useCallback(() => {
    setStack(s => s.length > 1 ? s.slice(0, -1) : s)
  }, [])

  const replace = useCallback((screen, data = null) => {
    setStack(s => [...s.slice(0, -1), { screen, data }])
  }, [])

  // ── Telegram BackButton ──────────────────────────────────────────────────
  useEffect(() => {
    if (!tg?.BackButton) return
    if (stack.length <= 1) {
      tg.BackButton.hide()
    } else {
      tg.BackButton.show()
      tg.BackButton.onClick(pop)
      return () => tg.BackButton.offClick(pop)
    }
  }, [stack.length, pop])

  // ── Props comune ─────────────────────────────────────────────────────────
  const nav = { push, pop, replace, toast }

  const { screen, data } = current

  return (
    <div className="min-h-screen bg-tg-bg text-tg-text">

      {screen === 'menu'     && <MainMenu    nav={nav} />}
      {screen === 'personal' && <PersonalList nav={nav} />}
      {screen === 'groups'   && <GroupsList   nav={nav} />}
      {screen === 'group'    && <GroupView    nav={nav} group={data} />}
      {screen === 'members'  && <Members      nav={nav} group={data} />}

      {/* Toast-uri suprapuse */}
      <div className="fixed bottom-4 left-0 right-0 flex flex-col items-center gap-2 z-50 pointer-events-none px-4">
        {toasts.map(t => <Toast key={t.id} msg={t.msg} type={t.type} />)}
      </div>
    </div>
  )
}
