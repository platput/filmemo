<script setup lang="ts">
import InfoCard from '@/components/InfoCard.vue';
import PlayersList from '@/components/PlayersList.vue';
import constants from '@/utils/constants';
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';


const route = useRoute()
const gameId = route.params.gameId
const results = ref({});
const isLoading = ref(true);
const isError = ref(false);
const loadingMessage = ref("Loading Results...")
const errorMessage = ref("")

onMounted(() => {
    const data = {"game_id": gameId}
    fetch(constants.apiGameWithResultsUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    }).then(async (response) => {
        isLoading.value = false;
        const respData = await response.json();
        if(response.status == 200) {
            results.value = respData.game.results
        } else {
            isError.value = true;
            errorMessage.value = "Error occurred while trying to get the results: " + respData;
        }
    });
});
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
          <PlayersList />
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
          <div v-if="isLoading" class="text-center">
            <v-progress-circular indeterminate :size="128" :width="12" color="brown" class="my-10"></v-progress-circular>
            <p class="text-h4 pb-10">{{ loadingMessage }}</p>
          </div>
          <div v-else>
            <div v-if="isError" class="text-center">
                <v-icon icon="fa-duotone fa-triangle-exclamation"></v-icon>
                <p class="text-h4 py-10">{{ errorMessage }}</p>
            </div>
            <div v-else>
                {{ results }}
            </div>
          </div>
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
          <InfoCard />
        </v-sheet>
      </v-col>
    </v-row>
  </v-container>
</template>
