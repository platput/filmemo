<template>
    <v-form class="ml-5 pr-5">
        <div class="text-caption">Number of Users</div>
        <v-slider
            v-model="state.userCount"
            :max="60"
            :step="1"
            thumb-label
            class="my-4"
        >
            <template v-slot:append>
                <v-text-field
                    v-model="state.userCount"
                    type="number"
                    style="width: 80px"
                    density="compact"
                    hide-details
                    variant="solo"
                ></v-text-field>
            </template>
        </v-slider>
        <div class="text-caption">Number of Rounds</div>
        <v-slider
            v-model="state.roundCount"
            :max="60"
            :step="1"
            thumb-label
            class="my-4"
        >
            <template v-slot:append>
                <v-text-field
                    v-model="state.roundCount"
                    type="number"
                    style="width: 80px"
                    density="compact"
                    hide-details
                    variant="solo"
                ></v-text-field>
            </template>
        </v-slider>
        <div class="text-caption">Round Duration: (in Minutes)</div>
        <v-slider
            v-model="state.roundDuration"
            :max="10"
            :step="1"
            thumb-label
            class="my-4"
        >
            <template v-slot:append>
                <v-text-field
                    v-model="state.roundDuration"
                    type="number"
                    style="width: 80px"
                    density="compact"
                    hide-details
                    variant="solo"
                ></v-text-field>
            </template>
        </v-slider>
        <v-text-field
            v-model="state.userHandle"
            label="Your Handle"
            density="compact"
            variant="solo"
            required
          ></v-text-field>        
        <AvatarSelector @set-avatar="setAvatar" />
        <div class="text-center pb-5">
            <v-btn @click="handleCreateGameClick" :disabled="isCreateGameDisabled" rounded="false" variant="flat" :loading="state.isLoading">
                Create Game
            </v-btn>
        </div>
    </v-form>
</template>

<script setup lang="ts">
import { computed, reactive } from 'vue';
import AvatarSelector from './AvatarSelector.vue';
import constants from '@/utils/constants.js'
import { useUserStore } from '@/stores/user';
import { useGameStore } from '@/stores/game';
import { useRouter } from 'vue-router';

const user = useUserStore()
const game = useGameStore()
const router = useRouter()

const state = reactive({
    userCount: 1,
    roundCount: 1,
    roundDuration: 1,
    userHandle: "",
    userAvatar: "",
    isLoading: false,
})

const isCreateGameDisabled = computed(() => {
    return !state.userHandle || !state.userAvatar || state.isLoading;
})

function setAvatar(avatarUrl:string) {
    state.userAvatar = avatarUrl;
}

function handleCreateGameClick() {
    if (state.userHandle && state.userAvatar) {
        createGame();
    } else {
        alert("Please enter your handle and select an avatar before creating a game.");
    }
}

function createGame() {
    state.isLoading = true;
    const data = {
        handle: state.userHandle,
        avatar: state.userAvatar,
        user_count: state.userCount,
        round_count: state.roundCount,
        round_duration: state.roundDuration
    };
    fetch(constants.apiCreateGameUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    }).then(async (response) => {
        let responseData =  await response.json();
        user.setUser(responseData.created_by_player, state.userHandle, state.userAvatar);
        game.setGame(responseData.game_id, responseData.created_by_player, state.userCount, state.roundCount, state.roundDuration);
        router.push(`/game/${game.getGameId()}`)
    }).catch((err) => {
        // TODO: Handling of this error has to be improved.
        alert("Error occurred while trying to create the game, please try again later.")
        console.log(err)
    });
}
</script>