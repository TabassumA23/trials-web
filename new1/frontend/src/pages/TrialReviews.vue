<template>
  <main class="review-page">
    <!-- Create Trial Review -->
    <div class="card form-card">
      <h3>Create a New Trial Review</h3>

      <label for="name">Title for Review:</label>
      <textarea
        id="name"
        v-model="newTrialReview.name"
        placeholder="Give your review a name..."
        rows="2"
      ></textarea>

      <label for="trial">Select Trial:</label>
      <select id="trial" v-model="newTrialReview.trial">
        <option v-for="t in trials" :key="t.id" :value="t">
          {{ t.name }}
        </option>
      </select>

      <label for="rating">Overall rating:</label>
      <input
        type="number"
        min="1"
        max="5"
        v-model="newTrialReview.rating"
        placeholder="Enter a number from 1 to 5"
      />

      <label for="description">Brief Description:</label>
      <textarea
        id="description"
        v-model="newTrialReview.description"
        placeholder="What did you think?..."
        rows="4"
      ></textarea>

      <button @click="createTrialReview">Add Review</button>
    </div>

    <h2>All Trial Reviews</h2>

    <!-- Filter by trial -->
    <input
      type="text"
      v-model="searchTrial"
      placeholder="Filter by trial name..."
    />

    <div class="card review-list-card">
      <div v-for="(review, idx) in paginatedTrialReviews" :key="review.id || idx" class="review-item">
        <!-- EDIT MODE -->
        <template v-if="review.user && user && review.user.id === user.id && editingId === review.id">
          <div class="review-edit-form">
            <input v-model="editedTrialReview.name" placeholder="Review title" />

            <select v-model="editedTrialReview.trialId">
              <option v-for="t in trials" :key="t.id" :value="t.id">
                {{ t.name }}
              </option>
            </select>

            <input type="number" min="1" max="5" v-model="editedTrialReview.rating" />

            <textarea v-model="editedTrialReview.description" rows="3" placeholder="Description"></textarea>

            <button @click="saveTrialReviewEdit(review.id)">Save</button>
            <button @click="cancelTrialReviewEdit()">Cancel</button>
          </div>
        </template>

        <!-- READ-ONLY MODE -->
        <template v-else>
          <div class="review-header">
            <h3>Title: {{ review.name }}</h3>

            <p>
              <strong>Trial:</strong>
              {{ review.trial?.name || review.trial?.trial_name || 'Unknown' }}
            </p>

            <p>
              <strong>By:</strong>
              {{ review.user.first_name }} {{ review.user.last_name }}
              |
              <strong>Date:</strong>
              {{ formatDate(review.date) }}
            </p>
          </div>

          <div class="review-content">
            <p>Review: {{ review.description }}</p>
            <p><strong>Rating:</strong> {{ review.rating }} ☆</p>
          </div>

          <div class="review-actions" v-if="review.user && user && review.user.id === user.id">
            <button @click="startTrialReviewEdit(review)">Edit</button>
            <button @click="deleteTrialReview(review.id)">Delete</button>
          </div>
        </template>
      </div>

      <!-- Pagination -->
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
import { useUserStore } from "../stores/user";
import { useUsersStore } from "../stores/users";
import { useTrialsStore } from "../stores/trials";
import { useTrialReviewsStore } from "../stores/trialReviews";
import { getCookie } from "../utils/cookies";

