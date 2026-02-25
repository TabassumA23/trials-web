<!-- src/pages/ProfilePage.vue -->
<template>
  <div class="profile-page">
    <section class="hero">
      <div class="hero-content">
        <h1>Welcome, {{ user.first_name }}</h1>
        <p class="subtitle">Manage your profile & view your trial activity</p>
      </div>

      <nav class="hero-nav">
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
            <strong>User type:</strong> {{ user.user_type }}
          </p>
        </section>
      </div>

      <!-- TRIALS JOINED -->
      <div class="card">
        <h2>Trials I Participated In</h2>

        <div v-if="participatedTrials.length">
          <div v-for="trial in participatedTrials" :key="trial.id" class="trial-block">
            <h3>{{ trial.name }}</h3>
            <p><strong>Question:</strong> {{ trial.question }}</p>
            <p><strong>Options:</strong> {{ trial.options.join(", ") }}</p>
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
import VueCookies from "vue-cookies";

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
            Authorization: `Bearer ${VueCookies.get("access_token")}`,
            "Content-Type": "application/json",
            "X-CSRFToken": VueCookies.get("csrftoken"),
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
      return this.trialParticipations.filter((p) => p.user === this.user.id);
    },

    participatedTrials(): Trial[] {
      const joinedTrialIds = new Set(this.myParticipations.map((p) => p.trial));
      return this.trials.filter((t) => joinedTrialIds.has(t.id));
    },

    myAnswers(): TrialQuestionAnswer[] {
      return this.trialQuestionAnswers.filter((a) => a.user === this.user.id);
    },

    mySelections(): TrialSpecificSelection[] {
      return this.trialSpecificSelections.filter((s) => s.user === this.user.id);
    },

    myReviews(): TrialReview[] {
      return this.trialReviews.filter((r) => r.user.id === this.user.id);
    },
  },
});
</script>

<style scoped>
:root {
  --bg-start: #0f0c29;
  --bg-end: #302b63;
  --card-bg: rgba(255, 255, 255, 0.05);
  --accent: #ff00c1;
  --text: #eee;
  --muted: #aaa;
  --radius: 12px;
}

.profile-page {
  font-family: "Segoe UI", sans-serif;
  color: var(--text);
  background: linear-gradient(135deg, var(--bg-start), var(--bg-end));
  min-height: 100vh;
  padding: 2rem;
}

.hero {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.hero-content h1 {
  font-size: 2.5rem;
  margin: 0;
  letter-spacing: 1px;
}

.subtitle {
  color: var(--muted);
  margin-top: 0.5rem;
}

.hero-nav {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.card {
  background: var(--card-bg);
  padding: 1.5rem;
  border-radius: var(--radius);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.card h2 {
  margin-top: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding-bottom: 0.5rem;
}

.profile-info .field {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0.6rem 0;
}

.profile-info .field button {
  margin-left: auto;
}

textarea,
input,
select {
  border: 2px solid #ff8c00;
  outline: none;
  background: rgba(255, 255, 255, 0.07);
  color: #fff;
  font-size: 1rem;
  padding: 0.75rem;
  border-radius: var(--radius);
  width: 100%;
}

textarea:focus,
input:focus,
select:focus {
  border-color: var(--accent);
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 0 3px rgba(255, 0, 193, 0.2);
}

.btn {
  background: linear-gradient(90deg, #ff0080, #ff8c00);
  border: none;
  padding: 0.65rem 1.2rem;
  color: #fff;
  font-weight: 600;
  border-radius: var(--radius);
  cursor: pointer;
  text-decoration: none;
  transition: transform 0.15s ease;
}

.btn:hover {
  transform: scale(1.03);
}

.btn-link {
  background: transparent;
  border: none;
  padding: 0;
}

.btn-link a {
  color: #fff;
  text-decoration: underline;
}

.empty-state {
  color: var(--muted);
  font-style: italic;
}

.trial-block {
  background: rgba(255, 255, 255, 0.06);
  padding: 0.75rem;
  border-radius: var(--radius);
  margin-top: 0.75rem;
}

.tag-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag-list li {
  background: rgba(255, 255, 255, 0.15);
  padding: 0.4rem 0.7rem;
  border-radius: var(--radius);
}

.muted {
  color: var(--muted);
}
</style>
