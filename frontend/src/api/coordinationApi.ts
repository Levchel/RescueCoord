// Coordination Service API client — mirrors client/coordination_client.py
import type {
  Mission,
  MissionCreate,
  MissionDetail,
  SearchZone,
  Assignment,
  TaskReassignment,
} from './types'

const BASE = '/api/coord'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${res.status} ${res.statusText}: ${text}`)
  }
  return res.json() as Promise<T>
}

export const coordinationApi = {
  /** POST /api/v1/missions */
  createMission: (data: MissionCreate): Promise<Mission> =>
    request('/api/v1/missions', { method: 'POST', body: JSON.stringify(data) }),

  /** GET /api/v1/missions/{id} */
  getMission: (id: number): Promise<MissionDetail> =>
    request(`/api/v1/missions/${id}`),

  /** POST /api/v1/missions/{id}/plan */
  planMission: (id: number): Promise<SearchZone[]> =>
    request(`/api/v1/missions/${id}/plan`, { method: 'POST' }),

  /** GET /api/v1/missions/{id}/assignments */
  getAssignments: (id: number): Promise<Assignment[]> =>
    request(`/api/v1/missions/${id}/assignments`),

  /** PATCH /api/v1/routes/{id}/reassign */
  reassignRoute: (
    routeId: number,
    newAgentId: number,
    reason: string,
  ): Promise<TaskReassignment> =>
    request(`/api/v1/routes/${routeId}/reassign`, {
      method: 'PATCH',
      body: JSON.stringify({ new_agent_id: newAgentId, reason }),
    }),

  /** GET /health */
  health: (): Promise<{ status: string }> => request('/health'),
}
