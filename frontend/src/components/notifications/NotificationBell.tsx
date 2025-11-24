/**
 * Notification bell component - displays reminders and goals
 */

import { useState, useEffect } from 'react';
import { Bell, RefreshCw } from 'lucide-react';
import { getReminders, getActiveGoals, syncVaultTasks, type Reminder, type Goal } from '../../services/proactive';

interface NotificationBellProps {
  className?: string;
}

export default function NotificationBell({ className = '' }: NotificationBellProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);

  const totalCount = reminders.length + goals.length;

  useEffect(() => {
    // Load notifications on mount and every 5 minutes
    loadNotifications();
    const interval = setInterval(loadNotifications, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const [remindersData, goalsData] = await Promise.all([
        getReminders(),
        getActiveGoals(),
      ]);
      setReminders(remindersData.reminders);
      setGoals(goalsData.goals);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDueDate = (hoursUntilDue: number): string => {
    if (hoursUntilDue < 0) {
      const hoursOverdue = Math.abs(hoursUntilDue);
      if (hoursOverdue < 24) {
        return `${Math.floor(hoursOverdue)}h overdue`;
      }
      return `${Math.floor(hoursOverdue / 24)}d overdue`;
    }

    if (hoursUntilDue < 24) {
      return `${Math.floor(hoursUntilDue)}h left`;
    }
    return `${Math.floor(hoursUntilDue / 24)}d left`;
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
                  {/* Reminders section */}
                  {reminders.length > 0 && (
                    <div className="border-b border-gray-200 dark:border-gray-700">
                      <div className="px-4 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">
                        Tasks ({reminders.length})
                      </div>
                      {reminders.map((reminder) => (
                        <div
                          key={reminder.memory_id}
                          className="px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                        >
                          <div className="flex items-start justify-between gap-2">
                            <p className="text-sm text-gray-900 dark:text-white flex-1">
                              {reminder.task_text}
                            </p>
                            <span
                              className={`text-xs px-2 py-0.5 rounded-full whitespace-nowrap ${
                                reminder.is_overdue
                                  ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                                  : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                              }`}
                            >
                              {formatDueDate(reminder.hours_until_due)}
                            </span>
                          </div>
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
                            <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                              <div
                                className="bg-blue-500 h-2 rounded-full transition-all"
                                style={{ width: `${goal.progress}%` }}
                              />
                            </div>
                            <span className="text-xs text-gray-500 dark:text-gray-400">
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
