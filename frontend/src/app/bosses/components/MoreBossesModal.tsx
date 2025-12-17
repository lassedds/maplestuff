'use client';

import React from 'react';
import { Boss } from '@/types';

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
  const [imageError, setImageError] = React.useState(false);
  const candidates = buildBossImageCandidates(boss);
  const [imageIdx, setImageIdx] = React.useState(0);
  const [imageSrc, setImageSrc] = React.useState<string | null>(candidates[0] ?? null);

  React.useEffect(() => {
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

interface MoreBossesModalProps {
  isOpen: boolean;
  onClose: () => void;
  hiddenBossGroups: Record<string, Boss[]>;
  pinnedBossIds: Map<string, Set<number>>;
  characterId: string;
  onPinBoss: (characterId: string, bossId: number) => void;
  maxPinned: number;
}

export default function MoreBossesModal({
  isOpen,
  onClose,
  hiddenBossGroups,
  pinnedBossIds,
  characterId,
  onPinBoss,
  maxPinned,
}: MoreBossesModalProps) {
  if (!isOpen) return null;

  const currentPinned = pinnedBossIds.get(characterId) || new Set<number>();
  const canPinMore = currentPinned.size < maxPinned;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-gray-800 rounded-lg border border-gray-700 w-full max-w-6xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-700">
          <h2 className="text-2xl font-bold text-white">
            More Bosses ({Object.keys(hiddenBossGroups).length})
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {Object.keys(hiddenBossGroups).length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-400 text-lg">All bosses are pinned!</p>
            </div>
          ) : (
            <>
              {!canPinMore && (
                <div className="mb-4 bg-yellow-900/20 border border-yellow-700 rounded-lg p-4">
                  <p className="text-yellow-400 text-sm">
                    You've reached the limit of {maxPinned} pinned bosses. Unpin a boss to pin another one.
                  </p>
                </div>
              )}
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                {Object.entries(hiddenBossGroups).map(([bossName, variants]) => {
                  const displayBoss = variants[0];
                  const isPinned = currentPinned.has(displayBoss.id);

                  return (
                    <div
                      key={bossName}
                      className={`bg-gray-700 rounded-lg p-4 border-2 transition-all ${
                        isPinned ? 'border-yellow-500 bg-yellow-900/20' : 'border-gray-600'
                      }`}
                    >
                      <BossImageDisplay boss={displayBoss} bossName={bossName} />
                      <h3 className="text-white font-semibold text-sm mb-2 text-center">{bossName}</h3>
                      <div className="text-gray-400 text-xs text-center mb-3">
                        {variants.length} variant{variants.length > 1 ? 's' : ''}
                      </div>
                      <button
                        onClick={() => {
                          if (canPinMore || isPinned) {
                            onPinBoss(characterId, displayBoss.id);
                          } else {
                            alert(`You can only pin ${maxPinned} bosses. Unpin another boss first.`);
                          }
                        }}
                        disabled={!canPinMore && !isPinned}
                        className={`w-full py-2 rounded text-xs font-medium transition-colors ${
                          isPinned
                            ? 'bg-yellow-600 hover:bg-yellow-700 text-white'
                            : canPinMore
                            ? 'bg-blue-600 hover:bg-blue-700 text-white'
                            : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                        }`}
                      >
                        {isPinned ? '✓ Pinned' : 'Pin Boss'}
                      </button>
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-700 p-4 flex justify-end">
          <button
            onClick={onClose}
            className="bg-gray-700 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
