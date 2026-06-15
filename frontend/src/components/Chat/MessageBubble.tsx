import type { Citation, Message } from "@/types";

interface Props {
  message: Message;
  onCitationsClick?: (citations: Citation[]) => void;
}

export function MessageBubble({ message, onCitationsClick }: Props) {
  const isUser = message.role === "user";
  const hasCitations = (message.citations?.length ?? 0) > 0;

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div className={`max-w-[75%] ${isUser ? "items-end" : "items-start"} flex flex-col gap-1`}>
        <div
          className={`rounded-2xl px-4 py-2.5 text-sm whitespace-pre-wrap leading-relaxed ${
            isUser
              ? "bg-primary text-primary-foreground rounded-tr-sm"
              : "bg-muted rounded-tl-sm"
          }`}
        >
          {message.content}
        </div>
        {hasCitations && !isUser && (
          <button
            className="text-xs text-muted-foreground underline hover:text-foreground ml-1"
            onClick={() => onCitationsClick?.(message.citations!)}
          >
            {message.citations!.length} source{message.citations!.length !== 1 ? "s" : ""}
          </button>
        )}
      </div>
    </div>
  );
}
