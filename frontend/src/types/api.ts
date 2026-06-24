export type Prediction = 'TOXIC' | 'NON-TOXIC'

export interface PredictResult {
  smiles: string
  prediction: Prediction
}

export interface HealthResult {
  status: string
  model_version: string
}
