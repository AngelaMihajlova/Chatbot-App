import api from "./client";
import type { Citation, Message, Session } from "@/types";

interface ChatResponse {
  session_id: string;
  message: string;
  citations: Citation[];
}

export const chatApi = {
  send: (message: string, session_id?: string) =>
    api.post<ChatResponse>("/chat", { message, session_id }),

  listSessions: () => api.get<Session[]>("/chat/sessions"),

  getMessages: (sessionId: string) =>
    api.get<Message[]>(`/chat/sessions/${sessionId}/messages`),

  deleteSession: (sessionId: string) =>
    api.delete(`/chat/sessions/${sessionId}`),
};
