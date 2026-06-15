export type UserRole = "superadmin" | "admin" | "user";
export type DocumentStatus = "pending" | "indexed" | "error";
export type StorageBackend = "minio" | "s3";
export type DynamoMode = "local" | "aws";
export type GroupRole = "admin" | "member";

export interface User {
  id: string;
  email: string;
  username: string | null;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface Document {
  id: string;
  filename: string;
  original_filename: string;
  mimetype: string;
  size: number;
  status: DocumentStatus;
  error_message: string | null;
  is_public: boolean;
  uploaded_by: string;
  created_at: string;
  updated_at: string;
}

export interface Group {
  id: string;
  name: string;
  description?: string;
  created_at: string;
}

export interface GroupMember {
  user_id: string;
  group_id: string;
  role: GroupRole;
  email: string;
  username?: string;
}

export interface Citation {
  filename: string;
  text: string;
  score: number;
}

export interface Message {
  role: "user" | "assistant";
  content: string;
  created_at: number;
  citations?: Citation[];
}

export interface Session {
  session_id: string;
  title: string;
  created_at: number;
}

export interface SystemSettings {
  STORAGE_BACKEND: StorageBackend;
  DYNAMO_MODE: DynamoMode;
}
