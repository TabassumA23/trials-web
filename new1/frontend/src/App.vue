<template>
    <main>
        <!--Nav bar for every page -->
        <div class="navbar">
       
                <h2>YumYelp</h2>
                <div class="nav-parts">
                      <!--Go to home page / profile page-->
                    <router-link
                        class="link"
                        :to="{name: 'Profile Page'}"
                    >
                        Home
                    </router-link>
                      <!-- Go to find friends-->
                    <router-link
                        class="link"
                        :to="{name: 'Trials'}"
                    >
                        Trials
                    </router-link>
                    <router-link
                        class="link"
                        :to="{name: 'Trial Participation'}"
                    >
                      
                        Participation
                    </router-link>
                    <!-- reservations page-->
                    <router-link
                        class="link"
                        :to="{name: 'Trial Dashboard'}"
                    >
                        Dashboard
                    </router-link>

                    <!-- wishlists page-->
                    <router-link
                        class="link"
                        :to="{name: 'Trial Reviews'}"
                    >
                        Reviews
                    </router-link>

                    <!-- Logout -->
                    <a href= 'http://localhost:8000/logout/'>Log Out</a>
                </div>
        </div>
        <RouterView class="flex-shrink-0" />
    </main>

</template>

<script lang="ts">
    import { defineComponent } from "vue";
    import { RouterView } from "vue-router";

    export default defineComponent({
        components: { RouterView },
    });

</script>

<style scoped>
:root {
  --bg-color:rgb(246, 248, 250); 
  --card-bg: rgba(255, 255, 255, 0.05);
  --accent: #ff00c1;
  --text: #fff;
  --muted: #ddd;
  --radius: 12px;
}

main {
  background-color: var(--bg-color);
  min-height: 100vh;
  padding: 2rem;
  font-family: 'Segoe UI', sans-serif;
  color: var(--text);
  display: flex;
  flex-direction: column;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--card-bg);
  padding: 1rem 2rem;
  border-radius: var(--radius);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
  margin-bottom: 2rem;
}

.navbar h2 {
  margin: 0;
  font-size: 1.8rem;
  color: var(--text);
}

.nav-parts {
  display: flex;
  gap: 1rem;
}

.nav-parts .link,
.nav-parts a {
  background: linear-gradient(90deg, #ff0080, #ff8c00);
  color: var(--text);
  padding: 0.6rem 1rem;
  border-radius: var(--radius);
  text-decoration: none;
  transition: transform 0.15s ease;
}

.nav-parts .link:hover,
.nav-parts a:hover {
  transform: scale(1.05);
}

.flex-shrink-0 {
  flex: 1;
}
</style>


