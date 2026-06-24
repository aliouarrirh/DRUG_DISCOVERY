import { motion } from 'framer-motion'
import { useHealth } from '../../hooks/useHealth'

export function HealthIndicator() {
  const { health, online } = useHealth()

  return (
    <motion.div
      initial={{ opacity: 0, x: 40 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 1, duration: 0.5 }}
      className="fixed top-4 right-4 z-50 glass rounded-full px-4 py-2 flex items-center gap-2"
    >
      <span
        className={`w-2 h-2 rounded-full ${online ? 'bg-lab-green animate-pulse' : 'bg-lab-red'}`}
      />
      <span className="font-mono text-xs text-lab-muted">
        {online ? `v${health?.model_version ?? '—'}` : 'offline'}
      </span>
    </motion.div>
  )
}
