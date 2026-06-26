import { motion } from 'framer-motion'
import { useHealth } from '../../hooks/useHealth'

export function HealthIndicator() {
  const { health, online, lastPing } = useHealth()

  const pingStr = lastPing
    ? lastPing.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : '—'

  return (
    <motion.div
      initial={{ opacity: 0, x: 40 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 1, duration: 0.5 }}
      className="fixed top-4 right-4 z-50 glass rounded-full px-4 py-2 flex items-center gap-2"
      title={`Last ping: ${pingStr}`}
    >
      <span
        className={`w-2 h-2 rounded-full ${online ? 'bg-lab-green animate-pulse' : 'bg-lab-red'}`}
      />
      <span className="font-mono text-xs text-lab-muted">
        {online ? `v${health?.model_version ?? '—'} · ${pingStr}` : 'offline'}
      </span>
    </motion.div>
  )
}
