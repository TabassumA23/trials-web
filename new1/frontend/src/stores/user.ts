import { defineStore } from "pinia";
import { User } from "../types";

export const useUserStore = defineStore("user", {
  state: (): {user: User, csrf:string} => ({
    
    user: {} as User, // Holds the currently selected user
    //users: [] as User[], // Holds an array of users
    csrf: ''
  }),
  /* getters: {
    // Example getter: find a user by ID
    getUserById: (state) => (id: number) => {
      return state.users.find((user) => user.id === id);
    },
  },*/
  actions: {
    // Save the list of users
    saveUsers(user: User) {
      this.user = user;
    },

    setCsrfToken(csrf: string){
      this.csrf = csrf;
    },
/*
    // Add a new user
    addUser(user: User) {
        this.user.push(user);
      },
  
      // Remove a user by ID
      removeUser(id: number) {
        this.users = this.users.filter((user) => user.id !== id);
      },
*/
    // Fetch a single user by ID from the backend
    async fetchUser(userId: number) {
      try {
        const response = await fetch(`http://localhost:8000/user/${userId}/`);
  
        if (!response.ok) {
          throw new Error("Failed to fetch user data");
        }
        const userData = await response.json();
        this.user = userData; // Update the state with the fetched user data
      
      } catch (error) {
        console.error("Error fetching user data:", error);
      }
    },

    async fetchUserReturn(userId: number) {
      try {
        const response = await fetch(`http://localhost:8000/user/${userId}/`);
  
        if (!response.ok) {
          throw new Error("Failed to fetch user data");
        }
        const userData = await response.json();
        this.user = userData; // Update the state with the fetched user data
        return this.user
      } catch (error) {
        console.error("Error fetching user data:", error);
      }
    },
  },
});