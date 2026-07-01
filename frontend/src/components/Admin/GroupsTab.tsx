import { useEffect, useState } from "react";
import { Trash2, Plus, Users, FileText, ShieldCheck } from "lucide-react";
import { groupsApi } from "@/api/groups";
import { documentsApi } from "@/api/documents";
import { usersApi } from "@/api/users";
import { useAuthStore } from "@/store/authStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Combobox } from "@/components/ui/combobox";
import type { Document, Group, GroupMember, User } from "@/types";

export function GroupsTab() {
  const currentUser = useAuthStore((s) => s.user);
  const isSuperadmin = currentUser?.role === "superadmin";
  const isAdmin = isSuperadmin || currentUser?.role === "admin";

  const [groups, setGroups] = useState<Group[]>([]);
  const [selected, setSelected] = useState<Group | null>(null);
  const [members, setMembers] = useState<GroupMember[]>([]);
  const [groupDocs, setGroupDocs] = useState<Document[]>([]);
  const [allDocs, setAllDocs] = useState<Document[]>([]);
  const [allUsers, setAllUsers] = useState<User[]>([]);

  const [newGroupName, setNewGroupName] = useState("");
  const [newGroupDesc, setNewGroupDesc] = useState("");
  const [selectedUserId, setSelectedUserId] = useState("");
  const [selectedDocId, setSelectedDocId] = useState("");

  function loadGroups() {
    groupsApi.list().then((r) => setGroups(r.data));
  }

  useEffect(() => {
    loadGroups();
    documentsApi.list().then((r) => setAllDocs(r.data));
    usersApi.list().then((r) => setAllUsers(r.data));
  }, []);

  useEffect(() => {
    if (!selected) return;
    groupsApi.listMembers(selected.id).then((r) => setMembers(r.data));
    groupsApi.listDocuments(selected.id).then((r) => setGroupDocs(r.data));
  }, [selected]);

  async function handleCreate() {
    if (!newGroupName.trim()) return;
    await groupsApi.create(newGroupName.trim(), newGroupDesc.trim() || undefined);
    setNewGroupName("");
    setNewGroupDesc("");
    loadGroups();
  }

  async function handleDelete(groupId: string) {
    if (!confirm("Delete this group? Members will lose access to its documents.")) return;
    await groupsApi.delete(groupId);
    if (selected?.id === groupId) setSelected(null);
    loadGroups();
  }

  async function handleAddMember() {
    if (!selected || !selectedUserId) return;
    await groupsApi.addMember(selected.id, selectedUserId);
    setSelectedUserId("");
    groupsApi.listMembers(selected.id).then((r) => setMembers(r.data));
  }

  async function handlePromote(userId: string) {
    if (!selected) return;
    await groupsApi.promoteMember(selected.id, userId);
    groupsApi.listMembers(selected.id).then((r) => setMembers(r.data));
  }

  async function handleRemoveMember(userId: string) {
    if (!selected) return;
    await groupsApi.removeMember(selected.id, userId);
    groupsApi.listMembers(selected.id).then((r) => setMembers(r.data));
  }

  async function handleAssignDoc() {
    if (!selected || !selectedDocId) return;
    await groupsApi.assignDocument(selected.id, selectedDocId);
    setSelectedDocId("");
    groupsApi.listDocuments(selected.id).then((r) => setGroupDocs(r.data));
  }

  async function handleRemoveDoc(docId: string) {
    if (!selected) return;
    await groupsApi.removeDocument(selected.id, docId);
    groupsApi.listDocuments(selected.id).then((r) => setGroupDocs(r.data));
  }

  async function handleTogglePublic(docId: string) {
    await documentsApi.togglePublic(docId);
    documentsApi.list().then((r) => setAllDocs(r.data));
    if (selected) groupsApi.listDocuments(selected.id).then((r) => setGroupDocs(r.data));
  }

  const memberIds = new Set(members.map((m) => m.user_id));
  const groupDocIds = new Set(groupDocs.map((d) => d.id));
  const availableUsers = allUsers.filter((u) => !memberIds.has(u.id) && u.role !== "superadmin");
  const availableDocs = allDocs.filter((d) => !groupDocIds.has(d.id));

  return (
    <div className="flex gap-6 h-full min-h-0">
      {/* Group list */}
      <div className="w-72 shrink-0 flex flex-col min-h-0 space-y-3">
        <h2 className="text-lg font-semibold shrink-0">Groups</h2>

        {isSuperadmin && (
          <div className="space-y-2 p-3 border rounded-lg bg-muted/30 shrink-0">
            <Input
              placeholder="Group name"
              value={newGroupName}
              onChange={(e) => setNewGroupName(e.target.value)}
            />
            <Input
              placeholder="Description (optional)"
              value={newGroupDesc}
              onChange={(e) => setNewGroupDesc(e.target.value)}
            />
            <Button size="sm" className="w-full" onClick={handleCreate}>
              <Plus className="h-4 w-4 mr-1" /> Create group
            </Button>
          </div>
        )}

        <div className="flex-1 min-h-0 overflow-y-auto space-y-1 pr-1">
          {groups.map((g) => (
            <div
              key={g.id}
              className={`group flex items-center gap-2 rounded-md px-2 py-2 cursor-pointer hover:bg-accent text-sm ${
                selected?.id === g.id ? "bg-accent font-medium" : ""
              }`}
              onClick={() => setSelected(g)}
            >
              <span className="flex-1 truncate">{g.name}</span>
              {isSuperadmin && (
                <button
                  className="opacity-0 group-hover:opacity-100 text-destructive"
                  onClick={(e) => { e.stopPropagation(); handleDelete(g.id); }}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              )}
            </div>
          ))}
          {groups.length === 0 && (
            <p className="text-xs text-muted-foreground text-center py-4">No groups yet</p>
          )}
        </div>
      </div>

      <Separator orientation="vertical" />

      {/* Group detail */}
      {selected ? (
        <div className="flex-1 min-h-0 flex flex-col space-y-6 overflow-y-auto">
          <div className="shrink-0">
            <h3 className="font-semibold text-base">{selected.name}</h3>
            {selected.description && (
              <p className="text-sm text-muted-foreground">{selected.description}</p>
            )}
          </div>

          {/* Members */}
          <div className="flex flex-col min-h-0 space-y-3">
            <div className="flex items-center gap-2 shrink-0">
              <Users className="h-4 w-4" />
              <span className="font-medium text-sm">Members</span>
            </div>
            <div className="flex gap-2 shrink-0">
              <Combobox
                value={selectedUserId}
                onChange={setSelectedUserId}
                options={availableUsers.map((u) => ({ value: u.id, label: u.username ?? u.email }))}
                placeholder="Add a user…"
                className="flex-1"
              />
              <Button size="sm" onClick={handleAddMember} disabled={!selectedUserId}>
                Add
              </Button>
            </div>
            <div className="space-y-1 max-h-64 overflow-y-auto pr-1">
              {members.map((m) => (
                <div key={m.user_id} className="flex items-center gap-2 text-sm py-1">
                  <span className="flex-1">{m.username ?? m.email}</span>
                  <Badge variant={m.role === "admin" ? "default" : "outline"}>{m.role}</Badge>
                  {isSuperadmin && m.role === "member" && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 text-xs"
                      onClick={() => handlePromote(m.user_id)}
                    >
                      <ShieldCheck className="h-3 w-3 mr-1" /> Promote
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 text-destructive"
                    onClick={() => handleRemoveMember(m.user_id)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              ))}
              {members.length === 0 && (
                <p className="text-xs text-muted-foreground">No members yet</p>
              )}
            </div>
          </div>

          <Separator className="shrink-0" />

          {/* Documents */}
          <div className="flex flex-col min-h-0 space-y-3">
            <div className="flex items-center gap-2 shrink-0">
              <FileText className="h-4 w-4" />
              <span className="font-medium text-sm">Documents</span>
            </div>
            <div className="flex gap-2 shrink-0">
              <Combobox
                value={selectedDocId}
                onChange={setSelectedDocId}
                options={availableDocs.map((d) => ({ value: d.id, label: d.original_filename }))}
                placeholder="Assign a document…"
                className="flex-1"
              />
              <Button size="sm" onClick={handleAssignDoc} disabled={!selectedDocId}>
                Assign
              </Button>
            </div>
            <div className="space-y-1 max-h-64 overflow-y-auto pr-1">
              {groupDocs.map((d) => (
                <div key={d.id} className="flex items-center gap-2 text-sm py-1">
                  <span className="flex-1 truncate">{d.original_filename}</span>
                  {isAdmin && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 text-xs"
                      onClick={() => handleTogglePublic(d.id)}
                    >
                      {d.is_public ? "Make private" : "Make public"}
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 text-destructive"
                    onClick={() => handleRemoveDoc(d.id)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              ))}
              {groupDocs.length === 0 && (
                <p className="text-xs text-muted-foreground">No documents assigned</p>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center text-muted-foreground text-sm">
          Select a group to manage its members and documents
        </div>
      )}
    </div>
  );
}
