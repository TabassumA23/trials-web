<!-- ViewTrials.vue -->
<template>
  <main class="restaurant-page">
    <!-- Filters -->
    <div class="card restaurant-card filter-card">
      <h3>Filter Trials</h3>

      <label for="filter-name">By Name:</label>
      <input id="filter-name" type="text" v-model="filterName" placeholder="Search by name..." />

      <label for="filter-question">By Question:</label>
      <select id="filter-question" v-model="filterQuestion">
        <option value="">All Questions</option>
        <option v-for="q in trialQuestions" :key="q.id" :value="q.name">{{ q.name }}</option>
      </select>
    </div>

    <!-- All Trials Listing -->
    <h2>All Trials</h2>
    <div class="card restaurant-card">
      <div class="restaurant-item" v-for="(trial, index) in paginatedTrials" :key="trial.id || index">
        <div class="restaurant-header">
          <h3>{{ trial.name }}</h3>
        </div>

        <div class="restaurant-content">
          <p><strong>Question:</strong> {{ trial.question }}</p>

          <p><strong>Options:</strong>
            <span v-for="(o, i) in trial.options" :key="i">
              {{ o }}<span v-if="i < trial.options.length - 1"> | </span>
            </span>
          </p>

          <p>
            <strong>Created by:</strong>
            {{ trial.user.first_name }} {{ trial.user.last_name }}
          </p>
        </div>

        <!-- OPTIONAL ACTION BUTTONS (keep if you want) -->
        <!--
        <div class="restaurant-actions">
          <button @click="joinTrial(trial.id)">Join Trial</button>
        </div>
        -->
      </div>

      <!-- Pagination Controls -->
      <div class="pagination-controls">
        <button @click="currentPage--" :disabled="currentPage === 1">Previous</button>
        <span>Page {{ currentPage }} of {{ totalPages }}</span>
        <button @click="currentPage++" :disabled="currentPage === totalPages">Next</button>
      </div>
    </div>
  </main>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { User, Trial, TrialQuestion } from "../types/index";
import { useUserStore } from "../stores/user";
import { useUsersStore } from "../stores/users";

import { useTrialsStore } from "../stores/trials";
import { useTrialQuestionsStore } from "../stores/trialQuestions";

import { useCookies } from "vue3-cookies";

