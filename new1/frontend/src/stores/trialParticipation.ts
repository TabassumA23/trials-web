import { defineStore } from "pinia";
import { TrialParticipation } from "../types";

export const useTrialParticipationStore = defineStore("trialParticipation", {
  state: (): { trialParticipation: TrialParticipation } => ({
    trialParticipation: {} as TrialParticipation, // Holds the currently selected trialParticipation
  }),

  actions: {
    // Save the selected trialParticipation
    saveTrialParticipation(trialParticipation: TrialParticipation) {
      this.trialParticipation = trialParticipation;
    },

    // Fetch a single trialParticipation by ID from the backend
    async fetchTrialParticipation(trialParticipationId: number) {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/trialParticipation/${trialParticipationId}/`
        );

        if (!response.ok) {
          throw new Error("Failed to fetch trialParticipation data");
        }

        const trialParticipationData = await response.json();
        this.trialParticipation = trialParticipationData; // Update state
      } catch (error) {
        console.error("Error fetching trialParticipation data:", error);
      }
    },
  },
});
