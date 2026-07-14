import { useState, useRef, useEffect } from "react";
import { api } from "../api";
import {
  MessageSquare, X, Send, Bot, Sparkles, MapPin, Minimize2,
  Maximize2, RotateCcw
} from "lucide-react";

interface Message {
  id: string;
  sender: "user" | "assistant";
  text: string;
  intent?: string;
  data?: any;
  timestamp: Date;
}

const QUICK_ACTIONS = [
  { label: "Who is unassigned?",          q: "How many employees are awaiting seat allocation?" },
  { label: "Floor 3 availability",        q: "How many available seats are on Floor 3?" },
  { label: "Show project teams",          q: "List all projects and their team sizes." },
  { label: "Seat utilization summary",    q: "What is the overall seat utilization rate?" },
];

/* ── chat bubble ─────────────────────────────────────── */
function Bubble({ msg }: { msg: Message }) {
  const isUser = msg.sender === "user";
  const fmtTime = (d: Date) =>
    d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  return (
    <div className={`flex gap-2.5 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      {/* avatar */}
      <div className={`h-8 w-8 shrink-0 rounded-full flex items-center justify-center text-white shadow-md ${
        isUser ? "bg-gradient-to-br from-purple-600 to-indigo-600" : "bg-gradient-to-br from-slate-700 to-slate-800 border border-slate-700"
      }`}>
        {isUser ? <span className="text-[11px] font-bold">You</span> : <Bot size={14} className="text-purple-300" />}
      </div>

      {/* bubble */}
      <div className={`max-w-[78%] space-y-1 ${isUser ? "items-end" : "items-start"} flex flex-col`}>
        <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
          isUser
            ? "bg-gradient-to-br from-purple-600 to-indigo-700 text-white rounded-tr-sm shadow-lg shadow-purple-500/20"
            : "glass-card text-slate-200 rounded-tl-sm border-slate-700/40"
        }`}>
          {msg.text}
        </div>
        <span className="text-[10px] text-slate-600 px-1">{fmtTime(msg.timestamp)}</span>
      </div>
    </div>
  );
}

