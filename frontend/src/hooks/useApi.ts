import { useState, useEffect, useCallback } from 'react'
import { monitoringApi } from '@/api/monitoringApi'
import { coordinationApi } from '@/api/coordinationApi'
import type { AgentStatus, Alert, Mission, Assignment, MissionDetail } from '@/api/types'

// ── generic async hook ────────────────────────────────────────────────────────

interface AsyncState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

function useAsync<T>(
  fn: () => Promise<T>,
  deps: unknown[] = [],
): AsyncState<T> & { refetch: () => void } {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: true,
    error: null,
  })

  const run = useCallback(() => {
    setState((s) => ({ ...s, loading: true, error: null }))
    fn()
      .then((data) => setState({ data, loading: false, error: null }))
      .catch((err: Error) => setState({ data: null, loading: false, error: err.message }))
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => { run() }, [run])

  return { ...state, refetch: run }
}

// ── Monitoring hooks ──────────────────────────────────────────────────────────

/** Available agents polled every 10 seconds */
export function useAvailableAgents(pollMs = 10_000) {
  const state = useAsync<AgentStatus[]>(() => monitoringApi.getAvailableAgents(), [])

  useEffect(() => {
    const id = setInterval(state.refetch, pollMs)
    return () => clearInterval(id)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pollMs])

  return state
}

/** Active alerts, optional filters */
export function useAlerts(params?: {
  agent_id?: number
  mission_id?: number
  severity?: string
  status?: string
}) {
  return useAsync<Alert[]>(() => monitoringApi.getAlerts(params), [
    params?.agent_id,
    params?.mission_id,
    params?.severity,
    params?.status,
  ])
}

// ── Coordination hooks ────────────────────────────────────────────────────────

/** All missions — no native list endpoint, so we return what we have */
export function useMissions() {
  // The coordination service has no GET /missions list endpoint.
  // We seed by fetching missions 1..20 and collecting those that exist.
  // In real production this would be a proper paginated endpoint.
  const [missions, setMissions] = useState<Mission[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchMissions = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const results = await Promise.allSettled(
        Array.from({ length: 20 }, (_, i) => coordinationApi.getMission(i + 1)),
      )
      const found: Mission[] = []
      for (const r of results) {
        if (r.status === 'fulfilled') found.push(r.value)
      }
      setMissions(found)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchMissions() }, [fetchMissions])

  return { data: missions, loading, error, refetch: fetchMissions }
}

/** Assignments for a mission */
export function useAssignments(missionId: number | null) {
  return useAsync<Assignment[]>(
    () =>
      missionId != null
        ? coordinationApi.getAssignments(missionId)
        : Promise.resolve([]),
    [missionId],
  )
}

/** Full mission detail */
export function useMissionDetail(missionId: number | null) {
  return useAsync<MissionDetail>(
    () =>
      missionId != null
        ? coordinationApi.getMission(missionId)
        : Promise.reject(new Error('no id')),
    [missionId],
  )
}
