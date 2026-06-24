import { type KeyboardEvent } from 'react'

interface SmilesInputProps {
  value: string
  onChange: (v: string) => void
  onSubmit: () => void
  disabled?: boolean
  valid: boolean
}

export function SmilesInput({ value, onChange, onSubmit, disabled, valid }: SmilesInputProps) {
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault()
      onSubmit()
    }
  }

  const borderColor = !valid
    ? 'border-lab-red/60 focus:border-lab-red'
    : 'border-lab-border focus:border-lab-cyan/60'

  return (
    <div className="relative">
      <label className="block font-mono text-xs text-lab-muted mb-2 tracking-widest uppercase">
        SMILES Notation
      </label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        rows={3}
        placeholder="CC(=O)Oc1ccccc1C(=O)O"
        className={`w-full bg-lab-surface/80 border rounded-xl px-4 py-3 font-mono text-sm text-lab-text
          placeholder:text-lab-muted/40 outline-none resize-none transition-all duration-200
          disabled:opacity-50 ${borderColor}`}
      />
      <div className="flex justify-between items-center mt-1">
        <span className="font-mono text-xs text-lab-muted/60">
          {!valid ? '⚠ Invalid SMILES' : 'Ctrl+Enter to analyze'}
        </span>
        <span className="font-mono text-xs text-lab-muted/40">{value.length}</span>
      </div>
    </div>
  )
}
