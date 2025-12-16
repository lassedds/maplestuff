'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface Boss {
  id: number;
  name: string;
  difficulty: string | null;
  reset_type: string;
  crystal_meso: number | null;
}

interface WeeklyProgress {
  boss_id: number;
  boss_name: string;
  boss_difficulty: string | null;
  crystal_meso: number | null;
  cleared: boolean;
  cleared_at: string | null;
  character_name: string | null;
}

interface WeeklySummary {
  week_start: string;
  week_end: string;
  total_bosses: number;
  cleared_count: number;
  total_meso: number;
  progress: WeeklyProgress[];
}

interface Character {
  id: string;
  character_name: string;
  world: string;
}

export default function BossesPage() {
  const [summary, setSummary] = useState<WeeklySummary | null>(null);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [selectedCharacter, setSelectedCharacter] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.getCharacters(),
      api.getWeeklyProgress(),
    ])
      .then(([charRes, summaryRes]) => {
        setCharacters(charRes.characters || []);
        setSummary(summaryRes);
      })
      .catch((err) => setError('Failed to load data. Please sign in.'))
      .finally(() => setLoading(false));
  }, []);

  const handleCharacterChange = async (characterId: string) => {
    setSelectedCharacter(characterId);
    setLoading(true);
    try {
      const summaryRes = await api.getWeeklyProgress(characterId || undefined);
      setSummary(summaryRes);
    } catch (err) {
      setError('Failed to load progress');
    }
    setLoading(false);
  };

  const handleMarkCleared = async (bossId: number) => {
    if (!selectedCharacter && characters.length > 0) {
      alert('Please select a character first');
      return;
    }
    const characterId = selectedCharacter || characters[0]?.id;
    if (!characterId) {
      alert('No character available. Please add a character first.');
      return;
    }

    try {
      await api.createBossRun({
        boss_id: bossId,
        character_id: characterId,
        party_size: 1,
      });
      // Refresh data
      const summaryRes = await api.getWeeklyProgress(selectedCharacter || undefined);
      setSummary(summaryRes);
    } catch (err: any) {
      alert('Failed to mark boss as cleared');
    }
  };

  const formatMeso = (meso: number) => {
    if (meso >= 1_000_000_000) return `${(meso / 1_000_000_000).toFixed(1)}B`;
    if (meso >= 1_000_000) return `${(meso / 1_000_000).toFixed(0)}M`;
    return meso.toLocaleString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-maple-accent"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card text-center">
        <p className="text-red-400">{error}</p>
        <a href="/api/auth/discord" className="btn btn-primary mt-4 inline-block">
          Sign In
        </a>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Weekly Boss Tracker</h1>
          {summary && (
            <p className="text-slate-400">
              {summary.week_start} - {summary.week_end}
            </p>
          )}
        </div>

        {characters.length > 0 && (
          <select
            value={selectedCharacter}
            onChange={(e) => handleCharacterChange(e.target.value)}
            className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2"
          >
            <option value="">All Characters</option>
            {characters.map((char) => (
              <option key={char.id} value={char.id}>
                {char.character_name} ({char.world})
              </option>
            ))}
          </select>
        )}
      </div>

      {summary && (
        <>
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="card text-center">
              <div className="text-3xl font-bold text-maple-accent">
                {summary.cleared_count}/{summary.total_bosses}
              </div>
              <div className="text-slate-400 text-sm">Bosses Cleared</div>
            </div>
            <div className="card text-center">
              <div className="text-3xl font-bold text-green-400">
                {formatMeso(summary.total_meso)}
              </div>
              <div className="text-slate-400 text-sm">Meso Earned</div>
            </div>
            <div className="card text-center">
              <div className="text-3xl font-bold text-yellow-400">
                {Math.round((summary.cleared_count / summary.total_bosses) * 100)}%
              </div>
              <div className="text-slate-400 text-sm">Progress</div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Weekly Bosses</h2>
            <div className="space-y-2">
              {summary.progress.map((boss) => (
                <div
                  key={boss.boss_id}
                  className={`flex items-center justify-between p-3 rounded-lg ${
                    boss.cleared ? 'bg-green-900/30' : 'bg-slate-700/50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={boss.cleared}
                      onChange={() => !boss.cleared && handleMarkCleared(boss.boss_id)}
                      disabled={boss.cleared}
                      className="w-5 h-5 rounded"
                    />
                    <div>
                      <div className={boss.cleared ? 'line-through text-slate-400' : ''}>
                        {boss.boss_difficulty} {boss.boss_name}
                      </div>
                      {boss.cleared && boss.character_name && (
                        <div className="text-xs text-slate-500">
                          Cleared by {boss.character_name}
                        </div>
                      )}
                    </div>
                  </div>
                  {boss.crystal_meso && (
                    <div className="text-slate-400">
                      {formatMeso(boss.crystal_meso)}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {(!summary || summary.progress.length === 0) && (
        <div className="card text-center">
          <p className="text-slate-400">No weekly bosses found.</p>
          <p className="text-sm text-slate-500 mt-2">
            Make sure the database is seeded with boss data.
          </p>
        </div>
      )}
    </div>
  );
}
