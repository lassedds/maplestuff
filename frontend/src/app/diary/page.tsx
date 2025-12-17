'use client';

import { useEffect, useMemo, useState } from 'react';
import { api } from '@/services/api';
import {
  DiaryEntry,
  DiaryStats,
  DiaryTimelineResponse,
  DiaryFilters,
  Character,
  Boss,
  Item,
} from '@/types';
import Link from 'next/link';

export default function DiaryPage() {
  const [entries, setEntries] = useState<DiaryEntry[]>([]);
  const [timeline, setTimeline] = useState<DiaryTimelineResponse | null>(null);
  const [stats, setStats] = useState<DiaryStats | null>(null);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'list' | 'timeline'>('list');
  const [filters, setFilters] = useState<DiaryFilters>({
    page: 1,
    page_size: 5,
  });
  const [totalPages, setTotalPages] = useState(1);
  // Manual drop entry
  const [bosses, setBosses] = useState<Boss[]>([]);
  const [items, setItems] = useState<Item[]>([]);
  const [addDropLoading, setAddDropLoading] = useState(false);
  const [addDropError, setAddDropError] = useState<string | null>(null);
  const userTimeZone =
    typeof Intl !== 'undefined'
      ? Intl.DateTimeFormat().resolvedOptions().timeZone || 'Europe/Berlin'
      : 'Europe/Berlin';

  const getLocalDateInput = () =>
    new Intl.DateTimeFormat('en-CA', {
      timeZone: userTimeZone,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    }).format(new Date());

  const toLocalISODateTime = (dateInput: string) => {
    // Interpret the provided date in the user's timezone at midnight, then convert to ISO
    const localDate = new Date(`${dateInput}T00:00:00`);
    const offsetMs = localDate.getTimezoneOffset() * 60000;
    return new Date(localDate.getTime() - offsetMs).toISOString();
  };

  const [dropForm, setDropForm] = useState({
    character_id: '',
    item_id: '',
    date: getLocalDateInput(),
  });

  const formatDate = (iso?: string | null) => {
    if (!iso) return 'Unknown';
    return new Intl.DateTimeFormat('en-CA', {
      timeZone: userTimeZone,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    }).format(new Date(iso));
  };
  const formatDateTime = (iso?: string | null) => {
    if (!iso) return 'Unknown';
    return new Intl.DateTimeFormat('en-GB', {
      timeZone: userTimeZone,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    }).format(new Date(iso));
  };

  const ICON_BASE =
    'https://ufbyqlficreixurzzgnm.supabase.co/storage/v1/object/public/images/drops/';
  const getItemIcon = (name?: string | null) => {
    if (!name) return null;
    const lower = name.toLowerCase();
    // Arcane boxes have no icon; use fallback
    if (/arcane\s+.*box/i.test(lower)) return null;
    // Mitra's Rage has class variants; default to warrior
    if (lower.includes("mitra's rage") || lower.includes('mitras rage')) {
      return `${ICON_BASE}mitra_rage_warrior.webp`;
    }
    // Map specific known variants to bucket naming
    if (/cursed\s+spellbook/i.test(lower)) {
      // default to warrior variant; adjust if more detailed data is available
      return `${ICON_BASE}cursed_spellbook_warrior.webp`;
    }
    const slug = name
      .toLowerCase()
      .replace(/['’]/g, '')
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '');
    return `${ICON_BASE}${slug}.webp`;
  };

  // Fixed item options for quick add (single entry per item) in desired order
  const ITEM_PATTERNS = useMemo(
    () => [
      { label: 'Black Heart', test: /black heart/i },
      { label: 'Endless Terror', test: /endless terror/i },
      { label: 'Source of Suffering', test: /source of suffering/i },
      { label: 'Magic Eyepatch', test: /magic eyepatch/i },
      { label: 'Berserked', test: /berserked/i },
      { label: 'Dreamy Belt', test: /dreamy belt/i },
      { label: 'Commanding Force Earring', test: /commanding force earring/i },
      // Only Mitra's Rage should appear (no other Mitra items)
      { label: "Mitra's Rage", test: /mitra's rage/i },
      { label: 'Cursed Spellbook', test: /cursed spellbook/i },
      { label: 'Grindstone', test: /grindstone/i },
      // Match Arcane Umbra variants as well
      { label: 'Arcane Armor Box', test: /arcane(\s+umbra)?\s+armor box/i },
      { label: 'Arcane Weapon Box', test: /arcane(\s+umbra)?\s+weapon box/i },
    ],
    []
  );

  useEffect(() => {
    loadData();
    loadSelectors();
  }, [filters, viewMode]);

  // Build daily series for bottom chart (cumulative over time)
  const dailySeries = useMemo(() => {
    const byDate = new Map<string, number>();
    if (viewMode === 'timeline' && timeline) {
      timeline.timeline.forEach((day) => {
        const d = formatDate(day.date);
        byDate.set(d, (byDate.get(d) || 0) + (day.total_drops || 0));
      });
    } else {
      entries.forEach((e) => {
        const d = formatDate(e.cleared_at || e.created_at);
        byDate.set(d, (byDate.get(d) || 0) + (e.quantity || 1));
      });
    }
    const sorted = Array.from(byDate.entries()).sort((a, b) => a[0].localeCompare(b[0]));
    let cumulative = 0;
    return sorted.map(([date, count]) => {
      cumulative += count;
      return { date, count, cumulative };
    });
  }, [entries, timeline, viewMode]);

  // Set sensible defaults once data arrives
  useEffect(() => {
    if (!dropForm.item_id && items.length > 0) {
      setDropForm((f) => ({ ...f, item_id: items[0].id.toString() }));
    }
    if (!dropForm.character_id && characters.length > 0) {
      setDropForm((f) => ({ ...f, character_id: characters[0].id }));
    }
  }, [items, characters, dropForm.item_id, dropForm.character_id]);

  async function loadData() {
    setLoading(true);
    try {
      // Load characters for filter
      const charsResponse = await api.getCharacters();
      setCharacters(charsResponse.characters);

      // Load stats
      const statsData = await api.getDiaryStats(filters);
      setStats(statsData);

      // Load entries or timeline based on view mode
      if (viewMode === 'timeline') {
        const timelineData = await api.getDiaryTimeline(filters);
        setTimeline(timelineData);
        setEntries([]);
      } else {
        const entriesData = await api.getDiaryEntries(filters);
        setEntries(entriesData.entries);
        setTotalPages(Math.ceil(entriesData.total / (filters.page_size || 20)));
        setTimeline(null);
      }
    } catch (error) {
      console.error('Failed to load diary data:', error);
    } finally {
      setLoading(false);
    }
  }

  async function loadSelectors() {
    try {
      const bossesResp = await api.getBosses();
      setBosses(bossesResp.bosses);
      // Limit to specific items only using patterns; pick first match per pattern
      const itemsResp = await api.getItems(undefined, true);
      const picked: Item[] = [];
      ITEM_PATTERNS.forEach((pat) => {
        const found = itemsResp.items.find((it) => pat.test.test(it.name));
        if (found) {
          picked.push({ ...found, name: pat.label });
        }
      });
      setItems(picked);
      // Set defaults if empty
      if (!dropForm.item_id && picked.length > 0) {
        setDropForm((f) => ({ ...f, item_id: picked[0].id.toString() }));
      }
      if (!dropForm.character_id && characters.length > 0) {
        setDropForm((f) => ({ ...f, character_id: characters[0].id }));
      }
    } catch (error) {
      console.error('Failed to load selectors:', error);
    }
  }

  async function handleAddDrop(e: React.FormEvent) {
    e.preventDefault();
    if (!dropForm.character_id || !dropForm.item_id) {
      setAddDropError('Select character and item');
      return;
    }
    setAddDropError(null);
    setAddDropLoading(true);
    try {
      // pick any boss (not shown in UI); default to first active or id 1
      const bossId = bosses[0]?.id ?? 1;
      const itemId = Number(dropForm.item_id);
      if (!Number.isFinite(itemId)) {
        throw new Error('Invalid item selection');
      }

      await api.createBossRunWithDrops(
        {
          boss_id: bossId,
          character_id: dropForm.character_id,
          cleared_at: toLocalISODateTime(dropForm.date),
        },
        itemId,
        1
      );
      await loadData();
    } catch (err: any) {
      setAddDropError(err.response?.data?.detail || 'Failed to add drop');
    } finally {
      setAddDropLoading(false);
    }
  }

  async function handleAddArcaneBox(type: 'armor' | 'weapon') {
    if (!dropForm.character_id) {
      setAddDropError('Select character first');
      return;
    }
    setAddDropError(null);
    setAddDropLoading(true);
    try {
      const bossId = bosses[0]?.id ?? 1;
      const matchName = type === 'armor' ? 'Arcane Armor Box' : 'Arcane Weapon Box';
      const item = items.find((it) => it.name === matchName);
      if (!item) {
        throw new Error(`${matchName} not found in item list`);
      }
      await api.createBossRunWithDrops(
        {
          boss_id: bossId,
          character_id: dropForm.character_id,
          cleared_at: toLocalISODateTime(dropForm.date),
        },
        item.id,
        1
      );
      await loadData();
    } catch (err: any) {
      setAddDropError(err.response?.data?.detail || err.message || 'Failed to add box');
    } finally {
      setAddDropLoading(false);
    }
  }

  function updateFilters(newFilters: Partial<DiaryFilters>) {
    setFilters({ ...filters, ...newFilters, page: 1 });
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
                href="/xp-tracker"
                className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
              >
                XP Tracker
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">Drop Diary</h2>
          <p className="text-gray-400">View your complete drop history and statistics</p>
        </div>

        {/* Manual drop entry - compact card */}
        <div className="bg-gray-800 rounded-lg p-5 mb-6 border border-gray-700 max-w-7xl">
          <h3 className="text-xl font-semibold text-white mb-3">Add Drop</h3>
          <form className="grid grid-cols-1 lg:grid-cols-5 gap-4 items-end" onSubmit={handleAddDrop}>
            <div className="flex flex-col">
              <label className="text-sm text-gray-300 mb-1">Character</label>
              <select
                value={dropForm.character_id}
                onChange={(e) => setDropForm({ ...dropForm, character_id: e.target.value })}
                className="bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select</option>
                {characters.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.character_name} ({c.world})
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-col">
              <label className="text-sm text-gray-300 mb-1">Item</label>
              <select
                value={dropForm.item_id}
                onChange={(e) => setDropForm({ ...dropForm, item_id: e.target.value })}
                className="bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select</option>
                {items.map((it) => (
                  <option key={it.id} value={it.id}>
                    {it.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-col">
              <label className="text-sm text-gray-300 mb-1">Date</label>
              <input
                type="date"
                value={dropForm.date}
                onChange={(e) => setDropForm({ ...dropForm, date: e.target.value })}
                className="bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="lg:col-span-5 flex justify-end gap-3">
              {addDropError && <span className="text-sm text-red-400">{addDropError}</span>}
              <button
                type="submit"
                disabled={addDropLoading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                {addDropLoading ? 'Saving…' : 'Save Drop'}
              </button>
              <button
                type="button"
                disabled={addDropLoading}
                onClick={() => handleAddArcaneBox('armor')}
                className="bg-green-700 hover:bg-green-800 disabled:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                +1 Arcane Armor Box
              </button>
              <button
                type="button"
                disabled={addDropLoading}
                onClick={() => handleAddArcaneBox('weapon')}
                className="bg-green-700 hover:bg-green-800 disabled:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                +1 Arcane Weapon Box
              </button>
            </div>
          </form>
        </div>

        {/* Filters and View Toggle */}
        <div className="bg-gray-800 rounded-lg p-6 mb-6 border border-gray-700">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Character</label>
              <select
                value={filters.character_id || ''}
                onChange={(e) => updateFilters({ character_id: e.target.value || undefined })}
                className="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Characters</option>
                {characters.map((char) => (
                  <option key={char.id} value={char.id}>
                    {char.character_name} ({char.world})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Start Date</label>
              <input
                type="date"
                value={filters.start_date || ''}
                onChange={(e) => updateFilters({ start_date: e.target.value || undefined })}
                className="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">End Date</label>
              <input
                type="date"
                value={filters.end_date || ''}
                onChange={(e) => updateFilters({ end_date: e.target.value || undefined })}
                className="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Search Items</label>
              <input
                type="text"
                placeholder="Search item names..."
                value={filters.search || ''}
                onChange={(e) => updateFilters({ search: e.target.value || undefined })}
                className="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div className="flex justify-between items-center">
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode('list')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'list'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                List View
              </button>
              <button
                onClick={() => setViewMode('timeline')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'timeline'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                Timeline View
              </button>
            </div>
            <button
              onClick={() => setFilters({ page: 1, page_size: 20 })}
              className="text-gray-400 hover:text-white text-sm"
            >
              Clear Filters
            </button>
          </div>
        </div>

        {/* Statistics */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <p className="text-gray-400 text-sm mb-1">Total Drops</p>
              <p className="text-2xl font-bold text-white">{stats.total_drops}</p>
            </div>
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <p className="text-gray-400 text-sm mb-1">Unique Items</p>
              <p className="text-2xl font-bold text-white">{stats.unique_items}</p>
            </div>
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <p className="text-gray-400 text-sm mb-1">Total Quantity</p>
              <p className="text-2xl font-bold text-white">{stats.total_quantity}</p>
            </div>
          </div>
        )}

        {/* Content */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
            <p className="text-gray-400">Loading...</p>
          </div>
        ) : viewMode === 'timeline' && timeline ? (
          <div className="space-y-6">
            {timeline.timeline.length === 0 ? (
              <div className="text-center py-12 bg-gray-800 rounded-lg border border-gray-700">
                <p className="text-gray-400 text-lg">No drops found for the selected filters.</p>
              </div>
            ) : (
              timeline.timeline.map((day) => (
                <div key={day.date} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <h3 className="text-lg font-semibold text-white mb-4">
                    {new Date(day.date).toLocaleDateString()} ({day.total_drops} drops)
                  </h3>
                  <div className="space-y-3">
                    {day.entries.map((entry) => (
                      <div
                        key={entry.id}
                        className="bg-gray-700 rounded p-3 flex items-center justify-between"
                      >
            <div className="flex items-center gap-4">
              {(() => {
                const iconUrl = getItemIcon(entry.item_name);
                return iconUrl ? (
                  <img
                    src={iconUrl}
                    alt={entry.item_name || 'Item'}
                    className="h-12 w-12 rounded-md object-cover border border-gray-700"
                  />
                ) : (
                  <div className="h-12 w-12 rounded-md bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold">
                    {entry.item_name?.[0] || '#'}
                  </div>
                );
              })()}
              <div>
                <p className="text-white font-medium">{entry.item_name || `Item ${entry.item_id}`}</p>
                <p className="text-gray-400 text-sm">
                  {entry.character_name && `${entry.character_name} • `}
                  x{entry.quantity}
                </p>
              </div>
            </div>
                        <div className="text-gray-400 text-sm">
                          {formatDateTime(entry.cleared_at || entry.created_at)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {entries.length === 0 ? (
              <div className="text-center py-12 bg-gray-800 rounded-lg border border-gray-700">
                <p className="text-gray-400 text-lg">No drops found for the selected filters.</p>
              </div>
            ) : (
              <>
                {entries.map((entry) => (
                  <div
                    key={entry.id}
                    className="bg-gray-800 rounded-lg p-4 border border-gray-700 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-4">
                      {(() => {
                        const iconUrl = getItemIcon(entry.item_name);
                        return iconUrl ? (
                          <img
                            src={iconUrl}
                            alt={entry.item_name || 'Item'}
                            className="h-12 w-12 rounded-md object-cover border border-gray-700"
                          />
                        ) : (
                          <div className="h-12 w-12 rounded-md bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold">
                            {entry.item_name?.[0] || '#'}
                          </div>
                        );
                      })()}
                      <div>
                        <p className="text-white font-medium">{entry.item_name || `Item ${entry.item_id}`}</p>
                        <p className="text-gray-400 text-sm">
                          {entry.character_name && `${entry.character_name} • `}
                          x{entry.quantity}
                        </p>
                      </div>
                    </div>
                    <div className="text-gray-400 text-sm">
                      {formatDateTime(entry.cleared_at || entry.created_at)}
                    </div>
                  </div>
                ))}
                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex justify-center gap-2 mt-6">
                    <button
                      onClick={() => updateFilters({ page: (filters.page || 1) - 1 })}
                      disabled={filters.page === 1}
                      className="px-4 py-2 bg-gray-700 text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600"
                    >
                      Previous
                    </button>
                    <span className="px-4 py-2 text-gray-300">
                      Page {filters.page || 1} of {totalPages}
                    </span>
                    <button
                      onClick={() => updateFilters({ page: (filters.page || 1) + 1 })}
                      disabled={filters.page === totalPages}
                      className="px-4 py-2 bg-gray-700 text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600"
                    >
                      Next
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* Bottom cumulative chart */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mt-6 max-w-7xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-xl font-semibold text-white">Drops Progress</h3>
              <p className="text-gray-400 text-sm">Cumulative drops over time (CET).</p>
            </div>
          </div>
          {dailySeries.length === 0 ? (
            <p className="text-gray-400 text-sm">No drops to graph yet.</p>
          ) : (
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
              {(() => {
                const width = 900;
                const height = 260;
                const padding = 50;
                const maxY = Math.max(...dailySeries.map((p) => p.cumulative), 1);
                const xScale = (idx: number) =>
                  padding + (idx / Math.max(dailySeries.length - 1, 1)) * (width - padding * 2);
                const yScale = (val: number) => height - padding - (val / maxY) * (height - padding * 2);
                const points = dailySeries
                  .map((p, idx) => `${xScale(idx)},${yScale(p.cumulative)}`)
                  .join(' ');
                const yTicks = 4;
                const yTickVals = Array.from({ length: yTicks }, (_, i) => (i / (yTicks - 1)) * maxY);
                return (
                  <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-72">
                    {/* Axes */}
                    <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="#4b5563" />
                    <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#4b5563" />
                    {/* Y ticks */}
                    {yTickVals.map((v, i) => {
                      const y = yScale(v);
                      return (
                        <g key={i}>
                          <line x1={padding - 5} y1={y} x2={padding} y2={y} stroke="#6b7280" />
                          <text
                            x={padding - 10}
                            y={y + 4}
                            fontSize="10"
                            fill="#9ca3af"
                            textAnchor="end"
                          >
                            {v.toLocaleString()}
                          </text>
                          <line
                            x1={padding}
                            y1={y}
                            x2={width - padding}
                            y2={y}
                            stroke="#374151"
                            strokeDasharray="2 4"
                          />
                        </g>
                      );
                    })}
                    {/* X labels */}
                    {dailySeries.map((p, idx) => (
                      <text
                        key={p.date}
                        x={xScale(idx)}
                        y={height - padding + 16}
                        fontSize="10"
                        fill="#9ca3af"
                        textAnchor="middle"
                      >
                        {p.date.slice(5)} {/* show MM-DD */}
                      </text>
                    ))}
                    {/* Line */}
                    <polyline
                      fill="none"
                      stroke="#c084fc"
                      strokeWidth="3"
                      points={points}
                      strokeLinejoin="round"
                      strokeLinecap="round"
                    />
                    {/* Points */}
                    {dailySeries.map((p, idx) => (
                      <circle
                        key={p.date}
                        cx={xScale(idx)}
                        cy={yScale(p.cumulative)}
                        r={4}
                        fill="#c084fc"
                        stroke="#111827"
                        strokeWidth="1"
                      />
                    ))}
                  </svg>
                );
              })()}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

