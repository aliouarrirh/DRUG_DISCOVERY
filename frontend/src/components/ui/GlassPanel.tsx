import { type ReactNode } from 'react'

interface GlassPanelProps {
  children: ReactNode
  className?: string
  glow?: 'cyan' | 'green' | 'red' | 'none'
}

export function GlassPanel({ children, className = '', glow = 'none' }: GlassPanelProps) {
  const glowClass = {
    cyan: 'glow-cyan border-lab-cyan/20',
    green: 'glow-green border-lab-green/30',
    red: 'glow-red border-lab-red/30',
    none: 'border-white/8',
  }[glow]

  return (
    <div className={`glass rounded-2xl ${glowClass} ${className}`}>
      {children}
    </div>
  )
}
