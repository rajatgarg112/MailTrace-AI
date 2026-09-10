/**
 * shared/types/contracts.ts
 * ─────────────────────────────────────────────────────────────────────────
 * TypeScript interfaces mirroring the Python shared contracts.
 *
 * Used by Member 1 (React Frontend) to type-check API responses and
 * enforce a consistent shape for email data consumed from the Backend.
 * ─────────────────────────────────────────────────────────────────────────
 */

import type { EmailStatus } from "./emailStatus";

// ── Attachment ─────────────────────────────────────────────────────────────

export interface AttachmentContract {
  filename: string;
  content_type: string;
  size_bytes?: number;
  sha256?: string;
  is_suspicious: boolean;
}

// ── Email Object ───────────────────────────────────────────────────────────

/**
 * Canonical shared email object returned by the Backend API.
 * Maps 1-to-1 with Python EmailContract.
 */
export interface EmailContract {
  id: string;
  message_id?: string;

  sender: string;
  senderEmail: string;
  recipient: string;

  subject?: string;
  body?: string;

  timestamp: string; // ISO-8601 UTC
  attachments: AttachmentContract[];

  status: EmailStatus;
  riskScore: number; // 0 – 100
  securityReasons: string[];
}

// ── Security Signal ────────────────────────────────────────────────────────

export interface SecuritySignal {
  signal: string;
  category: string;
  confidence: number; // 0.0 – 1.0
  risk: number;       // 0.0 – 100.0
  evidence?: string;
}

// ── Security Result ────────────────────────────────────────────────────────

export interface SecurityResultContract {
  emailId: string;
  signals: SecuritySignal[];
  overallVerdict: "SAFE" | "SUSPICIOUS" | "MALICIOUS" | "UNKNOWN";
  totalRiskScore: number;
  rawDetails?: Record<string, unknown>;
}

// ── ML Result ──────────────────────────────────────────────────────────────

export interface MLResultContract {
  source: "ml";
  label: "phishing" | "suspicious" | "benign" | "unknown";
  confidence: number; // 0.0 – 1.0
  signals: string[];
  explanation?: string;
  model_version?: string;
  is_placeholder: boolean;
  execution_time_ms?: number;
  metadata?: Record<string, unknown>;
}

// ── Risk Decision ──────────────────────────────────────────────────────────

export type RiskDecision =
  | "DELIVERED"
  | "WARNING"
  | "QUARANTINED"
  | "REJECTED"
  | "FAILED";

export interface RiskDecisionContract {
  emailId: string;
  riskScore: number; // 0 – 100
  decision: RiskDecision;
  reasons: string[];
  timestamp: string; // ISO-8601 UTC
}

// ── Email Event ────────────────────────────────────────────────────────────

export interface EmailEventContract {
  emailId: string;
  event: EmailStatus;
  fromStatus?: EmailStatus;
  timestamp: string; // ISO-8601 UTC
  metadata?: Record<string, unknown>;
}

// ── API Envelope ───────────────────────────────────────────────────────────

export interface ApiResponse<T = unknown> {
  success: boolean;
  message: string;
  data?: T;
}
