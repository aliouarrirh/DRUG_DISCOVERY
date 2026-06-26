import { motion, AnimatePresence } from 'framer-motion'
import { GlassPanel } from '../ui/GlassPanel'

interface MoleculePreviewProps {
  svg: string | null
  valid: boolean
  smiles: string
  rdkitReady: boolean
}

export function MoleculePreview({ svg, valid, smiles, rdkitReady }: MoleculePreviewProps) {
  const isEmpty = !smiles.trim()

  return (
    <GlassPanel className="h-40 sm:h-48 flex items-center justify-center overflow-hidden relative">
      <AnimatePresence mode="wait">
        {isEmpty ? (
          <motion.div
            key="empty"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="text-center"
          >
            <div className="text-4xl mb-2 opacity-20">⬡</div>
            <p className="font-mono text-xs text-lab-muted">
              {rdkitReady ? 'Enter a SMILES to preview' : 'Loading RDKit...'}
            </p>
          </motion.div>
        ) : !valid ? (
          <motion.div
            key="invalid"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="text-center"
          >
            <div className="text-2xl mb-2">⚠</div>
            <p className="font-mono text-xs text-lab-red">Invalid SMILES</p>
          </motion.div>
        ) : svg ? (
          <motion.div
            key={svg.slice(0, 40)}
            initial={{ opacity: 0, scale: 0.85 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.85 }}
            transition={{ duration: 0.3 }}
            className="molecule-svg w-full h-full p-2 sm:p-3"
            dangerouslySetInnerHTML={{ __html: svg }}
          />
        ) : (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="font-mono text-xs text-lab-muted animate-pulse"
          >
            rendering...
          </motion.div>
        )}
      </AnimatePresence>
    </GlassPanel>
  )
}
