<template>
  <main class="cuisine-page">
    <div class="card form-card">
      <h3>Create a New Trial Option</h3>

      <textarea v-model="newOption.name" placeholder="Name…" rows="1" />
      <textarea v-model="newOption.description" placeholder="Description…" rows="3" />

      <button @click="createTrialOption">Add Option</button>
    </div>
  </main>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { User, TrialOption } from "../types/index";

import { useUserStore } from "../stores/user";
import { useUsersStore } from "../stores/users";
import { useTrialOptionsStore } from "../stores/trialOptions";

import VueCookies from "vue-cookies";

export default defineComponent({
  data() {
    return {
      newOption: { name: "", description: "" },
    };
  },

  async mounted() {
    // ===== SAME SESSION / CSRF LOGIC (unchanged) =====
    const sessionCookie = document.cookie.split(";");
    let currentSessionid = "";

    for (let cookie of sessionCookie) {
      cookie = cookie.trim();
      if (cookie.startsWith("sessionid=")) {
        currentSessionid = cookie.substring("sessionid=".length);
      }
    }

    const previousSessionid: string | null = window.sessionStorage.getItem("session_id");

    if (currentSessionid === previousSessionid) {
      const userId = Number(window.sessionStorage.getItem("user_id"));
      try {
        await this.userStore.fetchUserReturn(userId);
      } catch (error) {
        console.error("Error fetching user:", error);
      }
    } else {
      const params = new URLSearchParams(window.location.search);
      const userId: number = parseInt(params.get("u") || "0");

      const user = await this.userStore.fetchUserReturn(userId);
      this.userStore.user = user;

      sessionStorage.setItem("user_id", userId.toString());

      const session_cookie = document.cookie.split(";");
      for (let cookie of session_cookie) {
        cookie = cookie.trim();

        if (cookie.startsWith("csrftoken=")) {
          this.userStore.setCsrfToken(cookie.substring("csrftoken=".length));
        }
        if (cookie.startsWith("sessionid=")) {
          sessionStorage.setItem("session_id", cookie.substring("sessionid=".length));
        }
      }
    }
  },

  methods: {
    /** Create new Trial Option */
    async createTrialOption() {
      const trialOptionsStore = useTrialOptionsStore();
      const userId = this.userStore.user.id;

      const rawName = this.newOption.name.trim();

      // Reject blank
      if (!rawName) {
        return alert("Option name can’t be empty!");
      }

      // Case-insensitive duplicate check
      const lc = rawName.toLowerCase();
      if (trialOptionsStore.trialOptions.some(o => o.name.toLowerCase() === lc)) {
        return alert("You already created an option with that name.");
      }

      const payload = {
        name: this.newOption.name,
        description: this.newOption.description,
        user_id: userId,
      };

      try {
        const response = await fetch("http://localhost:8000/trialOptions/", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${VueCookies.get("access_token")}`,
            "Content-Type": "application/json",
            "X-CSRFToken": VueCookies.get("csrftoken"),
          },
          credentials: "include",
          body: JSON.stringify(payload),
        });

        if (!response.ok) throw new Error("Failed to create option");

        const data = await response.json();
        const created = data.trialOption as TrialOption;

        trialOptionsStore.addTrialOption(created);

        window.location.reload();
        alert("Trial option added successfully!");
      } catch (error) {
        console.error("Error creating option:", error);
        alert("Failed to create trial option");
      }
    },
  },

  computed: {
    user(): User {
      return this.userStore.user;
    },

    trialOptions(): TrialOption[] {
      return this.trialOptionsStore.trialOptions;
    },
  },

  setup() {
    const userStore = useUserStore();
    const usersStore = useUsersStore();
    const trialOptionsStore = useTrialOptionsStore();

    return { userStore, usersStore, trialOptionsStore };
  },
});
</script>
