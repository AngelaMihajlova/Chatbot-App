import { ChevronLeft, ChevronRight, FileText } from "lucide-react";
import type { Citation } from "@/types";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface Props {
  citations: Citation[] | null;
  collapsed: boolean;
  onToggleCollapsed: () => void;
}

function groupBySource(citations: Citation[]) {
  const groups: { key: string; filename: string; items: Citation[] }[] = [];
  for (const c of citations) {
    const key = c.document_id ?? c.filename;
    const group = groups.find((g) => g.key === key);
    if (group) group.items.push(c);
    else groups.push({ key, filename: c.filename, items: [c] });
  }
  return groups;
}

export function CitationsPanel({ citations, collapsed, onToggleCollapsed }: Props) {
  const groups = citations ? groupBySource(citations) : [];
  const count = citations?.length ?? 0;

  if (collapsed) {
    return (
      <div className="absolute right-0 top-0 h-full w-10 border-l flex flex-col items-center gap-2 bg-background py-3 z-10">
        <Button size="icon" variant="ghost" onClick={onToggleCollapsed} title="Expand sources">
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <span className="mt-2 text-[10px] font-medium text-muted-foreground [writing-mode:vertical-rl] rotate-180">
          Sources
        </span>
      </div>
    );
  }

  return (
    <div className="w-80 border-l flex flex-col bg-background">
      <div className="flex items-center justify-between p-3 border-b">
        <div className="flex items-baseline gap-2">
          <span className="text-sm font-medium">Sources</span>
          {count > 0 && (
            <span className="text-xs text-muted-foreground">
              {count} source{count !== 1 ? "s" : ""}
            </span>
          )}
        </div>
        <Button size="icon" variant="ghost" onClick={onToggleCollapsed} title="Collapse sources">
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {count === 0 && (
          <p className="text-xs text-muted-foreground text-center mt-4">
            Click a message's "sources" link to view its references here.
          </p>
        )}
        {groups.map((group) => (
          <div key={group.key} className="rounded-lg border p-3 space-y-2">
            <div className="flex items-center gap-2">
              <FileText className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
              <span className="text-xs font-medium truncate">{group.filename}</span>
            </div>
            <div className="space-y-2">
              {group.items.map((c, i) => (
                <div key={i} className="pl-2 border-l space-y-1">
                  <Badge variant="outline" className="text-xs">
                    {Math.round(c.score * 100)}%
                  </Badge>
                  <p className="text-xs text-muted-foreground leading-relaxed line-clamp-4">{c.text}</p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
