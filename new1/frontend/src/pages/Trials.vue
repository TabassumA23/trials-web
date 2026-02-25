<template>
  <main class="restaurant-page">

    <!-- Create Trial -->
    <div class="card restaurant-card">
      <h3>Create a New Trial</h3>

      <label>Trial name:</label>
      <input v-model="newTrial.name" placeholder="Enter trial name" />

      <label>Select Question:</label>
      <select v-model="newTrial.question_id">
        <option v-for="q in trialQuestions" :key="q.id" :value="q.id">
          {{ q.name }}
        </option>
      </select>

      <label>Select Options:</label>
      <select v-model="newTrial.option_ids" multiple>
        <option v-for="o in trialOptions" :key="o.id" :value="o.id">
          {{ o.name }}
        </option>
      </select>

      <button @click="createTrial">Create Trial</button>
    </div>

    <!-- Filters -->
    <div class="card restaurant-card filter-card">
      <h3>Filter Trials</h3>

      <input v-model="filterName" placeholder="Search by trial name..." />

      <select v-model="filterQuestion">
        <option value="">All Questions</option>
        <option v-for="q in trialQuestions" :key="q.id" :value="q.name">
          {{ q.name }}
        </option>
      </select>
    </div>

    <!-- Trials List -->
    <h2>All Trials</h2>

    <div class="card restaurant-card">
      <div v-for="t in paginatedTrials" :key="t.id" class="restaurant-item">

        <!-- EDIT MODE -->
        <div v-if="editingId === t.id">
          <input v-model="editedTrial.name" />

          <select v-model="editedTrial.question_id">
            <option v-for="q in trialQuestions" :key="q.id" :value="q.id">
              {{ q.name }}
            </option>
          </select>

          <select v-model="editedTrial.option_ids" multiple>
            <option v-for="o in trialOptions" :key="o.id" :value="o.id">
              {{ o.name }}
            </option>
          </select>

          <button @click="saveTrial(t.id)">Save</button>
          <button @click="cancelEdit">Cancel</button>
        </div>

        <!-- VIEW MODE -->
        <div v-else>
          <h3>{{ t.name }}</h3>
          <p><strong>Question:</strong> {{ t.question }}</p>
          <p><strong>Options:</strong> {{ t.options.join(", ") }}</p>
          <p><strong>Creator:</strong> {{ t.user.first_name }} {{ t.user.last_name }}</p>

          <div v-if="t.user.id === user.id">
            <button @click="startEdit(t)">Edit</button>
            <button @click="deleteTrial(t.id)">Delete</button>
          </div>
        </div>

      </div>

      <!-- Pagination -->
      <div class="pagination-controls">
        <button @click="currentPage--" :disabled="currentPage === 1">Prev</button>
        <span>{{ currentPage }} / {{ totalPages }}</span>
        <button @click="currentPage++" :disabled="currentPage === totalPages">Next</button>
      </div>
    </div>

  </main>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { useUserStore } from "../stores/user";
import { useTrialsStore } from "../stores/trials";
import { useTrialQuestionsStore } from "../stores/trialQuestions";
import { useTrialOptionsStore } from "../stores/trialOptions";
import VueCookies from "vue-cookies";

export default defineComponent({
  data() {
    return {
      newTrial: {
        name: "",
        question_id: 0,
        option_ids: [] as number[],
      },

      editingId: null as number | null,
      editedTrial: {
        name: "",
        question_id: 0,
        option_ids: [] as number[],
      },

      currentPage: 1,
      perPage: 3,
      filterName: "",
      filterQuestion: "",
    };
  },

  async mounted() {
    // fetch trials
    const tRes = await fetch("http://localhost:8000/trials/");
    const tData = await tRes.json();
    this.trialsStore.saveTrials(tData.trials);

    // fetch questions
    const qRes = await fetch("http://localhost:8000/trialQuestions/");
    const qData = await qRes.json();
    this.trialQuestionsStore.saveTrialQuestions(qData.trialQuestions);

    // fetch options
    const oRes = await fetch("http://localhost:8000/trialOptions/");
    const oData = await oRes.json();
    this.trialOptionsStore.saveTrialOptions(oData.trialOptions);
  },

  methods: {
    startEdit(t) {
      this.editingId = t.id;
      this.editedTrial = {
        name: t.name,
        question_id: t.question_id,
        option_ids: t.option_ids,
      };
    },

    cancelEdit() {
      this.editingId = null;
    },

    async saveTrial(id: number) {
      const res = await fetch(`http://localhost:8000/trial/${id}/`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${VueCookies.get("access_token")}`,
          "Content-Type": "application/json",
          "X-CSRFToken": VueCookies.get("csrftoken"),
        },
        credentials: "include",
        body: JSON.stringify(this.editedTrial),
      });

      if (res.ok) {
        const { trial } = await res.json();
        this.trialsStore.updateTrial(trial);
        this.editingId = null;
      }
    },

    async deleteTrial(id: number) {
      await fetch(`http://localhost:8000/trial/${id}/`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${VueCookies.get("access_token")}`,
          "X-CSRFToken": VueCookies.get("csrftoken"),
        },
        credentials: "include",
      });

      this.trialsStore.removeTrial(id);
    },

    async createTrial() {
      const res = await fetch("http://localhost:8000/trials/", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${VueCookies.get("access_token")}`,
          "Content-Type": "application/json",
          "X-CSRFToken": VueCookies.get("csrftoken"),
        },
        credentials: "include",
        body: JSON.stringify({
          ...this.newTrial,
          user_id: this.user.id,
        }),
      });

      if (res.ok) {
        const { trial } = await res.json();
        this.trialsStore.addTrial(trial);
      }
    },
  },

  computed: {
    user() {
      return this.userStore.user;
    },

    trials() {
      return this.trialsStore.trials;
    },

    trialQuestions() {
      return this.trialQuestionsStore.trialQuestions;
    },

    trialOptions() {
      return this.trialOptionsStore.trialOptions;
    },

    filteredTrials() {
      return this.trials.filter(t => {
        const nameMatch = t.name.toLowerCase().includes(this.filterName.toLowerCase());
        const questionMatch = this.filterQuestion ? t.question === this.filterQuestion : true;
        return nameMatch && questionMatch;
      });
    },

    totalPages() {
      return Math.ceil(this.filteredTrials.length / this.perPage) || 1;
    },

    paginatedTrials() {
      const start = (this.currentPage - 1) * this.perPage;
      return this.filteredTrials.slice(start, start + this.perPage);
    },
  },

  setup() {
    return {
      userStore: useUserStore(),
      trialsStore: useTrialsStore(),
      trialQuestionsStore: useTrialQuestionsStore(),
      trialOptionsStore: useTrialOptionsStore(),
    };
  },
});
</script>
