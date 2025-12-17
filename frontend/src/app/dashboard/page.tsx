'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/services/api';
import { User, Character } from '@/types';
import Link from 'next/link';

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUser();
  }, []);

  async function loadUser() {
    try {
      // TEMPORARY: Try to get user, but don't fail if not authenticated
      // Backend will return mock user when DEBUG=true
      const currentUser = await api.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      // If auth fails, still allow access (temporary no-login mode)
      console.log('Auth not required in debug mode');
    } finally {
      setLoading(false);
    }
  }

  async function handleLogout() {
    try {
      await api.logout();
      router.push('/');
    } catch (error) {
      console.error('Logout failed:', error);
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

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-white">MapleStory Tracker</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-gray-300">{user.discord_username}</span>
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
                className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
              >
                XP Tracker
              </Link>
              <button
                onClick={handleLogout}
                className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">Dashboard</h2>
          <p className="text-gray-400">Welcome back, {user.discord_username}!</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-2">Boss Tracker</h3>
            <p className="text-gray-400 text-sm mb-4">Track your weekly and daily boss clears</p>
            <Link
              href="/bosses"
              className="text-blue-400 hover:text-blue-300 text-sm font-medium"
            >
              View Bosses →
            </Link>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-2">Characters</h3>
            <p className="text-gray-400 text-sm mb-4">Manage your characters</p>
            <Link
              href="/characters"
              className="text-blue-400 hover:text-blue-300 text-sm font-medium"
            >
              Manage Characters →
            </Link>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-2">Drop Diary</h3>
            <p className="text-gray-400 text-sm mb-4">View your complete drop history with filters and statistics</p>
            <Link
              href="/diary"
              className="text-blue-400 hover:text-blue-300 text-sm font-medium"
            >
              View Diary →
            </Link>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-2">XP Tracker</h3>
            <p className="text-gray-400 text-sm mb-4">Track daily XP gains with automatic calculations</p>
            <Link
              href="/xp-tracker"
              className="text-blue-400 hover:text-blue-300 text-sm font-medium"
            >
              View XP Tracker →
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}

