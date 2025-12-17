'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { api } from '@/services/api';
import {
  CharacterXPOverview,
  CharacterXPHistoryResponse,
  User,
} from '@/types';

export default function XPTrackerPage() {
  const [overview, setOverview] = useState<CharacterXPOverview[]>([]);
  const [selectedCharacter, setSelectedCharacter] = useState<string | null>(null);
  const [history, setHistory] = useState<CharacterXPHistoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [fetching, setFetching] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const router = useRouter();

  useEffect(() => {
    loadUserAndData();
  }, []);

  useEffect(() => {
    if (selectedCharacter) {
      loadHistory(selectedCharacter);
    } else {
      setHistory(null);
    }
  }, [selectedCharacter]);

  const loadOverview = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.getCharactersXPOverview();
      setOverview(response.characters);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load XP overview');
    } finally {
      setLoading(false);
    }
  };

  const loadUserAndData = async () => {
    try {
      setLoading(true);
      setError(null);
      // Try to load current user; tolerate failure in no-login mode
      try {
        const u = await api.getCurrentUser();
        setUser(u);
      } catch (e) {
        console.log('Auth not required in debug mode');
      }
      await loadOverview();
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await api.logout();
      router.push('/');
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  const loadHistory = async (characterId: string) => {
    try {
      setError(null);
      const response = await api.getCharacterXPHistory(characterId, 30);
      setHistory(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load XP history');
    }
  };

  const handleFetchXP = async (characterId: string) => {
    try {
      setFetching(characterId);
      setError(null);
      await api.fetchCharacterXP(characterId);
      // Reload overview and history
      await loadOverview();
      if (selectedCharacter === characterId) {
        await loadHistory(characterId);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch XP from Nexon');
    } finally {
      setFetching(null);
    }
  };

  const formatXP = (xp: string | null | undefined): string => {
    if (xp === null || xp === undefined) return '—';
    // Preserve full precision; just add thousands separators.
    const str = xp.toString();
    const [intPart, decimalPart] = str.split('.');
    const withCommas = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return decimalPart ? `${withCommas}.${decimalPart}` : withCommas;
  };

  const formatCompactXP = (xp: string | null | undefined): string => {
    if (xp === null || xp === undefined) return '—';
    const num = Number(xp);
    if (!Number.isFinite(num)) return '—';
    const abs = Math.abs(num);
    if (abs >= 1e12) return `${(num / 1e12).toFixed(2)}T`;
    if (abs >= 1e9) return `${(num / 1e9).toFixed(2)}B`;
    if (abs >= 1e6) return `${(num / 1e6).toFixed(2)}M`;
    return num.toLocaleString(undefined, { maximumFractionDigits: 2 });
  };

  const displayXP = (xp: string | null | undefined): string => {
    const full = formatXP(xp);
    if (xp === null || xp === undefined) return full;
    const compact = formatCompactXP(xp);
    return `${full} (${compact})`;
  };

  const formatPercent = (pct: string | null | undefined): string => {
    if (pct === null || pct === undefined) return '—';
    const num = Number(pct);
    if (!Number.isFinite(num)) return '—';
    return `${num.toFixed(2)}%/100%`;
  };

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString();
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Top navigation bar (consistent with dashboard) */}
        <nav className="bg-gray-800 border-b border-gray-700 mb-8">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-bold text-white">MapleStory Tracker</h1>
              </div>
              <div className="flex items-center gap-4">
                <Link
                  href="/dashboard"
                  className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                >
                  Dashboard
                </Link>
                {user && <span className="text-gray-300">{user.discord_username}</span>}
                <Link
                  href="/bosses"
                  className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                >
                  Bosses
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
                <Link
                  href="/xp-tracker"
                  className="text-white px-3 py-2 rounded-md text-sm font-medium bg-blue-700/40"
                >
                  XP Tracker
                </Link>
                <button
                  onClick={handleLogout}
                  className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                >
                  Logout
                </button>
                {selectedCharacter && (
                  <button
                    onClick={() => setSelectedCharacter(null)}
                    className="bg-gray-700 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors ml-2"
                  >
                    ← Back to Overview
                  </button>
                )}
              </div>
            </div>
          </div>
        </nav>

        {error && (
          <div className="bg-red-900/50 border border-red-700 text-red-200 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {selectedCharacter === null ? (
          /* Character Overview */
          <div className="space-y-6">
            {overview.length === 0 ? (
              <div className="text-center py-12 bg-gray-800 rounded-lg border border-gray-700">
                <p className="text-gray-400 text-lg">No characters found. Add a character first.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {overview.map((char) => (
                  <div
                    key={char.character_id}
                    onClick={() => setSelectedCharacter(char.character_id)}
                    className="bg-gray-800 rounded-lg p-6 border-2 border-gray-700 hover:border-blue-500 cursor-pointer transition-all"
                  >
                    {/* Character Header */}
                    <div className="flex items-center gap-4 mb-4">
                      {char.character_icon_url ? (
                        <img
                          src={char.character_icon_url}
                          alt={char.character_name}
                          className="w-16 h-16 rounded-full border-2 border-gray-600"
                        />
                      ) : (
                        <div className="w-16 h-16 rounded-full border-2 border-gray-600 bg-gray-700 flex items-center justify-center">
                          <span className="text-2xl">🎮</span>
                        </div>
                      )}
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-white">{char.character_name}</h3>
                        <p className="text-gray-400 text-sm">
                          {char.job || 'Unknown'} • Lv. {char.level || '?'} • {char.world}
                        </p>
                      </div>
                      <div className="text-sm text-gray-300 font-semibold">
                        {formatPercent(char.progress_percent)}
                      </div>
                    </div>

                    {/* XP Stats */}
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-400 text-sm">Current XP</span>
                        <span className="text-white font-semibold">
                          {displayXP(char.current_xp)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-400 text-sm">XP Today</span>
                        <span className="text-white font-semibold">
                          {displayXP(char.xp_today)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-400 text-sm">XP Yesterday</span>
                        <span className="text-white font-semibold">
                          {displayXP(char.xp_yesterday)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-400 text-sm">7-Day Average</span>
                        <span className="text-green-400 font-semibold">
                          {displayXP(char.average_xp)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center pt-2 border-t border-gray-700">
                        <span className="text-gray-400 text-sm">Total Gained</span>
                        <span className="text-yellow-400 font-semibold">
                          {displayXP(char.total_xp_gained)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-400 text-sm">Days Tracked</span>
                        <span className="text-gray-300">{char.days_tracked}</span>
                      </div>
                    </div>

                    {/* Fetch Button */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleFetchXP(char.character_id);
                      }}
                      disabled={fetching === char.character_id}
                      className="w-full mt-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                    >
                      {fetching === char.character_id ? 'Fetching...' : 'Fetch Current XP'}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          /* Detailed Character View */
          history && (() => {
            const selectedChar = overview.find(c => c.character_id === selectedCharacter);
            return (
              <div className="space-y-6">
                {/* Character Header */}
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <div className="flex items-center gap-4">
                    {selectedChar?.character_icon_url ? (
                      <img
                        src={selectedChar.character_icon_url}
                        alt={selectedChar.character_name}
                        className="w-20 h-20 rounded-full border-2 border-gray-600"
                      />
                    ) : (
                      <div className="w-20 h-20 rounded-full border-2 border-gray-600 bg-gray-700 flex items-center justify-center">
                        <span className="text-3xl">🎮</span>
                      </div>
                    )}
                    <div>
                      <h2 className="text-2xl font-bold text-white">{selectedChar?.character_name}</h2>
                      <p className="text-gray-400">
                        {selectedChar?.job || 'Unknown'} • Lv. {selectedChar?.level || '?'} • {selectedChar?.world}
                      </p>
                    </div>
                    <div className="ml-auto text-sm text-gray-300 font-semibold">
                      {formatPercent(selectedChar?.progress_percent)}
                    </div>
                    <div className="ml-auto">
                      <button
                        onClick={() => handleFetchXP(selectedCharacter)}
                        disabled={fetching === selectedCharacter}
                        className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                      >
                        {fetching === selectedCharacter ? 'Fetching...' : 'Fetch Current XP'}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Summary Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <p className="text-gray-400 text-sm mb-1">Current XP</p>
                    <p className="text-2xl font-bold text-white">
                      {displayXP(selectedChar?.current_xp)}
                    </p>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <p className="text-gray-400 text-sm mb-1">Total Days Tracked</p>
                    <p className="text-2xl font-bold text-white">{history.total_days}</p>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <p className="text-gray-400 text-sm mb-1">Total XP Gained</p>
                    <p className="text-2xl font-bold text-yellow-400">{displayXP(history.total_xp_gained)}</p>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <p className="text-gray-400 text-sm mb-1">Average Daily XP</p>
                    <p className="text-2xl font-bold text-green-400">{displayXP(history.average_daily_xp)}</p>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <p className="text-gray-400 text-sm mb-1">Today's XP</p>
                    <p className="text-2xl font-bold text-white">
                      {history.daily_gains.length > 0 && history.daily_gains[history.daily_gains.length - 1].date === new Date().toISOString().split('T')[0]
                        ? displayXP(history.daily_gains[history.daily_gains.length - 1].xp_gained)
                        : 'N/A'}
                    </p>
                  </div>
                </div>

                {/* Daily XP History */}
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <h3 className="text-xl font-semibold mb-4">Daily XP History (Last 30 Days)</h3>
                  {history.daily_gains.length === 0 ? (
                    <p className="text-gray-400">
                      No daily gains yet. Fetch XP again on a later day to see changes over time.
                    </p>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b border-gray-700">
                            <th className="text-left py-2 px-4">Date</th>
                            <th className="text-left py-2 px-4">Level</th>
                            <th className="text-left py-2 px-4">XP Gained</th>
                          </tr>
                        </thead>
                        <tbody>
                          {history.daily_gains.slice().reverse().map((gain, index) => (
                            <tr key={index} className="border-b border-gray-700">
                              <td className="py-2 px-4">{formatDate(gain.date)}</td>
                              <td className="py-2 px-4">{gain.level || 'N/A'}</td>
                              <td className="py-2 px-4 font-semibold">{formatXP(gain.xp_gained)}</td>
                              <td className="py-2 px-4 text-gray-400 text-sm">{formatCompactXP(gain.xp_gained)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>
            );
          })()
        )}
      </div>
    </div>
  );
}
