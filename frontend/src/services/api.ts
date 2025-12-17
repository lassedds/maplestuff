import axios, { AxiosInstance } from 'axios';
import {
  User,
  Character,
  CharacterCreate,
  CharacterUpdate,
  CharacterListResponse,
  CharacterLookupRequest,
  CharacterLookupResponse,
  DiaryListResponse,
  DiaryStats,
  DiaryTimelineResponse,
  DiaryItem,
  DiaryFilters,
  XPEntry,
  XPEntryCreate,
  XPEntryUpdate,
  XPEntryListResponse,
  XPStats,
  Boss,
  BossListResponse,
  BossRun,
  BossRunCreate,
  BossRunUpdate,
  BossRunListResponse,
  BossRunDrop,
  WeeklySummary,
  CharacterXPSnapshot,
  CharacterXPHistoryResponse,
  CharacterXPOverviewListResponse,
  ItemListResponse,
  Item,
} from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      withCredentials: true, // Important for cookies
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Auth endpoints
  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/api/auth/me');
    return response.data;
  }

  async logout(): Promise<void> {
    await this.client.post('/api/auth/logout');
  }

  getDiscordLoginUrl(): string {
    // Discord OAuth must redirect to backend directly, not through frontend proxy
    return `${API_URL}/api/auth/discord`;
  }

  // Character endpoints
  async getCharacters(): Promise<CharacterListResponse> {
    const response = await this.client.get<CharacterListResponse>('/api/characters');
    return response.data;
  }

  async createCharacter(data: CharacterCreate): Promise<Character> {
    const response = await this.client.post<Character>('/api/characters', data);
    return response.data;
  }

  async updateCharacter(id: string, data: CharacterUpdate): Promise<Character> {
    const response = await this.client.put<Character>(`/api/characters/${id}`, data);
    return response.data;
  }

  async deleteCharacter(id: string): Promise<void> {
    await this.client.delete(`/api/characters/${id}`);
  }

  async reorderCharacters(order: string[]): Promise<void> {
    await this.client.post('/api/characters/reorder', { character_ids: order });
  }

  async lookupCharacter(name: string, world: string): Promise<CharacterLookupResponse> {
    console.log('📡 API: lookupCharacter called', { name, world });
    try {
      const response = await this.client.post<CharacterLookupResponse>('/api/characters/lookup', {
        character_name: name,
        world,
      });
      console.log('✅ API: lookupCharacter response received', response.data);
      return response.data;
    } catch (error: any) {
      console.error('❌ API: lookupCharacter error', error);
      throw error;
    }
  }

  async refreshCharacter(id: string): Promise<Character> {
    const response = await this.client.post<Character>(`/api/characters/${id}/refresh`);
    return response.data;
  }

  // Diary endpoints
  async getDiaryEntries(filters: DiaryFilters = {}): Promise<DiaryListResponse> {
    const params = new URLSearchParams();
    if (filters.character_id) params.append('character_id', filters.character_id);
    if (filters.boss_id) params.append('boss_id', filters.boss_id.toString());
    if (filters.item_id) params.append('item_id', filters.item_id.toString());
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.search) params.append('search', filters.search);
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.page_size) params.append('page_size', filters.page_size.toString());

    const response = await this.client.get<DiaryListResponse>(`/api/diary?${params.toString()}`);
    return response.data;
  }

  async getDiaryStats(filters: DiaryFilters = {}): Promise<DiaryStats> {
    const params = new URLSearchParams();
    if (filters.character_id) params.append('character_id', filters.character_id);
    if (filters.boss_id) params.append('boss_id', filters.boss_id.toString());
    if (filters.item_id) params.append('item_id', filters.item_id.toString());
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);

    const response = await this.client.get<DiaryStats>(`/api/diary/stats?${params.toString()}`);
    return response.data;
  }

  async getDiaryItems(filters: DiaryFilters = {}): Promise<DiaryItem[]> {
    const params = new URLSearchParams();
    if (filters.character_id) params.append('character_id', filters.character_id);
    if (filters.boss_id) params.append('boss_id', filters.boss_id.toString());
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);

    const response = await this.client.get<DiaryItem[]>(`/api/diary/items?${params.toString()}`);
    return response.data;
  }

  async getDiaryTimeline(filters: DiaryFilters = {}): Promise<DiaryTimelineResponse> {
    const params = new URLSearchParams();
    if (filters.character_id) params.append('character_id', filters.character_id);
    if (filters.boss_id) params.append('boss_id', filters.boss_id.toString());
    if (filters.item_id) params.append('item_id', filters.item_id.toString());
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);

    const response = await this.client.get<DiaryTimelineResponse>(`/api/diary/timeline?${params.toString()}`);
    return response.data;
  }

  // XP Tracker endpoints
  async createXPEntry(data: XPEntryCreate): Promise<XPEntry> {
    const response = await this.client.post<XPEntry>('/api/xp', data);
    return response.data;
  }

  async getXPEntries(startDate?: string, endDate?: string, limit?: number, offset?: number): Promise<XPEntryListResponse> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (limit) params.append('limit', limit.toString());
    if (offset) params.append('offset', offset.toString());

    const response = await this.client.get<XPEntryListResponse>(`/api/xp?${params.toString()}`);
    return response.data;
  }

  async getXPStats(days: number = 7): Promise<XPStats> {
    const response = await this.client.get<XPStats>(`/api/xp/stats?days=${days}`);
    return response.data;
  }

  async getXPEntry(id: string): Promise<XPEntry> {
    const response = await this.client.get<XPEntry>(`/api/xp/${id}`);
    return response.data;
  }

  async updateXPEntry(id: string, data: XPEntryUpdate): Promise<XPEntry> {
    const response = await this.client.put<XPEntry>(`/api/xp/${id}`, data);
    return response.data;
  }

  async deleteXPEntry(id: string): Promise<void> {
    await this.client.delete(`/api/xp/${id}`);
  }

  // Boss endpoints
  async getBosses(resetType?: string, activeOnly: boolean = true): Promise<BossListResponse> {
    const params = new URLSearchParams();
    if (resetType) params.append('reset_type', resetType);
    params.append('active_only', activeOnly.toString());

    const response = await this.client.get<BossListResponse>(`/api/bosses?${params.toString()}`);
    return response.data;
  }

  async getBoss(bossId: number): Promise<Boss> {
    const response = await this.client.get<Boss>(`/api/bosses/${bossId}`);
    return response.data;
  }

  // Boss Run endpoints
  async createBossRun(data: BossRunCreate): Promise<BossRun> {
    const response = await this.client.post<BossRun>('/api/tracking/runs', data);
    return response.data;
  }

  async getBossRuns(
    characterId?: string,
    bossId?: number,
    weekStart?: string,
    page: number = 1,
    pageSize: number = 20
  ): Promise<BossRunListResponse> {
    const params = new URLSearchParams();
    if (characterId) params.append('character_id', characterId);
    if (bossId) params.append('boss_id', bossId.toString());
    if (weekStart) params.append('week_start', weekStart);
    params.append('page', page.toString());
    params.append('page_size', pageSize.toString());

    const response = await this.client.get<BossRunListResponse>(`/api/tracking/runs?${params.toString()}`);
    return response.data;
  }

  async getBossRun(runId: string): Promise<BossRun> {
    const response = await this.client.get<BossRun>(`/api/tracking/runs/${runId}`);
    return response.data;
  }

  // Items (for manual drop entry)
  async getItems(search?: string, activeOnly: boolean = true): Promise<ItemListResponse> {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    params.append('active_only', activeOnly.toString());
    const response = await this.client.get<ItemListResponse>(`/api/items?${params.toString()}`);
    return response.data;
  }

  async createBossRunWithDrops(data: BossRunCreate, dropItemId: number, quantity: number = 1): Promise<BossRun> {
    // The backend accepts drop_item_ids; we repeat the item ID quantity times.
    const dropIds: number[] = [];
    for (let i = 0; i < quantity; i++) dropIds.push(dropItemId);
    const payload: BossRunCreate = {
      ...data,
      drop_item_ids: dropIds,
      is_clear: true,
    };
    const response = await this.client.post<BossRun>('/api/tracking/runs', payload);
    return response.data;
  }

  async updateBossRun(runId: string, data: BossRunUpdate): Promise<BossRun> {
    const response = await this.client.put<BossRun>(`/api/tracking/runs/${runId}`, data);
    return response.data;
  }

  async deleteBossRun(runId: string): Promise<void> {
    await this.client.delete(`/api/tracking/runs/${runId}`);
  }

  async addDropToRun(runId: string, itemId: number, quantity: number = 1): Promise<BossRunDrop> {
    const response = await this.client.post<BossRunDrop>(`/api/tracking/runs/${runId}/drops`, {
      item_id: itemId,
      quantity,
    });
    return response.data;
  }

  async getWeeklyProgress(characterId?: string, resetType: string = 'weekly'): Promise<WeeklySummary> {
    const params = new URLSearchParams();
    if (characterId) params.append('character_id', characterId);
    params.append('reset_type', resetType);

    const response = await this.client.get<WeeklySummary>(`/api/tracking/weekly?${params.toString()}`);
    return response.data;
  }

  // Character XP endpoints
  async fetchCharacterXP(characterId: string): Promise<CharacterXPSnapshot> {
    const response = await this.client.post<CharacterXPSnapshot>(`/api/character-xp/fetch/${characterId}`);
    return response.data;
  }

  async getCharacterXPHistory(characterId: string, days: number = 30): Promise<CharacterXPHistoryResponse> {
    const response = await this.client.get<CharacterXPHistoryResponse>(
      `/api/character-xp/history/${characterId}?days=${days}`
    );
    return response.data;
  }

  async getCharactersXPOverview(): Promise<CharacterXPOverviewListResponse> {
    const response = await this.client.get<CharacterXPOverviewListResponse>('/api/character-xp/overview');
    return response.data;
  }
}

export const api = new ApiClient();

