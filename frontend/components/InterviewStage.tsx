"use client";

import { useEffect, useState } from "react";
import { useInterviewStore, MAX_QUESTIONS } from "@/store/interviewStore";
import { getNextQuestion, submitAnswer } from "@/lib/api";

const DIFFICULTY_STYLES: Record<string, string> = {
  easy: "bg-emerald-100 text-emerald-700",
  medium: "bg-amber-100 text-amber-700",
  hard: "bg-rose-100 text-rose-700",
};

export default function InterviewStage() {
  const sessionId = useInterviewStore((s) => s.sessionId);
  const currentQuestion = useInterviewStore((s) => s.currentQuestion);
  const questionsAsked = useInterviewStore((s) => s.questionsAsked);
  const setCurrentQuestion = useInterviewStore((s) => s.setCurrentQuestion);
  const incrementQuestionsAsked = useInterviewStore((s) => s.incrementQuestionsAsked);
  const setStage = useInterviewStore((s) => s.setStage);

  const [answer, setAnswer] = useState("");
  const [loadingQuestion, setLoadingQuestion] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showRationale, setShowRationale] = useState(false);

  useEffect(() => {
    if (!sessionId || currentQuestion) return;
    fetchNextQuestion();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  async function fetchNextQuestion() {
    if (!sessionId) return;
    setLoadingQuestion(true);
    setError(null);
    setShowRationale(false);
    try {
      const question = await getNextQuestion(sessionId);
      setCurrentQuestion(question);
      setAnswer("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not generate the next question.");
    } finally {
      setLoadingQuestion(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!sessionId || !currentQuestion || !answer.trim()) return;

    setSubmitting(true);
    setError(null);
    try {
      await submitAnswer(sessionId, currentQuestion.id, answer.trim());
      incrementQuestionsAsked();

      if (questionsAsked + 1 >= MAX_QUESTIONS) {
        setStage("summary");
      } else {
        setCurrentQuestion(null);
        await fetchNextQuestion();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not submit your answer.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-slate-900">Interview in progress</h2>
        <span className="text-sm text-slate-500">
          Question {Math.min(questionsAsked + 1, MAX_QUESTIONS)} of {MAX_QUESTIONS}
        </span>
      </div>

      {loadingQuestion && (
        <p className="text-slate-500 text-sm py-8 text-center">Generating your next question from the knowledge base...</p>
      )}

      {!loadingQuestion && currentQuestion && (
        <>
          <div className="mb-2 flex items-center gap-2">
            {currentQuestion.difficulty && (
              <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${DIFFICULTY_STYLES[currentQuestion.difficulty] ?? "bg-slate-100 text-slate-600"}`}>
                {currentQuestion.difficulty}
              </span>
            )}
          </div>
          <p className="text-slate-900 text-base leading-relaxed mb-4">{currentQuestion.text}</p>

          {currentQuestion.rationale && (
            <div className="mb-5">
              <button
                type="button"
                onClick={() => setShowRationale((v) => !v)}
                className="text-xs text-slate-400 hover:text-slate-600 underline underline-offset-2"
              >
                {showRationale ? "Hide" : "Why this question?"}
              </button>
              {showRationale && (
                <p className="mt-2 text-xs text-slate-500 bg-slate-50 border border-slate-200 rounded-lg p-3">
                  {currentQuestion.rationale}
                </p>
              )}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              rows={5}
              placeholder="Type your answer..."
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-slate-900 text-sm"
            />

            {error && <p className="text-sm text-red-600">{error}</p>}

            <button
              type="submit"
              disabled={submitting || !answer.trim()}
              className="w-full bg-slate-900 text-white rounded-lg py-2.5 font-medium disabled:opacity-50"
            >
              {submitting ? "Submitting..." : "Submit Answer"}
            </button>
          </form>
        </>
      )}
    </div>
  );
}
