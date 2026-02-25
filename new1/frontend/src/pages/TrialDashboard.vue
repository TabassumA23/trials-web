<!-- src/pages/TrialDashboard.vue -->
<template>
  <main class="dashboard-page">
    <div class="card dashboard-card">
      <h2>Trial Dashboard</h2>

      <!-- JOIN TRIAL -->
      <div class="card inner-card">
        <h3>Join a Trial</h3>

        <label for="trialSelect">Select Trial:</label>
        <select id="trialSelect" v-model="selectedTrialId">
          <option value="">-- choose --</option>
          <option v-for="t in trials" :key="t.id" :value="t.id">
            {{ t.name }} (by {{ t.user.first_name }} {{ t.user.last_name }})
          </option>
        </select>

        <button :disabled="!selectedTrialId" @click="joinSelectedTrial">
          Join Trial
        </button>
      </div>

      <!-- ANSWER QUESTION -->
      <div class="card inner-card" v-if="selectedTrial">
        <h3>Trial Question</h3>
        <p><strong>Trial:</strong> {{ selectedTrial.name }}</p>
        <p><strong>Question:</strong> {{ selectedTrial.question }}</p>

        <label for="answerText">Your Answer:</label>
        <textarea
          id="answerText"
          v-model="answerText"
          placeholder="Type your answer..."
          rows="3"
        />

        <button @click="submitSelectedTrialAnswer" :disabled="!answerText.trim()">
          Submit Answer
        </button>
      </div>

      <!-- SELECT OPTIONS -->
      <div class="card inner-card" v-if="selectedTrial">
        <h3>Select Options</h3>

        <div class="option-list">
          <label v-for="optName in selectedTrial.options" :key="optName" class="option-item">
            <input
              type="checkbox"
              :value="optName"
              v-model="selectedOptionNames"
            />
            {{ optName }}
          </label>
        </div>

        <button
          @click="submitSelectedTrialSelections"
          :disabled="selectedOptionNames.length === 0"
        >
          Submit Selections
        </button>
      </div>

      <!-- MY PARTICIPATIONS -->
      <div class="card inner-card">
        <h3>My Trial Participations</h3>

        <div v-if="myTrialParticipations.length === 0" class="muted">
          You haven't joined any trials yet.
        </div>

        <div
          class="item"
          v-for="p in myTrialParticipations"
          :key="p.id"
        >
          <div class="item-header">
            <strong>{{ trialNameById(p.trial) }}</strong>
          </div>
          <div class="item-sub muted">Participation ID: {{ p.id }}</div>
        </div>
      </div>

      <!-- MY ANSWERS -->
      <div class="card inner-card">
        <h3>My Answers</h3>

        <div v-if="myQuestionAnswers.length === 0" class="muted">
          No answers submitted yet.
        </div>

        <div class="item" v-for="a in myQuestionAnswers" :key="a.id">
          <div class="item-header">
            <strong>Question:</strong> {{ trialQuestionNameById(a.question) }}
          </div>
          <div class="item-sub"><strong>Answer:</strong> {{ a.answer_text }}</div>
        </div>
      </div>

      <!-- MY SELECTIONS -->
      <div class="card inner-card">
        <h3>My Option Selections</h3>

        <div v-if="mySpecificSelections.length === 0" class="muted">
          No selections submitted yet.
        </div>

        <div class="item" v-for="s in mySpecificSelections" :key="s.id">
          <div class="item-header">
            <strong>Option:</strong> {{ trialOptionNameById(s.option) }}
          </div>
        </div>
      </div>

      <!-- REVIEWS -->
      <div class="card inner-card">
        <h3>Trial Reviews</h3>

        <div v-if="trialReviews.length === 0" class="muted">
          No reviews yet.
        </div>

        <div class="item" v-for="r in trialReviews" :key="r.id">
          <div class="item-header">
            <strong>{{ r.trial.name }}</strong>
            <span class="muted"> — {{ r.rating }}★</span>
          </div>
          <div class="item-sub">{{ r.description }}</div>
          <div class="muted small">
            by {{ r.user.first_name }} {{ r.user.last_name }} • {{ formatDate(r.date) }}
          </div>
        </div>
      </div>

      <!-- PAGINATION (Trials list) -->
      <div class="pagination-controls">
        <button @click="currentPage--" :disabled="currentPage === 1">Previous</button>
        <span>Page {{ currentPage }} of {{ totalPages }}</span>
        <button @click="currentPage++" :disabled="currentPage === totalPages">Next</button>
      </div>

      <div class="card inner-card">
        <h3>All Trials (paged)</h3>

        <div class="item" v-for="t in paginatedTrials" :key="t.id">
          <div class="item-header">
            <strong>{{ t.name }}</strong>
          </div>
          <div class="item-sub">
            <strong>Question:</strong> {{ t.question }}
          </div>
          <div class="item-sub">
            <strong>Options:</strong> {{ t.options.join(", ") }}
          </div>
          <div class="muted small">
            Owner: {{ t.user.first_name }} {{ t.user.last_name }}
          </div>
        </div>
      </div>

    </div>
  </main>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import type {
  User,
  Trial,
  TrialQuestion,
  TrialOption,
  TrialParticipation,
  TrialQuestionAnswer,
  TrialSpecificSelection,
  TrialReview,
} from "../types/index";