/* ── typing indicator ────────────────────────────────── */
function TypingIndicator() {
  return (
    <div className="flex gap-2.5">
      <div className="h-8 w-8 shrink-0 rounded-full bg-gradient-to-br from-slate-700 to-slate-800 border border-slate-700 flex items-center justify-center">
        <Bot size={14} className="text-purple-300" />
      </div>
      <div className="glass-card px-4 py-3 rounded-2xl rounded-tl-sm border-slate-700/40 flex items-center gap-1.5">
        <span className="typing-dot" />
        <span className="typing-dot" />
        <span className="typing-dot" />
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════
   AIAssistant
   ═══════════════════════════════════════════════════════ */
export default function AIAssistant() {
  const [open,      setOpen]     = useState(false);
  const [expanded,  setExpanded] = useState(false);
  const [messages,  setMessages] = useState<Message[]>([
    {
      id: "welcome",
      sender: "assistant",
      text: "👋 Hi! I'm the Ethara Workspace AI. Ask me anything about seats, employees, or projects — in plain English.",
      timestamp: new Date(),
    },
  ]);
  const [input,   setInput]   = useState("");
  const [loading, setLoading] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef  = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 120);
  }, [open]);

  const send = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;
    setInput("");
    const userMsg: Message = {
      id: Date.now().toString(),
      sender: "user",
      text: trimmed,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);
    try {
      const res = await api.queryAI(trimmed);
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: "assistant",
        text: res.answer,
        intent: res.intent,
        data: res.data,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch {
      setMessages(prev => [
        ...prev,
        { id: Date.now().toString(), sender: "assistant", text: "⚠️ Could not reach the AI engine. Please check that the backend is running.", timestamp: new Date() },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => setMessages([{
    id: "welcome",
    sender: "assistant",
    text: "👋 Chat cleared. How can I help you?",
    timestamp: new Date(),
  }]);

  const panelWidth  = expanded ? "w-[480px]" : "w-[360px]";
  const panelHeight = expanded ? "h-[580px]" : "h-[480px]";

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">

      {/* ── Chat Panel ───────────────────────────── */}
      {open && (
        <div className={`glass-card rounded-2xl flex flex-col overflow-hidden shadow-2xl shadow-black/50 border border-slate-700/40 animate-scaleIn ${panelWidth} ${panelHeight} transition-all duration-300`}>

          {/* header */}
          <div className="bg-gradient-to-r from-purple-900/60 to-indigo-900/50 px-4 py-3.5 flex items-center gap-3 border-b border-slate-700/40 shrink-0">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-purple-500/30">
              <Sparkles size={14} className="text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold text-white leading-none">Ethara AI</p>
              <p className="text-[10px] text-purple-300 font-medium mt-0.5">Workspace intelligence</p>
            </div>
            <div className="flex items-center gap-1">
              <button onClick={clearChat}
                className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-700/50 transition-all"
                title="Clear chat">
                <RotateCcw size={13} />
              </button>
              <button onClick={() => setExpanded(!expanded)}
                className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-700/50 transition-all"
                title={expanded ? "Minimize" : "Expand"}>
                {expanded ? <Minimize2 size={13} /> : <Maximize2 size={13} />}
              </button>
              <button onClick={() => setOpen(false)}
                className="text-slate-400 hover:text-red-400 p-1.5 rounded-lg hover:bg-slate-700/50 transition-all"
                title="Close">
                <X size={14} />
              </button>
            </div>
          </div>

          {/* messages */}
          <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
            {messages.map(m => <Bubble key={m.id} msg={m} />)}
            {loading && <TypingIndicator />}
            <div ref={bottomRef} />
          </div>

          {/* quick actions */}
          {messages.length <= 2 && !loading && (
            <div className="px-4 pb-3 flex gap-2 flex-wrap">
              {QUICK_ACTIONS.map(({ label, q }) => (
                <button
                  key={label}
                  onClick={() => send(q)}
                  className="text-[11px] px-3 py-1.5 rounded-full border border-slate-700/60 bg-slate-800/50 text-slate-300 hover:text-white hover:border-purple-500/50 hover:bg-purple-500/10 transition-all font-medium"
                >
                  {label}
                </button>
              ))}
            </div>
          )}

          {/* input */}
          <div className="px-4 pb-4 shrink-0">
            <div className="flex items-center gap-2 bg-slate-900/70 border border-slate-700/60 rounded-xl px-3 py-2.5 focus-within:border-purple-500/50 focus-within:shadow-[0_0_0_2px_rgba(139,92,246,0.15)] transition-all">
              <MapPin size={13} className="text-slate-600 shrink-0" />
              <input
                ref={inputRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === "Enter" && !e.shiftKey && send(input)}
                placeholder="Ask about seats, employees…"
                className="flex-1 bg-transparent text-sm text-slate-200 placeholder:text-slate-600 outline-none min-w-0"
              />
              <button
                onClick={() => send(input)}
                disabled={!input.trim() || loading}
                className="h-7 w-7 rounded-lg btn-gradient flex items-center justify-center text-white disabled:opacity-30 disabled:transform-none shrink-0 transition-all"
              >
                <Send size={12} />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── FAB Button ───────────────────────────── */}
      <button
        onClick={() => setOpen(!open)}
        className="relative h-14 w-14 rounded-full btn-gradient text-white flex items-center justify-center shadow-xl shadow-purple-500/40 ring-pulse"
        aria-label="Toggle AI assistant"
      >
        {open
          ? <X size={22} />
          : <MessageSquare size={22} />
        }
        {!open && messages.length > 1 && (
          <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-emerald-500 border-2 border-slate-950 text-[9px] font-bold text-white flex items-center justify-center">
            {Math.min(messages.length - 1, 9)}
          </span>
        )}
      </button>
    </div>
  );
}
