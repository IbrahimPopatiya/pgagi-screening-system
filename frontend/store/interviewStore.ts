import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export type Stage = "entry" | "interview" | "summary";

export const MAX_QUESTIONS = 5;

export interface Question {
  id: number;
  text: string;
  rationale: string | null;
  difficulty: string | null;
  order: number;
}

interface InterviewState {
  stage: Stage;
  sessionId: number | null;
  role: string | null;
  currentQuestion: Question | null;
  questionsAsked: number;
  hasHydrated: boolean;
  setStage: (stage: Stage) => void;
  setSession: (sessionId: number, role: string) => void;
  setCurrentQuestion: (question: Question | null) => void;
  incrementQuestionsAsked: () => void;
  reset: () => void;
  setHasHydrated: (hasHydrated: boolean) => void;
}

export const useInterviewStore = create<InterviewState>()(
  persist(
    (set) => ({
      stage: "entry",
      sessionId: null,
      role: null,
      currentQuestion: null,
      questionsAsked: 0,
      hasHydrated: false,
      setStage: (stage) => set({ stage }),
      setSession: (sessionId, role) => set({ sessionId, role, stage: "interview", questionsAsked: 0 }),
      setCurrentQuestion: (currentQuestion) => set({ currentQuestion }),
      incrementQuestionsAsked: () => set((s) => ({ questionsAsked: s.questionsAsked + 1 })),
      reset: () => set({ stage: "entry", sessionId: null, role: null, currentQuestion: null, questionsAsked: 0 }),
      setHasHydrated: (hasHydrated) => set({ hasHydrated }),
    }),
    {
      name: "interview-session",
      storage: createJSONStorage(() => localStorage),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
      partialize: (state) => ({
        stage: state.stage,
        sessionId: state.sessionId,
        role: state.role,
        currentQuestion: state.currentQuestion,
        questionsAsked: state.questionsAsked,
      }),
    }
  )
);
