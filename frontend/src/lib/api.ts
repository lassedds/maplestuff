const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json();
}

export const api = {
  // Auth
  getCurrentUser: () => fetchApi<any>('/api/auth/me'),
  logout: () => fetchApi<void>('/api/auth/logout', { method: 'POST' }),

  // Bosses
  getBosses: (resetType?: string) => {
    const params = resetType ? `?reset_type=${resetType}` : '';
    return fetchApi<any>(`/api/bosses${params}`);
  },
  getBoss: (id: number) => fetchApi<any>(`/api/bosses/${id}`),

  // Items
  getItems: (category?: string) => {
    const params = category ? `?category=${category}` : '';
    return fetchApi<any>(`/api/items${params}`);
  },
  getItem: (id: number) => fetchApi<any>(`/api/items/${id}`),

  // Characters
  getCharacters: () => fetchApi<any>('/api/characters'),
  createCharacter: (data: any) => fetchApi<any>('/api/characters', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  deleteCharacter: (id: string) => fetchApi<void>(`/api/characters/${id}`, {
    method: 'DELETE',
  }),

  // Boss Tracking
  getWeeklyProgress: (characterId?: string) => {
    const params = characterId ? `?character_id=${characterId}` : '';
    return fetchApi<any>(`/api/tracking/weekly${params}`);
  },
  getBossRuns: (characterId?: string) => {
    const params = characterId ? `?character_id=${characterId}` : '';
    return fetchApi<any>(`/api/tracking/runs${params}`);
  },
  createBossRun: (data: any) => fetchApi<any>('/api/tracking/runs', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  deleteBossRun: (id: string) => fetchApi<void>(`/api/tracking/runs/${id}`, {
    method: 'DELETE',
  }),

  // Tasks
  getTasks: () => fetchApi<any>('/api/tasks'),
  getMyTasks: () => fetchApi<any>('/api/tasks/my'),
  addTaskToChecklist: (taskId: string) => fetchApi<any>('/api/tasks/my', {
    method: 'POST',
    body: JSON.stringify({ task_id: taskId }),
  }),
  removeTaskFromChecklist: (userTaskId: string) => fetchApi<void>(`/api/tasks/my/${userTaskId}`, {
    method: 'DELETE',
  }),
  completeTask: (userTaskId: string) => fetchApi<any>(`/api/tasks/my/${userTaskId}/complete`, {
    method: 'POST',
  }),
  uncompleteTask: (userTaskId: string) => fetchApi<void>(`/api/tasks/my/${userTaskId}/complete`, {
    method: 'DELETE',
  }),
  getDailyChecklist: () => fetchApi<any>('/api/tasks/checklist/daily'),
  getWeeklyChecklist: () => fetchApi<any>('/api/tasks/checklist/weekly'),

  // Stats
  getStatsOverview: () => fetchApi<any>('/api/stats/overview'),
  getBossDropRates: (bossId: number) => fetchApi<any>(`/api/stats/boss/${bossId}`),
  getItemDropRates: (itemId: number) => fetchApi<any>(`/api/stats/item/${itemId}`),
  getRareDropsLeaderboard: () => fetchApi<any>('/api/stats/leaderboard/rare'),
};
