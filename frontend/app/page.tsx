"use client";

import { useInterviewStore } from "@/store/interviewStore";
import EntryStage from "@/components/EntryStage";
import InterviewStage from "@/components/InterviewStage";
import SummaryStage from "@/components/SummaryStage";

export default function Home() {
  const stage = useInterviewStore((s) => s.stage);
  const hasHydrated = useInterviewStore((s) => s.hasHydrated);

  return (
    <main className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="w-full max-w-2xl">
        {!hasHydrated && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 text-center text-slate-400 text-sm">
            Loading...
          </div>
        )}
        {hasHydrated && stage === "entry" && <EntryStage />}
        {hasHydrated && stage === "interview" && <InterviewStage />}
        {hasHydrated && stage === "summary" && <SummaryStage />}
      </div>
    </main>
  );
}
