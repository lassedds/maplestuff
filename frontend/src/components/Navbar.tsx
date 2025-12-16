'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface User {
  id: string;
  discord_username: string;
  discord_avatar: string | null;
}

export function Navbar() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    api.getCurrentUser()
      .then(setUser)
      .catch(() => setUser(null));
  }, []);

  const handleLogout = async () => {
    await api.logout();
    setUser(null);
    window.location.href = '/';
  };

  return (
    <nav className="bg-slate-900/80 border-b border-slate-700 sticky top-0 z-50 backdrop-blur">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-8">
            <Link href="/" className="text-xl font-bold text-maple-accent">
              GMSTracker
            </Link>
            <div className="hidden md:flex items-center gap-6">
              <Link href="/bosses" className="text-slate-300 hover:text-white transition-colors">
                Bosses
              </Link>
              <Link href="/tasks" className="text-slate-300 hover:text-white transition-colors">
                Tasks
              </Link>
              <Link href="/stats" className="text-slate-300 hover:text-white transition-colors">
                Stats
              </Link>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {user ? (
              <>
                <span className="text-slate-300">{user.discord_username}</span>
                <button
                  onClick={handleLogout}
                  className="text-slate-400 hover:text-white transition-colors"
                >
                  Logout
                </button>
              </>
            ) : (
              <a
                href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/discord`}
                className="btn btn-primary text-sm"
              >
                Sign In
              </a>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
