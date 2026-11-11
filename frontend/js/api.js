import { getAccessToken } from "./supabase-client.js";

function apiBase() {
  const value = window.ACADZA_CONFIG?.apiBaseUrl;
  if (!value) throw new Error("Set apiBaseUrl in frontend/config.js");
  return value.replace(/\/+$/, "");
}

export async function apiRequest(path, options = {}) {
  const token = await getAccessToken();
  const response = await fetch(apiBase() + path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token,
      ...(options.headers || {}),
    },
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = payload.detail || payload.message || "API request failed (" + response.status + ")";
    const error = new Error(message);
    error.status = response.status;
    error.payload = payload;
    throw error;
  }
  return payload;
}

export const api = {
  getQueue: (status = "open") =>
    apiRequest("/api/faculty/queue?status=" + encodeURIComponent(status)),

  getQuestion: (questionId) =>
    apiRequest("/api/questions/" + encodeURIComponent(questionId)),

  getAuditLogs: () => apiRequest("/api/audit-logs"),

  submitReport: (body, idempotencyKey) =>
    apiRequest("/api/reports", {
      method: "POST",
      headers: idempotencyKey ? { "Idempotency-Key": idempotencyKey } : {},
      body: JSON.stringify(body),
    }),

  createProposal: (reportId, body) =>
    apiRequest("/api/reports/" + reportId + "/proposals", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  approve: (reportId, proposalId, expectedQuestionVersion, reason) =>
    apiRequest("/api/reports/" + reportId + "/proposals/" + proposalId + "/approve", {
      method: "POST",
      body: JSON.stringify({
        expected_question_version: expectedQuestionVersion,
        reason,
      }),
    }),

  reject: (reportId, proposalId, reason) =>
    apiRequest("/api/reports/" + reportId + "/proposals/" + proposalId + "/reject", {
      method: "POST",
      body: JSON.stringify({ reason }),
    }),
};
