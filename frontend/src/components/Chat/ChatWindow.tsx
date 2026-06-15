import { useEffect, useRef, useState } from "react";
import { Send, Loader2 } from "lucide-react";
import { chatApi } from "@/api/chat";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { MessageBubble } from "./MessageBubble";
import { CitationsPanel } from "./CitationsPanel";
import type { Citation, Message } from "@/types";

interface Props {
  sessionId: string | null;
  onSessionCreated: (id: string) => void;
}

export function ChatWindow({ sessionId, onSessionCreated }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [citations, setCitations] = useState<Citation[] | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sessionId) {
      setMessages([]);
      return;
    }
    chatApi.getMessages(sessionId).then((r) => setMessages(r.data));
  }, [sessionId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send() {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    const userMsg: Message = { role: "user", content: text, created_at: Date.now() };
    setMessages((m) => [...m, userMsg]);
    setLoading(true);
    try {
      const res = await chatApi.send(text, sessionId ?? undefined);
      const { session_id, message, citations: cits } = res.data;
      if (!sessionId) onSessionCreated(session_id);
      const assistantMsg: Message = {
        role: "assistant",
        content: message,
        created_at: Date.now(),
        citations: cits,
      };
      setMessages((m) => [...m, assistantMsg]);
      if (cits.length > 0) setCitations(cits);
    } finally {
      setLoading(false);
    }
  }

  function handleKey(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <div className="flex flex-1 overflow-hidden">
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6">
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full text-muted-foreground text-sm">
              Ask anything about your company's knowledge base.
            </div>
          )}
          {messages.map((m, i) => (
            <MessageBubble key={i} message={m} onCitationsClick={setCitations} />
          ))}
          {loading && (
            <div className="flex justify-start mb-4">
              <div className="bg-muted rounded-2xl rounded-tl-sm px-4 py-2.5">
                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="border-t p-4">
          <div className="flex gap-2 max-w-3xl mx-auto">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Type a message… (Enter to send, Shift+Enter for newline)"
              className="resize-none min-h-[44px] max-h-32"
              rows={1}
            />
            <Button onClick={send} disabled={loading || !input.trim()} size="icon">
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Citations panel */}
      {citations && <CitationsPanel citations={citations} onClose={() => setCitations(null)} />}
    </div>
  );
}
