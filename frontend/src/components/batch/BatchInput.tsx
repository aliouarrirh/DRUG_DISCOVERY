interface BatchInputProps {
  value: string
  onChange: (v: string) => void
  disabled?: boolean
}

export function BatchInput({ value, onChange, disabled }: BatchInputProps) {
  const count = value.split('\n').filter((l) => l.trim()).length

  return (
    <div>
      <label className="block font-mono text-xs text-lab-muted mb-2 tracking-widest uppercase">
        SMILES List — one per line
      </label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        rows={5}
        placeholder={`CC(=O)Oc1ccccc1C(=O)O\nCCO\nC1=CC=CC=C1`}
        className="w-full bg-lab-surface/80 border border-lab-border focus:border-lab-cyan/60 rounded-xl
          px-3 py-3 font-mono text-sm text-lab-text placeholder:text-lab-muted/40 outline-none
          resize-none transition-all duration-200 disabled:opacity-50"
      />
      <p className="font-mono text-xs text-lab-muted/60 mt-1">
        {count} molecule{count !== 1 ? 's' : ''} ready
      </p>
    </div>
  )
}
