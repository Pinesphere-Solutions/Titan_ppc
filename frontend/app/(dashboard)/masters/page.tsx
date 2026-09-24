"use client";

// M15 Masters
// Vendor code and name come from SAP (read-only here); email is app-owned
// local data, editable inline. Material, Model, Rack and Bin are simple
// code/name lookup lists maintained here — these were the remaining
// masters called out in the KT notes (User/Role masters live under
// Settings instead, since those are the app's own auth tables).

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/States";
import {
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableHeaderCell,
  TableCell,
} from "@/components/ui/Table";

interface Vendor {
  code: string;
  name: string;
  email: string | null;
}

interface CodeNameItem {
  code: string;
  name: string;
}

function extractError(err: unknown, fallback: string): string {
  const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail[0]?.msg ?? fallback;
  return fallback;
}

// Generic list + add-form card for a simple code/name master (Material,
// Model, Rack, Bin) — they all share the same shape and behavior.
function CodeNameMasterCard({
  title,
  endpoint,
  codeLabel,
  codePlaceholder,
}: {
  title: string;
  endpoint: string;
  codeLabel: string;
  codePlaceholder: string;
}) {
  const [items, setItems] = useState<CodeNameItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newCode, setNewCode] = useState("");
  const [newName, setNewName] = useState("");
  const [adding, setAdding] = useState(false);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get<CodeNameItem[]>(endpoint);
      setItems(res.data);
    } catch (err: unknown) {
      setError(extractError(err, `Failed to load ${title.toLowerCase()}.`));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleAdd() {
    if (!newCode.trim() || !newName.trim()) return;
    setAdding(true);
    setError(null);
    try {
      await apiClient.post(endpoint, { code: newCode.trim(), name: newName.trim() });
      setNewCode("");
      setNewName("");
      await load();
    } catch (err: unknown) {
      setError(extractError(err, `Failed to add ${title.toLowerCase()}.`));
    } finally {
      setAdding(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && <ErrorState message={error} />}

        {loading ? (
          <LoadingState label={`Loading ${title.toLowerCase()}...`} />
        ) : items.length === 0 ? (
          <EmptyState title={`No ${title.toLowerCase()} yet`} />
        ) : (
          <Table className="max-w-2xl">
            <TableHead>
              <TableRow>
                <TableHeaderCell>{codeLabel}</TableHeaderCell>
                <TableHeaderCell>Name</TableHeaderCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map((item) => (
                <TableRow key={item.code}>
                  <TableCell className="font-mono text-xs">{item.code}</TableCell>
                  <TableCell>{item.name}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}

        <div className="flex max-w-2xl flex-wrap items-end gap-2">
          <Input
            label={codeLabel}
            placeholder={codePlaceholder}
            value={newCode}
            onChange={(e) => setNewCode(e.target.value)}
          />
          <Input
            label="Name"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
          />
          <Button onClick={handleAdd} loading={adding} disabled={!newCode.trim() || !newName.trim()}>
            Add
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function VendorMasterCard() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingCode, setEditingCode] = useState<string | null>(null);
  const [emailDraft, setEmailDraft] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadVendors() {
    setLoading(true);
    try {
      const res = await apiClient.get<Vendor[]>("/masters/vendors");
      setVendors(res.data);
    } catch {
      setError("Failed to load vendors.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadVendors();
  }, []);

  function startEdit(vendor: Vendor) {
    setEditingCode(vendor.code);
    setEmailDraft(vendor.email ?? "");
    setError(null);
  }

  function cancelEdit() {
    setEditingCode(null);
    setEmailDraft("");
  }

  async function saveEmail(code: string) {
    setSaving(true);
    setError(null);
    try {
      await apiClient.patch(`/masters/vendors/${code}/email`, { email: emailDraft });
      setEditingCode(null);
      await loadVendors();
    } catch (err: unknown) {
      setError(extractError(err, "Failed to save email."));
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Vendor Master</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-text-muted">
        </p>

        {error && <ErrorState message={error} />}

        {loading ? (
          <LoadingState label="Loading vendors..." />
        ) : vendors.length === 0 ? (
          <EmptyState title="No vendors found yet" />
        ) : (
          <Table className="max-w-3xl">
            <TableHead>
              <TableRow>
                <TableHeaderCell>Vendor Code</TableHeaderCell>
                <TableHeaderCell>Name</TableHeaderCell>
                <TableHeaderCell>Email</TableHeaderCell>
                <TableHeaderCell></TableHeaderCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {vendors.map((vendor) => (
                <TableRow key={vendor.code}>
                  <TableCell className="font-mono text-xs">{vendor.code}</TableCell>
                  <TableCell>{vendor.name}</TableCell>
                  <TableCell>
                    {editingCode === vendor.code ? (
                      <Input
                        type="email"
                        value={emailDraft}
                        onChange={(e) => setEmailDraft(e.target.value)}
                        autoFocus
                      />
                    ) : (
                      vendor.email ?? <span className="text-text-muted">Not set</span>
                    )}
                  </TableCell>
                  <TableCell align="right">
                    {editingCode === vendor.code ? (
                      <div className="flex justify-end gap-2">
                        <Button size="sm" onClick={() => saveEmail(vendor.code)} loading={saving}>
                          {saving ? "Saving..." : "Save"}
                        </Button>
                        <Button size="sm" variant="outline" onClick={cancelEdit} disabled={saving}>
                          Cancel
                        </Button>
                      </div>
                    ) : (
                      <Button size="sm" variant="outline" onClick={() => startEdit(vendor)}>
                        Edit
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}

export default function MastersPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Masters"
        description="Vendor, Material, Model, Rack and Bin master data. User and Role masters are managed under Settings."
      />

      <VendorMasterCard />
      <CodeNameMasterCard
        title="Material Master"
        endpoint="/masters/materials"
        codeLabel="Material Code"
        codePlaceholder="e.g. MAT-1001"
      />
      <CodeNameMasterCard
        title="Model Master"
        endpoint="/masters/models"
        codeLabel="Model Code"
        codePlaceholder="e.g. MDL-A1"
      />
      <CodeNameMasterCard
        title="Rack Master"
        endpoint="/masters/racks"
        codeLabel="Rack Code"
        codePlaceholder="e.g. R-01"
      />
      <CodeNameMasterCard
        title="Bin Master"
        endpoint="/masters/bins"
        codeLabel="Bin Code"
        codePlaceholder="e.g. B-01"
      />
    </div>
  );
}
