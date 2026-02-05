import { LayoutDashboard, Activity, Gauge, ChevronLeft, ChevronRight, Kanban } from "lucide-react";
import React from "react";

const NAV_ITEMS = [
  { id: "board", label: "Board", icon: Kanban },
  { id: "mission", label: "Mission Control", icon: Activity },
  { id: "ops", label: "Token Maximizer", icon: Gauge },
];

export default function Sidebar({
  activeView,
  onNavigate,
  collapsed,
  onToggleCollapse,
  taskCount,
  gatewayAlive,
}) {
  return (
    <aside
      className={`
        flex flex-col bg-gray-950 border-r border-gray-800 h-screen
        transition-all duration-200 ease-in-out flex-shrink-0
        ${collapsed ? "w-14" : "w-60"}
      `}
    >
      {/* Logo / Brand */}
      <div className="flex items-center gap-2.5 px-3 h-14 border-b border-gray-800 flex-shrink-0">
        <LayoutDashboard className="w-6 h-6 text-blue-500 flex-shrink-0" />
        {!collapsed && (
          <span className="text-sm font-bold text-white truncate">Kanban Mission Control</span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-2 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`
                w-full flex items-center gap-2.5 px-3 py-2 text-sm transition-colors
                ${
                  isActive
                    ? "text-white bg-gray-800/60 border-l-2 border-blue-500"
                    : "text-gray-400 hover:text-white hover:bg-gray-800/40 border-l-2 border-transparent"
                }
              `}
              title={collapsed ? item.label : undefined}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && <span className="truncate">{item.label}</span>}
            </button>
          );
        })}
      </nav>

      {/* Footer stats */}
      <div className="border-t border-gray-800 px-3 py-2.5 flex-shrink-0">
        {collapsed ? (
          <div className="flex flex-col items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full ${gatewayAlive ? "bg-green-500" : "bg-red-500"}`}
            />
            <span className="text-xs text-gray-500 font-mono">{taskCount ?? 0}</span>
          </div>
        ) : (
          <div className="flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center gap-1.5">
              <span
                className={`w-2 h-2 rounded-full ${gatewayAlive ? "bg-green-500" : "bg-red-500"}`}
              />
              <span>{gatewayAlive ? "Online" : "Offline"}</span>
            </div>
            <span className="font-mono">{taskCount ?? 0} tasks</span>
          </div>
        )}
      </div>

      {/* Collapse toggle */}
      <button
        onClick={onToggleCollapse}
        className="flex items-center justify-center h-9 border-t border-gray-800
                   text-gray-500 hover:text-white hover:bg-gray-800/40 transition-colors"
        title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
      </button>
    </aside>
  );
}
