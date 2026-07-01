import { useEffect } from "react";
import { authApi } from "@/api/auth";
import { useAuthStore } from "@/store/authStore";

const RECONNECT_DELAY_MS = 3000;

export function useRoleSync() {
  const token = useAuthStore((s) => s.token);

  useEffect(() => {
    if (!token) return;

    let socket: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let stopped = false;

    function connect() {
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      socket = new WebSocket(`${protocol}://${window.location.host}/api/v1/ws?token=${encodeURIComponent(token!)}`);

      socket.onmessage = (event) => {
        let data: { type?: string };
        try {
          data = JSON.parse(event.data);
        } catch {
          return;
        }
        if (data.type === "role_updated") {
          authApi.me().then((r) => {
            const { token: currentToken, setAuth } = useAuthStore.getState();
            if (currentToken) setAuth(currentToken, r.data);
          });
        }
      };

      socket.onclose = () => {
        if (!stopped) reconnectTimer = setTimeout(connect, RECONNECT_DELAY_MS);
      };
    }

    connect();

    return () => {
      stopped = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, [token]);
}