import { useUserStore } from "../stores/user";

// Trial stores (create these files exactly like the stores I gave you)
import { useTrialsStore } from "../stores/trials";
import { useTrialQuestionsStore } from "../stores/trialQuestions";
import { useTrialOptionsStore } from "../stores/trialOptions";
import { useTrialParticipationsStore } from "../stores/trialParticipations";
import { useTrialQuestionAnswersStore } from "../stores/trialQuestionAnswers";
import { useTrialSpecificSelectionsStore } from "../stores/trialSpecificSelections";
import { useTrialReviewsStore } from "../stores/trialReviews";

import { getCookie } from "../utils/cookies";

export default defineComponent({
  data() {
    return {
      // pagination
      currentPage: 1,
      perPage: 5,

      // join / answer / select
      selectedTrialId: "" as number | "" ,
      answerText: "",
      selectedOptionNames: [] as string[],
    };
  },

  async mounted() {
    // ===============================
    // USER SESSION / CSRF (your block)
    // ===============================
    const sessionCookie = (document.cookie).split(";");
    let currentSessionid: string = "";

    for (let cookie of sessionCookie) {
      cookie = cookie.trim();
      if (cookie.startsWith("sessionid" + "=")) {
        currentSessionid = cookie.substring("sessionid".length + 1);
      }
    }

    const previousSessionid: string | null = window.sessionStorage.getItem("session_id");

    if (currentSessionid == previousSessionid) {
      try {
        await this.userStore.fetchUserReturn(Number(window.sessionStorage.getItem("user_id")));
      } catch (error) {
        console.error("Error fetching user:", error);
      }
    } else {
      const params = new URLSearchParams(window.location.search);
      const userId: number = parseInt(params.get("u") || "0");

      const user = await this.userStore.fetchUserReturn(userId);
      this.userStore.user = user;

      sessionStorage.setItem("user_id", userId.toString());

      const session_cookie = (document.cookie).split(";");

      for (let cookie of session_cookie) {
        cookie = cookie.trim();

        if (cookie.startsWith("csrftoken" + "=")) {
          this.userStore.setCsrfToken(cookie.substring("csrftoken".length + 1));
        }

        if (cookie.startsWith("sessionid" + "=")) {
          const sessionId = cookie.substring("csrftoken".length + 1);
          sessionStorage.setItem("session_id", sessionId);
        }
      }
    }

    // ===============================
    // TRIAL DATA FETCHING
    // ===============================
    // NOTE: change these endpoints if your Django urls are different.
    // I used consistent plural paths.
    try {
      // Trials
      const trialsResp = await fetch("http://127.0.0.1:8000/trials/");
      const trialsData = await trialsResp.json();
      this.trialsStore.saveTrials(trialsData.trials as Trial[]);

      // Trial Questions
      const tqResp = await fetch("http://127.0.0.1:8000/trialQuestions/");
      const tqData = await tqResp.json();
      this.trialQuestionsStore.saveTrialQuestions(tqData.trialQuestions as TrialQuestion[]);

      // Trial Options
      const toResp = await fetch("http://127.0.0.1:8000/trialOptions/");
      const toData = await toResp.json();
      this.trialOptionsStore.saveTrialOptions(toData.trialOptions as TrialOption[]);

      // Trial Participations
      const tpResp = await fetch("http://127.0.0.1:8000/trialParticipations/");
      const tpData = await tpResp.json();
      this.trialParticipationsStore.saveTrialParticipations(tpData.trialParticipations as TrialParticipation[]);

      // Trial Question Answers
      const tqaResp = await fetch("http://127.0.0.1:8000/trialQuestionAnswers/");
      const tqaData = await tqaResp.json();
      this.trialQuestionAnswersStore.saveTrialQuestionAnswers(tqaData.trialQuestionAnswers as TrialQuestionAnswer[]);

      // Trial Specific Selections
      const tssResp = await fetch("http://127.0.0.1:8000/trialSpecificSelections/");
      const tssData = await tssResp.json();
      this.trialSpecificSelectionsStore.saveTrialSpecificSelections(tssData.trialSpecificSelections as TrialSpecificSelection[]);

      // Trial Reviews
      const trResp = await fetch("http://127.0.0.1:8000/trialReviews/");
      const trData = await trResp.json();
      this.trialReviewsStore.saveTrialReviews(trData.trialReviews as TrialReview[]);
    } catch (e) {
      console.error("Error fetching trial data:", e);
    }
  },

  methods: {
    formatDate(dateStr: string) {
      const d = new Date(dateStr);
      return d.toLocaleDateString();
    },

    trialNameById(trialId: number) {
      const t = this.trials.find((x) => x.id === trialId);
      return t ? t.name : `Trial #${trialId}`;
    },

    trialQuestionNameById(questionId: number) {
      const q = this.trialQuestions.find((x) => x.id === questionId);
      return q ? q.name : `Question #${questionId}`;
    },

    trialOptionNameById(optionId: number) {
      const o = this.trialOptions.find((x) => x.id === optionId);
      return o ? o.name : `Option #${optionId}`;
    },

    async joinSelectedTrial() {
      if (!this.selectedTrialId) return;

      try {
        const response = await fetch("http://127.0.0.1:8000/trialParticipation/", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${getCookie("access_token")}`,
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          credentials: "include",
          body: JSON.stringify({
            user_id: this.user.id,
            trial_id: this.selectedTrialId,
          }),
        });

        if (!response.ok) throw new Error("Failed to join trial");

        alert("Joined trial successfully!");
        window.location.reload();
      } catch (e) {
        console.error(e);
        alert("Could not join trial.");
      }
    },

    async submitSelectedTrialAnswer() {
      if (!this.selectedTrial) return;

      // Your Trial model has ONE question FK, but your Trial.as_dict returns question name.
      // We need the question ID for TrialQuestionAnswer.
      // We'll find by question name from the store.
      const q = this.trialQuestions.find((x) => x.name === this.selectedTrial!.question);
      if (!q) {
        alert("Could not find the TrialQuestion id for this trial. (Check your as_dict output)");
        return;
      }

      try {
        const response = await fetch("http://127.0.0.1:8000/trialAnswer/", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${getCookie("access_token")}`,
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          credentials: "include",
          body: JSON.stringify({
            user_id: this.user.id,
            question_id: q.id,
            answer_text: this.answerText,
          }),
        });

        if (!response.ok) throw new Error("Failed to submit answer");

        alert("Answer submitted!");
        window.location.reload();
      } catch (e) {
        console.error(e);
        alert("Could not submit answer.");
      }
    },

    async submitSelectedTrialSelections() {
      if (!this.selectedTrial) return;

      // Convert selected option names -> option ids (because TrialSpecificSelection needs option_id)
      const optionIds = this.selectedOptionNames
        .map((name) => this.trialOptions.find((o) => o.name === name)?.id)
        .filter((id): id is number => typeof id === "number");

      if (optionIds.length === 0) {
        alert("Could not map selected option names to option ids. Check TrialOption store data.");
        return;
      }

      try {
        // If your backend expects one POST per selection, we do that.
        // If your backend supports bulk, change it here.
        for (const optionId of optionIds) {
          const response = await fetch("http://127.0.0.1:8000/trialSelection/", {
            method: "POST",
            headers: {
              Authorization: `Bearer ${getCookie("access_token")}`,
              "Content-Type": "application/json",
              "X-CSRFToken": getCookie("csrftoken"),
            },
            credentials: "include",
            body: JSON.stringify({
              user_id: this.user.id,
              option_id: optionId,
            }),
          });

          if (!response.ok) throw new Error("Failed to submit selection");
        }

        alert("Selections submitted!");
        window.location.reload();
      } catch (e) {
        console.error(e);
        alert("Could not submit selections.");
      }
    },
  },

  computed: {
    user(): User {
      return this.userStore.user;
    },

    trials(): Trial[] {
      return this.trialsStore.trials;
    },

    trialQuestions(): TrialQuestion[] {
      return this.trialQuestionsStore.trialQuestions;
    },

    trialOptions(): TrialOption[] {
      return this.trialOptionsStore.trialOptions;
    },

    trialParticipations(): TrialParticipation[] {
      return this.trialParticipationsStore?.trialParticipations ?? [];
    },

    trialQuestionAnswers(): TrialQuestionAnswer[] {
      return this.trialQuestionAnswersStore?.trialQuestionAnswers ?? [];
    },

    trialSpecificSelections(): TrialSpecificSelection[] {
      return this.trialSpecificSelectionsStore?.trialSpecificSelections ?? [];
    },

    trialReviews(): TrialReview[] {
      return this.trialReviewsStore?.trialReviews ?? [];
    },

    selectedTrial(): Trial | null {
      if (!this.selectedTrialId) return null;
      const id = Number(this.selectedTrialId);
      return this.trials.find((t) => t.id === id) || null;
    },

    myTrialParticipations(): TrialParticipation[] {
      return (this.trialParticipations ?? []).filter((p) => p.user === this.user.id);
    },

    myQuestionAnswers(): TrialQuestionAnswer[] {
      return (this.trialQuestionAnswers ?? []).filter((a) => a.user === this.user.id);
    },

    mySpecificSelections(): TrialSpecificSelection[] {
      return (this.trialSpecificSelections ?? []).filter((s) => s.user === this.user.id);
    },

    totalPages(): number {
      return Math.ceil(this.trials.length / this.perPage) || 1;
    },

    paginatedTrials(): Trial[] {
      const start = (this.currentPage - 1) * this.perPage;
      return this.trials.slice(start, start + this.perPage);
    },
  },

  watch: {
    selectedTrialId() {
      this.answerText = "";
      this.selectedOptionNames = [];
    },
  },

  setup() {
    const userStore = useUserStore();

    const trialsStore = useTrialsStore();
    const trialQuestionsStore = useTrialQuestionsStore();
    const trialOptionsStore = useTrialOptionsStore();
    const trialParticipationsStore = useTrialParticipationsStore();
    const trialQuestionAnswersStore = useTrialQuestionAnswersStore();
    const trialSpecificSelectionsStore = useTrialSpecificSelectionsStore();
    const trialReviewsStore = useTrialReviewsStore();

    return {
      userStore,
      trialsStore,
      trialQuestionsStore,
      trialOptionsStore,
      trialParticipationsStore,
      trialQuestionAnswersStore,
      trialSpecificSelectionsStore,
      trialReviewsStore,
    };
  },
});
</script>
