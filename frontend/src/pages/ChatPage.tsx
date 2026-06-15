import { useEffect, useState } from "react";
import { chatApi } from "@/api/chat";
import { SessionSidebar } from "@/components/Chat/SessionSidebar";
import { ChatWindow } from "@/components/Chat/ChatWindow";
import type { Session } from "@/types";

export function ChatPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentId, setCurrentId] = useState<string | null>(null);

  useEffect(() => {
    chatApi.listSessions().then((r) => setSessions(r.data));
  }, []);

  function handleNew() {
    setCurrentId(null);
  }

  function handleSelect(id: string) {
    setCurrentId(id);
  }

  function handleDelete(id: string) {
    chatApi.deleteSession(id).then(() => {
      setSessions((s) => s.filter((x) => x.session_id !== id));
      if (currentId === id) setCurrentId(null);
    });
  }

  function handleSessionCreated(id: string) {
    setCurrentId(id);
    chatApi.listSessions().then((r) => setSessions(r.data));
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <SessionSidebar
        sessions={sessions}
        currentId={currentId}
        onSelect={handleSelect}
        onNew={handleNew}
        onDelete={handleDelete}
      />
      <ChatWindow sessionId={currentId} onSessionCreated={handleSessionCreated} />
    </div>
  );
}
