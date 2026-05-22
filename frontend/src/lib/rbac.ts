export type WorkspaceRole =
  | "owner"
  | "admin"
  | "member"
  | "reviewer"
  | "client_viewer";

export type WorkspacePermission =
  | "workspace:manage"
  | "members:invite"
  | "billing:manage"
  | "sow:generate"
  | "sow:view"
  | "sow:edit"
  | "sow:export"
  | "sow:esign"
  | "sow:risk_audit";

const ROLE_PERMISSIONS: Record<WorkspaceRole, WorkspacePermission[]> = {
  owner: [
    "workspace:manage",
    "members:invite",
    "billing:manage",
    "sow:generate",
    "sow:view",
    "sow:edit",
    "sow:export",
    "sow:esign",
    "sow:risk_audit",
  ],
  admin: [
    "members:invite",
    "billing:manage",
    "sow:generate",
    "sow:view",
    "sow:edit",
    "sow:export",
    "sow:esign",
    "sow:risk_audit",
  ],
  member: ["sow:generate", "sow:view", "sow:edit", "sow:export", "sow:risk_audit"],
  reviewer: ["sow:view", "sow:risk_audit"],
  client_viewer: [],
};

export function can(role: WorkspaceRole | null | undefined, permission: WorkspacePermission) {
  if (!role) {
    return false;
  }

  return ROLE_PERMISSIONS[role]?.includes(permission) ?? false;
}

export function normalizeRole(role: string | null | undefined): WorkspaceRole | null {
  if (
    role === "owner" ||
    role === "admin" ||
    role === "member" ||
    role === "reviewer" ||
    role === "client_viewer"
  ) {
    return role;
  }

  return null;
}
