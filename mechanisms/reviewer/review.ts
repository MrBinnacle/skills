import { randomBytes } from "node:crypto";

// The closed vocabularies a reviewer must choose from, so reviews join without reconciliation.
export const SEVERITIES = ["critical", "major", "minor", "nit"] as const;
export const DISPOSITIONS = ["fix-now", "fix-later", "needs-decision", "no-action"] as const;
export const STATUSES = ["nominal", "degraded", "blocked"] as const;

export type Severity = (typeof SEVERITIES)[number];
export type Disposition = (typeof DISPOSITIONS)[number];
export type Status = (typeof STATUSES)[number];

/** What the reviewer submits. It never chooses ids. */
export interface SubmittedFinding {
  severity: Severity;
  file: string;
  line: number | null;
  evidence: string;
  disposition: Disposition;
  reasoning: string;
  whatWouldChangeIt: string;
}

export interface Submission {
  findings: SubmittedFinding[];
  status: Status;
  statusReason?: string;
  filesRead: string[];
}

export interface Finding extends SubmittedFinding {
  /** `<reviewId>-F<n>`: unique across reviews; paste through unchanged when consolidating. */
  id: string;
}

export interface ReviewMeta {
  reviewId: string;
  model: string;
  base: string;
  head: string;
}

export interface Review extends ReviewMeta {
  status: Status;
  statusReason: string;
  filesRead: string[];
  findings: Finding[];
}

export function newReviewId(): string {
  return `R${randomBytes(3).toString("hex")}`;
}

export function finalizeReview(
  meta: ReviewMeta,
  submission: Submission | undefined,
  diagnostics?: string,
): Review {
  if (!submission) {
    return {
      ...meta,
      status: "blocked",
      statusReason: `The reviewer finished without calling submit_review; its findings, if any, are lost.${diagnostics ? ` ${diagnostics}` : ""}`,
      filesRead: [],
      findings: [],
    };
  }
  return {
    ...meta,
    status: submission.status,
    statusReason: submission.statusReason ?? "",
    filesRead: submission.filesRead,
    findings: submission.findings.map((f, i) => ({ id: `${meta.reviewId}-F${i + 1}`, ...f })),
  };
}

export function renderReview(review: Review): string {
  const lines = [
    `Review ${review.reviewId} by ${review.model} of ${review.base}..working tree (HEAD ${review.head})`,
    `${review.findings.length} finding(s).`,
    "",
  ];
  for (const f of review.findings) {
    const where = f.line === null ? f.file : `${f.file}:${f.line}`;
    lines.push(
      `- ${f.id} [${f.severity}] ${where} → ${f.disposition}`,
      `  evidence: ${f.evidence}`,
      `  reasoning: ${f.reasoning}`,
      `  what would change it: ${f.whatWouldChangeIt}`,
    );
  }
  lines.push(
    "",
    `files read: ${review.filesRead.length ? review.filesRead.join(", ") : "(none reported)"}`,
    `status: ${review.status}${review.statusReason ? ` [${review.statusReason}]` : ""}`,
  );
  return lines.join("\n");
}
