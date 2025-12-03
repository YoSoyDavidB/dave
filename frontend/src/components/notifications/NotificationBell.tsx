/**
 * Notification bell component - displays reminders and goals
 */

import { useState, useEffect } from 'react';
import { Bell, RefreshCw, Check } from 'lucide-react';
import { getPendingTasks, getActiveGoals, syncVaultTasks, markTaskCompleted, updateGoalProgress, type Task, type Goal } from '../../services/proactive';

interface NotificationBellProps {
  className?: string;
}

export default function NotificationBell({ className = '' }: NotificationBellProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);

  const totalCount = tasks.length + goals.length;

  useEffect(() => {
    // Load notifications on mount and every 5 minutes
    loadNotifications();
    const interval = setInterval(loadNotifications, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const [tasksData, goalsData] = await Promise.all([
        getPendingTasks(),
        getActiveGoals(),
      ]);
      setTasks(tasksData.tasks);
      setGoals(goalsData.goals);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSyncVault = async () => {
    try {
      setSyncing(true);
      await syncVaultTasks();
      // Wait a bit for background processing, then reload
      setTimeout(() => {
        loadNotifications();
        setSyncing(false);
      }, 2000);
    } catch (error) {
      console.error('Failed to sync vault tasks:', error);
      setSyncing(false);
    }
  };

  const handleCompleteTask = async (memoryId: string) => {
    try {
      await markTaskCompleted(memoryId);
      // Remove task from local state immediately for responsive UI
      setTasks(tasks.filter(t => t.memory_id !== memoryId));
    } catch (error) {
      console.error('Failed to mark task as completed:', error);
      // Reload to get current state if failed
      loadNotifications();
    }
  };

  const handleUpdateGoalProgress = async (goalId: string, newProgress: number) => {
    try {
      await updateGoalProgress(goalId, newProgress);
      // Update local state immediately for responsive UI
      setGoals(goals.map(g =>
        g.memory_id === goalId ? { ...g, progress: newProgress } : g
      ));
    } catch (error) {
      console.error('Failed to update goal progress:', error);
      // Reload to get current state if failed
      loadNotifications();
    }
  };

  return (
    <div className={`relative ${className}`}>
      {/* Bell button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
        aria-label="Notifications"
      >
        <Bell className="w-5 h-5" />
        {totalCount > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 rounded-full text-[10px] text-white font-bold flex items-center justify-center">
            {totalCount > 9 ? '9+' : totalCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Notification panel */}
          <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-20">
            {/* Header */}
            <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white">
                Notifications
              </h3>
            </div>

            {/* Content */}
            <div className="max-h-96 overflow-y-auto">
              {loading ? (
                <div className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                  Loading...
                </div>
              ) : totalCount === 0 ? (
                <div className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                  No notifications
                </div>
              ) : (
                <>
                  {/* Tasks section */}
                  {tasks.length > 0 && (
                    <div className="border-b border-gray-200 dark:border-gray-700">
                      <div className="px-4 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">
                        Tasks ({tasks.length})
                      </div>
                      {tasks.map((task) => (
                        <div
                          key={task.memory_id}
                          className="px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors flex items-start gap-3 group"
                        >
                          <div className="flex-1">
                            <p className="text-sm text-gray-900 dark:text-white">
                              {task.task_text}
                            </p>
                            {task.source && (
                              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                {task.source.replace('vault:', '')}
                              </p>
                            )}
                          </div>
                          <button
                            onClick={() => handleCompleteTask(task.memory_id)}
                            className="flex-shrink-0 p-1.5 rounded-full text-gray-400 hover:text-green-600 hover:bg-green-50 dark:hover:text-green-400 dark:hover:bg-green-900/20 transition-colors opacity-0 group-hover:opacity-100"
                            title="Mark as completed"
                          >
                            <Check className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Goals section */}
                  {goals.length > 0 && (
                    <div>
                      <div className="px-4 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">
                        Goals ({goals.length})
                      </div>
                      {goals.map((goal) => (
                        <div
                          key={goal.memory_id}
                          className="px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                        >
                          <p className="text-sm text-gray-900 dark:text-white mb-2">
                            {goal.goal_text}
                          </p>
                          <div className="flex items-center gap-2">
                            <input
                              type="range"
                              min="0"
                              max="100"
                              step="5"
                              value={goal.progress}
                              onChange={(e) => handleUpdateGoalProgress(goal.memory_id, Number(e.target.value))}
                              className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-blue-500 [&::-webkit-slider-thumb]:cursor-pointer [&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:h-4 [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:bg-blue-500 [&::-moz-range-thumb]:border-0 [&::-moz-range-thumb]:cursor-pointer"
                              style={{
                                background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${goal.progress}%, rgb(229 231 235) ${goal.progress}%, rgb(229 231 235) 100%)`
                              }}
                            />
                            <span className="text-xs text-gray-500 dark:text-gray-400 font-medium min-w-[3ch]">
                              {Math.round(goal.progress)}%
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Footer */}
            <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <button
                onClick={loadNotifications}
                disabled={loading}
                className="text-xs text-blue-600 dark:text-blue-400 hover:underline disabled:opacity-50"
              >
                Refresh
              </button>
              <button
                onClick={handleSyncVault}
                disabled={syncing}
                className="text-xs text-blue-600 dark:text-blue-400 hover:underline disabled:opacity-50 flex items-center gap-1"
              >
                <RefreshCw className={`w-3 h-3 ${syncing ? 'animate-spin' : ''}`} />
                Sync Vault
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
