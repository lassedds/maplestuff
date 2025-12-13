'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/services/api';
import { Character, CharacterCreate } from '@/types';
import Link from 'next/link';

export default function CharactersPage() {
  const router = useRouter();
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<CharacterCreate>({
    character_name: '',
    world: '',
    job: '',
    level: undefined,
    is_main: false,
  });

  useEffect(() => {
    loadCharacters();
  }, []);

  async function loadCharacters() {
    try {
      const response = await api.getCharacters();
      setCharacters(response.characters);
    } catch (error) {
      console.error('Failed to load characters:', error);
      router.push('/');
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.createCharacter(formData);
      setShowForm(false);
      setFormData({
        character_name: '',
        world: '',
        job: '',
        level: undefined,
        is_main: false,
      });
      await loadCharacters();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create character');
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Are you sure you want to delete this character?')) {
      return;
    }
    try {
      await api.deleteCharacter(id);
      await loadCharacters();
    } catch (error) {
      alert('Failed to delete character');
    }
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
                MapleHub OSS
              </Link>
            </div>
            <div className="flex items-center gap-4">
              <Link
                href="/dashboard"
                className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
              >
                Dashboard
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold text-white mb-2">Characters</h2>
            <p className="text-gray-400">Manage your MapleStory characters</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
          >
            {showForm ? 'Cancel' : '+ Add Character'}
          </button>
        </div>

        {showForm && (
          <div className="bg-gray-800 rounded-lg p-6 mb-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">Add New Character</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Character Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.character_name}
                    onChange={(e) => setFormData({ ...formData, character_name: e.target.value })}
                    className="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    World *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.world}
                    onChange={(e) => setFormData({ ...formData, world: e.target.value })}
                    className="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Scania, Bera, Reboot"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Job
                  </label>
                  <input
                    type="text"
                    value={formData.job || ''}
                    onChange={(e) => setFormData({ ...formData, job: e.target.value })}
                    className="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Paladin, Bishop"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Level
                  </label>
                  <input
                    type="number"
                    value={formData.level || ''}
                    onChange={(e) => setFormData({ ...formData, level: e.target.value ? parseInt(e.target.value) : undefined })}
                    className="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_main"
                  checked={formData.is_main}
                  onChange={(e) => setFormData({ ...formData, is_main: e.target.checked })}
                  className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                />
                <label htmlFor="is_main" className="ml-2 text-sm text-gray-300">
                  Set as main character
                </label>
              </div>
              <button
                type="submit"
                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors"
              >
                Create Character
              </button>
            </form>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {characters.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <p className="text-gray-400 text-lg">No characters yet. Add your first character!</p>
            </div>
          ) : (
            characters.map((character) => (
              <div
                key={character.id}
                className="bg-gray-800 rounded-lg p-6 border border-gray-700"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold text-white">
                      {character.character_name}
                      {character.is_main && (
                        <span className="ml-2 text-xs bg-yellow-600 text-white px-2 py-1 rounded">
                          MAIN
                        </span>
                      )}
                    </h3>
                    <p className="text-gray-400">{character.world}</p>
                  </div>
                  <button
                    onClick={() => handleDelete(character.id)}
                    className="text-red-400 hover:text-red-300"
                  >
                    Delete
                  </button>
                </div>
                <div className="space-y-2">
                  {character.job && (
                    <p className="text-sm text-gray-300">
                      <span className="text-gray-500">Job:</span> {character.job}
                    </p>
                  )}
                  {character.level && (
                    <p className="text-sm text-gray-300">
                      <span className="text-gray-500">Level:</span> {character.level}
                    </p>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  );
}

