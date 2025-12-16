'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface Task {
  id: string;
  task_id: string;
  task_name: string;
  task_description: string | null;
  task_category: string | null;
  task_reset_type: string;
  is_completed: boolean;
  completed_at: string | null;
}

interface Checklist {
  date?: string;
  week_start?: string;
  week_end?: string;
  tasks: Task[];
  completed_count: number;
  total_count: number;
  completion_percent: number;
}

export default function TasksPage() {
  const [dailyTasks, setDailyTasks] = useState<Checklist | null>(null);
  const [weeklyTasks, setWeeklyTasks] = useState<Checklist | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<'daily' | 'weekly'>('daily');

  const loadTasks = async () => {
    try {
      const [daily, weekly] = await Promise.all([
        api.getDailyChecklist(),
        api.getWeeklyChecklist(),
      ]);
      setDailyTasks(daily);
      setWeeklyTasks(weekly);
    } catch (err) {
      setError('Failed to load tasks. Please sign in.');
    }
    setLoading(false);
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const handleToggleTask = async (task: Task) => {
    try {
      if (task.is_completed) {
        await api.uncompleteTask(task.id);
      } else {
        await api.completeTask(task.id);
      }
      await loadTasks();
    } catch (err) {
      alert('Failed to update task');
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

  const currentTasks = tab === 'daily' ? dailyTasks : weeklyTasks;

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Task Checklist</h1>

      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setTab('daily')}
          className={`btn ${tab === 'daily' ? 'btn-primary' : 'btn-secondary'}`}
        >
          Daily Tasks
        </button>
        <button
          onClick={() => setTab('weekly')}
          className={`btn ${tab === 'weekly' ? 'btn-primary' : 'btn-secondary'}`}
        >
          Weekly Tasks
        </button>
      </div>

      {currentTasks && currentTasks.tasks.length > 0 ? (
        <>
          <div className="card mb-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-lg font-semibold">
                  {currentTasks.completed_count} / {currentTasks.total_count} completed
                </div>
                <div className="text-slate-400 text-sm">
                  {tab === 'daily' ? currentTasks.date : `${currentTasks.week_start} - ${currentTasks.week_end}`}
                </div>
              </div>
              <div className="text-2xl font-bold text-maple-accent">
                {Math.round(currentTasks.completion_percent)}%
              </div>
            </div>
            <div className="mt-3 h-2 bg-slate-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-maple-accent transition-all"
                style={{ width: `${currentTasks.completion_percent}%` }}
              />
            </div>
          </div>

          <div className="card">
            <div className="space-y-2">
              {currentTasks.tasks.map((task) => (
                <div
                  key={task.id}
                  className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
                    task.is_completed
                      ? 'bg-green-900/30 hover:bg-green-900/40'
                      : 'bg-slate-700/50 hover:bg-slate-700'
                  }`}
                  onClick={() => handleToggleTask(task)}
                >
                  <input
                    type="checkbox"
                    checked={task.is_completed}
                    onChange={() => {}}
                    className="w-5 h-5 rounded pointer-events-none"
                  />
                  <div className="flex-1">
                    <div className={task.is_completed ? 'line-through text-slate-400' : ''}>
                      {task.task_name}
                    </div>
                    {task.task_description && (
                      <div className="text-xs text-slate-500">{task.task_description}</div>
                    )}
                  </div>
                  {task.task_category && (
                    <span className="text-xs px-2 py-1 bg-slate-600 rounded">
                      {task.task_category}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </>
      ) : (
        <div className="card text-center">
          <p className="text-slate-400">No {tab} tasks in your checklist.</p>
          <p className="text-sm text-slate-500 mt-2">
            Add tasks to your checklist to start tracking them.
          </p>
        </div>
      )}
    </div>
  );
}
