<!-- src/pages/ProfilePage.vue -->
<template>
  <div class="profile-page">
    <section class="hero">
      <div class="hero-content">
        <h1>Welcome, {{ user.first_name }}</h1>
        <p class="subtitle">Manage your profile & view your trial activity</p>
      </div>

      <nav class="hero-nav" v-if="user.is_staff">
        <RouterLink to="/trials" class="btn">View / Join Trials</RouterLink>
        <RouterLink to="/trialDashboard" class="btn">Trial Dashboard</RouterLink>
        <RouterLink to="/trialQuestions" class="btn">Add Trial Questions</RouterLink>
        <RouterLink to="/trialOptions" class="btn">Add Trial Options</RouterLink>
        <RouterLink to="/trialReviews" class="btn">Trial Reviews</RouterLink>
      </nav>
    </section>

    <div class="grid-container">
      <!-- PROFILE CARD -->
      <div class="card profile-card">
        <h2>Your Profile</h2>

        <section class="profile-info">
          <p class="field">
            <strong>Username:</strong> {{ user.username }}
            <button class="btn-link">
              <a href="http://localhost:8000/updateUser/">Change Username</a>
            </button>
          </p>

          <p class="field">
            <strong>First Name:</strong>
            <span v-if="!editFirstName">{{ user.first_name }}</span>
            <span v-else><input v-model="editedUser.first_name" type="text" /></span>
            <button v-if="!editFirstName" @click="toggleEditField('FirstName')">Edit</button>
            <button v-else @click="saveField('first_name')">Save</button>
          </p>

          <p class="field">
            <strong>Last Name:</strong>
            <span v-if="!editLastName">{{ user.last_name }}</span>
            <span v-else><input v-model="editedUser.last_name" type="text" /></span>
            <button v-if="!editLastName" @click="toggleEditField('LastName')">Edit</button>
            <button v-else @click="saveField('last_name')">Save</button>
          </p>

          <p class="field">
            <strong>Email:</strong>
            <span v-if="!editEmail">{{ user.email }}</span>
            <span v-else><input v-model="editedUser.email" type="email" /></span>
            <button v-if="!editEmail" @click="toggleEditField('Email')">Edit</button>
            <button v-else @click="saveField('email')">Save</button>
          </p>

          <p class="field">
            <strong>Date of Birth:</strong>
            <span v-if="!editDateOfBirth">{{ user.date_of_birth }}</span>
            <span v-else><input v-model="editedUser.date_of_birth" type="date" /></span>
            <button v-if="!editDateOfBirth" @click="toggleEditField('DateOfBirth')">Edit</button>
            <button v-else @click="saveField('date_of_birth')">Save</button>
          </p>

          <p class="field">
            <strong>Password:</strong> ********
            <button class="btn-link">
              <a href="http://localhost:8000/updatePass/">Change Password</a>
            </button>
          </p>

          <p class="field">
            <strong>User type:</strong> {{ user.is_staff ? "Staff" : "Client" }}
          </p>
        </section>
      </div>

      <!-- TRIALS JOINED -->
      <div class="card">
        <h2>Trials I Participated In</h2>

        <div v-if="participatedTrials.length">
          <div v-for="trial in participatedTrials" :key="trial.id" class="trial-block">
            <button type="button" @click="toggleTrialDetails(trial.id)">
              {{ trial.name }}
            </button>
            <div v-if="expandedTrialId === trial.id">
              <p><strong>Question:</strong> {{ trial.question }}</p>
              <div v-if="answersForTrial(trial).length">
                <p v-for="answer in answersForTrial(trial)" :key="answer.id">
                  <strong>Answer:</strong> {{ answer.answer_text }}
                </p>
              </div>
              <p v-else>No answers recorded for this trial yet.</p>
              <button type="button" @click="expandedTrialId = null">Hide</button>
            </div>
          </div>
        </div>
        <p v-else class="empty-state">No trials joined yet.</p>
      </div>

      <!-- MY ANSWERS -->
      <div class="card">
        <h2>My Answers</h2>

        <div v-if="myAnswers.length">
          <div v-for="answer in myAnswers" :key="answer.id" class="trial-block">
            <p><strong>Question:</strong> {{ questionNameById(answer.question) }}</p>
            <p><strong>Answer:</strong> {{ answer.answer_text }}</p>
          </div>
        </div>
        <p v-else class="empty-state">No answers submitted yet.</p>
      </div>

      <!-- MY SELECTIONS -->
      <div class="card">
        <h2>Selected Options</h2>

        <ul v-if="mySelections.length" class="tag-list">
          <li v-for="sel in mySelections" :key="sel.id">
            {{ optionNameById(sel.option) }}
          </li>
        </ul>
        <p v-else class="empty-state">No options selected yet.</p>
      </div>

      <!-- MY REVIEWS -->
      <div class="card">
        <h2>My Reviews</h2>

        <div v-if="myReviews.length">
          <div v-for="review in myReviews" :key="review.id" class="trial-block">
            <h3>{{ review.trial.name }}</h3>
            <p><strong>Rating:</strong> {{ review.rating }} ★</p>
            <p>{{ review.description }}</p>
            <p class="muted">{{ formatDate(review.date) }}</p>
          </div>
        </div>
        <p v-else class="empty-state">No reviews yet.</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { getCookie } from "../utils/cookies";

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

