import { defineStore } from "pinia";
import { Trial } from "../types";

// trials Store
export const useTrialsStore = defineStore("trials", {
  state: (): { trials: Trial[] } => ({
    trials: [] as Trial[], // Holds an array of trials
  }),
  getters: {
    // Example getter: find a trial by ID
    getTrialById: (state) => (id: number) => {
      return state.trials.find((trial) => trial.id === id);
    },
    getTrialByName: (state) => (name: string) => {
      return state.trials.find((trial) => trial.name === name);
    },
  },
  actions: {
    // Save the list of trials
    saveTrials(trials: Trial[]) {
      this.trials = trials;
    },

    // Add a new trial
    addTrial(trial: Trial) {
      this.trials.push(trial);
    },

    // Remove a trial by ID
    removeTrial(id: number) {
      this.trials = this.trials.filter((trial) => trial.id !== id);
    },

    // Update a trial
    updateTrial(updated: Trial) {
      const i = this.trials.findIndex((t) => t.id === updated.id);
      if (i > -1) this.trials.splice(i, 1, updated);
    },
  },
});