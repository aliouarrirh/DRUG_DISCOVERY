import type { HealthResult, PredictResult } from '../types/api'

const BASE = '/api'

export async function getHealth(): Promise<HealthResult> {
  const r = await fetch(`${BASE}/health`)
  if (!r.ok) throw new Error('Health check failed')
  return r.json()
}

export async function predictOne(smiles: string): Promise<PredictResult> {
  const r = await fetch(`${BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ smiles }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(err?.detail?.[0]?.msg ?? 'Prediction failed')
  }
  return r.json()
}

export async function predictBatch(smiles_list: string[]): Promise<PredictResult[]> {
  const r = await fetch(`${BASE}/predict/batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ smiles_list }),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(err?.detail?.[0]?.msg ?? 'Batch prediction failed')
  }
  return r.json()
}
