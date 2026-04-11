import { useState, useEffect, useCallback } from 'react'
import Header       from './Header.jsx'
import ProgressBar  from './ProgressBar.jsx'
import Spinner      from './Spinner.jsx'
import AddItemSheet from './AddItemSheet.jsx'
import * as api     from '../api.js'

export default function PersonalList({ nav }) {
  const [items,   setItems]   = useState([])
  const [loading, setLoading] = useState(true)
  const [adding,  setAdding]  = useState(false)
  const [showAdd, setShowAdd] = useState(false)

  const fetchList = useCallback(async () => {
    try {
      const data = await api.getPersonalList()
      setItems(data.items)
    } catch (e) {
      nav.toast(e.message, 'error')
    } finally {
      setLoading(false)
    }
  }, [nav])

  useEffect(() => { fetchList() }, [fetchList])

  async function handleToggle(id) {
    try {
      const updated = await api.togglePersonalItem(id)
      setItems(prev => prev.map(i => i.id === id ? updated : i))
    } catch (e) {
      nav.toast(e.message, 'error')
    }
  }

  async function handleDelete(id) {
    try {
      await api.deletePersonalItem(id)
      setItems(prev => prev.filter(i => i.id !== id))
    } catch (e) {
      nav.toast(e.message, 'error')
    }
  }

  async function handleAdd(item, quantity) {
    setAdding(true)
    try {
      const newItem = await api.addPersonalItem(item, quantity)
      setItems(prev => [newItem, ...prev])
      setShowAdd(false)
      nav.toast('Produs adăugat')
    } catch (e) {
      nav.toast(e.message, 'error')
    } finally {
      setAdding(false)
    }
  }

  async function handleClear() {
    try {
      const res = await api.clearPersonalDone()
      setItems(prev => prev.filter(i => !i.checked))
      nav.toast(`${res.count} produse șterse`)
    } catch (e) {
      nav.toast(e.message, 'error')
    }
  }

  const done     = items.filter(i => i.checked).length
  const hasDone  = done > 0
  const unchecked = items.filter(i => !i.checked)
  const checked   = items.filter(i =>  i.checked)

  return (
    <div className="flex flex-col min-h-screen animate-fade-in">
      <Header
        title="📝 Lista mea"
        onBack={nav.pop}
        action={
          hasDone && (
            <button
              onClick={handleClear}
              className="text-xs text-red-500 font-medium px-2 py-1"
            >
              Șterge bifate
            </button>
          )
        }
      />

      {loading ? (
        <Spinner />
      ) : (
        <div className="flex-1 overflow-y-auto scroll-hidden px-4 pb-24">
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
              <p className="font-semibold">Lista ta e goală</p>
              <p className="text-sm text-tg-hint mt-1">Apasă + pentru a adăuga primul produs</p>
            </div>
          )}

          {/* Produse necumpărate */}
          {unchecked.length > 0 && (
            <div className="flex flex-col gap-1 mt-1">
              {unchecked.map(item => (
                <ItemRow
                  key={item.id}
                  item={item}
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
                <ItemRow
                  key={item.id}
                  item={item}
                  onToggle={() => handleToggle(item.id)}
                  onDelete={() => handleDelete(item.id)}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* FAB Adaugă */}
      <button
        onClick={() => setShowAdd(true)}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-[var(--tg-btn)] text-[var(--tg-btn-text)] text-3xl shadow-lg flex items-center justify-center active:scale-95 transition-transform z-30"
        aria-label="Adaugă produs"
      >
        +
      </button>

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

function ItemRow({ item, onToggle, onDelete }) {
  return (
    <div className="flex items-center gap-3 bg-tg-bg2 rounded-xl px-3 py-3 group">
      {/* Checkbox */}
      <button
        onClick={onToggle}
        className={`w-6 h-6 rounded-full border-2 flex items-center justify-center shrink-0 transition ${
          item.checked
            ? 'bg-[var(--tg-btn)] border-[var(--tg-btn)]'
            : 'border-tg-hint'
        }`}
        aria-label={item.checked ? 'Debifează' : 'Bifează'}
      >
        {item.checked && (
          <svg className="w-3 h-3 text-[var(--tg-btn-text)]" viewBox="0 0 12 12" fill="none">
            <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        )}
      </button>

      {/* Nume + cantitate */}
      <div className="flex-1 min-w-0">
        <span className={`text-sm font-medium ${item.checked ? 'line-through text-tg-hint' : ''}`}>
          {item.item}
        </span>
        {item.quantity !== '1' && (
          <span className="ml-1.5 text-xs text-tg-hint">×{item.quantity}</span>
        )}
      </div>

      {/* Buton ștergere */}
      <button
        onClick={onDelete}
        className="text-tg-hint hover:text-red-500 transition p-1 opacity-0 group-hover:opacity-100 focus:opacity-100"
        aria-label="Șterge"
      >
        <svg className="w-4 h-4" viewBox="0 0 16 16" fill="none">
          <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      </button>
    </div>
  )
}
