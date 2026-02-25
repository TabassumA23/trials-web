import { defineStore } from 'pinia';
import { TrialQuestion } from '../types';

// TrialQuestions Store
export const useTrialQuestionsStore = defineStore('trialQuestions', {
    state: (): { trialQuestions: TrialQuestion[] } => ({
        trialQuestions: [] as TrialQuestion[],
    }),

    getters: {
        // Find a trial question by ID
        getTrialQuestionById: (state) => (id: number) => {
            return state.trialQuestions.find(question => question.id === id);
        },

        // Find a trial question by name
        getTrialQuestionByName: (state) => (name: string) => {
            return state.trialQuestions.find(question => question.name === name);
        },
    },

    actions: {
        // Save all trial questions
        saveTrialQuestions(trialQuestions: TrialQuestion[]) {
            this.trialQuestions = trialQuestions;
        },

        // Add a new trial question
        addTrialQuestion(trialQuestion: TrialQuestion) {
            this.trialQuestions.push(trialQuestion);
        },

        // Remove a trial question by ID
        removeTrialQuestion(id: number) {
            this.trialQuestions = this.trialQuestions.filter(
                question => question.id !== id
            );
        },
    },
});
