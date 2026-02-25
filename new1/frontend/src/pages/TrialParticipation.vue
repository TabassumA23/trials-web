<template>
  <div class="body">
    <div class="reservation-form">
      <h3>Join a Trial</h3>

      <label for="trial">Select Trial:</label>
      <select id="trial" v-model="selectedTrial">
        <option v-for="t in trials" :key="t.id" :value="t">
          {{ t.name }}
        </option>
      </select>

      <button @click="joinTrial">Join Trial</button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { User, Trial, TrialParticipation } from "../types/index";

import { useUserStore } from "../stores/user";
import { useUsersStore } from "../stores/users";

import { useTrialsStore } from "../stores/trials";
import { useTrialParticipationsStore } from "../stores/trialParticipations";

import { getCookie } from "../utils/cookies";

export default defineComponent({
  data() {
    return {
      selectedTrial: null as Trial | null,
      trialParticipationsLocal: [] as TrialParticipation[], // if you still want local copy like before
    };
  },

  async mounted() {
    // ===== SAME SESSION/CSRF LOGIC (unchanged) =====
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

    // ===== TRIAL DATA FETCHING =====

    // 1) fetch all trials
    const trialsResp = await fetch("http://localhost:8000/trials/");
    const trialsData = await trialsResp.json();
    const madeTrials = trialsData.trials as Trial[];
    const trialsStore = useTrialsStore();
    trialsStore.saveTrials(madeTrials);

    // 2) fetch all trial participations
    const tpResp = await fetch("http://localhost:8000/trialParticipations/");
    const tpData = await tpResp.json();

    const madeTP = tpData.trialParticipations as TrialParticipation[];
    const trialParticipationsStore = useTrialParticipationsStore();
    trialParticipationsStore.saveTrialParticipations(madeTP);

    // optional local mirror (since your old page used `this.reservations = ...`)
    this.trialParticipationsLocal = madeTP;
  },

  methods: {
    async joinTrial() {
      const trialParticipationsStore = useTrialParticipationsStore();
      const userId = this.userStore.user.id;

      if (!this.selectedTrial || !this.selectedTrial.id) {
        alert("Please select a valid trial.");
        return;
      }

      // prevent duplicate join (same user + trial)
      const alreadyJoined = trialParticipationsStore.trialParticipations.some(
        (tp) => tp.user === userId && tp.trial === this.selectedTrial!.id
      );

      if (alreadyJoined) {
        alert("You already joined this trial.");
        return;
      }

      const payload = {
        user_id: userId,
        trial_id: this.selectedTrial.id,
      };

      try {
        const response = await fetch("http://localhost:8000/trialParticipations/", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${getCookie("access_token")}`,
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          credentials: "include",
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error("Failed to join trial");
        }

        const data = await response.json();
        const created = data.trialParticipation as TrialParticipation;

        trialParticipationsStore.addTrialParticipation(created);

        window.location.reload();
        alert("Joined trial successfully!");
      } catch (error) {
        console.error("Error joining trial:", error);
        alert("Failed to join trial");
      }
    },

    async deleteTrialParticipation(trialParticipationId: number) {
      // optional delete logic if you want it like reservations
      try {
        const response = await fetch(`http://localhost:8000/trialParticipation/${trialParticipationId}/`, {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${getCookie("access_token")}`,
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          credentials: "include",
        });

        if (!response.ok) throw new Error("Delete failed");

        const trialParticipationsStore = useTrialParticipationsStore();
        trialParticipationsStore.removeTrialParticipation(trialParticipationId);

        window.location.reload();
        alert("Left trial successfully!");
      } catch (error) {
        console.error("Error deleting trial participation:", error);
        alert("Failed to leave trial");
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

    trialParticipations(): TrialParticipation[] {
      return this.trialParticipationsStore.trialParticipations;
    },
  },

  setup() {
    const userStore = useUserStore();
    const usersStore = useUsersStore();

    const trialsStore = useTrialsStore();
    const trialParticipationsStore = useTrialParticipationsStore();

    return {
      userStore,
      usersStore,
      trialsStore,
      trialParticipationsStore,
    };
  },
});
</script>
