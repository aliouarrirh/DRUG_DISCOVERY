import { useState, useEffect, useCallback } from 'react'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let rdkitPromise: Promise<any> | null = null

export function useRDKit() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [rdkit, setRdkit] = useState<any>(null)

  useEffect(() => {
    if (!rdkitPromise) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      rdkitPromise = (window as any)
        .initRDKitModule({ locateFile: () => '/RDKit_minimal.wasm' })
        .catch(() => null)
    }
    rdkitPromise!.then(setRdkit)
  }, [])

  const renderSMILES = useCallback(
    (smiles: string): string | null => {
      if (!rdkit) return null
      try {
        const mol = rdkit.get_mol(smiles)
        if (!mol) return null
        const svg = mol.get_svg()
        mol.delete()
        return svg
      } catch {
        return null
      }
    },
    [rdkit],
  )

  return { ready: !!rdkit, renderSMILES }
}
