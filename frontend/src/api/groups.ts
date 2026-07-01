import apiClient from "./client";
import type { Document, Group, GroupMember } from "@/types";

export const groupsApi = {
  list: () => apiClient.get<Group[]>("/groups"),
  create: (name: string, description?: string) =>
    apiClient.post<Group>("/groups", { name, description }),
  delete: (groupId: string) => apiClient.delete(`/groups/${groupId}`),

  listMembers: (groupId: string) =>
    apiClient.get<GroupMember[]>(`/groups/${groupId}/members`),
  addMember: (groupId: string, userId: string) =>
    apiClient.post<GroupMember>(`/groups/${groupId}/members`, { user_id: userId }),
  promoteMember: (groupId: string, userId: string) =>
    apiClient.patch<GroupMember>(`/groups/${groupId}/members/${userId}/promote`),
  removeMember: (groupId: string, userId: string) =>
    apiClient.delete(`/groups/${groupId}/members/${userId}`),

  listDocuments: (groupId: string) =>
    apiClient.get<Document[]>(`/groups/${groupId}/documents`),
  assignDocument: (groupId: string, documentId: string) =>
    apiClient.post<Document>(`/groups/${groupId}/documents`, { document_id: documentId }),
  removeDocument: (groupId: string, documentId: string) =>
    apiClient.delete(`/groups/${groupId}/documents/${documentId}`),
};
