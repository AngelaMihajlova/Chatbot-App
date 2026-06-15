import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { DocumentsTab } from "@/components/Admin/DocumentsTab";
import { UsersTab } from "@/components/Admin/UsersTab";
import { SettingsTab } from "@/components/Admin/SettingsTab";
import { GroupsTab } from "@/components/Admin/GroupsTab";
import { MessageSquare } from "lucide-react";

export function AdminPage() {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const [tab, setTab] = useState("documents");
  const isSuperadmin = user?.role === "superadmin";
  const isAdmin = user?.role === "admin" || isSuperadmin;

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b px-6 py-3 flex items-center justify-between">
        <div>
          <h1 className="font-semibold">Admin Panel</h1>
          <p className="text-xs text-muted-foreground">{user?.email}</p>
        </div>
        <Button variant="outline" size="sm" onClick={() => navigate("/chat")}>
          <MessageSquare className="h-4 w-4 mr-2" /> Back to chat
        </Button>
      </header>

      <main className="p-6 max-w-6xl mx-auto">
        <Tabs value={tab} onValueChange={setTab}>
          <TabsList>
            <TabsTrigger value="documents">Documents</TabsTrigger>
            {isAdmin && <TabsTrigger value="groups">Groups</TabsTrigger>}
            {isSuperadmin && <TabsTrigger value="users">Users</TabsTrigger>}
            {isSuperadmin && <TabsTrigger value="settings">Settings</TabsTrigger>}
          </TabsList>
          <TabsContent value="documents" className="mt-6">
            <DocumentsTab />
          </TabsContent>
          {isAdmin && (
            <TabsContent value="groups" className="mt-6">
              <GroupsTab />
            </TabsContent>
          )}
          {isSuperadmin && (
            <TabsContent value="users" className="mt-6">
              <UsersTab />
            </TabsContent>
          )}
          {isSuperadmin && (
            <TabsContent value="settings" className="mt-6">
              <SettingsTab />
            </TabsContent>
          )}
        </Tabs>
      </main>
    </div>
  );
}
