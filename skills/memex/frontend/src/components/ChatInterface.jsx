import { Send, Loader2 } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import useMemexStore from "../store/useMemexStore";
import Message from "./Message";

export default function ChatInterface() {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const { messages, isTyping, sendMessage, clearChat } = useMemexStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    // Focus input on mount
    inputRef.current?.focus();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isTyping) return;

    const query = input.trim();
    setInput("");
    await sendMessage(query);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const exampleQueries = [
    "What did I promise Mark about the demo?",
    "Summarize my work this week",
    "When did I last talk to Darwin?",
    "What action items do I have?",
  ];

  return (
    <div className="h-full flex flex-col bg-memex-bg">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-2xl mx-auto">
            <div className="text-6xl mb-6">🧠</div>
            <h2 className="text-3xl font-bold mb-4">Welcome to Memex</h2>
            <p className="text-slate-400 text-lg mb-8">
              Ask me anything about your past conversations and I'll search through your memories to
              find the answer.
            </p>

            <div className="w-full space-y-3">
              <p className="text-sm text-slate-500 font-medium mb-3">Try asking:</p>
              {exampleQueries.map((query, i) => (
                <button
                  key={i}
                  onClick={() => setInput(query)}
                  className="w-full text-left px-4 py-3 bg-memex-surface border border-slate-700/50 rounded-lg hover:border-memex-primary/50 transition-all duration-200 text-slate-300"
                >
                  "{query}"
                </button>
              ))}
            </div>

            {messages.length > 5 && (
              <button
                onClick={clearChat}
                className="mt-8 text-sm text-slate-500 hover:text-slate-400 underline"
              >
                Clear conversation
              </button>
            )}
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((message) => (
              <Message key={message.id} message={message} />
            ))}

            {isTyping && (
              <div className="flex items-start gap-3 fade-in">
                <div className="w-8 h-8 rounded-full bg-memex-primary flex items-center justify-center flex-shrink-0 mt-1">
                  🧠
                </div>
                <div className="message-assistant flex items-center gap-2">
                  <Loader2 className="animate-spin" size={16} />
                  <span className="text-slate-400">Thinking...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-slate-700/50 bg-memex-surface p-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex gap-3">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask me anything about your past conversations..."
              disabled={isTyping}
              className="input flex-1"
            />
            <button
              type="submit"
              disabled={!input.trim() || isTyping}
              className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={18} />
              <span className="hidden sm:inline">Send</span>
            </button>
          </div>

          <div className="flex items-center justify-between mt-3 text-xs text-slate-500">
            <p>
              Press{" "}
              <kbd className="px-2 py-0.5 bg-slate-800 rounded border border-slate-700">Enter</kbd>{" "}
              to send,
              <kbd className="px-2 py-0.5 bg-slate-800 rounded border border-slate-700 ml-1">
                Shift+Enter
              </kbd>{" "}
              for new line
            </p>
            {messages.length > 0 && (
              <button type="button" onClick={clearChat} className="hover:text-slate-400 underline">
                Clear chat
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
