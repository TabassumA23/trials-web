<template>
    <main>
        <!--Nav bar for every page -->
        <div class="navbar">
       
                <h2>Cure-Link</h2>
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
                    <a href= 'http://127.0.0.1:8000/logout/'>Log Out</a>
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

