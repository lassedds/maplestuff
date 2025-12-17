'use client';

import { useEffect, useState } from 'react';
import { api } from '@/services/api';
import {
  Boss,
  BossRun,
  BossRunCreate,
  Character,
  WeeklySummary,
  WeeklyBossProgress,
} from '@/types';
import Link from 'next/link';
import BossSelectionModal from './components/BossSelectionModal';
import BossComparison from './components/BossComparison';
import MoreBossesModal from './components/MoreBossesModal';

const BOSS_ICON_BASE =
  'https://ufbyqlficreixurzzgnm.supabase.co/storage/v1/object/public/images/bosses/';
const BOSS_ICON_OVERRIDES: Record<string, string> = {
  seren: 'chosen-seren',
  'chosen seren': 'chosen-seren',
  kalos: 'kalos-the-guardian',
};

// Helper function to normalize boss name for file lookup
function normalizeBossName(name: string): string {
  return name.toLowerCase()
    .replace(/\s+/g, '_')
    .replace(/[^a-z0-9_]/g, '');
}

function slugBossName(name: string): string {
  const base = name.toLowerCase().trim();
  if (BOSS_ICON_OVERRIDES[base]) return BOSS_ICON_OVERRIDES[base];
  return base
    .replace(/['’]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function buildBossImageCandidates(boss: Boss): string[] {
  const candidates: string[] = [];
  if (boss.image_url) candidates.push(boss.image_url);

  const nameSlug = slugBossName(boss.name);
  if (nameSlug) {
    candidates.push(`${BOSS_ICON_BASE}${nameSlug}.webp`);
  }

  // Local legacy fallbacks
  const nameNorm = normalizeBossName(boss.name);
  candidates.push(`/bosses/${nameNorm}.png`);
  candidates.push(`/bosses/${nameNorm}.webp`);

  return candidates;
}

// Helper function to get boss image URL from local files
function getBossImageUrl(boss: Boss): string {
  // First check if boss has image_url in database
  if (boss.image_url) {
    return boss.image_url;
  }
  
  // Try to find local image file
  const bossName = normalizeBossName(boss.name);
  const difficulty = boss.difficulty ? normalizeBossName(boss.difficulty) : null;
  
  // Try with difficulty first: boss_name_difficulty.png
  if (difficulty) {
    return `/bosses/${bossName}_${difficulty}.png`;
  }
  
  // Try without difficulty: boss_name.png
  return `/bosses/${bossName}.png`;
}

// Component to handle boss image display with fallback
function BossImageDisplay({ boss, bossName }: { boss: Boss; bossName: string }) {
  const [imageError, setImageError] = useState(false);
  const [imageIdx, setImageIdx] = useState(0);
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const candidates = buildBossImageCandidates(boss);

  useEffect(() => {
    setImageError(false);
    setImageIdx(0);
    setImageSrc(candidates[0] ?? null);
  }, [boss, candidates]);

  const handleError = () => {
    const nextIdx = imageIdx + 1;
    if (nextIdx < candidates.length) {
      setImageIdx(nextIdx);
      setImageSrc(candidates[nextIdx]);
      setImageError(false);
    } else {
      setImageError(true);
    }
  };

  if (imageError) {
    return (
      <div className="relative mb-3 bg-gray-900 rounded flex items-center justify-center" style={{ minHeight: '128px' }}>
        <div className="text-gray-500 text-xs text-center p-4">
          <div className="text-4xl mb-2">🎮</div>
          <div>{bossName}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative mb-3 bg-gray-900 rounded flex items-center justify-center" style={{ minHeight: '128px' }}>
      <img
        src={imageSrc || undefined}
        alt={bossName}
        className="w-full h-32 object-contain rounded"
        onError={handleError}
      />
    </div>
  );
}

interface BossSettings {
  boss_id: number;
  character_id: string;
  party_size: number;
  cleared: boolean;
  run_id?: string; // If already cleared, store the run ID
}

export default function BossesPage() {
  const [bosses, setBosses] = useState<Boss[]>([]);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [weeklyProgress, setWeeklyProgress] = useState<WeeklySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterResetType, setFilterResetType] = useState<string>('weekly');
  const [selectedCharacter, setSelectedCharacter] = useState<string | null>(null); // null = overview, string = detailed view
  const [bossSettings, setBossSettings] = useState<Map<string, Map<number, BossSettings>>>(new Map()); // character_id -> boss_id -> settings
  const [existingRuns, setExistingRuns] = useState<Map<number, BossRun>>(new Map());
  const [showBossSelectionModal, setShowBossSelectionModal] = useState(false);
  const [pinnedBossIds, setPinnedBossIds] = useState<Map<string, Set<number>>>(new Map()); // character_id -> Set<boss_id>
  const [showMoreBossesModal, setShowMoreBossesModal] = useState(false);
  const MAX_PINNED_BOSSES = 14;

  useEffect(() => {
    loadData();
  }, [filterResetType]);

  useEffect(() => {
    // Load pinned bosses for all characters when characters load
    if (characters.length > 0) {
      characters.forEach(char => {
        loadPinnedBosses(char.id);
      });
    }
  }, [characters.length, filterResetType]);

  function loadPinnedBosses(characterId: string) {
    const stored = localStorage.getItem(`pinned_bosses_${characterId}_${filterResetType}`);
    if (stored) {
      try {
        const pinnedIds = JSON.parse(stored);
        const newMap = new Map(pinnedBossIds);
        newMap.set(characterId, new Set(pinnedIds));
        setPinnedBossIds(newMap);
      } catch (e) {
        console.error('Failed to load pinned bosses:', e);
      }
    }
  }

  function savePinnedBosses(characterId: string, pinned: Set<number>) {
    localStorage.setItem(`pinned_bosses_${characterId}_${filterResetType}`, JSON.stringify(Array.from(pinned)));
    const newMap = new Map(pinnedBossIds);
    newMap.set(characterId, pinned);
    setPinnedBossIds(newMap);
  }

  function togglePinBoss(characterId: string, bossId: number) {
    const currentPinned = pinnedBossIds.get(characterId) || new Set<number>();
    const newPinned = new Set(currentPinned);
    if (newPinned.has(bossId)) {
      newPinned.delete(bossId);
    } else {
      if (newPinned.size >= MAX_PINNED_BOSSES) {
        alert(`You can only pin ${MAX_PINNED_BOSSES} bosses at a time. Unpin another boss first.`);
        return;
      }
      newPinned.add(bossId);
    }
    savePinnedBosses(characterId, newPinned);
  }

  async function loadData() {
    setLoading(true);
    try {
      // Load characters
      const charsResponse = await api.getCharacters();
      setCharacters(charsResponse.characters);

      // Load bosses
      const bossesResponse = await api.getBosses(filterResetType);
      console.log('Loaded bosses:', bossesResponse.bosses.length, 'for reset type:', filterResetType);
      setBosses(bossesResponse.bosses);

      // Load progress for current reset type
      const progress = await api.getWeeklyProgress(undefined, filterResetType);
      setWeeklyProgress(progress);

      // Load existing runs for current period
      const runsResponse = await api.getBossRuns(undefined, undefined, undefined, 1, 100);
      const runsMap = new Map<number, BossRun>();
      const now = new Date();
      const todayStr = now.toISOString().split('T')[0];
      
      runsResponse.runs.forEach(run => {
        if (filterResetType === 'daily') {
          const runDateStr = run.cleared_at.split('T')[0];
          if (runDateStr === todayStr) {
            runsMap.set(run.boss_id, run);
          }
        } else {
          if (run.week_start === progress?.week_start) {
            runsMap.set(run.boss_id, run);
          }
        }
      });
      setExistingRuns(runsMap);

      // Initialize boss settings per character from localStorage
      const allSettingsMap = new Map<string, Map<number, BossSettings>>();
      
      charsResponse.characters.forEach(character => {
        const charSettingsMap = new Map<number, BossSettings>();
        
        bossesResponse.bosses.forEach(boss => {
          // Check for existing run for this character
          const existingRun = Array.from(runsMap.values()).find(
            r => r.boss_id === boss.id && r.character_id === character.id
          );
          
          // Check localStorage for this character's boss settings
          const storedKey = `boss_${character.id}_${boss.id}_${filterResetType}`;
          const stored = localStorage.getItem(storedKey);
          
          if (existingRun) {
            charSettingsMap.set(boss.id, {
              boss_id: boss.id,
              character_id: character.id,
              party_size: existingRun.party_size,
              cleared: true,
              run_id: existingRun.id,
            });
          } else if (stored) {
            const parsed = JSON.parse(stored);
            charSettingsMap.set(boss.id, {
              boss_id: boss.id,
              character_id: character.id,
              party_size: parsed.party_size || 1,
              cleared: false,
            });
          }
          // Don't auto-create settings - only show bosses that are explicitly assigned
        });
        
        if (charSettingsMap.size > 0) {
          allSettingsMap.set(character.id, charSettingsMap);
        }
      });
      
      setBossSettings(allSettingsMap);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  }

  function saveBossSettings(characterId: string, bossId: number, settings: BossSettings) {
    const newAllSettings = new Map(bossSettings);
    const charSettings = newAllSettings.get(characterId) || new Map<number, BossSettings>();
    charSettings.set(bossId, settings);
    newAllSettings.set(characterId, charSettings);
    setBossSettings(newAllSettings);
    
    // Save to localStorage per character
    const storedKey = `boss_${characterId}_${bossId}_${filterResetType}`;
    localStorage.setItem(storedKey, JSON.stringify({
      party_size: settings.party_size,
    }));
  }

  async function handleToggleBoss(characterId: string, bossId: number, cleared: boolean) {
    if (!characterId) {
      alert('Please select a character first');
      return;
    }

    const charSettings = bossSettings.get(characterId);
    const settings = charSettings?.get(bossId);
    if (!settings) {
      // Initialize settings if they don't exist
      const newSettings: BossSettings = {
        boss_id: bossId,
        character_id: characterId,
        party_size: 1,
        cleared: false,
      };
      saveBossSettings(characterId, bossId, newSettings);
      if (cleared) {
        await handleToggleBoss(characterId, bossId, true);
      }
      return;
    }

    try {
      if (cleared) {
        // Create boss run
        const runData: BossRunCreate = {
          boss_id: bossId,
          character_id: characterId,
          party_size: settings.party_size,
          is_clear: true,
          cleared_at: new Date().toISOString(),
        };
        const newRun = await api.createBossRun(runData);
        
        // Update settings
        saveBossSettings(characterId, bossId, {
          ...settings,
          cleared: true,
          run_id: newRun.id,
        });
      } else {
        // Delete boss run
        if (settings.run_id) {
          await api.deleteBossRun(settings.run_id);
        }
        
        // Update settings
        saveBossSettings(characterId, bossId, {
          ...settings,
          cleared: false,
          run_id: undefined,
        });
      }
      
      // Reload progress
      const progress = await api.getWeeklyProgress(undefined, filterResetType);
      setWeeklyProgress(progress);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to update boss run');
    }
  }

  async function handleUpdateSettings(characterId: string, bossId: number, field: 'party_size', value: number) {
    const charSettings = bossSettings.get(characterId);
    const settings = charSettings?.get(bossId);
    if (!settings) return;

    const updated = { ...settings, [field]: value };
    saveBossSettings(characterId, bossId, updated);

    // If boss is already cleared, update the run
    if (settings.cleared && settings.run_id) {
      api.updateBossRun(settings.run_id, {
        party_size: value,
      }).catch(err => console.error('Failed to update run:', err));
    }
  }

  // Get bosses for a specific character
  function getCharacterBosses(characterId: string): Boss[] {
    const charSettings = bossSettings.get(characterId);
    if (!charSettings) return [];
    
    const charBossIds = Array.from(charSettings.keys());
    return bosses.filter(boss => charBossIds.includes(boss.id));
  }

  // Group bosses by name for a character
  function getGroupedBossesForCharacter(characterId: string): Record<string, Boss[]> {
    const charBosses = getCharacterBosses(characterId);
    return charBosses.reduce((acc, boss) => {
      const name = boss.name;
      if (!acc[name]) {
        acc[name] = [];
      }
      acc[name].push(boss);
      return acc;
    }, {} as Record<string, Boss[]>);
  }

  // Get pinned bosses for a character
  function getPinnedBossesForCharacter(characterId: string): Record<string, Boss[]> {
    const pinned = pinnedBossIds.get(characterId) || new Set<number>();
    const grouped = getGroupedBossesForCharacter(characterId);
    const pinnedGroups: Record<string, Boss[]> = {};
    
    Object.entries(grouped).forEach(([bossName, variants]) => {
      if (variants.some(boss => pinned.has(boss.id))) {
        pinnedGroups[bossName] = variants;
      }
    });
    
    return pinnedGroups;
  }

  // Get hidden bosses for a character
  function getHiddenBossesForCharacter(characterId: string): Record<string, Boss[]> {
    const pinned = pinnedBossIds.get(characterId) || new Set<number>();
    const grouped = getGroupedBossesForCharacter(characterId);
    const hiddenGroups: Record<string, Boss[]> = {};
    
    Object.entries(grouped).forEach(([bossName, variants]) => {
      if (!variants.some(boss => pinned.has(boss.id))) {
        hiddenGroups[bossName] = variants;
      }
    });
    
    return hiddenGroups;
  }

  // Get active boss variant for character
  function getActiveBossForCharacter(characterId: string, bossVariants: Boss[]): Boss | null {
    const charSettings = bossSettings.get(characterId);
    if (!charSettings) return bossVariants[0] || null;
    
    // Find cleared boss first, then any with settings, then first variant
    return bossVariants.find(boss => {
      const settings = charSettings.get(boss.id);
      return settings && settings.cleared;
    }) || bossVariants.find(boss => charSettings.has(boss.id)) || bossVariants[0] || null;
  }

  // Check if boss is cleared for character
  function isBossCleared(characterId: string, bossId: number): boolean {
    const charSettings = bossSettings.get(characterId);
    const settings = charSettings?.get(bossId);
    if (settings?.cleared) return true;
    
    // Check existing runs
    const run = Array.from(existingRuns.values()).find(
      r => r.boss_id === bossId && r.character_id === characterId
    );
    return !!run;
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link href="/dashboard" className="text-xl font-bold text-white">
                MapleStory Tracker
              </Link>
            </div>
            <div className="flex items-center gap-4">
              <Link
                href="/dashboard"
                className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
              >
                Dashboard
              </Link>
              <Link
                href="/characters"
                className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
              >
                Characters
              </Link>
              <Link
                href="/diary"
                className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
              >
                Diary
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold text-white mb-2">Boss Tracker</h2>
            <p className="text-gray-400">Track your weekly and daily boss clears</p>
          </div>
          <button
            onClick={() => setShowBossSelectionModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
          >
            + Add Bosses
          </button>
        </div>

        {/* Weekly Progress Summary - Show always */}
        {(() => {
          let totalBosses = 0;
          let clearedCount = 0;
          let totalCrystals = 0;
          let totalMeso = 0;
          
          if (selectedCharacter) {
            // Detailed view: calculate for selected character
            const charBosses = getCharacterBosses(selectedCharacter);
            totalBosses = charBosses.length;
            clearedCount = charBosses.filter(boss => isBossCleared(selectedCharacter, boss.id)).length;
            charBosses.forEach(boss => {
              const cleared = isBossCleared(selectedCharacter, boss.id);
              if (cleared) {
                totalCrystals += boss.crystal_meso || 0;
                totalMeso += boss.crystal_meso || 0;
              }
            });
          } else {
            // Overview: calculate for all characters
            characters.forEach(character => {
              const charBosses = getCharacterBosses(character.id);
              totalBosses += charBosses.length;
              charBosses.forEach(boss => {
                const cleared = isBossCleared(character.id, boss.id);
                if (cleared) {
                  clearedCount++;
                  totalCrystals += boss.crystal_meso || 0;
                  totalMeso += boss.crystal_meso || 0;
                }
              });
            });
          }
          
          return (
            <div className="bg-gray-800 rounded-lg p-6 mb-6 border border-gray-700">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-semibold text-white">Progress Summary</h3>
                <div className="text-gray-400 text-sm">
                  {filterResetType === 'weekly' ? 'Weekly' : 'Daily'} Bosses
                  {selectedCharacter && ` • ${characters.find(c => c.id === selectedCharacter)?.character_name || 'Character'}`}
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <div className="bg-gray-700 rounded p-4">
                  <p className="text-gray-400 text-sm mb-1">Total Bosses</p>
                  <p className="text-2xl font-bold text-white">{totalBosses}</p>
                </div>
                <div className="bg-gray-700 rounded p-4">
                  <p className="text-gray-400 text-sm mb-1">Cleared</p>
                  <p className="text-2xl font-bold text-green-400">{clearedCount}</p>
                </div>
                <div className="bg-gray-700 rounded p-4">
                  <p className="text-gray-400 text-sm mb-1">Remaining</p>
                  <p className="text-2xl font-bold text-yellow-400">{totalBosses - clearedCount}</p>
                </div>
                <div className="bg-gray-700 rounded p-4">
                  <p className="text-gray-400 text-sm mb-1">Crystals</p>
                  <p className="text-2xl font-bold text-white">{totalCrystals.toLocaleString()}</p>
                </div>
                <div className="bg-gray-700 rounded p-4">
                  <p className="text-gray-400 text-sm mb-1">Meso Income</p>
                  <p className="text-2xl font-bold text-white">{totalMeso.toLocaleString()}</p>
                </div>
              </div>
            </div>
          );
        })()}

        {/* Filter Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => {
              setFilterResetType('weekly');
              loadData();
            }}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              filterResetType === 'weekly'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Weekly Bosses
          </button>
          <button
            onClick={() => {
              setFilterResetType('daily');
              loadData();
            }}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              filterResetType === 'daily'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Daily Bosses
          </button>
        </div>

        {/* Character Overview or Detailed View */}
        {selectedCharacter === null ? (
          /* Character Overview */
          <div className="space-y-6">
            {characters.length === 0 ? (
              <div className="text-center py-12 bg-gray-800 rounded-lg border border-gray-700">
                <p className="text-gray-400 text-lg">No characters found. Add a character first.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {characters.map((character) => {
                  const charBosses = getCharacterBosses(character.id);
                  const clearedCount = charBosses.filter(boss => isBossCleared(character.id, boss.id)).length;
                  const totalCount = charBosses.length;
                  
                  return (
                    <div
                      key={character.id}
                      className="bg-gray-800 rounded-lg p-6 border-2 border-gray-700 transition-all"
                    >
                      {/* Character Header - Clickable to go to detailed view */}
                      <div 
                        onClick={() => setSelectedCharacter(character.id)}
                        className="flex items-center gap-4 mb-4 cursor-pointer hover:opacity-80 transition-opacity"
                      >
                        {character.character_icon_url ? (
                          <img
                            src={character.character_icon_url}
                            alt={character.character_name}
                            className="w-16 h-16 rounded-full border-2 border-gray-600"
                          />
                        ) : (
                          <div className="w-16 h-16 rounded-full border-2 border-gray-600 bg-gray-700 flex items-center justify-center">
                            <span className="text-2xl">🎮</span>
                          </div>
                        )}
                        <div className="flex-1">
                          <h3 className="text-xl font-bold text-white">{character.character_name}</h3>
                          <p className="text-gray-400 text-sm">
                            {character.job || 'Unknown'} • Lv. {character.level || '?'} • {character.world}
                          </p>
                        </div>
                      </div>
                      
                      {/* Boss List */}
                      {totalCount === 0 ? (
                        <p className="text-gray-500 text-sm">No bosses assigned</p>
                      ) : (
                        <div className="space-y-1">
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-gray-400 text-sm">
                              {clearedCount}/{totalCount} cleared
                            </span>
                          </div>
                          <div className="space-y-1">
                            {charBosses.slice(0, 15).map((boss) => {
                              const cleared = isBossCleared(character.id, boss.id);
                              return (
                                <div
                                  key={boss.id}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleToggleBoss(character.id, boss.id, !cleared);
                                  }}
                                  className={`flex items-center gap-2 text-xs px-2 py-1 rounded transition-colors cursor-pointer hover:opacity-90 ${
                                    cleared
                                      ? 'bg-green-900/30 text-green-300'
                                      : 'bg-gray-700 text-gray-300'
                                  }`}
                                >
                                  <div
                                    className={`flex-shrink-0 w-6 h-6 rounded border-2 flex items-center justify-center transition-all ${
                                      cleared
                                        ? 'bg-green-600 border-green-500 shadow-lg shadow-green-500/50'
                                        : 'bg-gray-600 border-gray-500'
                                    }`}
                                  >
                                    {cleared && (
                                      <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                      </svg>
                                    )}
                                  </div>
                                  <span className={cleared ? 'line-through' : ''}>
                                    {boss.name} {boss.difficulty ? `(${boss.difficulty})` : ''}
                                  </span>
                                </div>
                              );
                            })}
                            {totalCount > 15 && (
                              <div className="text-xs px-2 py-1 rounded bg-gray-700 text-gray-400">
                                +{totalCount - 15} more
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ) : (
          /* Detailed Character View */
          <div>
            {(() => {
              const character = characters.find(c => c.id === selectedCharacter);
              if (!character) return null;
              
              const groupedBosses = getGroupedBossesForCharacter(selectedCharacter);
              const pinnedBossGroups = getPinnedBossesForCharacter(selectedCharacter);
              const hiddenBossGroups = getHiddenBossesForCharacter(selectedCharacter);
              
              return (
                <>
                  {/* Back Button */}
                  <button
                    onClick={() => setSelectedCharacter(null)}
                    className="mb-4 text-blue-400 hover:text-blue-300 flex items-center gap-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    Back to Overview
                  </button>
                  
                  {/* Character Header */}
                  <div className="bg-gray-800 rounded-lg p-6 mb-6 border border-gray-700">
                    <div className="flex items-center gap-4">
                      {character.character_icon_url ? (
                        <img
                          src={character.character_icon_url}
                          alt={character.character_name}
                          className="w-20 h-20 rounded-full border-2 border-gray-600"
                        />
                      ) : (
                        <div className="w-20 h-20 rounded-full border-2 border-gray-600 bg-gray-700 flex items-center justify-center">
                          <span className="text-3xl">🎮</span>
                        </div>
                      )}
                      <div>
                        <h2 className="text-2xl font-bold text-white">{character.character_name}</h2>
                        <p className="text-gray-400">
                          {character.job || 'Unknown'} • Lv. {character.level || '?'} • {character.world}
                        </p>
                      </div>
                      <div className="ml-auto flex gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setShowBossSelectionModal(true);
                          }}
                          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                        >
                          + Add Bosses
                        </button>
                      </div>
                    </div>
                  </div>
                  
                  {/* Pinned Bosses */}
                  {Object.keys(pinnedBossGroups).length > 0 && (
                    <div className="mb-6">
                      <div className="flex justify-between items-center mb-4">
                        <h3 className="text-xl font-semibold text-white">
                          Pinned Bosses ({(pinnedBossIds.get(selectedCharacter) || new Set()).size}/{MAX_PINNED_BOSSES})
                        </h3>
                        {Object.keys(hiddenBossGroups).length > 0 && (
                          <button
                            onClick={() => setShowMoreBossesModal(true)}
                            className="bg-gray-700 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                          >
                            More Bosses ({Object.keys(hiddenBossGroups).length})
                          </button>
                        )}
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                        {Object.entries(pinnedBossGroups).map(([bossName, bossVariants]) => {
                          const activeBoss = getActiveBossForCharacter(selectedCharacter, bossVariants);
                          if (!activeBoss) return null;
                          
                          const charSettings = bossSettings.get(selectedCharacter);
                          const settings = charSettings?.get(activeBoss.id);
                          const isCleared = isBossCleared(selectedCharacter, activeBoss.id);
                          const isPinned = (pinnedBossIds.get(selectedCharacter) || new Set()).has(activeBoss.id);
                          
                          return (
                            <div
                              key={bossName}
                              onClick={() => handleToggleBoss(selectedCharacter, activeBoss.id, !isCleared)}
                              className={`bg-gray-800 rounded-lg p-4 border-2 transition-all relative cursor-pointer hover:border-gray-600 ${
                                isCleared ? 'border-green-500 bg-green-900/20' : 'border-gray-700'
                              }`}
                            >
                              {/* Pin Button */}
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  togglePinBoss(selectedCharacter, activeBoss.id);
                                }}
                                className="absolute top-2 left-2 z-20 bg-gray-700 hover:bg-gray-600 rounded-full p-1.5 transition-colors"
                                title={isPinned ? 'Unpin boss' : 'Pin boss'}
                              >
                                {isPinned ? (
                                  <svg className="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                                    <path d="M10 2L3 7v11h4v-6h6v6h4V7l-7-5z" />
                                  </svg>
                                ) : (
                                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                                  </svg>
                                )}
                              </button>
                              
                              {/* Boss Image */}
                              <div className="relative">
                                <BossImageDisplay boss={activeBoss} bossName={bossName} />
                                {isCleared && (
                                  <div className="absolute top-2 right-2 bg-green-500 rounded-full w-8 h-8 flex items-center justify-center z-10 shadow-lg">
                                    <span className="text-white text-sm font-bold">✓</span>
                                  </div>
                                )}
                              </div>
                              
                              {/* Boss Name */}
                              <h3 className={`text-white font-semibold text-sm mb-2 text-center ${isCleared ? 'line-through opacity-75' : ''}`}>
                                {bossName}
                              </h3>
                              
                              {/* Difficulty Dropdown */}
                              <select
                                value={activeBoss?.difficulty || 'Normal'}
                                onChange={(e) => {
                                  e.stopPropagation();
                                  const selectedBoss = bossVariants.find(b => (b.difficulty || 'Normal') === e.target.value);
                                  if (selectedBoss) {
                                    const oldSettings = settings;
                                    const newSettings: BossSettings = {
                                      boss_id: selectedBoss.id,
                                      character_id: selectedCharacter,
                                      party_size: oldSettings?.party_size || 1,
                                      cleared: false,
                                    };
                                    saveBossSettings(selectedCharacter, selectedBoss.id, newSettings);
                                  }
                                }}
                                onClick={(e) => e.stopPropagation()}
                                className="w-full bg-gray-700 border border-gray-600 rounded px-2 py-1 text-white text-xs mb-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                              >
                                {bossVariants.map(boss => (
                                  <option key={boss.id} value={boss.difficulty || 'Normal'}>
                                    {boss.difficulty || 'Normal'}
                                  </option>
                                ))}
                              </select>
                              
                              {/* Cleared Status Indicator */}
                              <div className={`w-full py-2 rounded-lg text-sm font-semibold text-center mb-2 ${
                                isCleared
                                  ? 'bg-green-600 text-white'
                                  : 'bg-gray-700 text-gray-300'
                              }`}>
                                {isCleared ? '✓ Cleared' : 'Click to Clear'}
                              </div>
                              
                              {/* Party Size */}
                              <input
                                type="number"
                                min="1"
                                max="6"
                                value={settings?.party_size || 1}
                                onChange={(e) => {
                                  e.stopPropagation();
                                  const partySize = parseInt(e.target.value) || 1;
                                  if (!settings) {
                                    saveBossSettings(selectedCharacter, activeBoss.id, {
                                      boss_id: activeBoss.id,
                                      character_id: selectedCharacter,
                                      party_size: partySize,
                                      cleared: false,
                                    });
                                  } else {
                                    handleUpdateSettings(selectedCharacter, activeBoss.id, 'party_size', partySize);
                                  }
                                }}
                                onClick={(e) => e.stopPropagation()}
                                className="w-full bg-gray-700 border border-gray-600 rounded px-2 py-1 text-white text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Party"
                              />
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                  
                  {/* No Bosses Message */}
                  {Object.keys(groupedBosses).length === 0 && (
                    <div className="text-center py-12 bg-gray-800 rounded-lg border border-gray-700">
                      <p className="text-gray-400 text-lg">No bosses assigned to this character.</p>
                      <button
                        onClick={() => setShowBossSelectionModal(true)}
                        className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                      >
                        Add Bosses
                      </button>
                    </div>
                  )}
                </>
              );
            })()}
          </div>
        )}

        {/* Boss Comparison Tool */}
        <div className="mt-8 mb-6">
          <BossComparison />
        </div>

        {/* More Bosses Modal */}
        {selectedCharacter && (
          <MoreBossesModal
            isOpen={showMoreBossesModal}
            onClose={() => setShowMoreBossesModal(false)}
            hiddenBossGroups={getHiddenBossesForCharacter(selectedCharacter)}
            pinnedBossIds={pinnedBossIds}
            characterId={selectedCharacter}
            onPinBoss={togglePinBoss}
            maxPinned={MAX_PINNED_BOSSES}
          />
        )}

        {/* Boss Selection Modal */}
        <BossSelectionModal
          isOpen={showBossSelectionModal}
          onClose={() => setShowBossSelectionModal(false)}
          onSave={async (selectedBossIds, characterId, partySize) => {
            // Replace all bosses for this character (don't stack)
            try {
              // Enforce 14 boss limit
              if (selectedBossIds.length > 14) {
                alert(`You can only select up to 14 bosses (in-game limit). You selected ${selectedBossIds.length}.`);
                return;
              }

              // Clear all existing bosses for this character for this reset type
              const charSettings = bossSettings.get(characterId);
              if (charSettings) {
                // Remove all existing boss settings for this character
                const newAllSettings = new Map(bossSettings);
                newAllSettings.delete(characterId);
                setBossSettings(newAllSettings);
                
                // Clear from localStorage
                charSettings.forEach((settings, bossId) => {
                  const storedKey = `boss_${characterId}_${bossId}_${filterResetType}`;
                  localStorage.removeItem(storedKey);
                });
              }

              // Add new selected bosses
              for (const bossId of selectedBossIds) {
                saveBossSettings(characterId, bossId, {
                  boss_id: bossId,
                  character_id: characterId,
                  party_size: partySize,
                  cleared: false,
                });
              }
              
              await loadData();
            } catch (error: any) {
              alert(error.response?.data?.detail || 'Failed to update bosses');
            }
          }}
          bosses={selectedCharacter ? getCharacterBosses(selectedCharacter) : []}
          characters={characters}
          resetType={filterResetType}
          defaultCharacterId={selectedCharacter || undefined}
          onLoadAllBosses={async () => {
            const response = await api.getBosses(filterResetType);
            return response.bosses;
          }}
        />
      </main>
    </div>
  );
}
