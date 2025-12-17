/**
 * MapleStory.io API client for frontend.
 * Provides utilities to get item sprites, character renders, etc.
 */

const MAPLESTORY_IO_BASE = 'https://maplestory.io/api';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class MapleStoryAPI {
  /**
   * Get item sprite URL from our backend proxy.
   */
  static getItemSpriteUrl(
    itemId: number,
    region: string = 'GMS',
    version: string = 'latest',
    resize?: number
  ): string {
    const params = new URLSearchParams({
      region,
      version,
    });
    if (resize) {
      params.append('resize', resize.toString());
    }
    return `${API_URL}/api/maplestory/item/${itemId}/sprite-url?${params.toString()}`;
  }

  /**
   * Get item sprite URL directly from maplestory.io (bypasses our backend).
   */
  static getItemSpriteUrlDirect(
    itemId: number,
    region: string = 'GMS',
    version: string = 'latest',
    resize?: number
  ): string {
    let url = `${MAPLESTORY_IO_BASE}/${region}/${version}/item/${itemId}/icon`;
    if (resize) {
      url += `?resize=${resize}`;
    }
    return url;
  }

  /**
   * Get item info from our backend proxy.
   */
  static async getItemInfo(
    itemId: number,
    region: string = 'GMS',
    version: string = 'latest'
  ): Promise<any> {
    const response = await fetch(
      `${API_URL}/api/maplestory/item/${itemId}/info?region=${region}&version=${version}`
    );
    if (!response.ok) {
      throw new Error(`Failed to fetch item info: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get character render URL.
   * Note: This requires character data (equipment, etc.)
   */
  static getCharacterRenderUrl(
    characterData: any,
    region: string = 'GMS',
    version: string = 'latest'
  ): string {
    // This is a placeholder - actual implementation would require
    // constructing the render request with character equipment data
    return `${MAPLESTORY_IO_BASE}/${region}/${version}/character/render`;
  }
}


