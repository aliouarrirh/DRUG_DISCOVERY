import { useState, useEffect } from 'react'
import { getHealth } from '../api/client'
import type { HealthResult } from '../types/api'

export function useHealth() {
  const [health, setHealth] = useState<HealthResult | null>(null)
  const [online, setOnline] = useState(false)

  useEffect(() => {
    const check = () =>
      getHealth()
        .then((h) => { setHealth(h); setOnline(true) })
        .catch(() => { setOnline(false) })

    check()
    const id = setInterval(check, 30_000)
    return () => clearInterval(id)
  }, [])

  return { health, online }
}
