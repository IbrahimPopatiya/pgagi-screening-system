import type { Question } from "@/store/interviewStore";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export interface QASummaryItem {
  question: string;
  answer: string | null;
  rationale: string | null;
  difficulty: string | null;
  source_page: number | null;
}

export interface SessionSummary {
  session_id: number;
  role: string;
  qa_pairs: QASummaryItem[];
  topics_covered: string[];
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export function createSession(role: string) {
  return request<{ session_id: number; role: string; status: string }>("/api/sessions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ role }),
  });
}

export function uploadResume(sessionId: number, file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return request(`/api/sessions/${sessionId}/resume`, { method: "POST", body: formData });
}

export function getNextQuestion(sessionId: number) {
  return request<Question>(`/api/sessions/${sessionId}/next-question`, { method: "POST" });
}

export function submitAnswer(sessionId: number, questionId: number, text: string) {
  return request<{ answer_id: number; status: string }>(`/api/sessions/${sessionId}/answer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question_id: questionId, text }),
  });
}

export function getSummary(sessionId: number) {
  return request<SessionSummary>(`/api/sessions/${sessionId}/summary`, { method: "GET" });
}
