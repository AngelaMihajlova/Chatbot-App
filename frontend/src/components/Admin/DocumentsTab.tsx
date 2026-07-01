import { useEffect, useRef, useState } from "react";
import { Upload, Trash2, RefreshCw, FileText, Globe } from "lucide-react";
import { documentsApi } from "@/api/documents";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { Document } from "@/types";

const STATUS_VARIANT: Record<string, "success" | "warning" | "destructive"> = {
  indexed: "success",
  pending: "warning",
  error: "destructive",
};

export function DocumentsTab() {
  const [docs, setDocs] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  function load() {
    documentsApi.list().then((r) => setDocs(r.data));
  }

  useEffect(load, []);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await documentsApi.upload(file);
      load();
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this document and remove it from the knowledge base?")) return;
    await documentsApi.delete(id);
    load();
  }

  async function handleSync(id: string) {
    await documentsApi.sync(id);
    load();
  }

  async function handleTogglePublic(id: string) {
    await documentsApi.togglePublic(id);
    load();
  }

  function fmt(bytes: number) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Knowledge Base Documents</h2>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={load}>
            <RefreshCw className="h-4 w-4 mr-2" /> Refresh
          </Button>
          <Button size="sm" onClick={() => fileRef.current?.click()} disabled={uploading}>
            <Upload className="h-4 w-4 mr-2" />
            {uploading ? "Uploading…" : "Upload document"}
          </Button>
          <input ref={fileRef} type="file" accept=".pdf,.txt,.md,.csv" className="hidden" onChange={handleUpload} />
        </div>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Size</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Uploaded</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {docs.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                  No documents yet. Upload a PDF, TXT, or Markdown file to get started.
                </TableCell>
              </TableRow>
            )}
            {docs.map((doc) => (
              <TableRow key={doc.id}>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-muted-foreground shrink-0" />
                    <span className="font-medium truncate max-w-xs" title={doc.original_filename}>
                      {doc.original_filename}
                    </span>
                  </div>
                  {doc.error_message && (
                    <p className="text-xs text-destructive mt-0.5">{doc.error_message}</p>
                  )}
                </TableCell>
                <TableCell className="text-muted-foreground text-sm">{doc.mimetype.split("/")[1]}</TableCell>
                <TableCell className="text-sm">{fmt(doc.size)}</TableCell>
                <TableCell>
                  <div className="flex gap-1 flex-wrap">
                    <Badge variant={STATUS_VARIANT[doc.status] ?? "outline"}>{doc.status}</Badge>
                    {doc.is_public && <Badge variant="secondary">public</Badge>}
                  </div>
                </TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {new Date(doc.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      title={doc.is_public ? "Make private" : "Make public"}
                      className={doc.is_public ? "text-primary" : ""}
                      onClick={() => handleTogglePublic(doc.id)}
                    >
                      <Globe className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      title="Re-index"
                      onClick={() => handleSync(doc.id)}
                    >
                      <RefreshCw className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      title="Delete"
                      className="text-destructive hover:text-destructive"
                      onClick={() => handleDelete(doc.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
