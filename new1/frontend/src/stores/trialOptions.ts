import { defineStore } from "pinia";
import { TrialOption } from "../types";

// TrialOptions Store
export const useTrialOptionsStore = defineStore("trialOptions", {
  state: (): { trialOptions: TrialOption[] } => ({
    trialOptions: [] as TrialOption[], // Holds an array of trial options
  }),
  getters: {
    // Example getter: find a trial option by ID
    getTrialOptionById: (state) => (id: number) => {
      return state.trialOptions.find((opt) => opt.id === id);
    },
    getTrialOptionByName: (state) => (name: string) => {
      return state.trialOptions.find((opt) => opt.name === name);
    },
  },
  actions: {
    // Save the list of trial options
    saveTrialOptions(trialOptions: TrialOption[]) {
      this.trialOptions = trialOptions;
    },

    // Add a new trial option
    addTrialOption(trialOption: TrialOption) {
      this.trialOptions.push(trialOption);
    },

    // Remove a trial option by ID
    removeTrialOption(id: number) {
      this.trialOptions = this.trialOptions.filter((opt) => opt.id !== id);
    },
  },
});
