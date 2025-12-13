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

