'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface Character {
  id: string;
  character_name: string;
  world: string;
  job: string | null;
  level: number | null;
  is_main: boolean;
}

const WORLDS = [
  'Reboot (NA)',
  'Bera',
  'Aurora',
  'Elysium',
  'Scania',
  'Kronos',
  'Hyperion',
];

export default function CharactersPage() {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    character_name: '',
    world: 'Reboot (NA)',
    job: '',
    level: '',
    is_main: false,
  });

  const loadCharacters = async () => {
    try {
      const res = await api.getCharacters();
      setCharacters(res.characters || []);
    } catch (err) {
      setError('Failed to load characters. Please sign in.');
    }
    setLoading(false);
  };

  useEffect(() => {
    loadCharacters();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createCharacter({
        character_name: formData.character_name,
        world: formData.world,
        job: formData.job || null,
        level: formData.level ? parseInt(formData.level) : null,
        is_main: formData.is_main,
      });
      setShowForm(false);
      setFormData({
        character_name: '',
        world: 'Reboot (NA)',
        job: '',
        level: '',
        is_main: false,
      });
      await loadCharacters();
    } catch (err) {
      alert('Failed to create character');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this character?')) return;
    try {
      await api.deleteCharacter(id);
      await loadCharacters();
    } catch (err) {
      alert('Failed to delete character');
    }
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
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">My Characters</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn btn-primary"
        >
          {showForm ? 'Cancel' : 'Add Character'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="card mb-6">
          <h2 className="text-lg font-semibold mb-4">Add Character</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-slate-400 mb-1">Character Name *</label>
              <input
                type="text"
                value={formData.character_name}
                onChange={(e) => setFormData({ ...formData, character_name: e.target.value })}
                required
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2"
                placeholder="Enter character name"
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">World *</label>
              <select
                value={formData.world}
                onChange={(e) => setFormData({ ...formData, world: e.target.value })}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2"
              >
                {WORLDS.map((world) => (
                  <option key={world} value={world}>{world}</option>
                ))}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-slate-400 mb-1">Job</label>
                <input
                  type="text"
                  value={formData.job}
                  onChange={(e) => setFormData({ ...formData, job: e.target.value })}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2"
                  placeholder="e.g. Adele"
                />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Level</label>
                <input
                  type="number"
                  value={formData.level}
                  onChange={(e) => setFormData({ ...formData, level: e.target.value })}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2"
                  placeholder="e.g. 275"
                  min="1"
                  max="300"
                />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_main"
                checked={formData.is_main}
                onChange={(e) => setFormData({ ...formData, is_main: e.target.checked })}
                className="w-4 h-4 rounded"
              />
              <label htmlFor="is_main" className="text-slate-400">This is my main character</label>
            </div>
            <button type="submit" className="btn btn-success w-full">
              Add Character
            </button>
          </div>
        </form>
      )}

      {characters.length > 0 ? (
        <div className="space-y-3">
          {characters.map((char) => (
            <div key={char.id} className="card flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold">{char.character_name}</span>
                  {char.is_main && (
                    <span className="text-xs px-2 py-0.5 bg-maple-accent rounded">Main</span>
                  )}
                </div>
                <div className="text-sm text-slate-400">
                  {char.world}
                  {char.job && ` • ${char.job}`}
                  {char.level && ` • Lv.${char.level}`}
                </div>
              </div>
              <button
                onClick={() => handleDelete(char.id)}
                className="text-red-400 hover:text-red-300 transition-colors"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className="card text-center">
          <p className="text-slate-400">No characters added yet.</p>
          <p className="text-sm text-slate-500 mt-2">
            Add a character to start tracking your progress!
          </p>
        </div>
      )}
    </div>
  );
}
