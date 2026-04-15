import type { Priority } from '../api'

const OPTIONS: Array<{ val: Priority; label: string; color: string }> = [
  { val: 1, label: '🔵 Mică',   color: 'hsl(240 5% 55%)' },
  { val: 2, label: '⚪ Normală', color: 'hsl(185 100% 50%)' },
  { val: 3, label: '🔴 Mare',   color: 'hsl(0 84% 60%)' },
]

interface Props {
  value: Priority
  onChange: (p: Priority) => void
}

export function PriorityPicker({ value, onChange }: Props) {
  return (
    <div>
      <p className="mb-1.5 text-xs font-medium text-muted-foreground">Prioritate</p>
      <div className="flex gap-2">
        {OPTIONS.map((opt) => (
          <button
            key={opt.val}
            type="button"
            onClick={() => onChange(opt.val)}
            className="flex-1 rounded-xl py-2 text-xs font-medium transition-all"
            style={{
              background: value === opt.val
                ? `${opt.color.replace(')', ' / 0.15)').replace('hsl(', 'hsl(')}`
                : 'hsl(0 0% 100% / 0.05)',
              border: `1px solid ${value === opt.val ? opt.color : 'hsl(0 0% 100% / 0.08)'}`,
              color: value === opt.val ? opt.color : 'hsl(240 5% 55%)',
            }}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  )
}
