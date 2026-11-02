// 与后端 Pydantic 模型一一对应。
// 面试可讲：这份类型定义就是"接口契约"，和后端 schema 同源。
export type ShotStatus = 'pending' | 'running' | 'succeeded' | 'failed'

export interface Project {
  id: number
  name: string
  created_at: string
}

export interface Candidate {
  id: number
  shot_id: number
  url: string
  seed: number
  is_selected: boolean
}

export interface Shot {
  id: number
  project_id: number
  idx: number
  prompt: string
  character_ref: string | null
  status: ShotStatus
  error: string | null
  attempts: number
  duration_seconds: number | null
  cost: number
  selected_candidate_id: number | null
  created_at: string
  updated_at: string
  candidates?: Candidate[]
}

export interface CostSummary {
  total_cost: number
  total_shots: number
  succeeded: number
  failed: number
  pending_or_running: number
  avg_cost_per_succeeded_shot: number
  attempts_total: number
}
