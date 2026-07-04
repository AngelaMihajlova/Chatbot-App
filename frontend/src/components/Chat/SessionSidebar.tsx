import { Trash2, Plus, MessageSquare, Settings, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useAuthStore } from "@/store/authStore";
import { useNavigate } from "react-router-dom";
import type { Session } from "@/types";

interface Props {
  sessions: Session[];
  currentId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
}

export function SessionSidebar({ sessions, currentId, onSelect, onNew, onDelete }: Props) {
  const { user, clearAuth } = useAuthStore();
  const navigate = useNavigate();
  const isAdmin = user?.role === "admin" || user?.role === "superadmin";

  return (
    <div className="flex flex-col h-full w-64 border-r bg-muted/30">
      <div className="p-3 flex items-center justify-between">
        <span className="font-bold text-base tracking-tight text-gray-800">Chats</span>
        <Button
          size="icon"
          variant="ghost"
          onClick={onNew}
          title="New chat"
          className="rounded-full border border-border/60 bg-gradient-to-b from-white to-gray-50 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-200"
        >
          <Plus className="h-4 w-4" />
        </Button>
      </div>
      <Separator />
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {sessions.length === 0 && (
          <p className="text-xs text-muted-foreground text-center mt-4">No conversations yet</p>
        )}
        {sessions.map((s) => (
          <div
            key={s.session_id}
            className={`group flex items-center gap-2 rounded-xl border border-border/60 bg-white px-3 py-2 cursor-pointer text-sm shadow-sm transition-all duration-200 hover:shadow-md hover:border-border ${
              currentId === s.session_id ? "bg-accent border-accent font-medium shadow-md" : ""
            }`}
            onClick={() => onSelect(s.session_id)}
          >
            <MessageSquare className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
            <span className="flex-1 truncate">{s.title || "New conversation"}</span>
            <button
              className="opacity-0 group-hover:opacity-100 hover:text-destructive"
              onClick={(e) => { e.stopPropagation(); onDelete(s.session_id); }}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          </div>
        ))}
      </div>
      <Separator />
      <div className="p-3 space-y-2">
        {isAdmin && (
          <Button
            variant="ghost"
            size="sm"
            className="
                w-full
                justify-start
                gap-2
                rounded-xl
                border
                border-border/60
                bg-gradient-to-b
                from-white
                to-gray-50
                shadow-md
                -translate-y-0.5
                transition-all
                duration-200
              "
            onClick={() => navigate("/admin")}
          >
            <ShieldCheck className="h-4 w-4" />
            Admin panel
          </Button>
        )}
        <div className="flex items-center justify-between gap-2">
          <span className="truncate rounded-lg border border-gray-200 bg-gradient-to-br from-gray-100 to-gray-200/80 px-3 py-1.5 text-xs font-medium text-gray-600 shadow-sm">
            {user?.email}
          </span>
          <Button
            variant="ghost"
            size="sm"
            className="text-xs"
            onClick={() => { clearAuth(); navigate("/login"); }}
          >
            Sign out
          </Button>
        </div>
      </div>
    </div>
  );
}
