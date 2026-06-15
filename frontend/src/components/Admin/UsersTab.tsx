import { useEffect, useState } from "react";
import { Trash2, RefreshCw } from "lucide-react";
import { usersApi } from "@/api/users";
import { useAuthStore } from "@/store/authStore";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { User, UserRole } from "@/types";

const ROLE_VARIANT: Record<UserRole, "default" | "secondary" | "outline"> = {
  superadmin: "default",
  admin: "secondary",
  user: "outline",
};

export function UsersTab() {
  const [users, setUsers] = useState<User[]>([]);
  const currentUser = useAuthStore((s) => s.user);

  function load() {
    usersApi.list().then((r) => setUsers(r.data));
  }

  useEffect(load, []);

  async function handleRoleChange(userId: string, role: UserRole) {
    await usersApi.updateRole(userId, role);
    load();
  }

  async function handleToggle(userId: string) {
    await usersApi.toggleActive(userId);
    load();
  }

  async function handleDelete(userId: string) {
    if (!confirm("Permanently delete this user?")) return;
    await usersApi.delete(userId);
    load();
  }

  const isSuperadmin = currentUser?.role === "superadmin";

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">User Management</h2>
        <Button variant="outline" size="sm" onClick={load}>
          <RefreshCw className="h-4 w-4 mr-2" /> Refresh
        </Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>User</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Joined</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {users.map((u) => {
              const isSelf = u.id === currentUser?.id;
              const isTargetSuperadmin = u.role === "superadmin";
              const canModify = !isTargetSuperadmin && !isSelf;
              const canChangeRole = canModify && (isSuperadmin || u.role !== "admin");

              return (
                <TableRow key={u.id} className={!u.is_active ? "opacity-50" : ""}>
                  <TableCell>
                    <div>
                      <p className="font-medium">{u.username ?? "—"}</p>
                      <p className="text-xs text-muted-foreground">{u.email}</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    {canChangeRole ? (
                      <Select
                        value={u.role}
                        onChange={(e) => handleRoleChange(u.id, e.target.value as UserRole)}
                        className="w-28"
                      >
                        <option value="user">User</option>
                        <option value="admin">Admin</option>
                      </Select>
                    ) : (
                      <Badge variant={ROLE_VARIANT[u.role]}>{u.role}</Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge variant={u.is_active ? "success" : "outline"}>
                      {u.is_active ? "Active" : "Disabled"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {new Date(u.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="text-right">
                    {canModify && (
                      <div className="flex justify-end gap-1">
                        <Button variant="ghost" size="sm" onClick={() => handleToggle(u.id)}>
                          {u.is_active ? "Disable" : "Enable"}
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-destructive hover:text-destructive"
                          onClick={() => handleDelete(u.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    )}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
