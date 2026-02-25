import { defineStore } from "pinia";
import { TrialQuestionAnswer } from "../types";

export const useTrialQuestionAnswerStore = defineStore("trialQuestionAnswer", {
  state: (): { trialQuestionAnswer: TrialQuestionAnswer } => ({
    trialQuestionAnswer: {} as TrialQuestionAnswer,
  }),

  actions: {
    // Save single trialQuestionAnswer
    saveTrialQuestionAnswer(trialQuestionAnswer: TrialQuestionAnswer) {
      this.trialQuestionAnswer = trialQuestionAnswer;
    },

    // Fetch a single trialQuestionAnswer by ID from the backend
    async fetchTrialQuestionAnswer(trialQuestionAnswerId: number) {
      try {
        const response = await fetch(
          `http://localhost:8000/trialQuestionAnswer/${trialQuestionAnswerId}/`
        );

        if (!response.ok) {
          throw new Error("Failed to fetch trialQuestionAnswer data");
        }

        const trialQuestionAnswerData = await response.json();
        this.trialQuestionAnswer = trialQuestionAnswerData;

      } catch (error) {
        console.error("Error fetching trialQuestionAnswer data:", error);
      }
    },
  },
});
