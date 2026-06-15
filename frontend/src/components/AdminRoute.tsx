import { Navigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";

export function AdminRoute({ children }: { children: React.ReactNode }) {
  const { token, user } = useAuthStore();
  if (!token) return <Navigate to="/login" replace />;
  if (!user || (user.role !== "admin" && user.role !== "superadmin")) {
    return <Navigate to="/chat" replace />;
  }
  return <>{children}</>;
}
