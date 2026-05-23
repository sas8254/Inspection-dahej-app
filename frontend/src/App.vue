<script setup>
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

async function onLogout() {
  await auth.logout()
}
</script>

<template>
  <v-app>
    <v-app-bar>
      <v-app-bar-title>INSP Dahej</v-app-bar-title>

      <template v-if="auth.isAuthenticated">
        <v-btn :to="{ name: 'jobs' }">Jobs</v-btn>
        <v-btn :to="{ name: 'overtimes' }">Overtime</v-btn>
        <v-menu>
          <template #activator="{ props }">
            <v-btn v-bind="props">Lookups <v-icon end>mdi-menu-down</v-icon></v-btn>
          </template>
          <v-list>
            <v-list-item :to="{ name: 'plants' }" title="Plants" />
            <v-list-item :to="{ name: 'job-types' }" title="Job types" />
          </v-list>
        </v-menu>
      </template>

      <v-spacer />

      <template v-if="auth.isAuthenticated">
        <v-btn :to="{ name: 'profile' }">Profile</v-btn>
        <v-btn @click="onLogout">Logout</v-btn>
      </template>
      <template v-else>
        <v-btn :to="{ name: 'login' }">Login</v-btn>
        <v-btn :to="{ name: 'register' }">Register</v-btn>
      </template>
    </v-app-bar>

    <v-main>
      <v-container class="pt-6">
        <RouterView />
      </v-container>
    </v-main>
  </v-app>
</template>
