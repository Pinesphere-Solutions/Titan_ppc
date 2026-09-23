"use client";

// M13 Storage Management — once ZQMTL1 Processing (M12) has posted SAP
// 313, the material is ready to be assigned a rack/row/bin and stored.
// Per D1's function list ("Assign Rack, Assign Bin, QR Scan, Location
// Search, Store Material") the assign+store actions are combined into
// one confirm step (same precedent as M10/M12), and a search box below
// serves "Location Search" over what's already stored.

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, CardContent } from "@/components/ui/Card";
import { Select } from "@/components/ui/Select";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/States";
import { Table, TableHead, TableBody, TableRow, TableHeaderCell, TableCell } from "@/components/ui/Table";

interface PendingItem {
  dc_no: string;
  vendor_name: string;
  material_code: string;
  model: string | null;
  quantity: number;
}

interface StorageResult {
  dc_no: string;
  vendor_name: string;
  rack: string;
  row: string;
  bin: string;
  storage_location: string;
  stored_by: string;
  message: string;
}

interface StoredItem {
  dc_no: string;
  vendor_name: string;
  material_code: string;
  model: string | null;
  rack: string;
  row: string;
  bin: string;
  storage_location: string;
  stored_by: string;
  stored_at: string;
}

export default function StorageManagementPage() {
  const [pendingDcs, setPendingDcs] = useState<PendingItem[]>([]);
  const [selectedDcNo, setSelectedDcNo] = useState("");
  const [rack, setRack] = useState("");
  const [row, setRow] = useState("");
  const [bin, setBin] = useState("");
  const [storageLocation, setStorageLocation] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<StorageResult | null>(null);

  const [search, setSearch] = useState("");
  const [storedItems, setStoredItems] = useState<StoredItem[]>([]);
  const [storedLoading, setStoredLoading] = useState(true);

  async function loadPendingDcs() {
    setLoading(true);
    try {
      const res = await apiClient.get<PendingItem[]>("/storage/pending");
      setPendingDcs(res.data);
    } catch {
      setError("Failed to load delivery challans awaiting storage assignment.");
    } finally {
      setLoading(false);
    }
  }

  async function loadStoredItems(searchTerm?: string) {
    setStoredLoading(true);
    try {
      const res = await apiClient.get<StoredItem[]>("/storage/list", {
        params: searchTerm ? { search: searchTerm } : undefined,
      });
      setStoredItems(res.data);
    } catch {
      // Non-fatal — the assign form above still works even if the
      // stored list / location search fails to load.
    } finally {
      setStoredLoading(false);
    }
  }

  useEffect(() => {
    loadPendingDcs();
    loadStoredItems();
  }, []);

  async function handleAssign() {
    if (!selectedDcNo) {
      setError("Select a delivery challan first.");
      return;
    }
    if (!rack.trim() || !row.trim() || !bin.trim() || !storageLocation.trim()) {
      setError("Fill in Rack, Row, Bin, and Storage Location.");
      return;
    }

    setError(null);
    setResult(null);
    setSubmitting(true);
    try {
      const res = await apiClient.post<StorageResult>(`/storage/${selectedDcNo}/assign`, {
        rack: rack.trim(),
        row: row.trim(),
        bin: bin.trim(),
        storage_location: storageLocation.trim(),
      });
      setResult(res.data);
      setSelectedDcNo("");
      setRack("");
      setRow("");
      setBin("");
      setStorageLocation("");
      await loadPendingDcs();
      await loadStoredItems(search);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Storage assignment failed.";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Storage Management"
        description="Assign a rack, row and bin, and confirm the material has been stored — the final step after ZQMTL1 / SAP 313 is posted."
      />

      {loading ? (
        <LoadingState label="Loading delivery challans awaiting storage assignment..." />
      ) : pendingDcs.length === 0 ? (
        <EmptyState
          title="Nothing awaiting storage"
          description="Delivery challans that have completed ZQMTL1 processing (SAP 313 posted) will appear here."
        />
      ) : (
        <Card className="max-w-md">
          <CardContent className="space-y-4">
            <Select
              label="Delivery Challan"
              value={selectedDcNo}
              onChange={(e) => setSelectedDcNo(e.target.value)}
            >
              <option value="">Select a DC...</option>
              {pendingDcs.map((d) => (
                <option key={d.dc_no} value={d.dc_no}>
                  {d.dc_no} — {d.vendor_name} ({d.material_code}, {d.model}, qty {d.quantity})
                </option>
              ))}
            </Select>

            <div className="grid grid-cols-3 gap-3">
              <Input label="Rack" placeholder="e.g. A" value={rack} onChange={(e) => setRack(e.target.value)} />
              <Input label="Row" placeholder="e.g. 2" value={row} onChange={(e) => setRow(e.target.value)} />
              <Input label="Bin" placeholder="e.g. 5" value={bin} onChange={(e) => setBin(e.target.value)} />
            </div>

            <Input
              label="Storage Location"
              placeholder="e.g. PPC Storage - Zone A"
              value={storageLocation}
              onChange={(e) => setStorageLocation(e.target.value)}
            />

            {error && <ErrorState message={error} />}

            <Button
              onClick={handleAssign}
              loading={submitting}
              disabled={!selectedDcNo || !rack.trim() || !row.trim() || !bin.trim() || !storageLocation.trim()}
              className="w-full"
            >
              {submitting ? "Storing..." : "Assign & Store Material"}
            </Button>
          </CardContent>
        </Card>
      )}

      {result && (
        <div className="mt-4 max-w-md rounded-lg border border-success-bg bg-success-bg p-5 shadow-sm">
          <p className="mb-1 text-sm font-semibold text-success-text">{result.message}</p>
          <p className="text-sm text-success-text">Stored by: {result.stored_by}</p>
        </div>
      )}

      <div className="mt-10">
        <h2 className="mb-3 text-lg font-semibold text-text-primary">Location Search</h2>
        <div className="mb-4 max-w-md">
          <Input
            placeholder="Search by DC No, Rack, Row, Bin, or Storage Location..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              loadStoredItems(e.target.value);
            }}
          />
        </div>

        {storedLoading ? (
          <LoadingState label="Loading stored materials..." />
        ) : storedItems.length === 0 ? (
          <EmptyState
            title="No stored materials found"
            description="Materials assigned to a storage location will appear here — searchable by DC No, Rack, Row, Bin, or Storage Location."
          />
        ) : (
          <Table>
            <TableHead>
              <TableRow>
                <TableHeaderCell>DC No</TableHeaderCell>
                <TableHeaderCell>Vendor</TableHeaderCell>
                <TableHeaderCell>Material</TableHeaderCell>
                <TableHeaderCell>Rack</TableHeaderCell>
                <TableHeaderCell>Row</TableHeaderCell>
                <TableHeaderCell>Bin</TableHeaderCell>
                <TableHeaderCell>Storage Location</TableHeaderCell>
                <TableHeaderCell>Stored By</TableHeaderCell>
                <TableHeaderCell>Stored Date</TableHeaderCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {storedItems.map((item) => (
                <TableRow key={item.dc_no}>
                  <TableCell>{item.dc_no}</TableCell>
                  <TableCell>{item.vendor_name}</TableCell>
                  <TableCell>{item.material_code}</TableCell>
                  <TableCell>{item.rack}</TableCell>
                  <TableCell>{item.row}</TableCell>
                  <TableCell>{item.bin}</TableCell>
                  <TableCell>{item.storage_location}</TableCell>
                  <TableCell>{item.stored_by}</TableCell>
                  <TableCell>{new Date(item.stored_at).toLocaleDateString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}
