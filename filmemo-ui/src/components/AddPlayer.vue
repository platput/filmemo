<template>
    <v-form class="ml-5 pr-5">
        <v-text-field
            v-model="state.userHandle"
            label="Your Handle"
            density="compact"
            variant="solo"
            required
          ></v-text-field>        
          <AvatarSelector @set-avatar="setAvatar" />
        <div class="text-center">
            <v-btn rounded="false" @click="joinGame" variant="flat">Join Game</v-btn>
        </div>
    </v-form>
</template>

<script setup lang="ts">
import { reactive } from 'vue';
import AvatarSelector from './AvatarSelector.vue';
import constants from '@/utils/constants';
import router from '@/router';
import { useUserStore } from '@/stores/user';
import { useRoute } from 'vue-router';

const user = useUserStore()
const route = useRoute()
const gameId = route.params.gameId
const state = reactive({
    userHandle: "",
    userAvatar: "",
    isLoading: false,
})

function joinGame() {
    if (state.userHandle && state.userAvatar) {
        addPlayer();
    } else {
        alert("Please enter your handle and select an avatar before creating a game.");
    }
}

function setAvatar(avatarUrl: string) {
    state.userAvatar = avatarUrl
}

function addPlayer() {
    state.isLoading = true;
    const data = {
        handle: state.userHandle,
        avatar: state.userAvatar,
        game_id: gameId
    };
    fetch(constants.apiAddPlayerUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    }).then(async (response) => {
        let responseData =  await response.json();
        user.setUser(responseData.player_id, state.userHandle, state.userAvatar);
        router.push(`/game/${gameId}`)
    }).catch((err) => {
        // TODO: Handling of this error has to be improved.
        alert("Error occurred while trying to join the game, please try again later.")
        console.log(err)
    });
}

</script>
<style scoped>
</style>