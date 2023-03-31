<script setup lang="ts">
import InfoCard from '@/components/InfoCard.vue';
import PlayersList from '@/components/PlayersList.vue';
import ShareGame from '@/components/ShareGame.vue';
import { useGameStore } from '@/stores/game';
import { useUserStore } from '@/stores/user';
import constants from '@/utils/constants';
import { ref, onBeforeMount } from 'vue';
import { useRoute } from 'vue-router';

const userStore = useUserStore()
const gameStore = useGameStore()

function isCurrentUserGameOwner() {
    return userStore.getUserID() == gameStore.getGameCreator()
}

const route = useRoute()
const gameId = route.params.gameId
const invalidGame = ref(false);
const isLoading = ref(true);

onBeforeMount(() => {
    // Checking if the game id is valid
    const data = {"game_id": gameId}
    fetch(constants.apiVerifyGameUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    }).then(async (response) => {
        isLoading.value = false
        if(response.status == 200) {
            const data = await response.json()
            gameStore.setGame(data.game_id, data.created_by, data.user_count, data.round_count, data.round_duration)
            invalidGame.value = false
            const socket = new WebSocket(constants.websocketUrl + `/${data.game_id}/${userStore.getUserID()}`)
            socket.addEventListener('message', event => {
              console.log(event.data)
            })
        } else {
            invalidGame.value = true
            alert("You are trying to join an invalid game.")
        }
        isLoading.value = false
    }).catch((err) => {
        isLoading.value = false
        // TODO: Handling of this error has to be improved.
        invalidGame.value = true
        alert("Unexpected error while trying to join the game.")
        console.log(err)
    });
    
})
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
            <p class="text-h4 pb-10">Fetching Game!</p>
          </div>
          <div v-else>
            <div v-if="invalidGame" class="text-center">
                <v-icon icon="fa-duotone fa-triangle-exclamation"></v-icon>
                <p class="text-h4 py-10">Invalid Game URL</p>
            </div>
            <div v-else>
                <ShareGame v-if="isCurrentUserGameOwner()" />
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