export default defineComponent({
  data() {
    return {
      selectedTrial: "",
      trial: null,

      currentPage: 1,
      perPage: 3,

      filterName: "",
      filterQuestion: "",

      // keep same style/format as your other pages
    };
  },

  async mounted() {
    // Fetching csrf token using session cookie information on mount
    const sessionCookie = (document.cookie).split(";");
    let currentSessionid: string = "";

    // Checking in UserStore with CSRF token
    for (let cookie of sessionCookie) {
      cookie = cookie.trim();

      if (cookie.startsWith("sessionid" + "=")) {
        currentSessionid = cookie.substring("sessionid".length + 1);
      }
    }

    const previousSessionid: string | null = window.sessionStorage.getItem("session_id");

    // Loading values from user store if sessionId matches
    if (currentSessionid == previousSessionid) {
      const userId = Number(window.sessionStorage.getItem("user_id"));
      try {
        const userCookie = await this.userStore.fetchUserReturn(
          Number(window.sessionStorage.getItem("user_id"))
        );
      } catch (error) {
        console.error("Error fetching user:", error);
      }
    } else {
      // Extracting user id from url query
      const params = new URLSearchParams(window.location.search);
      const userId: number = parseInt(params.get("u") || "0");

      // Fetch user data using url query information on mount
      let user = await this.userStore.fetchUserReturn(userId);

      this.userStore.user = user;
      // Set session variable
      sessionStorage.setItem("user_id", userId.toString());

      // Fetching csrf token using session cookie information on mount
      const session_cookie = (document.cookie).split(";");

      //Update user state in UserStore with CSRF token
      for (let cookie of session_cookie) {
        cookie = cookie.trim();

        if (cookie.startsWith("csrftoken" + "=")) {
          this.userStore.setCsrfToken(cookie.substring("csrftoken".length + 1));
        }

        //Update sessionStorage state in UserStore with CSRF token
        if (cookie.startsWith("sessionid" + "=")) {
          // Set session variable
          let sessionId = cookie.substring("csrftoken".length + 1);
          sessionStorage.setItem("session_id", sessionId);
        }
      }
    }

    // ✅ Fetch all trial questions
    let responseQ = await fetch(`http://localhost:8000/trialQuestions/`);
    let questionData = await responseQ.json();

    let madeQuestions = questionData.trialQuestions as TrialQuestion[];
    const trialQuestionsStore = useTrialQuestionsStore();
    trialQuestionsStore.saveTrialQuestions(madeQuestions);

    // ✅ Fetch all trials
    let responseT = await fetch(`http://localhost:8000/trials/`);
    let trialData = await responseT.json();

    let madeTrials = trialData.trials as Trial[];
    const trialsStore = useTrialsStore();
    trialsStore.saveTrials(madeTrials);
  },

  methods: {
    questionName(trial: any) {
      return trial.question ? trial.question : "";
    },

    async saveField(field: string) {
      try {
        const { cookies } = useCookies();
        const payload = {
          [field.toLowerCase()]: this.editedUser[field.toLowerCase()],
        };

        const response = await fetch(`http://localhost:8000/user/${this.user.id}/`, {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${cookies.get("access_token")}`,
            "Content-Type": "application/json",
            "X-CSRFToken": cookies.get("csrftoken"),
          },
          credentials: "include",
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error("Failed to update field");
        }

        const updatedUser = await response.json();

        this.userStore = this.userStore.saveUsers(updatedUser);
        window.location.reload();
        alert(`${field} updated successfully!`);
      } catch (error) {
        console.error(error);
        alert(`Failed to update ${field}.`);
      }
    },

    // OPTIONAL if you want join functionality here
    /*
    async joinTrial(trialId: number) {
      const { cookies } = useCookies();
      const response = await fetch("http://localhost:8000/trialParticipations/", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${cookies.get("access_token")}`,
          "Content-Type": "application/json",
          "X-CSRFToken": cookies.get("csrftoken"),
        },
        credentials: "include",
        body: JSON.stringify({ user_id: this.user.id, trial_id: trialId }),
      });

      if (response.ok) {
        alert("Joined trial!");
        window.location.reload();
      } else {
        alert("Failed to join trial");
      }
    },
    */
  },

  computed: {
    user(): User | undefined {
      const userStore = useUserStore();
      return userStore.user;
    },

    trials(): Trial[] {
      const trialsStore = useTrialsStore;
      return this.trialsStore.trials;
    },

    trialQuestions(): TrialQuestion[] {
      const trialQuestionsStore = useTrialQuestionsStore;
      return this.trialQuestionsStore.trialQuestions;
    },

    filteredTrials() {
      return this.trials.filter((t) => {
        const matchesName = t.name.toLowerCase().includes(this.filterName.toLowerCase());
        const matchesQuestion = this.filterQuestion ? t.question === this.filterQuestion : true;
        return matchesName && matchesQuestion;
      });
    },

    // Total pages based on filtered results
    totalPages() {
      return Math.ceil(this.filteredTrials.length / this.perPage) || 1;
    },

    // Slice filtered results for current page
    paginatedTrials() {
      const start = (this.currentPage - 1) * this.perPage;
      return this.filteredTrials.slice(start, start + this.perPage);
    },
  },

  watch: {
    filterName() {
      this.currentPage = 1;
    },
    filterQuestion() {
      this.currentPage = 1;
    },
  },

  setup() {
    const userStore = useUserStore();
    const usersStore = useUsersStore();

    const trialsStore = useTrialsStore();
    const trialQuestionsStore = useTrialQuestionsStore();

    return { userStore, usersStore, trialsStore, trialQuestionsStore };
  },
});
</script>
