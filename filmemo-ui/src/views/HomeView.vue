<script setup lang="ts">
import type InfoCardVue from '@/components/InfoCard.vue';
import type MovieCardVue from '@/components/MovieCard.vue';
import type PlayersListVue from '@/components/PlayersList.vue';

</script>

<template>
  <v-container>
    <v-row>
      <v-col
        cols="12"
        sm="2"
      >
        <v-sheet
          rounded="lg"
          min-height="268"
        >
          <PlayersListVue />
        </v-sheet>
      </v-col>

      <v-col
        cols="12"
        sm="8"
      >
        <v-sheet
          min-height="70vh"
          rounded="lg"
        >
          <MovieCardVue />
        </v-sheet>
      </v-col>

      <v-col
        cols="12"
        sm="2"
      >
        <v-sheet
          rounded="lg"
          min-height="268"
        >
          <InfoCardVue />
        </v-sheet>
      </v-col>
    </v-row>
  </v-container>
</template>
