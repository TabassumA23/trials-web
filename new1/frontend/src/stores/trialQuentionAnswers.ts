import { defineStore } from 'pinia'
import { TrialQuestionAnswer } from '../types'

export const useTrialQuestionAnswersStore = defineStore('trialQuestionAnswers', {
    state: () => ({
        trialQuestionAnswers: [] as TrialQuestionAnswer[],
    }),
    getters: {
        getTrialQuestionAnswerByText: (state) => (answer_text: string) => {
            return state.trialQuestionAnswers.find(a => a.answer_text === answer_text);
        },
    },
    actions: {
        saveTrialQuestionAnswers(trialQuestionAnswers: TrialQuestionAnswer[]) {
            this.trialQuestionAnswers = trialQuestionAnswers
        },
        // Add a new trialQuestionAnswer
        addTrialQuestionAnswer(trialQuestionAnswer: TrialQuestionAnswer) {
            this.trialQuestionAnswers.push(trialQuestionAnswer);
        },
        removeTrialQuestionAnswer(trialQuestionAnswerId: number) {
            this.trialQuestionAnswers = this.trialQuestionAnswers.filter(
                (a) => a.id !== trialQuestionAnswerId
            );
        }
    }
})
