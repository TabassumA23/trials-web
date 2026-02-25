import { defineStore } from 'pinia'
import { User } from '../types'

export const useUsersStore = defineStore('users', {
    state: () => ({ 
        users: [] as User[],
    }),
    actions: {
        saveUsers(users: User[]) {
            this.users = users
        }
    }
})