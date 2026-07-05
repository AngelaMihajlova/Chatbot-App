import { useEffect, useState } from "react";
import { settingsApi } from "@/api/settings";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { SystemSettings } from "@/types";

export function SettingsTab() {
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    settingsApi.get().then((r) => setSettings(r.data));
  }, []);

  async function handleSave() {
    if (!settings) return;
    setSaving(true);
    try {
      const res = await settingsApi.update(settings);
      setSettings(res.data);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } finally {
      setSaving(false);
    }
  }

  if (!settings) return <p className="text-muted-foreground text-sm">Loading…</p>;

  return (
    <div className="space-y-6 max-w-3xl">
      <h2 className="text-lg font-semibold">System Settings</h2>
      <p className="text-sm text-muted-foreground">
        Changes take effect immediately for new requests. A restart may be needed for infrastructure changes.
      </p>

      <div className="grid grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Document Storage</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Label>Storage backend</Label>
            <Select
              value={settings.STORAGE_BACKEND}
              onChange={(e) => setSettings({ ...settings, STORAGE_BACKEND: e.target.value as "minio" | "s3" })}
            >
              <option value="minio">MinIO (local)</option>
              <option value="s3">AWS S3</option>
            </Select>
            <p className="text-xs text-muted-foreground">
              Switching to S3 requires <code>AWS_ACCESS_KEY_ID</code>, <code>AWS_SECRET_ACCESS_KEY</code>, and{" "}
              <code>AWS_S3_BUCKET</code> to be set in environment variables.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Conversation History</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Label>DynamoDB mode</Label>
            <Select
              value={settings.DYNAMO_MODE}
              onChange={(e) => setSettings({ ...settings, DYNAMO_MODE: e.target.value as "local" | "aws" })}
            >
              <option value="local">Local DynamoDB</option>
              <option value="aws">AWS DynamoDB</option>
            </Select>
            <p className="text-xs text-muted-foreground">
              Switching to AWS DynamoDB requires <code>AWS_ACCESS_KEY_ID</code>, <code>AWS_SECRET_ACCESS_KEY</code>, and{" "}
              <code>AWS_DYNAMO_REGION</code> in environment variables.
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="flex items-center gap-3">
        <Button onClick={handleSave} disabled={saving}>
          {saving ? "Saving…" : "Save settings"}
        </Button>
        {saved && <span className="text-sm text-green-600">Settings saved.</span>}
      </div>
    </div>
  );
}
