"use client";

// M16 Settings — scoped to User Management and Role Management for now.
// SAP Configuration, Mail Configuration, QR Configuration, and Audit
// Logs are the remaining parts of M16 per the KT notes and are not yet
// implemented (see backend app/modules/settings/schemas.py).
//
// Every /settings/* endpoint is admin-only. A non-admin who lands here
// gets a clear "not permitted" state rather than a blank/broken page.
//
// Username is treated as the user's email (M1 Forgot Password decision
// with Athithya) — new users must be created with a real email address,
// since that's where their password reset link is sent.

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/States";
import {
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableHeaderCell,
  TableCell,
} from "@/components/ui/Table";

interface RoleItem {
  id: string;
  name: string;
}

interface UserItem {
  id: string;
  username: string;
  role_id: string;
  role_name: string;
}

function extractError(err: unknown, fallback: string): string {
  const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail[0]?.msg ?? fallback;
  return fallback;
}

export default function SettingsPage() {
  const [permitted, setPermitted] = useState<boolean | null>(null);
  const [roles, setRoles] = useState<RoleItem[]>([]);
  const [users, setUsers] = useState<UserItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [newRoleName, setNewRoleName] = useState("");
  const [addingRole, setAddingRole] = useState(false);

  const [newUsername, setNewUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newUserRoleId, setNewUserRoleId] = useState("");
  const [addingUser, setAddingUser] = useState(false);

  const [changingRoleForUserId, setChangingRoleForUserId] = useState<string | null>(null);

  async function loadAll() {
    setLoading(true);
    setError(null);
    try {
      const [rolesRes, usersRes] = await Promise.all([
        apiClient.get<RoleItem[]>("/settings/roles"),
        apiClient.get<UserItem[]>("/settings/users"),
      ]);
      setRoles(rolesRes.data);
      setUsers(usersRes.data);
      setPermitted(true);
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      if (status === 403) {
        setPermitted(false);
      } else {
        setError(extractError(err, "Failed to load settings."));
        setPermitted(true);
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAll();
  }, []);

  async function handleAddRole() {
    if (!newRoleName.trim()) return;
    setAddingRole(true);
    setError(null);
    try {
      await apiClient.post("/settings/roles", { name: newRoleName.trim() });
      setNewRoleName("");
      await loadAll();
    } catch (err: unknown) {
      setError(extractError(err, "Failed to add role."));
    } finally {
      setAddingRole(false);
    }
  }

  async function handleAddUser() {
    if (!newUsername.trim() || !newPassword || !newUserRoleId) {
      setError("Email, password, and role are all required.");
      return;
    }
    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    setAddingUser(true);
    setError(null);
    try {
      await apiClient.post("/settings/users", {
        username: newUsername.trim(),
        password: newPassword,
        role_id: newUserRoleId,
      });
      setNewUsername("");
      setNewPassword("");
      setNewUserRoleId("");
      await loadAll();
    } catch (err: unknown) {
      setError(extractError(err, "Failed to add user."));
    } finally {
      setAddingUser(false);
    }
  }

  async function handleChangeRole(userId: string, roleId: string) {
    setChangingRoleForUserId(userId);
    setError(null);
    try {
      await apiClient.patch(`/settings/users/${userId}/role`, { role_id: roleId });
      await loadAll();
    } catch (err: unknown) {
      setError(extractError(err, "Failed to change role."));
    } finally {
      setChangingRoleForUserId(null);
    }
  }

  if (loading) {
    return (
      <div>
        <PageHeader title="Settings" description="User Management and Role Management." />
        <LoadingState label="Loading settings..." />
      </div>
    );
  }

  if (permitted === false) {
    return (
      <div>
        <PageHeader title="Settings" description="User Management and Role Management." />
        <ErrorState message="You need admin access to view this page." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Settings"
        description="User Management and Role Management. SAP, Mail, and QR Configuration, and Audit Logs are not yet available here."
      />

      {error && <ErrorState message={error} />}

      <Card>
        <CardHeader>
          <CardTitle>Roles</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {roles.length === 0 ? (
            <EmptyState title="No roles yet" />
          ) : (
            <Table>
              <TableHead>
                <TableRow>
                  <TableHeaderCell>Role Name</TableHeaderCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {roles.map((role) => (
                  <TableRow key={role.id}>
                    <TableCell>{role.name}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}

          <div className="flex max-w-md items-end gap-2">
            <div className="flex-1">
              <Input
                label="Add a role"
                placeholder="e.g. warehouse_supervisor"
                value={newRoleName}
                onChange={(e) => setNewRoleName(e.target.value)}
              />
            </div>
            <Button onClick={handleAddRole} loading={addingRole} disabled={!newRoleName.trim()}>
              Add Role
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Users</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {users.length === 0 ? (
            <EmptyState title="No users yet" />
          ) : (
            <Table>
              <TableHead>
                <TableRow>
                  <TableHeaderCell>Email</TableHeaderCell>
                  <TableHeaderCell>Role</TableHeaderCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.username}</TableCell>
                    <TableCell>
                      <Select
                        value={user.role_id}
                        onChange={(e) => handleChangeRole(user.id, e.target.value)}
                        disabled={changingRoleForUserId === user.id}
                        className="max-w-xs"
                      >
                        {roles.map((role) => (
                          <option key={role.id} value={role.id}>
                            {role.name}
                          </option>
                        ))}
                      </Select>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}

          <div className="grid max-w-2xl gap-3 sm:grid-cols-3 sm:items-end">
            <Input
              label="Email"
              type="email"
              value={newUsername}
              onChange={(e) => setNewUsername(e.target.value)}
              placeholder="name@example.com"
            />
            <Input
              label="Password"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              minLength={8}
              placeholder="At least 8 characters"
            />
            <Select
              label="Role"
              value={newUserRoleId}
              onChange={(e) => setNewUserRoleId(e.target.value)}
            >
              <option value="">Select a role...</option>
              {roles.map((role) => (
                <option key={role.id} value={role.id}>
                  {role.name}
                </option>
              ))}
            </Select>
            <Button
              onClick={handleAddUser}
              loading={addingUser}
              disabled={!newUsername.trim() || !newPassword || !newUserRoleId}
              className="sm:col-span-3"
            >
              Add User
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
