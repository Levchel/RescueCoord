// Monitoring Service API client — mirrors client/monitoring_client.py
import type {
  AgentStatus,
  Telemetry,
  TelemetryCreate,
  Alert,
  AlertCreate,
} from './types'

const BASE = '/api/monitor'

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

export const monitoringApi = {
  /** POST /api/v1/telemetry */
  sendTelemetry: (data: TelemetryCreate): Promise<Telemetry> =>
    request('/api/v1/telemetry', { method: 'POST', body: JSON.stringify(data) }),

  /** GET /api/v1/agents/{id}/status */
  getAgentStatus: (agentId: number): Promise<AgentStatus> =>
    request(`/api/v1/agents/${agentId}/status`),

  /** GET /api/v1/agents/available */
  getAvailableAgents: (): Promise<AgentStatus[]> =>
    request('/api/v1/agents/available'),

  /** POST /api/v1/alerts */
  createAlert: (data: AlertCreate): Promise<Alert> =>
    request('/api/v1/alerts', { method: 'POST', body: JSON.stringify(data) }),

  /** GET /api/v1/alerts */
  getAlerts: (params?: {
    agent_id?: number
    mission_id?: number
    severity?: string
    status?: string
  }): Promise<Alert[]> => {
    const q = new URLSearchParams()
    if (params?.agent_id != null) q.set('agent_id', String(params.agent_id))
    if (params?.mission_id != null) q.set('mission_id', String(params.mission_id))
    if (params?.severity) q.set('severity', params.severity)
    if (params?.status) q.set('status', params.status)
    const qs = q.toString()
    return request(`/api/v1/alerts${qs ? `?${qs}` : ''}`)
  },

  /** GET /health */
  health: (): Promise<{ status: string }> => request('/health'),
}
