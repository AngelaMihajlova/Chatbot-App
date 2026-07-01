import api from "./client";
import type { Document } from "@/types";

export const documentsApi = {
  list: () => api.get<Document[]>("/documents"),

  upload: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return api.post<Document>("/documents", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  delete: (id: string) => api.delete(`/documents/${id}`),

  sync: (id: string) => api.post<Document>(`/documents/${id}/sync`),

  togglePublic: (id: string) => api.patch<Document>(`/documents/${id}/public`),
};
