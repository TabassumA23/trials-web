import App from './App.vue';
import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import router from './router/index.ts';
import { createPinia } from 'pinia';

import routes from './router/index.ts'; // Ensure the correct path to the routes file

const app = createApp(App);
const pinia = createPinia();



app.use(pinia);
app.use(router);
app.mount('#app');
