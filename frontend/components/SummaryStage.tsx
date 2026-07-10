"use client";

import { useEffect, useState } from "react";
import { useInterviewStore } from "@/store/interviewStore";
import { getSummary, type SessionSummary } from "@/lib/api";

export default function SummaryStage() {
  const sessionId = useInterviewStore((s) => s.sessionId);
  const reset = useInterviewStore((s) => s.reset);

  const [summary, setSummary] = useState<SessionSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    getSummary(sessionId)
      .then(setSummary)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load summary."))
      .finally(() => setLoading(false));
  }, [sessionId]);

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 text-center text-slate-500 text-sm">
        Compiling your interview summary...
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 text-center text-red-600 text-sm">
        {error ?? "Something went wrong loading your summary."}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">
        <h2 className="text-xl font-semibold text-slate-900 mb-1">Interview Summary</h2>
        <p className="text-slate-500 text-sm mb-4">
          Role: {summary.role.replace(/_/g, " ")} · {summary.qa_pairs.length} questions answered
        </p>

        {summary.topics_covered.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-5">
            {summary.topics_covered.map((topic) => (
              <span key={topic} className="text-xs font-medium bg-slate-100 text-slate-600 px-2.5 py-1 rounded-full">
                {topic}
              </span>
            ))}
          </div>
        )}

        <div>
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs font-medium text-slate-500">Core topic coverage</span>
            <span className="text-xs font-medium text-slate-700">{summary.coverage_percent}%</span>
          </div>
          <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-slate-900 rounded-full transition-all"
              style={{ width: `${summary.coverage_percent}%` }}
            />
          </div>
        </div>
      </div>

      {summary.qa_pairs.map((qa, i) => (
        <div key={i} className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-medium text-slate-400">Q{i + 1}</span>
            {qa.difficulty && (
              <span className="text-xs font-medium bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
                {qa.difficulty}
              </span>
            )}
            {qa.source_page && (
              <span className="text-xs text-slate-400">source: page {qa.source_page}</span>
            )}
          </div>
          <p className="text-slate-900 text-sm mb-3">{qa.question}</p>
          <p className="text-slate-600 text-sm bg-slate-50 border border-slate-200 rounded-lg p-3 mb-2">
            {qa.answer ?? <span className="italic text-slate-400">No answer submitted</span>}
          </p>
          {qa.score !== null && (
            <div className="flex items-start gap-2 text-xs">
              <span className="font-medium text-slate-700 whitespace-nowrap">Score: {qa.score}/5</span>
              {qa.score_justification && <span className="text-slate-400">— {qa.score_justification}</span>}
            </div>
          )}
        </div>
      ))}

      <button
        onClick={reset}
        className="w-full bg-slate-900 text-white rounded-lg py-2.5 font-medium"
      >
        Start a New Interview
      </button>
    </div>
  );
}
