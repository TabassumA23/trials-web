<template>
  <main class="cuisine-page">
    <div class="card form-card">
      <h3>Create a New Trial Question</h3>

      <textarea
        v-model="newTrialQuestion.name"
        placeholder="Question name…"
        rows="1"
      />

      <button @click="createTrialQuestion">Add Trial Question</button>
    </div>
  </main>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { TrialQuestion } from "../types/index";
import { useUserStore } from "../stores/user";
import { useUsersStore } from "../stores/users";
import { useTrialQuestionsStore } from "../stores/trialQuestions";
import { getCookie } from "../utils/cookies";

export default defineComponent({
  data() {
    return {
      newTrialQuestion: { name: "" },
    };
  },

  async mounted() {
    /** SAME AUTH LOGIC — unchanged **/
    const sessionCookie = document.cookie.split(";");
    let currentSessionid = "";

    for (let cookie of sessionCookie) {
      cookie = cookie.trim();
      if (cookie.startsWith("sessionid=")) {
        currentSessionid = cookie.substring("sessionid=".length);
      }
    }

    const previousSessionid = window.sessionStorage.getItem("session_id");

    if (currentSessionid === previousSessionid) {
      const userId = Number(window.sessionStorage.getItem("user_id"));
      await this.userStore.fetchUserReturn(userId);
    } else {
      const params = new URLSearchParams(window.location.search);
      const userId = parseInt(params.get("u") || "0");

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
    /** CREATE TRIAL QUESTION **/
    async createTrialQuestion() {
      const trialQuestionsStore = useTrialQuestionsStore();

      const rawName = this.newTrialQuestion.name.trim();

      // 1️⃣ Reject blank
      if (!rawName) {
        return alert("Trial question name can’t be empty!");
      }

      // 2️⃣ Case-insensitive duplicate check
      const lc = rawName.toLowerCase();
      if (trialQuestionsStore.trialQuestions.some(q => q.name.toLowerCase() === lc)) {
        return alert("You already created a trial question with that name.");
      }

      const payload = {
        name: this.newTrialQuestion.name,
      };

      try {
        const response = await fetch("http://localhost:8000/trialQuestions/", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${getCookie("access_token")}`,
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          credentials: "include",
          body: JSON.stringify(payload),
        });

        if (!response.ok) throw new Error("Failed to create trial question");

        window.location.reload();
        alert("Trial question added successfully!");
      } catch (error) {
        console.error("Error creating trial question:", error);
        alert("Failed to create trial question");
      }
    },
  },

  computed: {
    user() {
      return this.userStore.user;
    },

    trialQuestions(): TrialQuestion[] {
      return this.trialQuestionsStore.trialQuestions;
    },
  },

  setup() {
    const userStore = useUserStore();
    const trialQuestionsStore = useTrialQuestionsStore();
    const usersStore = useUsersStore();

    return { userStore, trialQuestionsStore, usersStore };
  },
});
</script>
