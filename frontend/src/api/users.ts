import api from "./client";
import type { User, UserRole } from "@/types";

export const usersApi = {
  list: () => api.get<User[]>("/users"),

  updateRole: (userId: string, role: UserRole) =>
    api.patch<User>(`/users/${userId}/role`, { role }),

  toggleActive: (userId: string) =>
    api.patch<User>(`/users/${userId}/toggle-active`),

  delete: (userId: string) => api.delete(`/users/${userId}`),
};
