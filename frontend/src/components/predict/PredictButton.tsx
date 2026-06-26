import { motion } from 'framer-motion'

type Status = 'idle' | 'loading' | 'done'

interface PredictButtonProps {
  onClick: () => void
  status: Status
  disabled?: boolean
}

export function PredictButton({ onClick, status, disabled }: PredictButtonProps) {
  const isLoading = status === 'loading'

  return (
    <motion.button
      onClick={onClick}
      disabled={disabled || isLoading}
      whileHover={!isLoading ? { scale: 1.02 } : {}}
      whileTap={!isLoading ? { scale: 0.97 } : {}}
      className={`relative w-full py-4 sm:py-4 rounded-xl font-display font-semibold text-sm tracking-widest uppercase
        overflow-hidden transition-all duration-300 disabled:cursor-not-allowed touch-manipulation
        ${isLoading
          ? 'bg-lab-surface border border-lab-cyan/30 text-lab-cyan'
          : 'bg-gradient-to-r from-cyan-900 via-lab-cyan/20 to-cyan-900 border border-lab-cyan/40 text-lab-cyan hover:border-lab-cyan/70 hover:glow-cyan'
        }`}
    >
      {isLoading && <div className="scan-line" />}

      <span className="relative z-10">
        {isLoading ? 'SCANNING...' : 'ANALYZE MOLECULE'}
      </span>

      {!isLoading && (
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-lab-cyan/10 to-transparent"
          initial={{ x: '-100%' }}
          whileHover={{ x: '100%' }}
          transition={{ duration: 0.6 }}
        />
      )}
    </motion.button>
  )
}
