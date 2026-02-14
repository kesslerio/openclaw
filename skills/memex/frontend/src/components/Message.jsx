import { format } from "date-fns";
import { FileText, AlertCircle } from "lucide-react";
import ReactMarkdown from "react-markdown";

export default function Message({ message }) {
  const { role, content, sources, confidence, error, timestamp } = message;

  const isUser = role === "user";
  const time = timestamp ? format(new Date(timestamp), "HH:mm") : "";

  return (
    <div className={`flex items-start gap-3 fade-in ${isUser ? "justify-end" : ""}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-memex-primary flex items-center justify-center flex-shrink-0 mt-1">
          🧠
        </div>
      )}

      <div className={`flex flex-col ${isUser ? "items-end" : "items-start"} max-w-[80%]`}>
        <div className={isUser ? "message-user" : "message-assistant"}>
          {error ? (
            <div className="flex items-start gap-2 text-red-400">
              <AlertCircle size={20} className="flex-shrink-0 mt-0.5" />
              <div className="prose prose-sm">
                <ReactMarkdown>{content}</ReactMarkdown>
              </div>
            </div>
          ) : (
            <div className="prose prose-sm">
              <ReactMarkdown>{content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Metadata */}
        <div className="flex items-center gap-3 mt-2 text-xs text-slate-500">
          <span>{time}</span>

          {!isUser && confidence !== undefined && (
            <span
              className={`flex items-center gap-1 ${
                confidence >= 0.8
                  ? "text-green-500"
                  : confidence >= 0.5
                    ? "text-yellow-500"
                    : "text-red-500"
              }`}
            >
              <div className="w-1.5 h-1.5 rounded-full bg-current"></div>
              {Math.round(confidence * 100)}% confident
            </span>
          )}
        </div>

        {/* Sources */}
        {sources && sources.length > 0 && (
          <div className="mt-3 space-y-2 w-full">
            <div className="text-xs font-medium text-slate-400 flex items-center gap-1">
              <FileText size={14} />
              Sources ({sources.length})
            </div>
            {sources.map((source, i) => (
              <SourceCard key={i} source={source} index={i + 1} />
            ))}
          </div>
        )}
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-full bg-memex-secondary flex items-center justify-center flex-shrink-0 mt-1 font-semibold text-sm">
          A
        </div>
      )}
    </div>
  );
}

function SourceCard({ source, index }) {
  const { date, snippet, score, transcript_path } = source;

  const scoreColor =
    score >= 0.8 ? "text-green-500" : score >= 0.6 ? "text-yellow-500" : "text-slate-500";

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-3 text-sm">
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2">
          <span className="text-memex-primary font-semibold">#{index}</span>
          <span className="text-slate-400">📅 {date}</span>
        </div>
        <span className={`text-xs font-mono ${scoreColor}`}>{(score * 100).toFixed(0)}%</span>
      </div>

      <p className="text-slate-300 leading-relaxed">{snippet}</p>

      {transcript_path && (
        <button className="mt-2 text-xs text-memex-secondary hover:text-cyan-400 flex items-center gap-1">
          <FileText size={12} />
          View full transcript
        </button>
      )}
    </div>
  );
}
