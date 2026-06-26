import { useState, useEffect } from 'react'
import { getHealth } from '../api/client'
import type { HealthResult } from '../types/api'

export function useHealth() {
  const [health, setHealth] = useState<HealthResult | null>(null)
  const [online, setOnline] = useState(false)
  const [lastPing, setLastPing] = useState<Date | null>(null)

  useEffect(() => {
    const check = () =>
      getHealth()
        .then((h) => {
          setHealth(h)
          setOnline(true)
          setLastPing(new Date())
        })
        .catch(() => {
          setOnline(false)
        })

    check()
    const id = setInterval(check, 60_000)
    return () => clearInterval(id)
  }, [])

  return { health, online, lastPing }
}
