// TypeScript API types — mirrors client/models.py

export interface AgentStatus {
  agent_id: number
  last_seen_at: string
  battery_level: number
  link_status: 'ONLINE' | 'DEGRADED' | 'OFFLINE'
  health_state: 'HEALTHY' | 'WARNING' | 'CRITICAL' | 'OFFLINE'
  mission_status: string
}

export interface Telemetry {
  id: number
  agent_id: number
  timestamp: string
  latitude: number
  longitude: number
  battery_level: number
  speed: number
  link_status: string
  mission_status: string
}

export interface TelemetryCreate {
  agent_id: number
  latitude: number
  longitude: number
  battery_level: number
  speed: number
  link_status: string
  mission_status: string
}

export interface Alert {
  id: number
  agent_id: number
  mission_id: number | null
  alert_type: string
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  message: string
  created_at: string
  status: 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED'
}

export interface AlertCreate {
  agent_id: number
  alert_type: string
  severity: string
  message: string
  mission_id?: number
}

export interface Mission {
  id: number
  incident_type: string
  location: string
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  created_at: string
  status: 'CREATED' | 'PLANNING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'
  required_agents: number
}

export interface MissionCreate {
  incident_type: string
  location: string
  priority: string
  required_agents: number
}

export interface SearchZone {
  id: number
  mission_id: number
  zone_code: string
  geometry: Record<string, unknown> | null
  priority: string
  assigned_agent_id: number | null
  status: 'PENDING' | 'ASSIGNED' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED'
}

export interface Assignment {
  zone_code: string
  zone_id: number
  agent_id: number | null
  agent_name: string | null
  route_id: number | null
  route_status: string | null
}

export interface MissionDetail extends Mission {
  zones: SearchZone[]
  routes: Route[]
}

export interface Route {
  id: number
  mission_id: number
  agent_id: number
  zone_id: number
  route_points: [number, number][] | null
  assigned_at: string
  route_status: 'PLANNED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED' | 'REASSIGNED'
}

export interface TaskReassignment {
  id: number
  mission_id: number
  from_agent_id: number
  to_agent_id: number
  reason: string
  created_at: string
}
