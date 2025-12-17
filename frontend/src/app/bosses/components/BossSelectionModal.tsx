'use client';

import React, { useState, useEffect } from 'react';
import { Boss, Character } from '@/types';

const BOSS_ICON_BASE =
  'https://ufbyqlficreixurzzgnm.supabase.co/storage/v1/object/public/images/bosses/';
const BOSS_ICON_OVERRIDES: Record<string, string> = {
  seren: 'chosen-seren',
  'chosen seren': 'chosen-seren',
  kalos: 'kalos-the-guardian',
};

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
  // Local legacy fallbacks (name only)
  const nameNorm = boss.name
    .toLowerCase()
    .replace(/\s+/g, '_')
    .replace(/[^a-z0-9_]/g, '');
  candidates.push(`/bosses/${nameNorm}.png`);
  candidates.push(`/bosses/${nameNorm}.webp`);
  return candidates;
}

// Component to handle boss image display with fallback
function BossImageDisplay({ boss, bossName }: { boss: Boss; bossName: string }) {
  const [imageError, setImageError] = useState(false);
  const candidates = buildBossImageCandidates(boss);
  const [imageIdx, setImageIdx] = useState(0);
  const [imageSrc, setImageSrc] = useState<string | null>(candidates[0] ?? null);

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
        src={imageSrc}
        alt={bossName}
        className="w-full h-32 object-contain rounded"
        onError={handleError}
      />
    </div>
  );
}

interface BossPreset {
  id: string;
  name: string;
  boss_ids: number[];
  created_at: string;
}

interface BossSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (selectedBossIds: number[], characterId: string, partySizes: Map<number, number>) => void;
  bosses: Boss[];
  characters: Character[];
  resetType: string;
  defaultCharacterId?: string;
  onLoadAllBosses?: () => Promise<Boss[]>;
}

