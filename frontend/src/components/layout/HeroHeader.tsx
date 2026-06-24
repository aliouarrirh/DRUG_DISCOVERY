import { motion } from 'framer-motion'

export function HeroHeader() {
  return (
    <motion.div
      initial={{ opacity: 0, y: -30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: 'easeOut' }}
      className="text-center pt-16 pb-10"
    >
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="font-mono text-xs tracking-[0.3em] text-lab-cyan uppercase mb-4 animate-flicker"
      >
        ⬡ Drug Toxicity Analysis System ⬡
      </motion.p>

      <h1 className="font-display text-6xl md:text-7xl font-bold text-lab-text text-glow-cyan mb-3 tracking-tight">
        Toxi<span className="text-lab-cyan">Scan</span>
      </h1>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="text-lab-muted font-body text-lg"
      >
        AI-powered molecular safety screening via XGBoost + RDKit
      </motion.p>

      <motion.div
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ delay: 0.7, duration: 0.6 }}
        className="mt-6 h-px bg-gradient-to-r from-transparent via-lab-cyan/40 to-transparent"
      />
    </motion.div>
  )
}
