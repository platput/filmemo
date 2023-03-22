<script setup lang="ts">
</script>

<template>
  <v-app id="inspire">
    <v-app-bar
    :elevation="2"
      class="px-3 py-3"
      color="#2D3D53"
      flat
      density="comfortable"
    >
      <v-spacer></v-spacer>
      <RouterLink to="/">
        <img src="@/assets/4.png" height="256" />
      </RouterLink>
      <v-spacer></v-spacer>
    </v-app-bar>

    <v-main class="bg-blue-grey-lighten-2 mt-8">
      <RouterView />
    </v-main>
    <v-bottom-navigation>
      <v-btn variant="plain" :to="{ name: 'about' }">
        <v-icon icon="fa-sharp fa-solid fa-address-card fa-flip" class="mb-2"></v-icon>
        About
      </v-btn>
    </v-bottom-navigation>
  </v-app>
</template>

<style scoped>
</style>
