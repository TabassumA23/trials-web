import { createRouter, createWebHistory } from "vue-router";
import ProfilePage from "../pages/ProfilePage.vue";
import Trials from "../pages/Trials.vue";
import ViewTrials from "../pages/ViewTrials.vue";
import TrialDashboard from "../pages/TrialDashboard.vue";
import TrialQuestions from "../pages/TrialQuestions.vue";
import TrialOptions from "../pages/TrialOptions.vue";
import TrialParticipation from "../pages/TrialParticipation.vue";
import TrialReviews from "../pages/TrialReviews.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "Profile Page", component: ProfilePage },
    { path: "/trials", name: "Trials", component: Trials },
    { path: "/view-trials", name: "View Trials", component: ViewTrials },
    { path: "/trialDashboard", name: "Trial Dashboard", component: TrialDashboard },
    { path: "/trialQuestions", name: "Trial Questions", component: TrialQuestions },
    { path: "/trialOptions", name: "Trial Options", component: TrialOptions },
    { path: "/trialParticipation", name: "Trial Participation", component: TrialParticipation },
    { path: "/trialReviews", name: "Trial Reviews", component: TrialReviews },
  ],
});

export default router;
