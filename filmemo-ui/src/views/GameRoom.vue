<script setup lang="ts">
import InfoCard from '@/components/InfoCard.vue';
import MovieCard from '@/components/MovieCard.vue';
import PlayersList from '@/components/PlayersList.vue';
import ShareGame from '@/components/ShareGame.vue';
import router from '@/router';
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
const loadingMessage = ref("Loading...")
const emoji = ref("")
const roundId = ref("")

onBeforeMount(() => {
    loadingMessage.value = "Fetching Game!"
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
              const message_data = JSON.parse(event.data)
              if (message_data.message_type == "new_round") {
                console.log("roundId: " + roundId.value)
                console.log("message_data.meta.round_id: " + message_data.meta.round_id)
                  roundId.value = message_data.meta.round_id
                  emoji.value = message_data.meta.emoji
              } else if(message_data.message_type == "end_game") {
                console.log("Game Ended!")
                router.push(`/game/${gameId}/results`)
              } else if (message_data.message_type == "guess_result") {
                let guessCorrectnessFlag = message_data.meta.guess_result;
                console.log("guessCorrectnessFlag", guessCorrectnessFlag);
              }
            })
        } else {
            invalidGame.value = true
            alert("You are trying to join an invalid game.")
        }
        isLoading.value = false
        loadingMessage.value = "Loading..."
    }).catch((err) => {
        isLoading.value = false
        loadingMessage.value = "Loading..."
        // TODO: Handling of this error has to be improved.
        invalidGame.value = true
        alert("Unexpected error while trying to join the game.")
        console.log(err)
    });  
})
function submitGuess(movieName:string) {
  isLoading.value = true
  loadingMessage.value = "Waiting for other players..."
  const data = {
    game_id: gameStore.getGameId(),
    round_id: roundId.value,
    player_id: userStore.getUserID(),
    movie_name: movieName
  }
  fetch(constants.apiSubmitGuessUrl, {
    method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
  }).then(() => {
    isLoading.value = false
    loadingMessage.value = "Loading..."
  })
}
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
            <div v-if="invalidGame" class="text-center">
                <v-icon icon="fa-duotone fa-triangle-exclamation"></v-icon>
                <p class="text-h4 py-10">Invalid Game URL</p>
            </div>
            <div v-else>
                <ShareGame v-if="isCurrentUserGameOwner()" />
                <MovieCard :emoji="emoji" @submit-guess="submitGuess"/>
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
