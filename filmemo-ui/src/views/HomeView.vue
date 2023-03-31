<script setup lang="ts">
import MovieCard from '@/components/MovieCard.vue';

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
          <MovieCard />
        </v-sheet>
      </v-col>
    </v-row>
  </v-container>
</template>
