import api from "./client";
import type { User } from "@/types";

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export const authApi = {
  register: (email: string, username: string, password: string) =>
    api.post<TokenResponse>("/auth/register", { email, username, password }),

  login: (email: string, password: string) =>
    api.post<TokenResponse>("/auth/login", { email, password }),

  googleAuth: (credential: string) =>
    api.post<TokenResponse>("/auth/google", { credential }),

  me: () => api.get<User>("/auth/me"),
};
