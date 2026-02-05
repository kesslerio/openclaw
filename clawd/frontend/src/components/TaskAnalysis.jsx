import {
  ChevronDown,
  ChevronUp,
  Bot,
  User,
  Users,
  Ban,
  Clock,
  Zap,
  AlertCircle,
  CheckCircle2,
  ListChecks,
} from "lucide-react";
import React, { useState } from "react";

const automationIcons = {
  llm: { icon: Bot, color: "text-green-400", bg: "bg-green-500/10", label: "AI Automatable" },
  hybrid: { icon: Users, color: "text-blue-400", bg: "bg-blue-500/10", label: "AI + Human" },
  human: { icon: User, color: "text-amber-400", bg: "bg-amber-500/10", label: "Human Required" },
  blocked: { icon: Ban, color: "text-red-400", bg: "bg-red-500/10", label: "Blocked" },
};

export default function TaskAnalysis({ task }) {
  const [expanded, setExpanded] = useState(false);

  if (!task.analysis) {
    return (
      <div className="mt-3 pt-3 border-t border-gray-700/50">
        <div className="text-xs text-gray-500 italic">No analysis available</div>
      </div>
    );
  }

  const { analysis } = task;
  const autoConfig = automationIcons[analysis.automationType] || automationIcons.human;
  const AutoIcon = autoConfig.icon;

  return (
    <div className="mt-3 pt-3 border-t border-gray-700/50">
      {/* Summary Header */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          setExpanded(!expanded);
        }}
        className="w-full flex items-center justify-between hover:bg-gray-700/30 rounded p-2 transition-colors"
      >
        <div className="flex items-center gap-2">
          <div className={`p-1 rounded ${autoConfig.bg}`}>
            <AutoIcon className={`w-4 h-4 ${autoConfig.color}`} />
          </div>
          <span className="text-sm font-medium">{autoConfig.label}</span>
          {analysis.isBlocked && <AlertCircle className="w-4 h-4 text-red-400" />}
        </div>
        <div className="flex items-center gap-2">
          {analysis.estimatedMinutes && (
            <span className="text-xs text-gray-500 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {analysis.estimatedMinutes}m
            </span>
          )}
          {expanded ? (
            <ChevronUp className="w-4 h-4 text-gray-500" />
          ) : (
            <ChevronDown className="w-4 h-4 text-gray-500" />
          )}
        </div>
      </button>

      {/* Expanded Details */}
      {expanded && (
        <div className="mt-2 space-y-3 text-sm">
          {/* Automation Reason */}
          <div className="bg-gray-700/30 rounded p-2">
            <div className="text-xs text-gray-400 mb-1">Analysis</div>
            <div className="text-gray-300">{analysis.automationReason}</div>
          </div>

          {/* Blockage */}
          {analysis.isBlocked && analysis.blockageReason && (
            <div className="bg-red-500/10 border border-red-500/30 rounded p-2">
              <div className="flex items-center gap-2 text-red-400 mb-1">
                <AlertCircle className="w-4 h-4" />
                <span className="text-xs font-medium">BLOCKED</span>
              </div>
              <div className="text-red-300 text-xs">{analysis.blockageReason}</div>
            </div>
          )}

          {/* Steps */}
          {analysis.steps && analysis.steps.length > 0 && (
            <div>
              <div className="flex items-center gap-2 text-gray-400 mb-2">
                <ListChecks className="w-4 h-4" />
                <span className="text-xs font-medium">Action Steps</span>
              </div>
              <div className="space-y-1.5">
                {analysis.steps.map((step, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <div className="mt-0.5 flex-shrink-0 w-5 h-5 rounded-full bg-gray-700 flex items-center justify-center text-xs font-medium">
                      {idx + 1}
                    </div>
                    <div className="text-gray-300 text-xs flex-1">{step}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Capabilities */}
          {analysis.aiCapabilities && analysis.aiCapabilities.length > 0 && (
            <div>
              <div className="flex items-center gap-2 text-green-400 mb-1.5">
                <Zap className="w-4 h-4" />
                <span className="text-xs font-medium">AI Can Help With</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {analysis.aiCapabilities.map((cap, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 bg-green-500/10 text-green-400 rounded text-xs"
                  >
                    {cap}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Human Requirements */}
          {analysis.humanRequirements && analysis.humanRequirements.length > 0 && (
            <div>
              <div className="flex items-center gap-2 text-amber-400 mb-1.5">
                <User className="w-4 h-4" />
                <span className="text-xs font-medium">Human Needed For</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {analysis.humanRequirements.map((req, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 bg-amber-500/10 text-amber-400 rounded text-xs"
                  >
                    {req}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
