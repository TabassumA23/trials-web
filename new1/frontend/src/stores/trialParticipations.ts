import { defineStore } from 'pinia'
import { TrialParticipation } from '../types'

export const useTrialParticipationsStore = defineStore('trialParticipations', {
    state: () => ({
        trialParticipations: [] as TrialParticipation[],
    }),

    getters: {
        // Find participation by trial ID
        getByTrialId: (state) => (trialId: number) => {
            return state.trialParticipations.find(p => p.trial === trialId);
        },

        // Find all participations for a user
        getByUserId: (state) => (userId: number) => {
            return state.trialParticipations.filter(p => p.user === userId);
        },
    },

    actions: {
        // Save all participations
        saveTrialParticipations(trialParticipations: TrialParticipation[]) {
            this.trialParticipations = trialParticipations
        },

        // Add a participation
        addTrialParticipation(trialParticipation: TrialParticipation) {
            this.trialParticipations.push(trialParticipation);
        },

        // Remove participation by ID
        removeTrialParticipation(trialParticipationId: number) {
            this.trialParticipations = this.trialParticipations.filter(
                (p) => p.id !== trialParticipationId
            );
        }
    }
})
