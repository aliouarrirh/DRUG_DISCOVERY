import { motion, AnimatePresence } from 'framer-motion'
import type { PredictResult } from '../../types/api'
import { GlassPanel } from '../ui/GlassPanel'

interface ResultCardProps {
  result: PredictResult | null
  error: string | null
}

export function ResultCard({ result, error }: ResultCardProps) {
  const isToxic = result?.prediction === 'TOXIC'

  return (
    <AnimatePresence mode="wait">
      {error ? (
        <motion.div
          key="error"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
        >
          <GlassPanel className="p-5 border-lab-red/30">
            <p className="font-mono text-sm text-lab-red">⚠ {error}</p>
          </GlassPanel>
        </motion.div>
      ) : result ? (
        <motion.div
          key={result.smiles + result.prediction}
          initial={{ opacity: 0, scale: 0.85 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          transition={{ duration: 0.4, ease: 'backOut' }}
        >
          <GlassPanel
            glow={isToxic ? 'red' : 'green'}
            className="p-6 relative overflow-hidden"
          >
            {/* Pulsing ring */}
            <motion.div
              animate={{ scale: [1, 1.6, 1], opacity: [0.5, 0, 0.5] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
              className={`absolute inset-0 rounded-2xl border-2 pointer-events-none
                ${isToxic ? 'border-lab-red/40' : 'border-lab-green/40'}`}
            />

            <div className="relative z-10 text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.1, type: 'spring', stiffness: 200 }}
                className="text-5xl mb-3"
              >
                {isToxic ? '☠' : '✓'}
              </motion.div>

              <motion.h2
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className={`font-display text-3xl font-bold tracking-wide mb-1
                  ${isToxic ? 'text-lab-red' : 'text-lab-green'}`}
                style={{
                  textShadow: isToxic
                    ? '0 0 20px rgba(255,34,68,0.6)'
                    : '0 0 20px rgba(0,255,136,0.6)',
                }}
              >
                {isToxic ? 'TOXIC' : 'NON-TOXIC'}
              </motion.h2>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="font-mono text-xs text-lab-muted mb-4"
              >
                {isToxic ? 'Compound flagged as hazardous' : 'Compound cleared as safe'}
              </motion.p>

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="bg-lab-bg/60 rounded-lg px-4 py-2 font-mono text-xs text-lab-muted break-all"
              >
                {result.smiles}
              </motion.div>
            </div>
          </GlassPanel>
        </motion.div>
      ) : null}
    </AnimatePresence>
  )
}
