import type { Candidate, CostSummary, Project, Shot } from './types'

const BASE = ''  // 走 vite proxy，前端代码写相对路径

async function req<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + url, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
  })
  if (!res.ok) {
    const detail = await res.text()
    throw new Error(`${res.status} ${detail}`)
  }
  return res.json() as Promise<T>
}

export const api = {
  listProjects: () => req<Project[]>('/api/projects'),
  createProject: (name: string) =>
    req<Project>('/api/projects', { method: 'POST', body: JSON.stringify({ name }) }),

  listShots: (projectId?: number) =>
    req<Shot[]>(`/api/shots${projectId ? `?project_id=${projectId}` : ''}`),

  submitShots: (projectId: number, prompts: string[], characterRef?: string) =>
    req<Shot[]>('/api/shots', {
      method: 'POST',
      body: JSON.stringify({ project_id: projectId, prompts, character_ref: characterRef ?? null }),
    }),

  getShot: (id: number) => req<Shot & { candidates: Candidate[] }>(`/api/shots/${id}`),

  retryShot: (id: number) => req<Shot>(`/api/shots/${id}/retry`, { method: 'POST' }),

  selectCandidate: (shotId: number, candidateId: number) =>
    req<Shot>(`/api/shots/${shotId}/select`, {
      method: 'POST',
      body: JSON.stringify({ candidate_id: candidateId }),
    }),

  cost: () => req<CostSummary>('/api/cost'),
}
