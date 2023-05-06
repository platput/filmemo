<script setup lang="ts">
import InfoCard from '@/components/InfoCard.vue';
import PlayersList from '@/components/PlayersList.vue';
import { useUserStore } from '@/stores/user';
import constants from '@/utils/constants';
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

interface Result {
  id: string;
  score: number;
  avatar: string;
  handle: string;
}

const route = useRoute()
const gameId = route.params.gameId
const results = ref<Result[]>();
const isLoading = ref(true);
const isError = ref(false);
const loadingMessage = ref("Loading Results...")
const errorMessage = ref("")
// TODO: Use user store to show some sort of indication for the current user in the results page!
// const userStore = useUserStore();

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
            let resultsResp: {[key: string]: string};
            resultsResp = respData.game.results;
            let resultsList: {id: string, score: number, avatar: string, handle: string}[] = [];
            const players = respData.game.players;
            for(const key in resultsResp) {
                const playerId = key;
                const score = resultsResp[key];
                for (let index = 0; index < respData.game.players.length; index++) {
                    const player = players[index];
                    if (player.id === playerId) {
                        const result = {
                            id: player.id,
                            score: parseInt(score),
                            handle: player.handle,
                            avatar: player.avatar,
                        }
                        resultsList.push(result);
                    }
                }
            }
            resultsList.sort((a, b) => b.score - a.score)
            console.log(resultsList);
            results.value = resultsList;
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
                <v-list lines="two">
                    <v-list-item
                        v-for="item, index in results"
                        :key="item.id"
                        :title="item.handle"
                        :score="`Score: ${item.score}`"
                        :prepend-avatar="item.avatar"
                    >
                        <template v-slot:prepend>
                            <v-icon v-if="index === 0" icon="fa-crown fa-solid" color="yellow-darken-4" size="x-large"></v-icon>
                            <span class="text-h5 mr-10" v-else>#{{ index+1 }}</span>
                            <v-avatar>
                                <img :src="item.avatar" alt="avatar">
                            </v-avatar>
                        </template>
                        <span class="text-h6">Score: {{ item.score }}</span>
                    </v-list-item>
                </v-list>
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
