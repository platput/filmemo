<script setup lang="ts">
import CreateGame from '../components/CreateGame.vue';

</script>

<template>
  <v-container>
    <v-row>
      <v-col
        cols="12"
        sm="12"
      >
        <v-sheet
          min-height="70vh"
          rounded="lg"
        >
          <v-sheet class="pt-5">
            <p class="text-h4 text-center mb-5">Create Game</p>
            <CreateGame />
          </v-sheet>
        </v-sheet>
      </v-col>
    </v-row>
  </v-container>
</template>
