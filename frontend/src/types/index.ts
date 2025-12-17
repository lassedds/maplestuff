// API Types
export interface User {
  id: string;
  discord_id: string;
  discord_username: string;
  discord_avatar: string | null;
  created_at: string;
  updated_at: string;
}

export interface Character {
  id: string;
  user_id: string;
  character_name: string;
  world: string;
  job: string | null;
  level: number | null;
  is_main: boolean;
  nexon_ocid: string | null;
  character_icon_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface CharacterCreate {
  character_name: string;
  world: string;
  job?: string;
  level?: number;
  is_main?: boolean;
}

export interface CharacterUpdate {
  job?: string;
  level?: number;
  is_main?: boolean;
}

export interface CharacterListResponse {
  characters: Character[];
  total: number;
}

export interface CharacterLookupRequest {
  character_name: string;
  world: string;
}

export interface CharacterLookupResponse {
  character_name: string;
  world: string;
  level: number | null;
  job: string | null;
  character_image: string | null;
  character_icon_url: string | null;
  nexon_ocid: string | null;
}

// Diary Types
export interface DiaryEntry {
  id: number;
  boss_run_id: string;
  item_id: number;
  item_name: string | null;
  quantity: number;
  character_id: string | null;
  character_name: string | null;
  boss_id: number | null;
  boss_name: string | null;
  boss_difficulty: string | null;
  cleared_at: string | null;
  created_at: string;
}

export interface DiaryListResponse {
  entries: DiaryEntry[];
  total: number;
  page: number;
  page_size: number;
}

export interface DiaryStats {
  total_drops: number;
  unique_items: number;
  unique_bosses: number;
  total_quantity: number;
  date_range_start: string | null;
  date_range_end: string | null;
  drops_by_boss: Array<{ boss_id: number; boss_name: string; count: number }>;
  drops_by_item: Array<{ item_id: number; item_name: string; count: number }>;
}

export interface DiaryTimelineEntry {
  date: string;
  entries: DiaryEntry[];
  total_drops: number;
}

export interface DiaryTimelineResponse {
  timeline: DiaryTimelineEntry[];
  total_entries: number;
}

export interface DiaryItem {
  item_id: number;
  item_name: string;
  drop_count: number;
  total_quantity: number;
  first_dropped: string | null;
  last_dropped: string | null;
}

export interface DiaryFilters {
  character_id?: string;
  boss_id?: number;
  item_id?: number;
  start_date?: string;
  end_date?: string;
  search?: string;
  page?: number;
  page_size?: number;
}

// XP Tracker Types
export interface XPEntry {
  id: string;
  user_id: string;
  entry_date: string;
  level: number;
  old_percent: number;
  new_percent: number;
  xp_gained_trillions: number;
  xp_gained_billions: number;
  epic_dungeon: boolean;
  epic_dungeon_xp_trillions: number | null;
  epic_dungeon_xp_billions: number | null;
  epic_dungeon_multiplier: number;
  total_daily_xp_trillions: number;
  total_daily_xp_billions: number;
  created_at: string;
  updated_at: string;
}

export interface XPEntryCreate {
  entry_date: string;
  level: number;
  old_percent: number;
  new_percent: number;
  epic_dungeon?: boolean;
  epic_dungeon_multiplier?: number;
}

export interface XPEntryUpdate {
  level?: number;
  old_percent?: number;
  new_percent?: number;
  epic_dungeon?: boolean;
  epic_dungeon_multiplier?: number;
}

export interface XPEntryListResponse {
  entries: XPEntry[];
  total: number;
}

export interface XPStats {
  seven_day_average_trillions: number;
  seven_day_average_billions: number;
  total_xp_trillions: number;
  total_xp_billions: number;
  entry_count: number;
}

// Character XP Tracking Types
export interface CharacterXPSnapshot {
  id: string;
  character_id: string;
  snapshot_date: string;
  total_xp: string; // Decimal as string
  level: number | null;
  created_at: string;
  updated_at: string;
}

export interface CharacterXPDailyGain {
  date: string;
  xp_gained: string; // Decimal as string
  level: number | null;
}

export interface CharacterXPHistoryResponse {
  character_id: string;
  character_name: string;
  daily_gains: CharacterXPDailyGain[];
  total_days: number;
  average_daily_xp: string; // Decimal as string
  total_xp_gained: string; // Decimal as string
}

export interface CharacterXPOverview {
  character_id: string;
  character_name: string;
  world: string;
  job: string | null;
  level: number | null;
  character_icon_url: string | null;
  current_xp: string | null; // Decimal as string
  xp_today: string | null; // Decimal as string
  xp_yesterday: string | null; // Decimal as string
  average_xp: string | null; // Decimal as string
  total_xp_gained: string | null; // Decimal as string
   progress_percent: string | null; // Decimal as string
  days_tracked: number;
}

export interface CharacterXPOverviewListResponse {
  characters: CharacterXPOverview[];
}

// Boss Types
export interface Boss {
  id: number;
  name: string;
  difficulty: string | null;
  reset_type: string;
  party_size: number;
  crystal_meso: number | null;
  image_url: string | null;
  sort_order: number;
  is_active: boolean;
}

export interface BossListResponse {
  bosses: Boss[];
  total: number;
}

export interface BossRunCreate {
  boss_id: number;
  character_id: string;
  cleared_at?: string;
  party_size?: number;
  notes?: string;
  is_clear?: boolean;
  drop_item_ids?: number[];
}

export interface BossRunUpdate {
  party_size?: number;
  notes?: string;
  is_clear?: boolean;
}

export interface BossRunDrop {
  id: number;
  item_id: number;
  item_name: string | null;
  quantity: number;
}

export interface BossRun {
  id: string;
  character_id: string;
  boss_id: number;
  cleared_at: string;
  week_start: string;
  party_size: number;
  notes: string | null;
  is_clear: boolean;
  created_at: string;
  character_name?: string | null;
  boss_name?: string | null;
  boss_difficulty?: string | null;
  drops?: BossRunDrop[];
}

export interface BossRunListResponse {
  runs: BossRun[];
  total: number;
  page: number;
  page_size: number;
}

export interface WeeklyBossProgress {
  boss_id: number;
  boss_name: string;
  boss_difficulty: string | null;
  reset_type: string;
  crystal_meso: number | null;
  cleared: boolean;
  cleared_at: string | null;
  character_id: string | null;
  character_name: string | null;
}

export interface WeeklySummary {
  week_start: string;
  week_end: string;
  total_bosses: number;
  cleared_count: number;
  total_meso: number;
  progress: WeeklyBossProgress[];
}

export interface Item {
  id: number;
  name: string;
  category: string | null;
  subcategory: string | null;
  rarity: string | null;
  image_url: string | null;
  is_active: boolean;
}

export interface ItemListResponse {
  items: Item[];
  total: number;
}

