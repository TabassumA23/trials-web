<template>
  <main class="cuisine-page">
    <div class="card form-card">
      <h3>Create a New Trial Option</h3>

      <label>Select Question:</label>
      <select v-model="newOption.question_id">
        <option :value="0">Choose a question</option>
        <option v-for="q in trialQuestions" :key="q.id" :value="q.id">
          {{ q.name }}
        </option>
      </select>

      <textarea v-model="newOption.name" placeholder="Name…" rows="1" />

      <button @click="createTrialOption">Add Option</button>
    </div>
  </main>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { User, TrialOption, TrialQuestion } from "../types/index";

import { useUserStore } from "../stores/user";
import { useUsersStore } from "../stores/users";
import { useTrialOptionsStore } from "../stores/trialOptions";
import { useTrialQuestionsStore } from "../stores/trialQuestions";

import { getCookie } from "../utils/cookies";

export default defineComponent({
  data() {
    return {
      newOption: { name: "", question_id: 0 },
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

    const qResp = await fetch("http://127.0.0.1:8000/trialQuestions/");
    const qData = await qResp.json();
    this.trialQuestionsStore.saveTrialQuestions(
      (qData.trialQuestions ?? qData.trial_questions ?? []) as TrialQuestion[]
    );

    const oResp = await fetch("http://127.0.0.1:8000/trialOptions/");
    const oData = await oResp.json();
    this.trialOptionsStore.saveTrialOptions(
      (oData.trialOptions ?? oData.trial_options ?? []) as TrialOption[]
    );
  },

  methods: {
    /** Create new Trial Option */
    async createTrialOption() {
      const trialOptionsStore = useTrialOptionsStore();
      const userId = this.userStore.user.id;

      const rawName = this.newOption.name.trim();
      const questionId = Number(this.newOption.question_id);

      // Reject blank
      if (!rawName) {
        return alert("Option name can’t be empty!");
      }
      if (!questionId) {
        return alert("Please select a trial question first.");
      }

      // Case-insensitive duplicate check
      const lc = rawName.toLowerCase();
      if (trialOptionsStore.trialOptions.some(o => o.name.toLowerCase() === lc && o.question_id === questionId)) {
        return alert("You already created an option with that name.");
      }

      const payload = {
        name: this.newOption.name,
        question_id: questionId,
        user_id: userId,
      };

      try {
        const response = await fetch("http://127.0.0.1:8000/trialOptions/", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${getCookie("access_token")}`,
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          credentials: "include",
          body: JSON.stringify(payload),
        });

        if (!response.ok) throw new Error("Failed to create option");

        const created = (await response.json()) as TrialOption;

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
    trialQuestions(): TrialQuestion[] {
      return this.trialQuestionsStore.trialQuestions;
    },
  },

  setup() {
    const userStore = useUserStore();
    const usersStore = useUsersStore();
    const trialOptionsStore = useTrialOptionsStore();
    const trialQuestionsStore = useTrialQuestionsStore();

    return { userStore, usersStore, trialOptionsStore, trialQuestionsStore };
  },
});
</script>
