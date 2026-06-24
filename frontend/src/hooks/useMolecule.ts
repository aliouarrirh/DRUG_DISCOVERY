import { useState, useEffect } from 'react'
import { useRDKit } from './useRDKit'

export function useMolecule(smiles: string) {
  const { ready, renderSMILES } = useRDKit()
  const [svg, setSvg] = useState<string | null>(null)
  const [valid, setValid] = useState(true)

  useEffect(() => {
    if (!ready || !smiles.trim()) {
      setSvg(null)
      setValid(true)
      return
    }
    const id = setTimeout(() => {
      const result = renderSMILES(smiles.trim())
      if (result) {
        // Post-process SVG for dark theme
        const themed = result
          .replace(/fill:#000000/g, 'fill:#e0f4ff')
          .replace(/stroke:#000000/g, 'stroke:#00d4ff')
          .replace(/fill:#ffffff/gi, 'fill:transparent')
          .replace(/fill:white/gi, 'fill:transparent')
        setSvg(themed)
        setValid(true)
      } else {
        setSvg(null)
        setValid(false)
      }
    }, 300)
    return () => clearTimeout(id)
  }, [smiles, ready, renderSMILES])

  return { svg, valid: smiles.trim() === '' ? true : valid, rdkitReady: ready }
}
