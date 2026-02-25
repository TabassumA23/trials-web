import { defineStore } from "pinia";
import { TrialReview } from "../types";

// trialReviews Store
export const useTrialReviewsStore = defineStore("trialReviews", {
  state: (): { trialReviews: TrialReview[] } => ({
    trialReviews: [] as TrialReview[],
  }),

  getters: {
    // Find review by ID
    getTrialReviewById: (state) => (id: number) => {
      return state.trialReviews.find((r) => r.id === id);
    },

    // Get all reviews for a trial
    getTrialReviewsByTrialId: (state) => (trialId: number) => {
      return state.trialReviews.filter((r) => r.trial?.id === trialId);
    },

    // Get all reviews made by a user
    getTrialReviewsByUserId: (state) => (userId: number) => {
      return state.trialReviews.filter((r) => r.user?.id === userId);
    },
  },

  actions: {
    // Save the list of trial reviews
    saveTrialReviews(trialReviews: TrialReview[]) {
      this.trialReviews = trialReviews;
    },

    // Add a new trial review
    addTrialReview(trialReview: TrialReview) {
      this.trialReviews.push(trialReview);
    },

    // Remove trial review by ID
    removeTrialReview(id: number) {
      this.trialReviews = this.trialReviews.filter((r) => r.id !== id);
    },

    // Update review in store
    updateTrialReview(updated: TrialReview) {
      const i = this.trialReviews.findIndex((r) => r.id === updated.id);
      if (i > -1) this.trialReviews.splice(i, 1, updated);
    },
  },
});
