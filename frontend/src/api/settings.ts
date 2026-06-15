import api from "./client";
import type { SystemSettings } from "@/types";

export const settingsApi = {
  get: () => api.get<SystemSettings>("/settings"),

  update: (patch: Partial<SystemSettings>) =>
    api.patch<SystemSettings>("/settings", patch),
};
