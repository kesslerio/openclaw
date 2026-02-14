import { X, Send, Copy, CheckCircle } from "lucide-react";
import { useState, useEffect } from "react";
import useMemexStore from "../store/useMemexStore";

export default function EmailComposeModal() {
  const { emailComposeOpen, emailComposeDefaults, closeEmailCompose, integrationStatus } =
    useMemexStore();
  const [to, setTo] = useState("");
  const [cc, setCc] = useState("");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [copied, setCopied] = useState(false);

  // Sync defaults when modal opens
  useEffect(() => {
    if (emailComposeDefaults) {
      setTo((emailComposeDefaults.to || []).join(", "));
      setSubject(emailComposeDefaults.subject || "");
      setBody("");
      setCc("");
      setCopied(false);
    }
  }, [emailComposeDefaults]);

  if (!emailComposeOpen) return null;

  const canSend = integrationStatus?.gmail_send_available;

  const handleCopyToClipboard = async () => {
    const emailText = [`To: ${to}`, cc ? `Cc: ${cc}` : "", `Subject: ${subject}`, "", body]
      .filter(Boolean)
      .join("\n");

    try {
      await navigator.clipboard.writeText(emailText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  const handleSend = async () => {
    if (!canSend) {
      handleCopyToClipboard();
      return;
    }

    try {
      const toList = to
        .split(",")
        .map((e) => e.trim())
        .filter(Boolean);
      const ccList = cc
        ? cc
            .split(",")
            .map((e) => e.trim())
            .filter(Boolean)
        : [];

      await fetch("/api/email/compose", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ to: toList, cc: ccList, subject, body }),
      });
    } catch (err) {
      console.error("Send failed:", err);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-memex-surface border border-slate-700/50 rounded-xl w-full max-w-2xl mx-4 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-700/50">
          <h3 className="text-lg font-semibold">Compose Email</h3>
          <button
            onClick={closeEmailCompose}
            className="p-1.5 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Fields */}
        <div className="p-4 space-y-3">
          <div className="flex items-center gap-3">
            <label className="text-sm text-slate-400 w-12">To</label>
            <input
              type="text"
              value={to}
              onChange={(e) => setTo(e.target.value)}
              className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-memex-primary"
            />
          </div>

          <div className="flex items-center gap-3">
            <label className="text-sm text-slate-400 w-12">Cc</label>
            <input
              type="text"
              value={cc}
              onChange={(e) => setCc(e.target.value)}
              placeholder="Optional"
              className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-memex-primary"
            />
          </div>

          <div className="flex items-center gap-3">
            <label className="text-sm text-slate-400 w-12">Subject</label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-memex-primary"
            />
          </div>

          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            rows={8}
            placeholder="Write your email..."
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-memex-primary resize-none"
          />

          {!canSend && (
            <p className="text-xs text-amber-400 bg-amber-900/20 px-3 py-2 rounded-lg">
              Gmail send scope is not authorized. Use "Copy to Clipboard" and paste into your email
              client.
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-2 p-4 border-t border-slate-700/50">
          <button
            onClick={closeEmailCompose}
            className="px-4 py-2 text-sm text-slate-400 hover:text-white transition-colors"
          >
            Cancel
          </button>

          <button
            onClick={handleCopyToClipboard}
            className="flex items-center gap-1.5 px-4 py-2 text-sm bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-colors"
          >
            {copied ? <CheckCircle size={14} className="text-green-400" /> : <Copy size={14} />}
            {copied ? "Copied!" : "Copy to Clipboard"}
          </button>

          {canSend && (
            <button
              onClick={handleSend}
              className="flex items-center gap-1.5 px-4 py-2 text-sm bg-memex-primary text-white rounded-lg hover:bg-memex-primary/80 transition-colors"
            >
              <Send size={14} /> Send
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
