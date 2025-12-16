'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface Overview {
  total_runs_logged: number;
  total_drops_logged: number;
  unique_contributors: number;
  most_tracked_boss: string | null;
  most_dropped_item: string | null;
}

interface LeaderboardEntry {
  rank: number;
  item_name: string;
  boss_name: string;
  drop_rate: number;
  sample_size: number;
}

interface Leaderboard {
  title: string;
  entries: LeaderboardEntry[];
}

export default function StatsPage() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [leaderboard, setLeaderboard] = useState<Leaderboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getStatsOverview(),
      api.getRareDropsLeaderboard(),
    ])
      .then(([overviewRes, leaderboardRes]) => {
        setOverview(overviewRes);
        setLeaderboard(leaderboardRes);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-maple-accent"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Community Statistics</h1>

      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="card text-center">
            <div className="text-2xl font-bold text-maple-accent">
              {overview.total_runs_logged.toLocaleString()}
            </div>
            <div className="text-slate-400 text-sm">Total Runs</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-green-400">
              {overview.total_drops_logged.toLocaleString()}
            </div>
            <div className="text-slate-400 text-sm">Drops Logged</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-yellow-400">
              {overview.unique_contributors}
            </div>
            <div className="text-slate-400 text-sm">Contributors</div>
          </div>
          <div className="card text-center">
            <div className="text-lg font-bold text-purple-400 truncate">
              {overview.most_tracked_boss || 'N/A'}
            </div>
            <div className="text-slate-400 text-sm">Most Tracked</div>
          </div>
        </div>
      )}

      {leaderboard && leaderboard.entries.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">{leaderboard.title}</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-slate-400 border-b border-slate-700">
                  <th className="pb-2 w-12">#</th>
                  <th className="pb-2">Item</th>
                  <th className="pb-2">Boss</th>
                  <th className="pb-2 text-right">Drop Rate</th>
                  <th className="pb-2 text-right">Sample</th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.entries.map((entry) => (
                  <tr key={entry.rank} className="border-b border-slate-700/50">
                    <td className="py-3 text-slate-400">{entry.rank}</td>
                    <td className="py-3">{entry.item_name}</td>
                    <td className="py-3 text-slate-400">{entry.boss_name}</td>
                    <td className="py-3 text-right text-yellow-400">
                      {(entry.drop_rate * 100).toFixed(2)}%
                    </td>
                    <td className="py-3 text-right text-slate-400">
                      {entry.sample_size}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {(!leaderboard || leaderboard.entries.length === 0) && (
        <div className="card text-center">
          <p className="text-slate-400">No drop statistics available yet.</p>
          <p className="text-sm text-slate-500 mt-2">
            Start logging boss runs to contribute to community statistics!
          </p>
        </div>
      )}
    </div>
  );
}
