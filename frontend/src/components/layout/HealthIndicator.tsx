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
      className="fixed top-3 right-3 sm:top-4 sm:right-4 z-50 glass rounded-full px-3 sm:px-4 py-1.5 sm:py-2 flex items-center gap-1.5 sm:gap-2 max-w-[180px]"
      title={`Last ping: ${pingStr}`}
    >
      <span
        className={`w-2 h-2 rounded-full shrink-0 ${online ? 'bg-lab-green animate-pulse' : 'bg-lab-red'}`}
      />
      <span className="font-mono text-xs text-lab-muted truncate">
        {online ? (
          <>
            <span className="hidden sm:inline">v{health?.model_version ?? '—'} · {pingStr}</span>
            <span className="sm:hidden">{online ? 'online' : 'offline'}</span>
          </>
        ) : 'offline'}
      </span>
    </motion.div>
  )
}