import { useUserStore } from "@/stores/user";

// ✅ trial stores (match the names we used in TrialDashboard.vue)
import { useTrialsStore } from "@/stores/trials";
import { useTrialQuestionsStore } from "@/stores/trialQuestions";
import { useTrialOptionsStore } from "@/stores/trialOptions";
import { useTrialParticipationsStore } from "@/stores/trialParticipations";
import { useTrialQuestionAnswersStore } from "@/stores/trialQuestionAnswers";
import { useTrialSpecificSelectionsStore } from "@/stores/trialSpecificSelections";
import { useTrialReviewsStore } from "@/stores/trialReviews";

export default defineComponent({
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

  data() {
    return {
      editFirstName: false,
      editLastName: false,
      editEmail: false,
      editDateOfBirth: false,

      editedUser: {
        first_name: "",
        last_name: "",
        email: "",
        date_of_birth: "",
      },
      expandedTrialId: null as number | null,
    };
  },

  async mounted() {
    // ---------------------------
    // SESSION CHECK (your logic)
    // ---------------------------
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
      try {
        await this.userStore.fetchUserReturn(userId);
      } catch (error) {
        console.error("Error fetching user:", error);
      }
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
          const sessionId = cookie.substring("sessionid=".length);
          sessionStorage.setItem("session_id", sessionId);
        }
      }
    }

    // ---------------------------
    // TRIAL DATA FETCHING
    // ---------------------------
    // ⚠️ Adjust endpoints if your Django urls differ.
    try {
      // trials
      const resTrials = await fetch("http://localhost:8000/trials/");
      const dataTrials = await resTrials.json();
      this.trialsStore.saveTrials(dataTrials.trials as Trial[]);

      // trial questions
      const resQuestions = await fetch("http://localhost:8000/trialQuestions/");
      const dataQuestions = await resQuestions.json();
      this.trialQuestionsStore.saveTrialQuestions(dataQuestions.trialQuestions as TrialQuestion[]);

      // trial options
      const resOptions = await fetch("http://localhost:8000/trialOptions/");
      const dataOptions = await resOptions.json();
      this.trialOptionsStore.saveTrialOptions(dataOptions.trialOptions as TrialOption[]);

      // participations
      const resParts = await fetch("http://localhost:8000/trialParticipations/");
      const dataParts = await resParts.json();
      this.trialParticipationsStore.saveTrialParticipations(
        dataParts.trialParticipations as TrialParticipation[]
      );

      // question answers
      const resAnswers = await fetch("http://localhost:8000/trialQuestionAnswers/");
      const dataAnswers = await resAnswers.json();
      this.trialQuestionAnswersStore.saveTrialQuestionAnswers(
        dataAnswers.trialQuestionAnswers as TrialQuestionAnswer[]
      );

      // specific selections
      const resSel = await fetch("http://localhost:8000/trialSpecificSelections/");
      const dataSel = await resSel.json();
      this.trialSpecificSelectionsStore.saveTrialSpecificSelections(
        dataSel.trialSpecificSelections as TrialSpecificSelection[]
      );

      // reviews
      const resReviews = await fetch("http://localhost:8000/trialReviews/");
      const dataReviews = await resReviews.json();
      this.trialReviewsStore.saveTrialReviews(dataReviews.trialReviews as TrialReview[]);
    } catch (error) {
      console.error("Error loading trial data:", error);
    }
  },

  methods: {
    toggleTrialDetails(trialId: number) {
      this.expandedTrialId = this.expandedTrialId === trialId ? null : trialId;
    },

    questionIdForTrial(trial: Trial): number | null {
      if (trial.question_id) return trial.question_id;
      const found = this.trialQuestions.find((q) => q.name === trial.question);
      return found ? found.id : null;
    },

    answersForTrial(trial: Trial): TrialQuestionAnswer[] {
      const questionId = this.questionIdForTrial(trial);
      if (!questionId) return [];
      return this.myAnswers.filter((answer) => answer.question === questionId);
    },

    toggleEditField(field: string) {
      // field comes in like 'FirstName' etc.
      // @ts-ignore
      this[`edit${field}`] = !this[`edit${field}`];

      // @ts-ignore
      if (this[`edit${field}`]) {
        const key = field
          .replace("FirstName", "first_name")
          .replace("LastName", "last_name")
          .replace("DateOfBirth", "date_of_birth")
          .toLowerCase();

        // @ts-ignore
        this.editedUser[key] = (this.user as any)[key];
      }
    },

    async saveField(field: string) {
      try {
        const payload: any = {
          [field]: (this.editedUser as any)[field],
        };

        const response = await fetch(`http://localhost:8000/user/${this.user.id}/`, {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${getCookie("access_token")}`,
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          credentials: "include",
          body: JSON.stringify(payload),
        });

        if (!response.ok) throw new Error("Failed to update field");

        const updatedUser = await response.json();
        // Update store
        this.userStore.user = updatedUser.user ?? updatedUser;
        window.location.reload();
      } catch (error) {
        console.error(error);
        alert(`Failed to update ${field}.`);
      }
    },

    questionNameById(questionId: number) {
      const q = this.trialQuestions.find((x) => x.id === questionId);
      return q ? q.name : `Question #${questionId}`;
    },

    optionNameById(optionId: number) {
      const o = this.trialOptions.find((x) => x.id === optionId);
      return o ? o.name : `Option #${optionId}`;
    },

    formatDate(dateStr: string) {
      const d = new Date(dateStr);
      return d.toLocaleDateString();
    },
  },

  computed: {
    user(): User {
      return this.userStore.user;
    },

    // store-backed lists
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
      return this.trialParticipationsStore.trialParticipations;
    },
    trialQuestionAnswers(): TrialQuestionAnswer[] {
      return this.trialQuestionAnswersStore.trialQuestionAnswers;
    },
    trialSpecificSelections(): TrialSpecificSelection[] {
      return this.trialSpecificSelectionsStore.trialSpecificSelections;
    },
    trialReviews(): TrialReview[] {
      return this.trialReviewsStore.trialReviews;
    },

    // derived “my …”
    myParticipations(): TrialParticipation[] {
      return (this.trialParticipations ?? []).filter((p) => p.user === this.user.id);
    },

    participatedTrials(): Trial[] {
      const joinedTrialIds = new Set(this.myParticipations.map((p) => p.trial));
      return this.trials.filter((t) => joinedTrialIds.has(t.id));
    },

    myAnswers(): TrialQuestionAnswer[] {
      return (this.trialQuestionAnswers ?? []).filter((a) => a.user === this.user.id);
    },

    mySelections(): TrialSpecificSelection[] {
      return (this.trialSpecificSelections ?? []).filter((s) => s.user === this.user.id);
    },

    myReviews(): TrialReview[] {
      return (this.trialReviews ?? []).filter((r) => r.user.id === this.user.id);
    },
  },
});
</script>
