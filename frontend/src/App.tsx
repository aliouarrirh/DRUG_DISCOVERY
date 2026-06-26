import { useState } from 'react'
import { MolecularBackground } from './components/canvas/MolecularBackground'
import { HeroHeader } from './components/layout/HeroHeader'
import { HealthIndicator } from './components/layout/HealthIndicator'
import { SmilesInput } from './components/input/SmilesInput'
import { MoleculePreview } from './components/input/MoleculePreview'
import { PredictButton } from './components/predict/PredictButton'
import { ResultCard } from './components/predict/ResultCard'
import { BatchInput } from './components/batch/BatchInput'
import { BatchResultsTable } from './components/batch/BatchResultsTable'
import { useMolecule } from './hooks/useMolecule'
import { predictOne, predictBatch } from './api/client'
import type { PredictResult } from './types/api'

type Mode = 'single' | 'batch'
type Status = 'idle' | 'loading' | 'done'

export default function App() {
  const [mode, setMode] = useState<Mode>('single')
  const [smiles, setSmiles] = useState('')
  const [batchText, setBatchText] = useState('')
  const [status, setStatus] = useState<Status>('idle')
  const [result, setResult] = useState<PredictResult | null>(null)
  const [batchResults, setBatchResults] = useState<PredictResult[]>([])
  const [error, setError] = useState<string | null>(null)

  const { svg, valid, rdkitReady } = useMolecule(smiles)

  const handleSinglePredict = async () => {
    if (!smiles.trim() || !valid) return
    setStatus('loading')
    setResult(null)
    setError(null)
    try {
      const r = await predictOne(smiles.trim())
      setResult(r)
      setStatus('done')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error')
      setStatus('idle')
    }
  }

  const handleBatchPredict = async () => {
    const list = batchText
      .split('\n')
      .map((l) => l.trim())
      .filter(Boolean)
    if (list.length === 0) return
    setStatus('loading')
    setBatchResults([])
    setError(null)
    try {
      const r = await predictBatch(list)
      setBatchResults(r)
      setStatus('done')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error')
      setStatus('idle')
    }
  }

  const handleModeChange = (m: Mode) => {
    setMode(m)
    setStatus('idle')
    setResult(null)
    setBatchResults([])
    setError(null)
  }

  return (
    <div className="min-h-screen bg-lab-bg grid-overlay relative">
      <MolecularBackground />
      <HealthIndicator />

      <div className="relative z-10 max-w-3xl mx-auto px-3 sm:px-4 pb-10 md:pb-20">
        <HeroHeader />

        {/* Mode Toggle */}
        <div className="flex justify-center mb-8">
          <div className="glass rounded-full p-1 flex gap-1">
            {(['single', 'batch'] as Mode[]).map((m) => (
              <button
                key={m}
                onClick={() => handleModeChange(m)}
                className={`px-6 py-2 rounded-full font-mono text-xs uppercase tracking-widest transition-all duration-200
                  ${mode === m
                    ? 'bg-lab-cyan/20 text-lab-cyan border border-lab-cyan/40'
                    : 'text-lab-muted hover:text-lab-text'
                  }`}
              >
                {m === 'single' ? 'Single' : 'Batch'}
              </button>
            ))}
          </div>
        </div>

        {/* Single Mode */}
        {mode === 'single' && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              <SmilesInput
                value={smiles}
                onChange={(v) => { setSmiles(v); setResult(null); setError(null) }}
                onSubmit={handleSinglePredict}
                disabled={status === 'loading'}
                valid={valid}
              />
              <MoleculePreview svg={svg} valid={valid} smiles={smiles} rdkitReady={rdkitReady} />
            </div>

            <PredictButton
              onClick={handleSinglePredict}
              status={status}
              disabled={!smiles.trim() || !valid}
            />

            <ResultCard result={result} error={error} />
          </div>
        )}

        {/* Batch Mode */}
        {mode === 'batch' && (
          <div className="space-y-4">
            <BatchInput
              value={batchText}
              onChange={setBatchText}
              disabled={status === 'loading'}
            />

            <PredictButton
              onClick={handleBatchPredict}
              status={status}
              disabled={batchText.trim() === ''}
            />

            {error && (
              <div className="glass rounded-xl p-4">
                <p className="font-mono text-sm text-lab-red">⚠ {error}</p>
              </div>
            )}

            <BatchResultsTable results={batchResults} />
          </div>
        )}
      </div>
    </div>
  )
}
