import {
  Gauge,
  Timer,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  BarChart3,
  RefreshCw,
} from "lucide-react";
import React from "react";
import { useOps } from "../hooks/useOps";

const URGENCY_COLORS = {
  low: { bg: "bg-green-500/10", text: "text-green-400", label: "On Track" },
  medium: { bg: "bg-blue-500/10", text: "text-blue-400", label: "Moderate" },
  high: { bg: "bg-amber-500/10", text: "text-amber-400", label: "Use More" },
  critical: { bg: "bg-red-500/10", text: "text-red-400", label: "Burning Tokens!" },
  maxed: { bg: "bg-purple-500/10", text: "text-purple-400", label: "Maxed Out" },
};

function QuotaBar({ label, pct, hrUsed, hrBudget, hrLeft, waste }) {
  const capped = Math.min(pct, 100);
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-gray-400">{label}</span>
        <span className="text-gray-300 font-mono">
          {hrUsed}h / {hrBudget}h
        </span>
      </div>
      <div className="h-2.5 bg-gray-700 rounded-full overflow-hidden relative">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            pct > 80
              ? "bg-green-500"
              : pct > 50
                ? "bg-blue-500"
                : pct > 25
                  ? "bg-amber-500"
                  : "bg-red-500"
          }`}
          style={{ width: `${capped}%` }}
        />
      </div>
      <div className="flex justify-between text-xs">
        <span className={pct < 30 ? "text-red-400" : "text-gray-500"}>{hrLeft}h remaining</span>
        {waste > 0 && (
          <span className="text-amber-400">{waste.toLocaleString()} tokens at risk</span>
        )}
      </div>
    </div>
  );
}

function CronStatus({ job }) {
  const statusIcon = {
    success: <CheckCircle className="w-3.5 h-3.5 text-green-400" />,
    failed: <XCircle className="w-3.5 h-3.5 text-red-400" />,
    never: <Clock className="w-3.5 h-3.5 text-gray-500" />,
  };

  const ago = job.lastRun ? timeAgo(job.lastRun) : "never";

  return (
    <div className="flex items-center justify-between py-1.5 border-b border-gray-700/50 last:border-0">
      <div className="flex items-center gap-2">
        {statusIcon[job.status] || statusIcon.never}
        <span className="text-xs text-gray-300">{job.name}</span>
      </div>
      <div className="flex items-center gap-3 text-xs">
        <span className="text-gray-500 font-mono">{job.schedule}</span>
        <span className="text-gray-500">{ago}</span>
      </div>
    </div>
  );
}

function timeAgo(ts) {
  const diff = Date.now() - new Date(ts).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function OpsPanel() {
  const { ops, loading, error, refresh } = useOps(60000);

  if (loading && !ops) {
    return (
      <div className="animate-pulse">
        <div className="h-32 bg-gray-700 rounded-lg"></div>
      </div>
    );
  }

  if (!ops || (Object.keys(ops.quota || {}).length === 0 && !ops.todayUsage?.cost)) {
    return null;
  }

  const q = ops.quota || {};
  const u = ops.todayUsage || {};
  const jobs = ops.cronJobs || [];
  const urgency = URGENCY_COLORS[q.urgency] || URGENCY_COLORS.low;

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Gauge className="w-5 h-5 text-cyan-400" />
          <h2 className="text-lg font-bold">Token Maximizer</h2>
        </div>
        <div className="flex items-center gap-3">
          <span
            className={`text-xs px-2 py-0.5 rounded-full font-medium ${urgency.bg} ${urgency.text}`}
          >
            {urgency.label}
          </span>
          <button
            onClick={refresh}
            className="p-1 hover:bg-gray-700 rounded transition-colors text-gray-500"
            title="Refresh ops"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {/* Quota + Usage Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Quota Bars */}
          <div className="md:col-span-2 bg-gray-800/50 rounded-lg p-4 space-y-4 border border-gray-700/50">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-gray-300">Weekly Quota (Max 20x)</span>
              <span className="text-xs text-gray-500">
                {q.days_left}d left &middot; resets {q.week_end}
              </span>
            </div>

            <QuotaBar
              label="Sonnet 4"
              pct={q.sonnet_pct}
              hrUsed={q.sonnet_hr_used}
              hrBudget={q.sonnet_hr_budget}
              hrLeft={q.sonnet_hr_left}
              waste={q.sonnet_waste}
            />
            <QuotaBar
              label="Opus 4.5"
              pct={q.opus_pct}
              hrUsed={q.opus_hr_used}
              hrBudget={q.opus_hr_budget}
              hrLeft={q.opus_hr_left}
              waste={q.opus_waste}
            />

            {/* Time elapsed bar */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-gray-400">Week elapsed</span>
                <span className="text-gray-300 font-mono">{q.time_pct}%</span>
              </div>
              <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-gray-500 transition-all duration-500"
                  style={{ width: `${Math.min(q.time_pct, 100)}%` }}
                />
              </div>
            </div>

            {/* Billable tokens summary */}
            <div className="flex gap-4 text-xs text-gray-500 pt-1 border-t border-gray-700/50">
              <span>Sonnet: {(q.sonnet_bill || 0).toLocaleString()} tok</span>
              <span>Opus: {(q.opus_bill || 0).toLocaleString()} tok</span>
              <span>Haiku: {(q.haiku_bill || 0).toLocaleString()} tok</span>
              <span className="text-gray-300 font-medium">
                Total: {(q.total_bill || 0).toLocaleString()}
              </span>
            </div>
          </div>

          {/* Today's Usage Card */}
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
            <div className="flex items-center gap-2 mb-3">
              <BarChart3 className="w-4 h-4 text-amber-400" />
              <span className="text-sm font-medium text-gray-300">Today</span>
            </div>

            <div className="space-y-3">
              <div>
                <div className="text-2xl font-bold text-amber-400">${(u.cost || 0).toFixed(4)}</div>
                <div className="text-xs text-gray-500">
                  {(u.tokens || 0).toLocaleString()} tokens &middot; {u.invocations || 0} calls
                </div>
              </div>

              {/* Top models */}
              {u.top_models?.length > 0 && (
                <div>
                  <div className="text-xs text-gray-500 mb-1">Top models</div>
                  {u.top_models.slice(0, 3).map(([model, cost, tokens], i) => (
                    <div key={i} className="flex justify-between text-xs py-0.5">
                      <span className="text-gray-400 truncate mr-2">
                        {model.replace(/^claude-/, "").replace(/-\d{8}$/, "")}
                      </span>
                      <span className="text-gray-300 font-mono">${cost.toFixed(4)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Cron Jobs */}
        {jobs.length > 0 && (
          <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700/50">
            <div className="flex items-center gap-2 mb-2">
              <Timer className="w-4 h-4 text-purple-400" />
              <span className="text-sm font-medium text-gray-300">Ops Agent Jobs</span>
              <span className="text-xs text-gray-500">({jobs.length})</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6">
              {jobs.map((job) => (
                <CronStatus key={job.id} job={job} />
              ))}
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-2 flex items-center gap-2 text-amber-400 text-xs bg-amber-500/10 rounded p-2">
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>Ops data unavailable: {error}</span>
        </div>
      )}
    </div>
  );
}
