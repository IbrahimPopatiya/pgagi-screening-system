"use client";

import { useState } from "react";
import { useInterviewStore } from "@/store/interviewStore";
import { createSession, uploadResume } from "@/lib/api";

const ROLES = [{ value: "ai_ml_engineer", label: "AI / ML Engineer" }];

export default function EntryStage() {
  const [role, setRole] = useState(ROLES[0].value);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const setSession = useInterviewStore((s) => s.setSession);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) {
      setError("Please upload your resume as a PDF.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const session = await createSession(role);
      await uploadResume(session.session_id, file);
      setSession(session.session_id, role);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">
      <h1 className="text-2xl font-semibold text-slate-900 mb-1">Start your interview</h1>
      <p className="text-slate-500 mb-6">Upload your resume and pick the role you're interviewing for.</p>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Target role</label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-slate-900"
          >
            {ROLES.map((r) => (
              <option key={r.value} value={r.value}>{r.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Resume (PDF)</label>
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-slate-900 text-white rounded-lg py-2.5 font-medium disabled:opacity-50"
        >
          {loading ? "Setting up your interview..." : "Start Interview"}
        </button>
      </form>
    </div>
  );
}
