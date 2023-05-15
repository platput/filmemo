<script setup lang="ts">
import InfoCard from '@/components/InfoCard.vue';
import MovieCard from '@/components/MovieCard.vue';
// import PlayersList from '@/components/PlayersList.vue';
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
    return userStore.getCurrentUserID() == gameStore.getGameCreator()
}

const route = useRoute()
const gameId = route.params.gameId
const invalidGame = ref(false);
const isLoading = ref(true);
const loadingMessage = ref("Loading...")
const emoji = ref("")
const roundId = ref("")
const resultSnackbarText = ref("")
const resultSnackbar = ref(false)

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
        if(response.status == 200) {
            loadingMessage.value = "Waiting for players to join..."
            const data = await response.json()
            gameStore.setGame(data.game_id, data.created_by, data.user_count, data.round_count, data.round_duration, false)
            invalidGame.value = false
            const socket = new WebSocket(constants.websocketUrl + `/${data.game_id}/${userStore.getCurrentUserID()}`)
            socket.addEventListener('message', event => {
              const message_data = JSON.parse(event.data)
              if (message_data.message_type == "new_round") {
                gameStore.setGameStartedFlag();
                // console.log("roundId: " + roundId.value)
                // console.log("message_data.meta.round_id: " + message_data.meta.round_id)
                  roundId.value = message_data.meta.round_id
                  emoji.value = message_data.meta.emoji
                  isLoading.value = false;
              } else if(message_data.message_type == "end_game") {
                // console.log("Game Ended!")
                loadingMessage.value = "Game finished, loading results..."
                socket.close();
                userStore.clear()
                router.push(`/game/${gameId}/results`)
              } else if(message_data.message_type == "player_join") {
                // console.log(message_data.meta);
                // console.log("Player Joined!");
                if (userStore.getPlayersList().length <= 1) {
                  message_data.meta.existing_players.forEach((player: { id: string; handle: string; avatar: string; }) => {
                    const userID = player.id;
                    const userHandle = player.handle;
                    const userAvatar = player.avatar;
                    userStore.addPlayer(userID, userHandle, userAvatar);
                  });
                }
                const userID = message_data.meta.new_player.id;
                const userHandle = message_data.meta.new_player.handle;
                const userAvatar = message_data.meta.new_player.avatar;
                userStore.addPlayer(userID, userHandle, userAvatar);
              } else if(message_data.message_type == "game_start") {
                // console.log("game_start!");
                isLoading.value = false;
                // console.log(message_data);
              } else if (message_data.message_type == "guess_result") {
                let guessCorrectnessFlag = message_data.meta.guess_result;
                resultSnackbar.value = true;
                if(guessCorrectnessFlag) {
                  resultSnackbarText.value = "👏 You guessed it right!"
                } else {
                  resultSnackbarText.value = "👎 Sorry, your guess is wrong!"
                }
              }
            })
        } else {
            invalidGame.value = true
            alert("You are trying to join an invalid game.")
        }        
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
    player_id: userStore.getCurrentUserID(),
    movie_name: movieName
  }
  fetch(constants.apiSubmitGuessUrl, {
    method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
  })
}
function startGame() {
  const data = {
    game_id: gameStore.getGameId(),
    player_id: userStore.getCurrentUserID(),
  }
   fetch(constants.apiStartGameUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
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
        <!-- <v-sheet
          rounded="lg"
          min-height="268"
        >
          <PlayersList />
        </v-sheet> -->
      </v-col>

      <v-col
        cols="12"
        sm="8"
      >
        <v-sheet
          min-height="70vh"
          rounded="lg"
        >
          <ShareGame v-if="isCurrentUserGameOwner()" />
          <div v-if="isLoading" class="text-center">
            <v-progress-circular indeterminate :size="128" :width="12" color="brown" class="my-10"></v-progress-circular>
            <p class="text-h4 pb-10">{{ loadingMessage }}</p>
            <div v-if="isCurrentUserGameOwner() && !gameStore.checkIfGameHasStarted()" class="py-20">
              <v-btn @click="startGame()" class="mx-auto mb-15">
                Start Game
              </v-btn>
            </div>
          </div>
          <div v-else>
            <div v-if="invalidGame" class="text-center">
                <v-icon icon="fa-duotone fa-triangle-exclamation"></v-icon>
                <p class="text-h4 py-10">Invalid Game URL</p>
            </div>
            <div v-else>
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
    <v-snackbar
      v-model="resultSnackbar"
      :timeout="2000"
    >
      {{ resultSnackbarText }}

      <template v-slot:actions>
        <v-btn
          color="blue"
          variant="text"
          @click="resultSnackbar = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>
