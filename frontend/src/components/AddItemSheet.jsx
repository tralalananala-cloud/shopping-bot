/**
 * Bottom sheet pentru adăugarea unui produs nou.
 * Parsează automat cantitatea din text: "lapte 2" → lapte ×2
 */
import { useState, useRef, useEffect } from 'react'

export default function AddItemSheet({ onAdd, onClose, loading }) {
  const [text, setText] = useState('')
  const inputRef = useRef(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  function parseInput(raw) {
    const t = raw.trim()
    const parts = t.rsplit ? t.rsplit(' ', 1) : t.split(' ')
    // Parsare simplă: ultimul cuvânt numeric = cantitate
    const last = parts[parts.length - 1]
    if (parts.length >= 2 && /^\d+$/.test(last) && parseInt(last) > 0) {
      return { item: parts.slice(0, -1).join(' '), quantity: last }
    }
    return { item: t, quantity: '1' }
  }

  async function submit(e) {
    e.preventDefault()
    const trimmed = text.trim()
    if (!trimmed) return
    const { item, quantity } = parseInput(trimmed)
    await onAdd(item, quantity)
    setText('')
  }

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black/40 z-40 animate-fade-in"
        onClick={onClose}
      />

      {/* Sheet */}
      <div className="fixed bottom-0 left-0 right-0 z-50 bg-tg-bg rounded-t-2xl p-4 pb-8 shadow-2xl animate-slide-up">
        <div className="w-10 h-1 bg-tg-bg2 rounded-full mx-auto mb-4" />
        <p className="font-semibold mb-3 text-sm text-tg-hint">Adaugă produs</p>

        <form onSubmit={submit} className="flex gap-2">
          <input
            ref={inputRef}
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder="ex: lapte 2"
            className="flex-1 bg-tg-bg2 rounded-xl px-4 py-3 text-tg-text placeholder:text-tg-hint outline-none focus:ring-2 focus:ring-[var(--tg-btn)] text-sm"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!text.trim() || loading}
            className="bg-[var(--tg-btn)] text-[var(--tg-btn-text)] px-5 rounded-xl font-semibold text-sm disabled:opacity-40 transition"
          >
            {loading ? '...' : '➕'}
          </button>
        </form>
        <p className="text-xs text-tg-hint mt-2">
          Adaugă cantitatea la final: <span className="text-tg-text">lapte 2</span>
        </p>
      </div>
    </>
  )
}
