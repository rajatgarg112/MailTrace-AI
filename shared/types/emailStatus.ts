/**
 * shared/types/emailStatus.ts
 * ─────────────────────────────────────────────────────────────────────────
 * TypeScript mirror of shared/enums/email_status.py
 *
 * Used by Member 1 (React Frontend) to type-check email status values
 * returned from the Backend API.
 *
 * IMPORTANT: If you change EmailStatus values in Python, update this file too.
 * ─────────────────────────────────────────────────────────────────────────
 */

/** All lifecycle states an email can be in. */
export const EmailStatus = {
  RECEIVED: "RECEIVED",
  SCANNING: "SCANNING",
  DECISION: "DECISION",
  DELIVERED: "DELIVERED",
  WARNING: "WARNING",
  QUARANTINED: "QUARANTINED",
  REJECTED: "REJECTED",
  FAILED: "FAILED",
  UNKNOWN: "UNKNOWN",
} as const;

export type EmailStatus = (typeof EmailStatus)[keyof typeof EmailStatus];

/** The set of states from which no further transitions occur. */
export const TERMINAL_STATUSES: readonly EmailStatus[] = [
  EmailStatus.DELIVERED,
  EmailStatus.WARNING,
  EmailStatus.QUARANTINED,
  EmailStatus.REJECTED,
  EmailStatus.FAILED,
];

/** States representing active in-flight processing. */
export const ACTIVE_STATUSES: readonly EmailStatus[] = [
  EmailStatus.RECEIVED,
  EmailStatus.SCANNING,
  EmailStatus.DECISION,
];

/** Returns true if the status is a terminal state. */
export function isTerminal(status: EmailStatus): boolean {
  return TERMINAL_STATUSES.includes(status);
}

/** Returns a human-readable label for display in the UI. */
export function getStatusLabel(status: EmailStatus): string {
  const labels: Record<EmailStatus, string> = {
    RECEIVED: "Received",
    SCANNING: "Scanning…",
    DECISION: "Deciding…",
    DELIVERED: "Delivered",
    WARNING: "Warning",
    QUARANTINED: "Quarantined",
    REJECTED: "Rejected",
    FAILED: "Failed",
    UNKNOWN: "Unknown",
  };
  return labels[status] ?? status;
}

/** Returns the Tailwind CSS colour class appropriate for each status. */
export function getStatusColor(status: EmailStatus): string {
  const colors: Record<EmailStatus, string> = {
    RECEIVED: "text-blue-400",
    SCANNING: "text-yellow-400",
    DECISION: "text-orange-400",
    DELIVERED: "text-green-400",
    WARNING: "text-amber-400",
    QUARANTINED: "text-red-400",
    REJECTED: "text-red-600",
    FAILED: "text-gray-400",
    UNKNOWN: "text-gray-500",
  };
  return colors[status] ?? "text-gray-400";
}
