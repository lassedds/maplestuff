import axios, { AxiosInstance } from 'axios';
import { User, Character, CharacterCreate, CharacterUpdate, CharacterListResponse } from '@/types';

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
}

export const api = new ApiClient();