export default function BossSelectionModal({
  isOpen,
  onClose,
  onSave,
  bosses: trackedBosses,
  characters,
  resetType,
  defaultCharacterId,
  onLoadAllBosses,
}: BossSelectionModalProps) {
  const [selectedBossIds, setSelectedBossIds] = useState<Set<number>>(new Set());
  const [selectedCharacter, setSelectedCharacter] = useState<string>('');
  const [defaultPartySize, setDefaultPartySize] = useState<number>(1);
  const [bossPartySizes, setBossPartySizes] = useState<Map<number, number>>(new Map()); // boss_id -> party_size
  const [presets, setPresets] = useState<BossPreset[]>([]);
  const [presetName, setPresetName] = useState<string>('');
  const [showPresetSave, setShowPresetSave] = useState(false);
  const [allBosses, setAllBosses] = useState<Boss[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedBossDifficulties, setSelectedBossDifficulties] = useState<Map<string, string>>(new Map()); // boss name -> difficulty
  const [clearedBosses, setClearedBosses] = useState<Set<number>>(new Set()); // boss IDs that are cleared

  async function loadAllBosses() {
    if (onLoadAllBosses) {
      setLoading(true);
      try {
        const bosses = await onLoadAllBosses();
        setAllBosses(bosses);
      } catch (error) {
        console.error('Failed to load all bosses:', error);
        setAllBosses(trackedBosses);
      } finally {
        setLoading(false);
      }
    } else {
      setAllBosses(trackedBosses);
    }
  }

  function loadPresets() {
    const stored = localStorage.getItem(`boss_presets_${resetType}`);
    if (stored) {
      setPresets(JSON.parse(stored));
    }
  }

  useEffect(() => {
    if (isOpen) {
      if (characters.length > 0) {
        const charId = defaultCharacterId || characters[0].id;
        setSelectedCharacter(charId);
        
        // Pre-populate with character's current bosses from trackedBosses prop
        const currentBossIds = new Set<number>();
        const currentDifficulties = new Map<string, string>();
        
        // trackedBosses contains the bosses currently assigned to this character
        trackedBosses.forEach(boss => {
          currentBossIds.add(boss.id);
          currentDifficulties.set(boss.name, boss.difficulty || 'Normal');
        });
        
        setSelectedBossIds(currentBossIds);
        setSelectedBossDifficulties(currentDifficulties);
      }
      loadPresets();
      loadAllBosses();
    } else {
      // Reset when modal closes
      setSelectedBossIds(new Set());
      setSelectedBossDifficulties(new Map());
      setClearedBosses(new Set());
      setBossPartySizes(new Map());
    }
  }, [isOpen, characters.length, defaultCharacterId, resetType, trackedBosses]);

  function savePreset() {
    if (!presetName.trim() || selectedBossIds.size === 0) {
      alert('Please enter a preset name and select at least one boss');
      return;
    }

    const newPreset: BossPreset = {
      id: Date.now().toString(),
      name: presetName.trim(),
      boss_ids: Array.from(selectedBossIds),
      created_at: new Date().toISOString(),
    };

    const updated = [...presets, newPreset];
    localStorage.setItem(`boss_presets_${resetType}`, JSON.stringify(updated));
    setPresets(updated);
    setPresetName('');
    setShowPresetSave(false);
  }

  function loadPreset(preset: BossPreset) {
    setSelectedBossIds(new Set(preset.boss_ids));
  }

  function deletePreset(presetId: string) {
    const updated = presets.filter(p => p.id !== presetId);
    localStorage.setItem(`boss_presets_${resetType}`, JSON.stringify(updated));
    setPresets(updated);
  }

  function clonePresetToCharacter(preset: BossPreset, targetCharacterId: string) {
    // Clone preset settings for each boss to the target character
    preset.boss_ids.forEach(bossId => {
      const storedKey = `boss_${bossId}_${resetType}`;
      const stored = localStorage.getItem(storedKey);
      let settings: any = {};
      
      if (stored) {
        try {
          settings = JSON.parse(stored);
        } catch (e) {
          console.error('Failed to parse stored settings:', e);
        }
      }
      
      // Update character_id to target character
      settings.character_id = targetCharacterId;
      localStorage.setItem(storedKey, JSON.stringify(settings));
    });
    
    alert(`Preset "${preset.name}" cloned to ${characters.find(c => c.id === targetCharacterId)?.character_name || 'selected character'}`);
  }

  function handleBossClick(bossName: string, difficulties: Boss[]) {
    // Toggle selection - if already selected, deselect
    const currentBossId = Array.from(selectedBossIds).find(id => {
      const boss = allBosses.find(b => b.id === id);
      return boss?.name === bossName;
    });

    if (currentBossId) {
      // Deselect
      const newSet = new Set(selectedBossIds);
      newSet.delete(currentBossId);
      setSelectedBossIds(newSet);
      const newCleared = new Set(clearedBosses);
      newCleared.delete(currentBossId);
      setClearedBosses(newCleared);
    } else {
      // Check if we're at the limit
      if (selectedBossIds.size >= 14) {
        alert('You can only select up to 14 bosses (in-game limit).');
        return;
      }
      // Select first difficulty by default, but prefer Easy if available
      if (difficulties.length > 0) {
        const easyBoss = difficulties.find(b => b.difficulty === 'Easy');
        const defaultBoss = easyBoss || difficulties[0];
        setSelectedBossIds(new Set([...selectedBossIds, defaultBoss.id]));
        setSelectedBossDifficulties(new Map(selectedBossDifficulties).set(bossName, defaultBoss.difficulty || 'Normal'));
      }
    }
  }

  function handleDifficultyChange(bossName: string, difficulty: string, difficulties: Boss[]) {
    const boss = difficulties.find(b => (b.difficulty || 'Normal') === difficulty);
    if (boss) {
      // Remove old selection
      const oldBossId = Array.from(selectedBossIds).find(id => {
        const b = allBosses.find(bb => bb.id === id);
        return b?.name === bossName;
      });
      
      const newSet = new Set(selectedBossIds);
      if (oldBossId) newSet.delete(oldBossId);
      newSet.add(boss.id);
      setSelectedBossIds(newSet);
      
      setSelectedBossDifficulties(new Map(selectedBossDifficulties).set(bossName, difficulty));
    }
  }

  function toggleCleared(bossId: number) {
    const newCleared = new Set(clearedBosses);
    if (newCleared.has(bossId)) {
      newCleared.delete(bossId);
    } else {
      newCleared.add(bossId);
    }
    setClearedBosses(newCleared);
  }

  function getBossPartySize(bossId: number): number {
    return bossPartySizes.get(bossId) || defaultPartySize;
  }

  function setBossPartySize(bossId: number, size: number) {
    const newMap = new Map(bossPartySizes);
    newMap.set(bossId, size);
    setBossPartySizes(newMap);
  }

  function handleSave() {
    if (selectedBossIds.size === 0) {
      alert('Please select at least one boss');
      return;
    }
    if (selectedBossIds.size > 14) {
      alert(`You can only select up to 14 bosses (in-game limit). You selected ${selectedBossIds.size}.`);
      return;
    }
    if (!selectedCharacter) {
      alert('Please select a character');
      return;
    }
    // Build party sizes map with defaults for any bosses not explicitly set
    const finalPartySizes = new Map<number, number>();
    selectedBossIds.forEach(bossId => {
      finalPartySizes.set(bossId, getBossPartySize(bossId));
    });
    onSave(Array.from(selectedBossIds), selectedCharacter, finalPartySizes);
    setSelectedBossIds(new Set());
    setClearedBosses(new Set());
    setSelectedBossDifficulties(new Map());
    setBossPartySizes(new Map());
    onClose();
  }

  // Group bosses by name
  const bossesByName = new Map<string, Boss[]>();
  allBosses.forEach(boss => {
    const name = boss.name;
    if (!bossesByName.has(name)) {
      bossesByName.set(name, []);
    }
    bossesByName.get(name)!.push(boss);
  });

  // Get selected boss ID for a boss name
  function getSelectedBossId(bossName: string): number | null {
    return Array.from(selectedBossIds).find(id => {
      const boss = allBosses.find(b => b.id === id);
      return boss?.name === bossName;
    }) || null;
  }

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75">
      <div className="bg-gray-800 rounded-lg border border-gray-700 w-full max-w-6xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-700 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-white">Select Bosses</h2>
            <p className="text-gray-400 text-sm mt-1">
              Click on boss images to select them
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl font-bold"
          >
            ×
          </button>
        </div>

        {/* Controls */}
        <div className="p-4 border-b border-gray-700 flex gap-4 items-center flex-wrap">
          <div className="flex gap-2 items-center">
            <select
              value={selectedCharacter}
              onChange={(e) => setSelectedCharacter(e.target.value)}
              className="bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {characters.map(char => (
                <option key={char.id} value={char.id}>
                  {char.character_name}
                </option>
              ))}
            </select>

            <select
              value={defaultPartySize}
              onChange={(e) => setDefaultPartySize(parseInt(e.target.value) || 1)}
              className="bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              title="Default party size for new bosses"
            >
              <option value={1}>Default: Solo (1)</option>
              <option value={2}>Default: Duo (2)</option>
              <option value={3}>Default: 3 Players</option>
              <option value={4}>Default: 4 Players</option>
              <option value={5}>Default: 5 Players</option>
              <option value={6}>Default: Full Party (6)</option>
            </select>
          </div>

          {presets.length > 0 && (
            <div className="flex-1">
              <span className="text-gray-400 text-sm mb-2 block">Presets:</span>
              <div className="space-y-2">
                {presets.map(preset => (
                  <div key={preset.id} className="flex items-center gap-2 bg-gray-700 rounded px-3 py-2">
                    <button
                      onClick={() => loadPreset(preset)}
                      className="text-white hover:text-blue-400 text-sm flex-1 text-left"
                    >
                      {preset.name} ({preset.boss_ids.length} bosses)
                    </button>
                    <select
                      onChange={(e) => {
                        if (e.target.value) {
                          clonePresetToCharacter(preset, e.target.value);
                          e.target.value = '';
                        }
                      }}
                      className="bg-gray-600 border border-gray-500 rounded px-2 py-1 text-white text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
                      defaultValue=""
                    >
                      <option value="">Clone to...</option>
                      {characters.map(char => (
                        <option key={char.id} value={char.id}>
                          {char.character_name}
                        </option>
                      ))}
                    </select>
                    <button
                      onClick={() => {
                        if (confirm(`Delete preset "${preset.name}"?`)) {
                          deletePreset(preset.id);
                        }
                      }}
                      className="text-red-400 hover:text-red-300 text-lg px-2"
                      title="Delete preset"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {selectedBossIds.size > 0 && (
            <button
              onClick={() => setShowPresetSave(!showPresetSave)}
              className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded-md text-sm font-medium"
            >
              {showPresetSave ? 'Cancel' : 'Save Preset'}
            </button>
          )}

          {showPresetSave && (
            <div className="flex gap-2 items-center">
              <input
                type="text"
                placeholder="Preset name..."
                value={presetName}
                onChange={(e) => setPresetName(e.target.value)}
                className="bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                onKeyPress={(e) => e.key === 'Enter' && savePreset()}
              />
              <button
                onClick={savePreset}
                className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded-md text-sm font-medium"
              >
                Save
              </button>
            </div>
          )}
        </div>

        {/* Boss Grid */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="mb-4 flex justify-between items-center">
            <span className="text-gray-400 text-sm">
              Selected: {selectedBossIds.size}/14 boss{selectedBossIds.size !== 1 ? 'es' : ''}
            </span>
            {selectedBossIds.size >= 14 && (
              <span className="text-yellow-400 text-xs">⚠️ 14 boss limit reached</span>
            )}
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
              <p className="text-gray-400">Loading bosses...</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              {Array.from(bossesByName.entries()).map(([bossName, difficulties]) => {
                const selectedBossId = getSelectedBossId(bossName);
                const selectedBoss = selectedBossId ? allBosses.find(b => b.id === selectedBossId) : null;
                const selectedDifficulty = selectedBossDifficulties.get(bossName) || (difficulties[0]?.difficulty || 'Normal');
                const isSelected = selectedBossId !== null;
                const isCleared = selectedBossId ? clearedBosses.has(selectedBossId) : false;
                const displayBoss = selectedBoss || difficulties[0];

                return (
                  <div
                    key={bossName}
                    className={`bg-gray-700 rounded-lg p-4 border-2 transition-all cursor-pointer ${
                      isSelected ? 'border-blue-500 bg-blue-900/20' : 'border-gray-600 hover:border-gray-500'
                    }`}
                    onClick={() => handleBossClick(bossName, difficulties)}
                  >
                    {/* Boss Image */}
                    <div className="relative">
                      <BossImageDisplay boss={displayBoss} bossName={bossName} />
                      {isSelected && (
                        <div className="absolute top-2 right-2 bg-blue-500 rounded-full w-6 h-6 flex items-center justify-center z-10">
                          <span className="text-white text-xs">✓</span>
                        </div>
                      )}
                    </div>

                    {/* Boss Name */}
                    <h3 className="text-white font-semibold text-sm mb-2 text-center">{bossName}</h3>

                    {/* Difficulty & Party Size Dropdowns */}
                    {isSelected && selectedBossId && (
                      <div className="space-y-2" onClick={(e) => e.stopPropagation()}>
                        <select
                          value={selectedDifficulty}
                          onChange={(e) => handleDifficultyChange(bossName, e.target.value, difficulties)}
                          className="w-full bg-gray-600 border border-gray-500 rounded px-2 py-1 text-white text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          {difficulties.map(boss => (
                            <option key={boss.id} value={boss.difficulty || 'Normal'}>
                              {boss.difficulty || 'Normal'}
                            </option>
                          ))}
                        </select>

                        {/* Party Size Dropdown */}
                        <select
                          value={getBossPartySize(selectedBossId)}
                          onChange={(e) => setBossPartySize(selectedBossId, parseInt(e.target.value) || 1)}
                          className="w-full bg-gray-600 border border-gray-500 rounded px-2 py-1 text-white text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value={1}>Solo (1)</option>
                          <option value={2}>Duo (2)</option>
                          <option value={3}>3 Players</option>
                          <option value={4}>4 Players</option>
                          <option value={5}>5 Players</option>
                          <option value={6}>Full Party (6)</option>
                        </select>

                        {/* Cleared Toggle */}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            if (selectedBossId) toggleCleared(selectedBossId);
                          }}
                          className={`w-full py-1.5 rounded text-xs font-medium transition-colors ${
                            isCleared
                              ? 'bg-green-600 hover:bg-green-700 text-white'
                              : 'bg-gray-600 hover:bg-gray-500 text-gray-300'
                          }`}
                        >
                          {isCleared ? '✓ Cleared' : 'Not Cleared'}
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-700 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-md font-medium"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium"
          >
            Add {selectedBossIds.size} Boss{selectedBossIds.size !== 1 ? 'es' : ''}
          </button>
        </div>
      </div>
    </div>
  );
}
