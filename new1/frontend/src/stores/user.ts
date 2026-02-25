import { defineStore } from "pinia";
import { User } from "../types";

export const useUserStore = defineStore("user", {
  state: (): {user: User, csrf:string} => ({
    
    user: {
      id: 0,
      api: "",
      username: "",
      first_name: "",
      last_name: "",
      email: "",
      phone_number: "",
      date_of_birth: "",
      is_staff: false,
    }, // Holds the currently selected user
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
      if (!userId || userId <= 0) {
        window.location.href = "http://127.0.0.1:8000/login/";
        return;
      }
      try {
        const response = await fetch(`http://127.0.0.1:8000/user/${userId}/`, {
          credentials: "include",
        });
  
        if (response.status === 401) {
          window.location.href = "http://127.0.0.1:8000/login/";
          return;
        }
        if (response.status === 404) {
          window.location.href = "http://127.0.0.1:8000/login/";
          return;
        }
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
      if (!userId || userId <= 0) {
        window.location.href = "http://127.0.0.1:8000/login/";
        return this.user;
      }
      try {
        const response = await fetch(`http://127.0.0.1:8000/user/${userId}/`, {
          credentials: "include",
        });
  
        if (response.status === 401) {
          window.location.href = "http://127.0.0.1:8000/login/";
          return this.user;
        }
        if (response.status === 404) {
          window.location.href = "http://127.0.0.1:8000/login/";
          return this.user;
        }
        if (!response.ok) {
          throw new Error("Failed to fetch user data");
        }
        const userData = await response.json();
        this.user = userData; // Update the state with the fetched user data
        return this.user
      } catch (error) {
        console.error("Error fetching user data:", error);
        return this.user;
      }
    },
  },
});