export default defineComponent({
  data() {
    return {
      trialReviewsLocal: [] as any[], // local array (like your old file did)
      searchTrial: "",
      currentPage: 1,
      itemsPerPage: 4,

      editingId: null as number | null,
      editedTrialReview: {
        name: "",
        trialId: 0,
        rating: 1,
        description: "",
      },

      newTrialReview: {
        name: "",
        trial: null as any | null,
        rating: 1,
        description: "",
      },
    };
  },

  async mounted() {
    // 1) user load (keeping your flow)
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

    // 2) fetch trials (dropdown + filter)
    const trialsResp = await fetch("http://127.0.0.1:8000/trials/");
    const trialsData = await trialsResp.json();
    this.trialsStore.saveTrials(trialsData.trials);

    // 3) fetch trial reviews
    const resp = await fetch("http://127.0.0.1:8000/trialReviews/");
    const data = await resp.json();
    this.trialReviewsLocal = data.trialReviews; // backend should send { trialReviews: [...] }
  },

  methods: {
    formatDate(date: string) {
      const d = new Date(date);
      return d.toLocaleDateString();
    },

    startTrialReviewEdit(r: any) {
      this.editingId = r.id;
      this.editedTrialReview = {
        name: r.name,
        trialId: r.trial?.id ?? r.trial_id ?? 0,
        rating: r.rating,
        description: r.description,
      };
    },

    cancelTrialReviewEdit() {
      this.editingId = null;
    },

    async saveTrialReviewEdit(id: number) {
      try {
        const payload = {
          name: this.editedTrialReview.name.trim(),
          trial_id: this.editedTrialReview.trialId,
          rating: this.editedTrialReview.rating,
          description: this.editedTrialReview.description.trim(),
        };

        const res = await fetch(`http://127.0.0.1:8000/trialReview/${id}/`, {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${getCookie("access_token")}`,
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          credentials: "include",
          body: JSON.stringify(payload),
        });

        if (!res.ok) throw new Error("Update failed");

        const updated = await res.json();
        const idx = this.trialReviewsLocal.findIndex((r) => r.id === id);
        if (idx > -1) this.trialReviewsLocal.splice(idx, 1, updated.trialReview);

        this.cancelTrialReviewEdit();
        window.location.reload();
        alert("Trial review updated!");
      } catch (e) {
        console.error(e);
        alert("Could not save changes.");
      }
    },

    async createTrialReview() {
      if (!this.newTrialReview.trial) {
        alert("Please select a trial.");
        return;
      }

      const payload = {
        name: this.newTrialReview.name,
        trial_id: this.newTrialReview.trial.id,
        rating: this.newTrialReview.rating,
        description: this.newTrialReview.description,
        user_id: this.user.id,
      };

      try {
        await fetch("http://127.0.0.1:8000/trialReviews/", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${getCookie("access_token")}`,
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          credentials: "include",
          body: JSON.stringify(payload),
        });

        window.location.reload();
        alert("Trial review added successfully!");
      } catch (error) {
        console.error("Error creating trial review:", error);
        alert("Failed to create trial review");
      }
    },

    async deleteTrialReview(reviewId: number) {
      const reviewToDelete = this.trialReviewsLocal.find((r) => r.id === reviewId);
      if (!reviewToDelete || !reviewToDelete.user || reviewToDelete.user.id !== this.user.id) {
        alert("You cannot delete this review. Only the author can delete it.");
        return;
      }

      try {
        const response = await fetch(`http://127.0.0.1:8000/trialReview/${reviewId}/`, {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${getCookie("access_token")}`,
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          credentials: "include",
        });

        if (response.ok) {
          this.trialReviewsLocal = this.trialReviewsLocal.filter((r) => r.id !== reviewId);
          alert("Trial review deleted successfully!");
        } else {
          alert("Failed to delete the trial review.");
        }
      } catch (error) {
        console.error("Error deleting trial review:", error);
        alert("Failed to delete the trial review.");
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

    filteredTrialReviews() {
      if (!this.searchTrial) return this.trialReviewsLocal;

      return this.trialReviewsLocal.filter((r) => {
        const trialName = r.trial?.name || "";
        return trialName.toLowerCase().includes(this.searchTrial.toLowerCase());
      });
    },

    paginatedTrialReviews() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      return this.filteredTrialReviews.slice(start, start + this.itemsPerPage);
    },

    totalPages() {
      return Math.ceil(this.filteredTrialReviews.length / this.itemsPerPage) || 1;
    },
  },

  setup() {
    const userStore = useUserStore();
    const trialReviewsStore = useTrialReviewsStore();
    const trialsStore = useTrialsStore();
    const usersStore = useUsersStore();
    return { userStore, trialReviewsStore, trialsStore, usersStore };
  },
});
</script>
