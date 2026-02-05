import {
  Activity,
  Zap,
  Target,
  AlertTriangle,
  RefreshCw,
  Wifi,
  WifiOff,
  DollarSign,
} from "lucide-react";
import React from "react";
import { useStatus } from "../hooks/useStatus";

export default function MissionControl() {
  const { status, loading, error, lastUpdated, refresh } = useStatus(30000);

  if (loading && !status) {
    return (
      <div className="animate-pulse">
        <div className="h-24 bg-gray-700 rounded-lg"></div>
      </div>
    );
  }

  const gatewayAlive = status?.gateway?.alive;
  const tokenCost = status?.tokens?.estimatedCost || "0.00";
  const topTask = status?.sprint?.topTask;
  const doingCount = status?.sprint?.doing || 0;
  const overdueCount = status?.sprint?.overdue || 0;

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-400" />
          Mission Control
        </h2>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span>Updated: {lastUpdated?.toLocaleTimeString()}</span>
          <button
            onClick={refresh}
            className="p-1 hover:bg-gray-700 rounded transition-colors"
            title="Refresh now"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Gateway Status */}
        <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700/50">
          <div className="flex items-center gap-2 mb-1">
            {gatewayAlive ? (
              <Wifi className="w-4 h-4 text-green-400 status-alive" />
            ) : (
              <WifiOff className="w-4 h-4 text-red-400" />
            )}
            <span className="text-xs text-gray-400">Gateway</span>
          </div>
          <div className={`text-xl font-bold ${gatewayAlive ? "text-green-400" : "text-red-400"}`}>
            {gatewayAlive ? "Online" : "Offline"}
          </div>
          <div className="text-xs text-gray-500">Port {status?.gateway?.port || 18789}</div>
        </div>

        {/* Token Cost */}
        <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700/50">
          <div className="flex items-center gap-2 mb-1">
            <DollarSign className="w-4 h-4 text-amber-400" />
            <span className="text-xs text-gray-400">Today's Cost</span>
          </div>
          <div className="text-xl font-bold text-amber-400">${tokenCost}</div>
          <div className="text-xs text-gray-500">
            {status?.tokens?.totalTokens?.toLocaleString() || 0} tokens
          </div>
        </div>

        {/* Active Tasks */}
        <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700/50">
          <div className="flex items-center gap-2 mb-1">
            <Zap className="w-4 h-4 text-blue-400" />
            <span className="text-xs text-gray-400">In Progress</span>
          </div>
          <div className="text-xl font-bold text-blue-400">{doingCount}</div>
          <div className="text-xs text-gray-500">{status?.sprint?.todo || 0} in queue</div>
        </div>

        {/* Focus Task */}
        <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700/50">
          <div className="flex items-center gap-2 mb-1">
            <Target className="w-4 h-4 text-purple-400" />
            <span className="text-xs text-gray-400">Focus</span>
          </div>
          {topTask ? (
            <>
              <div className="text-sm font-medium text-white truncate" title={topTask.title}>
                {topTask.title}
              </div>
              <div className="flex items-center gap-2 mt-1">
                <span className={`text-xs px-1.5 py-0.5 rounded priority-${topTask.priority}`}>
                  {topTask.priority}
                </span>
                {topTask.dueDate && (
                  <span className="text-xs text-gray-500">
                    Due: {new Date(topTask.dueDate).toLocaleDateString()}
                  </span>
                )}
              </div>
            </>
          ) : (
            <div className="text-sm text-gray-500">No active tasks</div>
          )}
        </div>
      </div>

      {/* Alerts */}
      {overdueCount > 0 && (
        <div className="mt-3 flex items-center gap-2 text-red-400 text-sm bg-red-500/10 rounded-lg p-2">
          <AlertTriangle className="w-4 h-4" />
          <span>
            {overdueCount} overdue task{overdueCount > 1 ? "s" : ""}
          </span>
        </div>
      )}

      {error && (
        <div className="mt-3 flex items-center gap-2 text-amber-400 text-sm bg-amber-500/10 rounded-lg p-2">
          <AlertTriangle className="w-4 h-4" />
          <span>Status update failed: {error}</span>
        </div>
      )}
    </div>
  );
}
