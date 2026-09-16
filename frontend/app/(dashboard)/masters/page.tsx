"use client";

// M15 Masters
// Scoped to Vendor for now. Code and name come from SAP (read-only here);
// email is app-owned local data, editable inline — this is what closes
// the gap we kept hitting manually via a Python shell during testing.

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

interface Vendor {
  code: string;
  name: string;
  email: string | null;
}

export default function MastersPage() {
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
      const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
      const message = Array.isArray(detail)
        ? detail[0]?.msg
        : typeof detail === "string"
        ? detail
        : "Failed to save email.";
      setError(message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="p-6">
      <h1 className="mb-1 text-xl font-semibold">M15 — Masters</h1>
      <p className="mb-4 text-sm text-gray-500">
        Vendor code and name come from SAP. Email is maintained here, since SAP
        does not currently send it.
      </p>

      {loading ? (
        <p className="text-sm text-gray-500">Loading vendors...</p>
      ) : vendors.length === 0 ? (
        <p className="text-sm text-gray-500">No vendors found yet.</p>
      ) : (
        <div className="max-w-2xl overflow-x-auto rounded border">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Vendor Code</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Name</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Email</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {vendors.map((vendor) => (
                <tr key={vendor.code}>
                  <td className="px-4 py-2 font-mono text-xs">{vendor.code}</td>
                  <td className="px-4 py-2">{vendor.name}</td>
                  <td className="px-4 py-2">
                    {editingCode === vendor.code ? (
                      <input
                        type="email"
                        className="w-full rounded border px-2 py-1 text-sm"
                        value={emailDraft}
                        onChange={(e) => setEmailDraft(e.target.value)}
                        autoFocus
                      />
                    ) : (
                      vendor.email ?? <span className="text-gray-400">Not set</span>
                    )}
                  </td>
                  <td className="px-4 py-2 text-right">
                    {editingCode === vendor.code ? (
                      <div className="flex gap-2 justify-end">
                        <button
                          onClick={() => saveEmail(vendor.code)}
                          disabled={saving}
                          className="rounded bg-blue-600 px-2 py-1 text-xs font-medium text-white disabled:opacity-50"
                        >
                          {saving ? "Saving..." : "Save"}
                        </button>
                        <button
                          onClick={cancelEdit}
                          disabled={saving}
                          className="rounded border px-2 py-1 text-xs font-medium text-gray-600"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => startEdit(vendor)}
                        className="rounded border px-2 py-1 text-xs font-medium text-gray-600 hover:bg-gray-50"
                      >
                        Edit
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
    </div>
  );
}