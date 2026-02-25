import { defineStore } from "pinia";
import { TrialSpecificSelection } from "../types";

export const useTrialSpecificSelectionStore = defineStore("trialSpecificSelection", {
  state: (): { trialSpecificSelection: TrialSpecificSelection } => ({
    trialSpecificSelection: {} as TrialSpecificSelection,
  }),

  actions: {
    // Save a single selection
    saveTrialSpecificSelection(selection: TrialSpecificSelection) {
      this.trialSpecificSelection = selection;
    },

    // Fetch a single selection by ID
    async fetchTrialSpecificSelection(id: number) {
      try {
        const response = await fetch(`http://localhost:8000/trialSpecificSelection/${id}/`);

        if (!response.ok) {
          throw new Error("Failed to fetch trial specific selection");
        }

        const data = await response.json();
        this.trialSpecificSelection = data;

      } catch (error) {
        console.error("Error fetching trial specific selection:", error);
      }
    },
  },
});
