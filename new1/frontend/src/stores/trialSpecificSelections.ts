import { defineStore } from "pinia";
import { TrialSpecificSelection } from "../types";

export const useTrialSpecificSelectionsStore = defineStore("trialSpecificSelections", {
  state: () => ({
    trialSpecificSelections: [] as TrialSpecificSelection[],
  }),

  getters: {
    getByUser: (state) => (userId: number) => {
      return state.trialSpecificSelections.filter(sel => sel.user === userId);
    },

    getByOption: (state) => (optionId: number) => {
      return state.trialSpecificSelections.filter(sel => sel.option === optionId);
    },
  },

  actions: {
    saveTrialSpecificSelections(selections: TrialSpecificSelection[]) {
      this.trialSpecificSelections = selections;
    },

    addTrialSpecificSelection(selection: TrialSpecificSelection) {
      this.trialSpecificSelections.push(selection);
    },

    removeTrialSpecificSelection(id: number) {
      this.trialSpecificSelections =
        this.trialSpecificSelections.filter(sel => sel.id !== id);
    },
  },
});
