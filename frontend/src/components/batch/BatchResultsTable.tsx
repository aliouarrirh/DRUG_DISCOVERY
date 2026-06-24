import { motion } from 'framer-motion'
import type { PredictResult } from '../../types/api'
import { GlassPanel } from '../ui/GlassPanel'

interface BatchResultsTableProps {
  results: PredictResult[]
}

export function BatchResultsTable({ results }: BatchResultsTableProps) {
  if (results.length === 0) return null

  const sorted = [...results].sort((a, b) =>
    a.prediction === 'TOXIC' && b.prediction !== 'TOXIC' ? -1 : 1,
  )
  const toxicCount = results.filter((r) => r.prediction === 'TOXIC').length
  const safeCount = results.length - toxicCount

  return (
    <GlassPanel className="p-5 mt-4">
      {/* Summary bar */}
      <div className="mb-4">
        <div className="flex justify-between font-mono text-xs text-lab-muted mb-2">
          <span>
            <span className="text-lab-red">{toxicCount} toxic</span>
            {' / '}
            <span className="text-lab-green">{safeCount} safe</span>
            {' out of '}
            {results.length}
          </span>
          <span>{Math.round((safeCount / results.length) * 100)}% safe</span>
        </div>
        <div className="h-1.5 bg-lab-bg rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${(safeCount / results.length) * 100}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className="h-full bg-gradient-to-r from-lab-green to-lab-cyan rounded-full"
          />
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-lab-border">
              <th className="font-mono text-xs text-lab-muted pb-2 pr-4">#</th>
              <th className="font-mono text-xs text-lab-muted pb-2 pr-4">SMILES</th>
              <th className="font-mono text-xs text-lab-muted pb-2">Result</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((r, i) => (
              <motion.tr
                key={r.smiles + i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.04, duration: 0.25 }}
                className="border-b border-lab-border/30 hover:bg-lab-surface/30 transition-colors"
              >
                <td className="font-mono text-xs text-lab-muted/50 py-2.5 pr-4">{i + 1}</td>
                <td className="font-mono text-xs text-lab-text py-2.5 pr-4 max-w-xs">
                  <span className="block truncate" title={r.smiles}>
                    {r.smiles}
                  </span>
                </td>
                <td className="py-2.5">
                  <span
                    className={`inline-flex items-center gap-1.5 font-mono text-xs font-semibold
                      px-3 py-1 rounded-full border
                      ${r.prediction === 'TOXIC'
                        ? 'text-lab-red border-lab-red/30 bg-lab-red/10'
                        : 'text-lab-green border-lab-green/30 bg-lab-green/10'
                      }`}
                  >
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${
                        r.prediction === 'TOXIC' ? 'bg-lab-red animate-pulse' : 'bg-lab-green'
                      }`}
                    />
                    {r.prediction}
                  </span>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </GlassPanel>
  )
}
